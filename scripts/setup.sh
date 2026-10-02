#!/bin/bash
# code-server / natapp 两个后台服务的统一生命周期管理入口。
# 用法: setup.sh {start|stop|restart|run} {code-server|natapp} {dev|prod}
#       setup.sh status [code-server|natapp] [dev|prod]
#
# - code-server 依赖环境变量 CODE_SERVER_PASSWORD
# - natapp 依赖环境变量 NATAPP_AUTH_TOKEN（或在调用 Python 侧显式传参）
set -euo pipefail

ROOT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
RUN_DIR="$ROOT_DIR/.run"

usage() {
    echo "用法: $0 {start|stop|restart|run} {code-server|natapp} {dev|prod}" >&2
    echo "       $0 status [code-server|natapp] [dev|prod]" >&2
    exit 1
}

pid_file() { echo "$RUN_DIR/$1-$2.pid"; }
log_file() { echo "$RUN_DIR/$1-$2.log"; }

pid_matches() {
    local service="$1" env="$2" pid="$3" cmdline
    [ -r "/proc/$pid/cmdline" ] || return 1
    cmdline=$(tr '\0' ' ' <"/proc/$pid/cmdline")
    [[ "$cmdline" == *"start_cmd '$service' '$env'"* ]]
}

is_running() {
    local f pid
    f="$(pid_file "$1" "$2")"
    [ -f "$f" ] || return 1
    pid=$(cat "$f")
    kill -0 "$pid" 2>/dev/null && pid_matches "$1" "$2" "$pid"
}

check_prod_installed() {
    # prod 只能跑已安装的正式包，不能回退到本仓库源码；
    # 通过比对 funcomputer 包的实际加载路径是否落在本仓库目录内来判断。
    python3 - "$ROOT_DIR" <<'PYEOF'
import os
import sys

root_dir = os.path.realpath(sys.argv[1])
try:
    import funcomputer
except ImportError:
    print("error: 未安装 funcomputer 正式包，请先 pip install funcomputer（或 uv pip install funcomputer）", file=sys.stderr)
    sys.exit(1)

pkg_path = os.path.realpath(funcomputer.__file__)
if pkg_path.startswith(root_dir + os.sep):
    print(
        "error: 当前 funcomputer 是从本仓库源码目录加载的（{}），".format(pkg_path)
        + "prod 模式禁止直接跑源码，请先安装正式发布包",
        file=sys.stderr,
    )
    sys.exit(1)
PYEOF
}

start_cmd() {
    local service="$1"
    local env="$2"
    local py_code
    case "$service" in
        code-server)
            py_code="from funcomputer.install.core_server import start_code_server; start_code_server()"
            ;;
        natapp)
            py_code="from funcomputer.install.core_server import start_natapp; start_natapp()"
            ;;
        *)
            usage
            ;;
    esac
    if [ "$env" = "prod" ]; then
        # 必须显式 `|| exit 1`：do_start 用 `nohup bash -c ...` 起的是一个全新的
        # shell，它不会继承本脚本顶部的 `set -e`，所以只写 `check_prod_installed`
        # 的话校验失败后仍然会继续往下跑 python3，prod 校验等于被架空（实测过）。
        check_prod_installed || exit 1
        python3 -c "$py_code"
    else
        # dev 模式强制优先加载本仓库 src/ 下的源码，避免被系统/全局环境里
        # 恰好装着的其它 funcomputer 版本掩盖，保证跑的就是本地改动。
        (cd "$ROOT_DIR" && PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}" python3 -c "$py_code")
    fi
}

