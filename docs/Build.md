# Build

## Release (CI)

Push a tag; GitHub Actions (`.github/workflows/build.yml`) runs tests on
Linux/Windows/macOS, builds every package and attaches them to a GitHub Release:

```
# bump __version__ in squareroot/__init__.py (and pkgver in packaging/aur/PKGBUILD), commit, then:
git tag v0.1.0 && git push origin v0.1.0
```

`Actions → Build → Run workflow` builds everything without publishing a release.

| Artifact | Runner |
|---|---|
| `squareroot_<v>_all.deb` (Debian/Ubuntu/Kubuntu) | ubuntu |
| `squareroot-<v>-1-any.pkg.tar.zst` (Arch/Manjaro/CachyOS) | ubuntu + archlinux container |
| `SquareRoot-linux-x86_64` | ubuntu |
| `SquareRoot-windows-x86_64.exe` | windows |
| `SquareRoot-macos.dmg` | macos |

Windows/macOS builds are unsigned (SmartScreen/Gatekeeper will warn).

## Local (Linux)

```
pacman -S pyinstaller dpkg xorg-server-xvfb   # Arch/Manjaro
pyinstaller --noconfirm packaging/pyinstaller/squareroot.spec   # dist/SquareRoot
packaging/deb/build_deb.sh                                      # dist/*.deb
packaging/aur/build_pkg.sh                                      # dist/*.pkg.tar.zst (needs committed HEAD)
```
