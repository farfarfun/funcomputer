# Changelog

## Unreleased

### Breaking

- Renamed the Python package / import name from `notecomputer` to `funcomputer` to
  match the GitHub repo name (part of farfarfun/todo-list#298). Update any imports
  from `notecomputer...` to `funcomputer...`.
- `notecomputer` was never published to PyPI (confirmed via
  `pypi.org/pypi/notecomputer/json` returning 404), so no forwarding release of the
  old name is needed.
- Out of scope for this change: `git@github.com:notechats/notecomputer.git` clone
  URLs still hardcoded in `funcomputer/workspace/core.py`,
  `funcomputer/install/config.py`, and `script/core.sh` reference the pre-rename
  GitHub org/repo and were left as-is — this rename only covers the internal
  package/import name, not those external references.
