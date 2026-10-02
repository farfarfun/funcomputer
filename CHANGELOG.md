# Changelog

## Unreleased

### 新增

- 依赖补充版本下限，新增 `uv.lock` 保证可复现构建。
- `scripts/setup.sh`：code-server / natapp 的统一生命周期管理入口，负责后台化、PID 文件与日志重定向，运行时文件落在 `.run/`。
- `tests/` 按公开 API 补齐正常路径、参数边界与失败路径测试（`run_cmd`、`config_*`、`install_*`、`start_*`、setup.sh 生命周期），外部命令与 Colab 依赖全部用 mock 或假可执行文件隔离。

### 修复

- `script/build.sh` 里 `if [ "push" = "push" ]` 恒真的判断错误，导致无论传什么参数都会执行 push；改为对 `$1` 做正确匹配并启用 `set -euo pipefail`。
- **安全**：`start_natapp()` 不再把 natapp authtoken 写死为函数默认值，改为从显式参数或 `NATAPP_AUTH_TOKEN` 环境变量读取，两者都没有时直接 `raise ValueError`。
- **安全**：`start_code_server()` 不再传 `--auth none`（会暴露一个无需认证、可执行任意代码的 code-server），改为必须通过 `CODE_SERVER_PASSWORD` 提供密码、走 `--auth password`，缺失时拒绝启动。
- `run_cmd()` 抛出的错误信息会把 `NATAPP_AUTH_TOKEN` / `CODE_SERVER_PASSWORD` 的值替换成 `[REDACTED]`，避免凭据随异常进日志。
- `scripts/setup.sh stop` 只 `kill` nohup 的 bash 包装层，底下的 python 解释器和真正的 code-server / natapp 会被 reparent 成孤儿继续运行，而脚本已经打印了「已停止」；改为用 `setsid` 让服务自成进程组，stop 按进程组回收并在 SIGTERM 超时后补 SIGKILL。
- `scripts/setup.sh` 的 prod 校验被架空：`nohup bash -c` 起的是新 shell，不继承脚本顶部的 `set -e`，`check_prod_installed` 失败后仍会继续执行 python3，`start prod` 实际跑的还是仓库源码；改为显式 `|| exit 1`。

### 变更

- 依赖按 SPEC §2 收敛：移除已冻结的 `nltlog`（funshell 1.0.23 起自己声明 `farlog`，不再隐式 import 它），下限提到 `funshell>=1.0.23`、`farlog>=1.1.7`。
- README 改用 uv 安装流程，修正源码路径为 `src/funcomputer/...`，并如实描述「只检查 `SSH_AUTH_SOCK`、不从 Google Drive 恢复 SSH 私钥」的实际行为。
- 运行时依赖清掉源码里并未 import 的 `requests` / `tqdm` / `cryptography` / `pycurl` / `urllib3` / `requests_toolbelt`。
- `config_init()` 改为安装 `ruff`，不再安装 `pylint`（SPEC §7 统一用 ruff 做 lint 与格式化）；新增 `[tool.ruff]` 配置。
- 注释与 docstring 统一中文。
- 删除空文件 `examples/install.py` 和没有任何引用的再导出垫片 `src/funcomputer/install/base.py`（`run_cmd` 的入口是 `funcomputer.run`）。
- 源码目录改为 `src/funcomputer/` 标准布局（原先平铺在仓库根目录）。
- `script/build.sh` 改用 `funbuild build/install/push/clean-history`，不再调用已不存在的 `setup.py`。
- 内部命令执行改用 `funshell.run_shell`，失败时抛出 `RuntimeError` 而不是静默吞掉退出码。
- 日志改用 `farlog.getLogger`，不再使用 `funtool.log` 或裸 `print`。
- **破坏性变更**：import 名改为 `funcomputer`，与 GitHub 仓库名一致（farfarfun/todo-list#298）。
  旧 import 名从未发布到 PyPI，因此不提供转发版本。同时把源码与 `script/core.sh` 里的
  clone 地址统一到 `git@github.com:farfarfun/...`。

### 废弃

（无）
