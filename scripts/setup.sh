#!/bin/bash
# code-server / natapp 两个后台服务的统一生命周期管理入口。
# 用法: setup.sh {start|stop|restart|run} {code-server|natapp}
#       setup.sh status [code-server|natapp]
#
# - code-server 依赖环境变量 CODE_SERVER_PASSWORD
# - natapp 依赖环境变量 NATAPP_AUTH_TOKEN（或在调用 Python 侧显式传参）
set -euo pipefail

ROOT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
RUN_DIR="$ROOT_DIR/.run"

usage() {
    echo "用法: $0 {start|stop|restart|run} {code-server|natapp}" >&2
    echo "       $0 status [code-server|natapp]" >&2
    exit 1
}

pid_file() { echo "$RUN_DIR/$1.pid"; }
log_file() { echo "$RUN_DIR/$1.log"; }

pid_matches() {
    local service="$1" pid="$2" cmdline
    [ -r "/proc/$pid/cmdline" ] || return 1
    cmdline=$(tr '\0' ' ' <"/proc/$pid/cmdline")
    case "$service" in
        code-server) [[ "$cmdline" == *"start_code_server"* ]] ;;
        natapp) [[ "$cmdline" == *"start_natapp"* ]] ;;
    esac
}

pid_file_state() {
    local f pid
    f="$(pid_file "$1")"
    [ -f "$f" ] || return 1
    pid=$(cat "$f")
    [[ "$pid" =~ ^[1-9][0-9]*$ ]] || return 2
    kill -0 "$pid" 2>/dev/null && pid_matches "$1" "$pid" && return 0
    return 2
}

is_running() {
    pid_file_state "$1"
}

start_cmd() {
    local service="$1"
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
    cd "$ROOT_DIR"
    exec env PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}" python3 -c "$py_code"
}

do_start() {
    local service="$1"
    local f pid i state
    mkdir -p "$RUN_DIR"
    if pid_file_state "$service"; then
        echo "$service 已在运行 (pid $(cat "$(pid_file "$service")"))" >&2
        exit 1
    else
        state=$?
    fi
    f="$(pid_file "$service")"
    if [ "$state" -eq 2 ]; then
        echo "$service 检测到陈旧 PID 文件，正在清理: $f" >&2
    fi
    rm -f "$f"
    # nohup 起的是一个全新的 bash 进程，不会继承当前 shell 里的变量/函数，
    # 必须显式 export，否则子进程里 ROOT_DIR 为空；CODE_SERVER_PASSWORD/
    # NATAPP_AUTH_TOKEN 等环境变量本身会随进程环境自动继承，无需额外处理。
    # usage 也要 export：start_cmd 的兜底分支会调用它。
    export ROOT_DIR
    export -f start_cmd usage
    # setsid 让服务自成一个会话/进程组，这样 do_stop 可以 `kill -- -PGID`
    # 一次带走 Python 服务入口和底下真正的 code-server/natapp。
    # 只 kill 服务入口 PID 的话，真正的服务会被 reparent 成孤儿继续运行，
    # 而脚本已经打印了「已停止」（实测过，对无认证 code-server 尤其危险）。
    # pid 由启动 shell 自己写 $$：setsid 在自身已是进程组首进程时会先 fork，
    # 那种情况下 $! 拿到的是 setsid 而不是 bash，不能依赖 $!。
    setsid nohup bash -c "echo \$\$ >'$f'; start_cmd '$service'" \
        >"$(log_file "$service")" 2>&1 &
    for i in 1 2 3 4 5 6 7 8 9 10; do
        [ -s "$f" ] && break
        sleep 0.1
    done
    if [ ! -s "$f" ]; then
        echo "$service 启动失败：未能记录 pid，详见 $(log_file "$service")" >&2
        return 1
    fi
    pid=$(cat "$f")
    # PID 文件写入并不代表服务成功启动；短暂确认包装进程仍在运行。
    for i in 1 2 3 4 5 6 7 8 9 10; do
        if ! is_running "$service"; then
            rm -f "$f"
            echo "$service 启动失败：进程提前退出，详见 $(log_file "$service")" >&2
            return 1
        fi
        sleep 0.1
    done
    echo "$service 已在后台启动 (pid $pid)"
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
    local f pid pgid i
    f="$(pid_file "$service")"
    if ! is_running "$service"; then
        echo "$service 未在运行"
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
    echo "$service 已停止"
}

do_run() {
    local service="$1"
    mkdir -p "$RUN_DIR"
    start_cmd "$service"
}

do_status() {
    local service="$1"
    if is_running "$service"; then
        echo "$service 运行中 (pid $(cat "$(pid_file "$service")"))"
    else
        echo "$service 未运行"
    fi
}

do_all_status() {
    local service
    for service in code-server natapp; do
        do_status "$service"
    done
}

action="${1:-}"
service="${2:-}"
[ "$#" -le 2 ] || usage

case "$action" in
    start|stop|restart|run)
        case "$service" in
            code-server|natapp) ;;
            *) usage ;;
        esac
        ;;
    status)
        if [ -n "$service" ]; then
            case "$service" in
                code-server|natapp) ;;
                *) usage ;;
            esac
        fi
        ;;
    *)
        usage
        ;;
esac

case "$action" in
    start)
        do_start "$service"
        ;;
    stop)
        do_stop "$service"
        ;;
    restart)
        do_stop "$service" || true
        do_start "$service"
        ;;
    run)
        do_run "$service"
        ;;
    status)
        if [ -z "$service" ]; then
            do_all_status
        else
            do_status "$service"
        fi
        ;;
    *)
        usage
        ;;
esac
