# Changelog

## Unreleased

### 新增

- 依赖补充版本下限，新增 `uv.lock` 保证可复现构建。

### 修复

- `script/build.sh` 里 `if [ "push" = "push" ]` 恒真的判断错误，导致无论传什么参数都会执行 push；改为对 `$1` 做正确匹配并启用 `set -euo pipefail`。

### 变更

- 源码目录改为 `src/funcomputer/` 标准布局（原 `funcomputer/` 平铺在仓库根目录）。
- `script/build.sh` 改用 `funbuild build/install/push/clean-history`，不再调用已不存在的 `setup.py`。
- 内部命令执行改用 `funshell.run_shell`，失败时抛出 `RuntimeError` 而不是静默吞掉退出码。
- 日志改用 `farlog.getLogger`，不再使用 `funtool.log` 或裸 `print`。
- **破坏性变更**：Renamed the Python package / import name from `notecomputer` to
  `funcomputer` to match the GitHub repo name (part of farfarfun/todo-list#298).
  Update any imports from `notecomputer...` to `funcomputer...`.
  `notecomputer` was never published to PyPI (confirmed via
  `pypi.org/pypi/notecomputer/json` returning 404), so no forwarding release of the
  old name is needed. Out of scope for this change: `git@github.com:notechats/notecomputer.git`
  clone URLs still hardcoded in `funcomputer/workspace/core.py`,
  `funcomputer/install/config.py`, and `script/core.sh` reference the pre-rename
  GitHub org/repo and were left as-is — this rename only covers the internal
  package/import name, not those external references.

### 废弃

（无）