do_start() {
    local service="$1"
    local env="$2"
    local f pid i
    mkdir -p "$RUN_DIR"
    if is_running "$service" "$env"; then
        echo "$service[$env] 已在运行 (pid $(cat "$(pid_file "$service" "$env")"))" >&2
        exit 1
    fi
    f="$(pid_file "$service" "$env")"
    rm -f "$f"
    # nohup 起的是一个全新的 bash 进程，不会继承当前 shell 里的变量/函数，
    # 必须显式 export，否则子进程里 ROOT_DIR 为空；CODE_SERVER_PASSWORD/
    # NATAPP_AUTH_TOKEN 等环境变量本身会随进程环境自动继承，无需额外处理。
    # usage 也要 export：start_cmd 的兜底分支会调用它。
    export ROOT_DIR
    export -f start_cmd check_prod_installed usage
    # setsid 让服务自成一个会话/进程组，这样 do_stop 可以 `kill -- -PGID`
    # 一次带走 bash 包装层 + python 解释器 + 底下真正的 code-server/natapp。
    # 只 kill 包装层 PID 的话，真正的服务会被 reparent 成孤儿继续运行，
    # 而脚本已经打印了「已停止」（实测过，对无认证 code-server 尤其危险）。
    # pid 由包装层自己写 $$：setsid 在自身已是进程组首进程时会先 fork，
    # 那种情况下 $! 拿到的是 setsid 而不是 bash，不能依赖 $!。
    setsid nohup bash -c "echo \$\$ >'$f'; start_cmd '$service' '$env'" \
        >"$(log_file "$service" "$env")" 2>&1 &
    for i in 1 2 3 4 5 6 7 8 9 10; do
        [ -s "$f" ] && break
        sleep 0.1
    done
    if [ ! -s "$f" ]; then
        echo "$service[$env] 启动失败：未能记录 pid，详见 $(log_file "$service" "$env")" >&2
        exit 1
    fi
    pid=$(cat "$f")
    echo "$service[$env] 已在后台启动 (pid $pid)"
}

# 打印 pid 所在的进程组号；仅当进程组首进程就是 pid 本身时才输出，
# 否则返回非 0——避免误杀本脚本自己所在的进程组。
own_pgid() {
    local pid="$1" pgid
    pgid=$(ps -o pgid= -p "$pid" 2>/dev/null | tr -d ' ')
    [ -n "$pgid" ] && [ "$pgid" = "$pid" ] || return 1
    echo "$pgid"
}

do_stop() {
    local service="$1"
    local env="$2"
    local f pid pgid i
    f="$(pid_file "$service" "$env")"
    if ! is_running "$service" "$env"; then
        echo "$service[$env] 未在运行"
        rm -f "$f"
        return
    fi
    pid=$(cat "$f")
    pgid=$(own_pgid "$pid" || true)
    if [ -n "$pgid" ]; then
        kill -- "-$pgid" 2>/dev/null || true
    else
        kill "$pid" 2>/dev/null || true
    fi
    # 等它真的退出；SIGTERM 两秒内没走掉就 SIGKILL，不留孤儿。
    for i in $(seq 1 20); do
        kill -0 "$pid" 2>/dev/null || break
        sleep 0.1
    done
    if kill -0 "$pid" 2>/dev/null; then
        if [ -n "$pgid" ]; then
            kill -9 -- "-$pgid" 2>/dev/null || true
        else
            kill -9 "$pid" 2>/dev/null || true
        fi
    fi
    rm -f "$f"
    echo "$service[$env] 已停止"
}

do_run() {
    local service="$1"
    local env="$2"
    mkdir -p "$RUN_DIR"
    start_cmd "$service" "$env"
}

do_status() {
    local service="$1" env="$2"
    if is_running "$service" "$env"; then
        echo "$service[$env] 运行中 (pid $(cat "$(pid_file "$service" "$env")"))"
    else
        echo "$service[$env] 未运行"
    fi
}

do_all_status() {
    local service env
    for service in code-server natapp; do
        for env in dev prod; do
            do_status "$service" "$env"
        done
    done
}

action="${1:-}"
service="${2:-}"
env="${3:-}"

case "$action" in
    start|stop|restart|run)
        case "$service" in
            code-server|natapp) ;;
            *) usage ;;
        esac
        [ "$env" = "dev" ] || [ "$env" = "prod" ] || usage
        ;;
    status)
        if [ -n "$service" ]; then
            case "$service" in
                code-server|natapp) ;;
                *) usage ;;
            esac
            [ -z "$env" ] || [ "$env" = "dev" ] || [ "$env" = "prod" ] || usage
        fi
        ;;
    *)
        usage
        ;;
esac

case "$action" in
    start)
        do_start "$service" "$env"
        ;;
    stop)
        do_stop "$service" "$env"
        ;;
    restart)
        do_stop "$service" "$env" || true
        do_start "$service" "$env"
        ;;
    run)
        do_run "$service" "$env"
        ;;
    status)
        if [ -z "$service" ]; then
            do_all_status
        elif [ -z "$env" ]; then
            do_status "$service" dev
            do_status "$service" prod
        else
            do_status "$service" "$env"
        fi
        ;;
    *)
        usage
        ;;
esac
