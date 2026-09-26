# PyInstaller spec for all platforms. Run from the repo root:
#   pyinstaller --noconfirm packaging/pyinstaller/squareroot.spec
import sys

sys.path.insert(0, SPECPATH + "/../..")
from squareroot import __version__

a = Analysis(["../../run_gui.py"], pathex=["../.."])
pyz = PYZ(a.pure)

if sys.platform == "darwin":
    # macOS: onedir + .app bundle (onefile .app is discouraged)
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="SquareRoot", console=False)
    coll = COLLECT(exe, a.binaries, a.datas, name="SquareRoot")
    app = BUNDLE(
        coll,
        name="SquareRoot.app",
        bundle_identifier="com.imredtea.squareroot",
        version=__version__,
    )
else:
    # Windows / Linux: single-file executable
    exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name="SquareRoot", console=False)
