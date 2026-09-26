# Build

The app is distributed as portable binaries (no installer). Settings are the
only thing it writes: `~/.squareroot/config.json` (chosen language).

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
| `SquareRoot-macos.dmg` | macos |

Windows/macOS builds are unsigned (SmartScreen/Gatekeeper will warn).

## Local (Linux)

```
pip install pyinstaller
pyinstaller --noconfirm packaging/pyinstaller/squareroot.spec   # dist/SquareRoot
```
