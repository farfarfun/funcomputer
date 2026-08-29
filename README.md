# funcomputer

Google Colab / 云端开发环境的个人一次性配置脚本集合：挂载 Google Drive、恢复 SSH 和 Git 配置、安装并启动 code-server（网页版 VSCode）、通过 natapp 做内网穿透、拉取 fun 系列仓库到 workspace。代码里硬编码了大量个人路径（如 `/content/gdrive/My Drive/core/configs/`）和账号信息，本质是作者自用的 Colab 环境初始化脚本，没有做通用化封装，也没有 CLI 入口，目前不在维护中。

该包未发布到 PyPI，因此本 README 不提供 `pip install` 说明。

## 结构

- `funcomputer/run/__init__.py`：`run_cmd(cmd)`，执行 shell 命令（传 list 时用 `&&` 拼接后执行）
- `funcomputer/config/core.py`：`config_all()` / `config_init()` / `config_ssh()` / `config_git()` / `config_workspace()`，从 Google Drive 恢复 SSH key、配置 git 用户名邮箱，并把 `funtool`、`funkeras`、`fundrive`、`funcomputer` 克隆到 `/root/workspace`
- `funcomputer/install/base.py`：`install_drive()` 挂载 Google Drive；`install_code_server()` 安装 code-server 并装一批 VSCode 插件；`start_code_server()` / `start_natapp()` 后台启动 code-server 和 natapp 内网穿透
- `funcomputer/install/core_server.py`：`config_all()` / `config_ssh()`，同样是从 Google Drive 恢复个人配置

## 用法示例

```python
from funcomputer.install.base import install_drive, install_code_server, start_code_server
from funcomputer.config.core import config_all

install_drive()        # 挂载 Google Drive（需在 Colab 环境中运行）
config_all()           # 从 Drive 恢复 ssh/git 配置，克隆 fun 系列仓库
install_code_server()  # 安装 code-server 及常用插件
start_code_server()    # 后台启动 code-server
```

## 说明

代码中的路径（`/content/gdrive/...`）、git 账号邮箱、natapp token 等都是写死的个人配置，直接搬到其他环境大概率跑不通，需要按自己的情况修改。项目没有测试、没有对外发布，属于一次性的个人工具脚本。
