# Build

The app is distributed as portable binaries (no installer). It writes nothing
to disk (the UI language comes from the system locale), so deleting the binary
removes it completely.

## Release (CI)

Push a tag; GitHub Actions (`.github/workflows/build.yml`) runs tests on
Linux/Windows/macOS, builds the binaries and attaches them to a GitHub Release:

```
# bump __version__ in squareroot/__init__.py, commit, then:
git tag v0.1.0 && git push origin v0.1.0
```

`Actions → Build → Run workflow` builds everything without publishing a release
(artifacts appear on the run page).

| Artifact | Runner |
|---|---|
| `SquareRoot-linux-x86_64` | ubuntu |
| `SquareRoot-windows-x86_64.exe` | windows |
| `SquareRoot-macos-arm64.dmg` | macos-latest (Apple Silicon) |
| `SquareRoot-macos-x86_64.dmg` | macos-15-intel (Intel Macs) |

The two macOS builds are separate on purpose: PyInstaller bundles the runner's
Python, and a universal2 build would need every bundled binary to be fat.
Each job checks the architecture with `lipo` and prints the minimum macOS
version (`minos`), then launches the app for 5 seconds.

Windows/macOS builds are unsigned (SmartScreen/Gatekeeper will warn).
Supported OS versions and hardware: `docs/SystemRequirements.md`.

## Local (Linux)

```
pip install pyinstaller
pyinstaller --noconfirm packaging/pyinstaller/squareroot.spec   # dist/SquareRoot
```
