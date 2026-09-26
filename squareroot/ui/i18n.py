"""Translation dictionaries and lookup helpers for the SquareRoot UI.

No `tkinter` import here -- like `ui.logic`, this module must stay
importable and unit-testable on systems where Tk is not installed.
"""

import locale
import os

LANGUAGES = {
    "ru": "Русский",
    "en": "English",
    "es": "Español",
    "zh": "中文",
    "ja": "日本語",
}

DEFAULT_LANGUAGE = "ru"

# Language-name prefixes as reported by Windows (e.g. "Russian_Russia").
_WINDOWS_LANGUAGE_NAMES = {
    "russian": "ru",
    "english": "en",
    "spanish": "es",
    "chinese": "zh",
    "japanese": "ja",
}


def detect_language(environ=None, getlocale=locale.getlocale):
    """Pick a UI language from the system locale; never touches the disk.

    Checks LC_ALL, LC_MESSAGES, LANG, then `getlocale()`. Falls back to
    DEFAULT_LANGUAGE for anything unrecognised ("C", "POSIX", empty, ...).
    """
    environ = os.environ if environ is None else environ
    candidates = [environ.get(name) for name in ("LC_ALL", "LC_MESSAGES", "LANG")]
    try:
        candidates.append(getlocale()[0])
    except (ValueError, TypeError, IndexError):
        pass
    for value in candidates:
        if not value:
            continue
        value = value.lower()
        code = value.split("_", 1)[0].split(".", 1)[0]
        if code in LANGUAGES:
            return code
        if code in _WINDOWS_LANGUAGE_NAMES:
            return _WINDOWS_LANGUAGE_NAMES[code]
    return DEFAULT_LANGUAGE

# Human labels for the parser's grammar-terminal token types, used inside
# the expected_token/unexpected_token error templates so a parse error
# never shows a raw internal identifier like "RPAREN" to the user.
_TOKEN_LABELS = {
    "ru": {
        "PLUS": "«+»",
        "MINUS": "«-»",
        "STAR": "«*»",
        "SLASH": "«/»",
        "CARET": "«^»",
        "LPAREN": "«(»",
        "RPAREN": "«)»",
        "NUMBER": "число",
        "IMAG": "мнимое число",
        "IDENT": "идентификатор",
        "EOF": "конец выражения",
    },
    "en": {
        "PLUS": "'+'",
        "MINUS": "'-'",
        "STAR": "'*'",
        "SLASH": "'/'",
        "CARET": "'^'",
        "LPAREN": "'('",
        "RPAREN": "')'",
        "NUMBER": "number",
        "IMAG": "imaginary number",
        "IDENT": "identifier",
        "EOF": "end of expression",
    },
    "es": {
        "PLUS": "«+»",
        "MINUS": "«-»",
        "STAR": "«*»",
        "SLASH": "«/»",
        "CARET": "«^»",
        "LPAREN": "«(»",
        "RPAREN": "«)»",
        "NUMBER": "número",
        "IMAG": "número imaginario",
        "IDENT": "identificador",
        "EOF": "fin de la expresión",
    },
    "zh": {
        "PLUS": "“+”",
        "MINUS": "“-”",
        "STAR": "“*”",
        "SLASH": "“/”",
        "CARET": "“^”",
        "LPAREN": "“(”",
        "RPAREN": "“)”",
        "NUMBER": "数字",
        "IMAG": "虚数",
        "IDENT": "标识符",
        "EOF": "表达式结尾",
    },
    "ja": {
        "PLUS": "「+」",
        "MINUS": "「-」",
        "STAR": "「*」",
        "SLASH": "「/」",
        "CARET": "「^」",
        "LPAREN": "「(」",
        "RPAREN": "「)」",
        "NUMBER": "数値",
        "IMAG": "虚数",
        "IDENT": "識別子",
        "EOF": "式の終端",
    },
}

