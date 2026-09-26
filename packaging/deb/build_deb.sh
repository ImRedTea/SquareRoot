#!/usr/bin/env bash
# Build squareroot_<version>_all.deb. Run from anywhere; output goes to dist/.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VERSION="$(python3 -c "import re;print(re.search(r'__version__ = \"(.+?)\"', open('$ROOT/squareroot/__init__.py').read()).group(1))")"
STAGE="$ROOT/build/deb/squareroot_${VERSION}_all"

rm -rf "$STAGE"
install -d "$STAGE/DEBIAN" "$STAGE/usr/bin" "$STAGE/usr/lib/python3/dist-packages" \
  "$STAGE/usr/share/applications" "$STAGE/usr/share/doc/squareroot"
cp -r "$ROOT/squareroot" "$STAGE/usr/lib/python3/dist-packages/"
find "$STAGE" -name __pycache__ -prune -exec rm -rf {} +
sed "s/@VERSION@/$VERSION/" "$ROOT/packaging/deb/control" > "$STAGE/DEBIAN/control"
printf '#!/bin/sh\nexec python3 -m squareroot.ui "$@"\n' > "$STAGE/usr/bin/squareroot-gui"
chmod 755 "$STAGE/usr/bin/squareroot-gui"
install -m 644 "$ROOT/packaging/common/squareroot.desktop" "$STAGE/usr/share/applications/"
install -m 644 "$ROOT/LICENSE" "$STAGE/usr/share/doc/squareroot/copyright"
find "$STAGE" -type d -exec chmod 755 {} +

mkdir -p "$ROOT/dist"
dpkg-deb --root-owner-group --build "$STAGE" "$ROOT/dist/squareroot_${VERSION}_all.deb"
