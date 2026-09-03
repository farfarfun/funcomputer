#!/usr/bin/env bash
# 全新 Colab/云端环境的一次性初始化脚本：安装发布工具、配置 git、拉取 fun 系列仓库。
# set -e 保证任意一步失败都会立即以非 0 状态退出，不再继续执行后续步骤。
set -euo pipefail

# twine/farfuntool 是要装到宿主机环境里的独立命令行工具，不是 funcomputer 包自身的运行时
# 依赖，因此不登记进 pyproject.toml 的 [project].dependencies；改用 `uv tool install`
# （而非裸 pip）安装，符合“依赖与环境管理必须使用 uv”的约束。
uv tool install twine
uv tool install farfuntool

git config --global user.email "1007530194@qq.com"
git config --global user.name "niuliangtao"

mkdir -vp /root/workspace
cd /root/workspace
git clone git@github.com:farfarfun/funtool.git
git clone git@github.com:farfarfun/funkeras.git
git clone git@github.com:farfarfun/fundrive.git
git clone git@github.com:farfarfun/funcomputer.git