# Display labels for exception class names. `error_type` itself (the class
# name) always stays untranslated -- this is only for what's shown to the
# user.
_ERROR_TYPE_LABELS = {
    "ru": {
        "TokenizeError": "Ошибка токенизации",
        "ParseError": "Ошибка разбора",
        "DivisionByZeroError": "Деление на ноль",
        "UnknownFunctionError": "Неизвестная функция",
        "UnsupportedOperationError": "Неподдерживаемая операция",
    },
    "en": {
        "TokenizeError": "Tokenize error",
        "ParseError": "Parse error",
        "DivisionByZeroError": "Division by zero",
        "UnknownFunctionError": "Unknown function",
        "UnsupportedOperationError": "Unsupported operation",
    },
    "es": {
        "TokenizeError": "Error de tokenización",
        "ParseError": "Error de análisis",
        "DivisionByZeroError": "División por cero",
        "UnknownFunctionError": "Función desconocida",
        "UnsupportedOperationError": "Operación no admitida",
    },
    "zh": {
        "TokenizeError": "词法错误",
        "ParseError": "解析错误",
        "DivisionByZeroError": "除以零",
        "UnknownFunctionError": "未知函数",
        "UnsupportedOperationError": "不支持的操作",
    },
    "ja": {
        "TokenizeError": "トークン化エラー",
        "ParseError": "構文解析エラー",
        "DivisionByZeroError": "ゼロ除算",
        "UnknownFunctionError": "未知の関数",
        "UnsupportedOperationError": "サポートされていない操作",
    },
}

# Error-message templates, keyed by the `code` set on SquareRootError
# subclasses in squareroot/{parser,simplify,complex_number}.py. Formatted
# against `exc.params`, with `expected`/`found` token types pre-resolved
# through _TOKEN_LABELS before formatting (see translate_error).
_ERROR_TEMPLATES = {
    "ru": {
        "invalid_number": "недопустимое число в позиции {position}",
        "unexpected_character": "неожиданный символ {char!r} в позиции {position}",
        "expected_token": "ожидалось {expected}, но найдено {found} в позиции {position}",
        "unexpected_token": "неожиданный токен {found} в позиции {position}",
        "unknown_function": "неизвестная функция {name!r}",
        "division_by_zero": "деление на ноль",
        "zero_to_nonpositive_power": "0 нельзя возвести в неположительную степень",
        "non_integer_power_complex_base": (
            "нецелая степень поддерживается только для неотрицательного "
            "вещественного основания и вещественного показателя"
        ),
    },
    "en": {
        "invalid_number": "invalid number at position {position}",
        "unexpected_character": "unexpected character {char!r} at position {position}",
        "expected_token": "expected {expected} but found {found} at position {position}",
        "unexpected_token": "unexpected token {found} at position {position}",
        "unknown_function": "unknown function {name!r}",
        "division_by_zero": "division by zero",
        "zero_to_nonpositive_power": "0 cannot be raised to a non-positive power",
        "non_integer_power_complex_base": (
            "a non-integer power is only supported for a non-negative real "
            "base with a real exponent"
        ),
    },
    "es": {
        "invalid_number": "número no válido en la posición {position}",
        "unexpected_character": "carácter inesperado {char!r} en la posición {position}",
        "expected_token": "se esperaba {expected} pero se encontró {found} en la posición {position}",
        "unexpected_token": "token inesperado {found} en la posición {position}",
        "unknown_function": "función desconocida {name!r}",
        "division_by_zero": "división por cero",
        "zero_to_nonpositive_power": "0 no se puede elevar a una potencia no positiva",
        "non_integer_power_complex_base": (
            "una potencia no entera solo se admite para una base real no "
            "negativa con un exponente real"
        ),
    },
    "zh": {
        "invalid_number": "位置 {position} 处的数字无效",
        "unexpected_character": "位置 {position} 处出现意外字符 {char!r}",
        "expected_token": "位置 {position} 处应为 {expected},但发现 {found}",
        "unexpected_token": "位置 {position} 处出现意外的记号 {found}",
        "unknown_function": "未知函数 {name!r}",
        "division_by_zero": "除以零",
        "zero_to_nonpositive_power": "0 不能被提升到非正数次幂",
        "non_integer_power_complex_base": (
            "非整数次幂仅支持非负实数底数与实数指数"
        ),
    },
    "ja": {
        "invalid_number": "位置 {position} に無効な数値があります",
        "unexpected_character": "位置 {position} に予期しない文字 {char!r} があります",
        "expected_token": "位置 {position} では {expected} が期待されましたが、{found} が見つかりました",
        "unexpected_token": "位置 {position} に予期しないトークン {found} があります",
        "unknown_function": "未知の関数 {name!r}",
        "division_by_zero": "ゼロ除算です",
        "zero_to_nonpositive_power": "0 を非正の指数で累乗することはできません",
        "non_integer_power_complex_base": (
            "非整数の指数は、非負の実数の底と実数の指数の場合のみサポートされます"
        ),
    },
}

