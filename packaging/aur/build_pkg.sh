#!/usr/bin/env bash
# Build the Arch package. Run on Arch, or inside an archlinux container as a non-root user.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VERSION="$(python -c "import re;print(re.search(r'__version__ = \"(.+?)\"', open('$ROOT/squareroot/__init__.py').read()).group(1))")"
WORK="$ROOT/build/aur"

rm -rf "$WORK"; mkdir -p "$WORK" "$ROOT/dist"
git -C "$ROOT" archive --prefix="squareroot-$VERSION/" -o "$WORK/squareroot-$VERSION.tar.gz" HEAD
sed "s/^pkgver=.*/pkgver=$VERSION/" "$ROOT/packaging/aur/PKGBUILD" > "$WORK/PKGBUILD"
cp "$ROOT/packaging/common/squareroot.desktop" "$WORK/"
cd "$WORK"
makepkg --force --nocheck
cp ./*.pkg.tar.* "$ROOT/dist/"
