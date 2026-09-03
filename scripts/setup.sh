#!/bin/bash
# code-server / natapp 两个后台服务的统一生命周期管理入口。
# 用法: setup.sh {start|stop|restart|run|status} {code-server|natapp} {dev|prod}
#
# - code-server 依赖环境变量 CODE_SERVER_PASSWORD
# - natapp 依赖环境变量 NATAPP_AUTH_TOKEN（或在调用 Python 侧显式传参）
set -euo pipefail

ROOT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
RUN_DIR="$ROOT_DIR/.run"

usage() {
    echo "用法: $0 {start|stop|restart|run|status} {code-server|natapp} {dev|prod}" >&2
    exit 1
}

pid_file() { echo "$RUN_DIR/$1.pid"; }
log_file() { echo "$RUN_DIR/$1.log"; }

is_running() {
    local f
    f="$(pid_file "$1")"
    [ -f "$f" ] && kill -0 "$(cat "$f")" 2>/dev/null
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
        check_prod_installed
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
    mkdir -p "$RUN_DIR"
    if is_running "$service"; then
        echo "$service 已在运行 (pid $(cat "$(pid_file "$service")"))" >&2
        exit 1
    fi
    # nohup 起的是一个全新的 bash 进程，不会继承当前 shell 里的变量/函数，
    # 必须显式 export，否则子进程里 ROOT_DIR 为空；CODE_SERVER_PASSWORD/
    # NATAPP_AUTH_TOKEN 等环境变量本身会随进程环境自动继承，无需额外处理。
    export ROOT_DIR
    export -f start_cmd check_prod_installed
    nohup bash -c "start_cmd '$service' '$env'" >"$(log_file "$service")" 2>&1 &
    echo $! > "$(pid_file "$service")"
    echo "$service 已在后台启动 (env=$env, pid $(cat "$(pid_file "$service")"))"
}

do_stop() {
    local service="$1"
    if ! is_running "$service"; then
        echo "$service 未在运行" >&2
        rm -f "$(pid_file "$service")"
        return
    fi
    kill "$(cat "$(pid_file "$service")")"
    rm -f "$(pid_file "$service")"
    echo "$service 已停止"
}

do_run() {
    local service="$1"
    local env="$2"
    mkdir -p "$RUN_DIR"
    start_cmd "$service" "$env"
}

do_status() {
    local service="$1"
    if is_running "$service"; then
        echo "$service 运行中 (pid $(cat "$(pid_file "$service")"))"
    else
        echo "$service 未运行"
    fi
}

action="${1:-}"
service="${2:-}"
env="${3:-}"

case "$service" in
    code-server|natapp)
        ;;
    *)
        usage
        ;;
esac

case "$action" in
    start|stop|restart|run)
        [ "$env" = "dev" ] || [ "$env" = "prod" ] || usage
        ;;
esac

case "$action" in
    start)
        do_start "$service" "$env"
        ;;
    stop)
        do_stop "$service"
        ;;
    restart)
        do_stop "$service" || true
        do_start "$service" "$env"
        ;;
    run)
        do_run "$service" "$env"
        ;;
    status)
        do_status "$service"
        ;;
    *)
        usage
        ;;
esac