# Static UI chrome + logic.py templates.
TRANSLATIONS = {
    "ru": {
        "menu.file": "Файл",
        "menu.file.quit": "Выход",
        "menu.edit": "Правка",
        "menu.edit.copy_result": "Копировать результат",
        "menu.help": "Справка",
        "menu.help.about": "О программе SquareRoot",
        "menu.language": "Язык",
        "section.expression": "ВЫРАЖЕНИЕ (ПОД КОРНЕМ)",
        "section.precision": "ТОЧНОСТЬ",
        "section.variables": "ПЕРЕМЕННЫЕ",
        "section.variables_hint": "подставляются в упрощённый результат",
        "button.evaluate": "Извлечь корень",
        "result.ready": "Готово.",
        "status.ready": "Готово",
        "status.ok": "OK",
        "status.symbolic": "Символьно",
        "status.precision": "decimal · точность {precision}",
        "dialog.invalid_precision.title": "Некорректная точность",
        "dialog.invalid_precision.message": (
            "Точность должна быть целым числом от {min} до {max}."
        ),
        "dialog.about.title": "О программе SquareRoot",
        "dialog.about.message": (
            "SquareRoot — калькулятор комплексного квадратного корня\n"
            "Точная десятичная арифметика и аналитическое упрощение, "
            "только стандартная библиотека Python."
        ),
        "header.symbolic_suffix": " упрощается до",
        "hint.provide_value": "Укажите значение свободной переменной(ых) выше, чтобы получить число.",
    },
    "en": {
        "menu.file": "File",
        "menu.file.quit": "Quit",
        "menu.edit": "Edit",
        "menu.edit.copy_result": "Copy Result",
        "menu.help": "Help",
        "menu.help.about": "About SquareRoot",
        "menu.language": "Language",
        "section.expression": "EXPRESSION (UNDER THE SQUARE ROOT)",
        "section.precision": "PRECISION",
        "section.variables": "VARIABLES",
        "section.variables_hint": "substituted into the simplified result",
        "button.evaluate": "Take Square Root",
        "result.ready": "Ready.",
        "status.ready": "Ready",
        "status.ok": "OK",
        "status.symbolic": "Symbolic",
        "status.precision": "decimal · precision {precision}",
        "dialog.invalid_precision.title": "Invalid precision",
        "dialog.invalid_precision.message": (
            "Precision must be a whole number between {min} and {max}."
        ),
        "dialog.about.title": "About SquareRoot",
        "dialog.about.message": (
            "SquareRoot — complex square root calculator\n"
            "Exact decimal arithmetic and analytical simplification, "
            "Python standard library only."
        ),
        "header.symbolic_suffix": " simplifies to",
        "hint.provide_value": "Provide a value for the free variable(s) above to get a number.",
    },
    "es": {
        "menu.file": "Archivo",
        "menu.file.quit": "Salir",
        "menu.edit": "Edición",
        "menu.edit.copy_result": "Copiar resultado",
        "menu.help": "Ayuda",
        "menu.help.about": "Acerca de SquareRoot",
        "menu.language": "Idioma",
        "section.expression": "EXPRESIÓN (BAJO LA RAÍZ CUADRADA)",
        "section.precision": "PRECISIÓN",
        "section.variables": "VARIABLES",
        "section.variables_hint": "se sustituyen en el resultado simplificado",
        "button.evaluate": "Calcular raíz cuadrada",
        "result.ready": "Listo.",
        "status.ready": "Listo",
        "status.ok": "OK",
        "status.symbolic": "Simbólico",
        "status.precision": "decimal · precisión {precision}",
        "dialog.invalid_precision.title": "Precisión no válida",
        "dialog.invalid_precision.message": (
            "La precisión debe ser un número entero entre {min} y {max}."
        ),
        "dialog.about.title": "Acerca de SquareRoot",
        "dialog.about.message": (
            "SquareRoot — calculadora de raíz cuadrada compleja\n"
            "Aritmética decimal exacta y simplificación analítica, "
            "solo con la biblioteca estándar de Python."
        ),
        "header.symbolic_suffix": " se simplifica a",
        "hint.provide_value": "Indique un valor para la(s) variable(s) libre(s) de arriba para obtener un número.",
    },
    "zh": {
        "menu.file": "文件",
        "menu.file.quit": "退出",
        "menu.edit": "编辑",
        "menu.edit.copy_result": "复制结果",
        "menu.help": "帮助",
        "menu.help.about": "关于 SquareRoot",
        "menu.language": "语言",
        "section.expression": "表达式(根号下)",
        "section.precision": "精度",
        "section.variables": "变量",
        "section.variables_hint": "代入化简后的结果",
        "button.evaluate": "求平方根",
        "result.ready": "就绪。",
        "status.ready": "就绪",
        "status.ok": "OK",
        "status.symbolic": "符号结果",
        "status.precision": "decimal · 精度 {precision}",
        "dialog.invalid_precision.title": "精度无效",
        "dialog.invalid_precision.message": "精度必须是介于 {min} 和 {max} 之间的整数。",
        "dialog.about.title": "关于 SquareRoot",
        "dialog.about.message": (
            "SquareRoot — 复数平方根计算器\n"
            "精确的十进制运算与解析化简，仅使用 Python 标准库。"
        ),
        "header.symbolic_suffix": " 化简为",
        "hint.provide_value": "请为上面的自由变量提供值以获得数值结果。",
    },
    "ja": {
        "menu.file": "ファイル",
        "menu.file.quit": "終了",
        "menu.edit": "編集",
        "menu.edit.copy_result": "結果をコピー",
        "menu.help": "ヘルプ",
        "menu.help.about": "SquareRoot について",
        "menu.language": "言語",
        "section.expression": "式 (平方根の中身)",
        "section.precision": "精度",
        "section.variables": "変数",
        "section.variables_hint": "簡略化された結果に代入されます",
        "button.evaluate": "平方根を計算",
        "result.ready": "準備完了。",
        "status.ready": "準備完了",
        "status.ok": "OK",
        "status.symbolic": "記号的",
        "status.precision": "decimal · 精度 {precision}",
        "dialog.invalid_precision.title": "精度が無効です",
        "dialog.invalid_precision.message": "精度は {min} から {max} までの整数で指定してください。",
        "dialog.about.title": "SquareRoot について",
        "dialog.about.message": (
            "SquareRoot — 複素数平方根計算機\n"
            "正確な10進演算と解析的簡略化、Python標準ライブラリのみ使用。"
        ),
        "header.symbolic_suffix": " を簡略化すると",
        "hint.provide_value": "数値を得るには、上の自由変数に値を指定してください。",
    },
}


