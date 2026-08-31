#!/usr/bin/env bash
set -euo pipefail

case "${1:-}" in
  build)
    funbuild build
    ;;
  install)
    funbuild install
    ;;
  push)
    funbuild push
    ;;
  clean_history)
    funbuild clean-history
    ;;
  *)
    echo "usage: $0 {build|install|push|clean_history}" >&2
    exit 1
    ;;
esac
