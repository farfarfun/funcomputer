# funcomputer

Google Colab / 云端开发环境的个人一次性配置脚本集合：挂载 Google Drive、恢复 SSH 和 Git 配置、安装并启动 code-server（网页版 VSCode）、通过 natapp 做内网穿透、拉取 fun 系列仓库到 workspace。代码里硬编码了大量个人路径（如 `/content/gdrive/My Drive/core/configs/`）和账号信息，本质是作者自用的 Colab 环境初始化脚本，没有做通用化封装，也没有 CLI 入口，目前不在维护中。

该包未发布到 PyPI，只能从源码安装：

```bash
git clone git@github.com:farfarfun/funcomputer.git
cd funcomputer
pip install -e .
```

## 结构

- `funcomputer/run/__init__.py`：`run_cmd(cmd)`，执行 shell 命令（传 list 时依次执行，遇到失败即抛出 `RuntimeError`）
- `funcomputer/config/core.py`：`config_all()` / `config_ssh()`，从 Google Drive 恢复 SSH key
- `funcomputer/install/config.py`：`config_all()` / `config_init()` / `config_ssh()` / `config_git()` / `config_workspace()`，从 Google Drive 恢复 SSH key、配置 git 用户名邮箱，并把 `funtool`、`funkeras`、`fundrive`、`funcomputer` 克隆到 `/root/workspace`
- `funcomputer/install/core_server.py`：`install_drive()` 挂载 Google Drive；`install_code_server()` 安装 code-server 并装一批 VSCode 插件；`start_code_server()` / `start_natapp()` 后台启动 code-server 和 natapp 内网穿透
- `funcomputer/workspace/core.py`：`init()`，创建 `/root/workspace` 并克隆 fun 系列仓库

## 用法示例

```python
from funcomputer.install.core_server import install_drive, install_code_server, start_code_server
from funcomputer.install.config import config_all

install_drive()        # 挂载 Google Drive（需在 Colab 环境中运行）
config_all()           # 从 Drive 恢复 ssh/git 配置，克隆 fun 系列仓库
install_code_server()  # 安装 code-server 及常用插件
start_code_server()    # 后台启动 code-server（需先设置 CODE_SERVER_PASSWORD 环境变量）
```

## 说明

代码中的路径（`/content/gdrive/...`）、git 账号邮箱、natapp token 等都是写死的个人配置，直接搬到其他环境大概率跑不通，需要按自己的情况修改。项目只有 `tests/test_smoke.py` 一个导入冒烟测试，没有对外发布，属于一次性的个人工具脚本。

---

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