def translate(lang, key, **kwargs):
    table = TRANSLATIONS.get(lang) or TRANSLATIONS[DEFAULT_LANGUAGE]
    template = table.get(key) or TRANSLATIONS[DEFAULT_LANGUAGE][key]
    return template.format(**kwargs) if kwargs else template


def _token_label(lang, token_type):
    labels = _TOKEN_LABELS.get(lang) or _TOKEN_LABELS[DEFAULT_LANGUAGE]
    return labels.get(token_type, token_type)


def translate_error(lang, exc):
    """Render `exc` (a SquareRootError) in `lang`, falling back to str(exc)
    for anything without a known `code` (e.g. a non-SquareRootError, or a
    future error type that hasn't been given a template yet).
    """
    code = getattr(exc, "code", None)
    templates = _ERROR_TEMPLATES.get(lang) or _ERROR_TEMPLATES[DEFAULT_LANGUAGE]
    if code not in templates:
        return str(exc)

    params = dict(getattr(exc, "params", {}) or {})
    for key in ("expected", "found"):
        if key in params:
            params[key] = _token_label(lang, params[key])
    return templates[code].format(**params)


def error_type_label(lang, exc):
    labels = _ERROR_TYPE_LABELS.get(lang) or _ERROR_TYPE_LABELS[DEFAULT_LANGUAGE]
    class_name = type(exc).__name__
    return labels.get(class_name, class_name)
