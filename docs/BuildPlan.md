# Build & Packaging Plan (RoadMap item 9)

> **Decision update:** no installers. The app is a portable single-file
> binary that leaves nothing behind (settings persistence was removed),
> so the `.deb` and Arch `PKGBUILD` were dropped. Shipped artifacts: Linux
> binary, Windows `.exe`, macOS `.dmg` (all built on GitHub Actions). See
> `docs/Build.md`. Sections below on `.deb`/`PKGBUILD` are historical.

## Goal

Produce installable/distributable packages of SquareRoot for:

- **Windows**
- **macOS**
- **Linux**: Arch, Debian, Ubuntu, Kubuntu, Manjaro, CachyOS

Build machine: Linux (this dev/CI environment).

## Constraints discovered

- No Wine, no macOS SDK/toolchain on the Linux build machine → Windows and
  macOS binaries cannot be reliably cross-compiled *or tested* from Linux
  alone. Producing them requires either native Windows/macOS machines or
  CI runners that provide them (e.g. GitHub Actions' `windows-latest` /
  `macos-latest`).
- The app is pure Python + stdlib (`tkinter`, `decimal`) — no compiled
  extensions, no third-party runtime dependencies.
- No existing packaging metadata anywhere (no `setup.py`/`pyproject.toml`),
  and no version string anywhere in the codebase.
- The six named Linux targets collapse into two packaging families:
  - **Debian-based** (`apt`/`dpkg`): Debian, Ubuntu, Kubuntu → one `.deb`
    covers all three (Kubuntu is Ubuntu + KDE; same base packaging).
  - **Arch-based** (`pacman`): Arch, Manjaro, CachyOS → one `PKGBUILD`
    covers all three.
  So "6 distros" really means **2 build recipes**, not 6.
- Docker is available on the build machine, so the Arch package can be
  built and smoke-tested locally via an `archlinux` container even though
  the host itself is Ubuntu. The `.deb` can be built and verified natively
  (`dpkg-deb`, `lintian`) since the host is already Debian-family.

## Proposed architecture

1. **Packaging metadata** — add `pyproject.toml` (PEP 621): package name,
   version (start at `0.1.0`), console/GUI entry point
   (`squareroot-gui = squareroot.ui.app:main`), minimum Python version,
   license. Mirror the version into `squareroot/__init__.py` as
   `__version__` so there is one source of truth every build script reads
   from (no version drift between the `.deb`, the `PKGBUILD`, and the
   PyInstaller builds).

2. **App bundling** — PyInstaller, one spec file per OS target
   (`packaging/pyinstaller/windows.spec`, `macos.spec`, `linux.spec`).
   Onefile builds; the app has no data files beyond source, so specs stay
   simple.

3. **Linux native packages**
   - `packaging/deb/` — `debian/control` + a build script driving
     `dpkg-deb`, producing `squareroot_<version>_amd64.deb`. Runtime deps:
     `python3`, `python3-tk`.
   - `packaging/aur/PKGBUILD` — Arch package definition, `depends=(python
     tk)`. Built/tested locally via Docker (`archlinux` base image +
     `makepkg`).

4. **CI (GitHub Actions)** — a build matrix:
   - `ubuntu-latest`: builds the `.deb`, builds+tests the `PKGBUILD` inside
     an `archlinux` container, and produces a PyInstaller Linux binary.
   - `windows-latest`: PyInstaller `.exe`.
   - `macos-latest`: PyInstaller `.app` + `.dmg`.
   Artifacts are uploaded as workflow artifacts, and optionally attached to
   a GitHub Release when the workflow is triggered by a version tag.

## Open decisions (need your call before I implement)

1. **Windows/macOS build strategy** — GitHub Actions native runners
   (recommended: only reliable option, produces real working artifacts on
   push/tag, though I can't run or verify the Win/Mac legs myself from
   this Linux session) **vs.** Linux-only scope for now (I build and
   verify only what's actually testable here — `.deb` + `PKGBUILD` + a
   Linux PyInstaller binary — and just document the Windows/macOS
   PyInstaller steps for someone with those machines to run later).
2. **Trigger** — build on every push to `main` **vs.** only on version
   tags like `v0.1.0` (recommended: keeps regular pushes fast, avoids
   building installers for every commit).
3. **Distribution** — do built artifacts get published anywhere (GitHub
   Releases) or just produced as CI artifacts for manual download?
4. **Code signing** — unsigned Windows/macOS builds will trigger
   SmartScreen/Gatekeeper warnings on install. Do you have signing
   certificates, or is unsigned acceptable for now?

## Work breakdown (once the above is decided)

1. `pyproject.toml` + `squareroot.__version__`
2. PyInstaller spec files (windows/macos/linux) + smoke-test the Linux one
   locally (headless, via Xvfb)
3. Debian packaging — build & verify the `.deb` locally with `dpkg-deb` +
   `lintian`
4. Arch packaging — build & verify via the `archlinux` Docker container +
   `makepkg`
5. GitHub Actions workflow implementing the matrix, artifact upload (and
   release publishing if tag-triggered)
6. `docs/Build.md` — "build from source" + "install" instructions per
   platform
7. Update `docs/RoadMap.md` to reflect item 9 progress

## Verification plan

- **Local**: install the built `.deb` in a throwaway container/chroot;
  build and install the Arch package via Docker; run the resulting Linux
  PyInstaller binary headless (Xvfb) and confirm it launches and evaluates
  an expression end-to-end.
- **CI**: once the workflow is merged, confirm it runs green on all three
  OS legs. The Windows/macOS artifacts themselves can't be executed or
  verified from this Linux session — that needs either you, or a
  follow-up check against the GitHub Actions run logs/artifacts.
