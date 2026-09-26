#!/bin/sh
# SquareRoot: полное удаление (Linux / macOS).
# Использование: sh uninstall.sh [путь-к-SquareRoot-или-SquareRoot.app]
# Без аргумента ищет программу в текущей папке, ~/Downloads, ~/Desktop, /Applications.
set -u

remove() { [ -e "$1" ] && rm -rf -- "$1" && echo "удалено: $1"; }

# Не удаляем то, что сейчас запущено.
if pgrep -x 'SquareRoot|SquareRoot-linu' >/dev/null 2>&1; then
    echo "Закройте SquareRoot и запустите скрипт ещё раз." >&2
    exit 1
fi

if [ $# -gt 0 ]; then
    remove "$1"
else
    for dir in "$PWD" "$HOME/Downloads" "$HOME/Desktop" "$HOME/Загрузки" "$HOME/Рабочий стол" /Applications "$HOME/Applications"; do
        remove "$dir/SquareRoot-linux-x86_64"
        remove "$dir/SquareRoot.app"
        for f in "$dir"/SquareRoot-macos-*.dmg; do [ -e "$f" ] && remove "$f"; done
    done
fi

# Остатки распаковки PyInstaller (остаются только после аварийного завершения).
TMP="${TMPDIR:-/tmp}"
for d in "$TMP"/_MEI*; do
    [ -e "$d/SQUAREROOT_BUNDLE" ] && remove "$d"
done

# macOS: сохранённое системой состояние окна и кэш.
remove "$HOME/Library/Saved Application State/com.imredtea.squareroot.savedState"
remove "$HOME/Library/Caches/com.imredtea.squareroot"
remove "$HOME/Library/Preferences/com.imredtea.squareroot.plist"

echo "SquareRoot удалён полностью."
