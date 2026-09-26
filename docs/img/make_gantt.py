# Regenerates docs/img/gantt.png (run from the repo root: python docs/img/make_gantt.py).
# The Mermaid version in docs/ProjectManagement.md mirrors the task list below.
import datetime as dt, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

START = dt.date(2026, 9, 28)  # день 1 = понедельник
def day(n):  # рабочий день n (1..10) -> дата
    d, k = START, 1
    while k < n:
        d += dt.timedelta(days=1)
        if d.weekday() < 5: k += 1
    return d

# (секция, id, задача, исполнитель, день_начала, длительность_в_раб_днях, milestone)
T = [
 ("Старт","t1","Kickoff, требования, роли","Все",1,1,0),
 ("Старт","t2","Архитектура и контракт API","РП",1,2,0),
 ("Старт","t3","Репозиторий, CI, правила веток","Адм",1,2,0),
 ("Старт","t4","План, Гант, бюджет, план поддержки","РП+Адм",2,1,0),
 ("Ядро","t5","Complex на Decimal","Ядро",2,2,0),
 ("Ядро","t6","Парсер выражений","РП",3,2,0),
 ("Ядро","t7","Упрощение и точная форма","Ядро",4,2,0),
 ("Ядро","t8","Ошибки и отказоустойчивость","РП+Ядро",5,2,0),
 ("Ядро","m1","Ядро готово (API заморожен)","",6,0,1),
 ("Интерфейс","t9","Макет, каркас на заглушке API","UI",2,2,0),
 ("Интерфейс","t10","Дизайн-документ","UI",3,1,0),
 ("Интерфейс","t11","Локализация (5 языков)","UI",4,2,0),
 ("Интерфейс","t12","Интеграция с ядром, точность","UI",6,2,0),
 ("Сборка","t13","Сборка Win/macOS/Linux в CI","Адм",5,3,0),
 ("Сборка","t14","Система обновлений","Адм+UI",7,2,0),
 ("Сборка","t15","Переносимость, скрипты удаления","Адм",8,1,0),
 ("Качество","t16","Тест-план, юнит-тесты","QA",3,4,0),
 ("Качество","t17","Чёрный ящик, покрытие","QA",6,3,0),
 ("Качество","m2","Feature freeze","",8,0,1),
 ("Документы","t18","Техническая документация","РП",8,2,0),
 ("Документы","t19","README, требования, установка","QA",8,2,0),
 ("Релиз","t20","Регресс, релиз v1.0","Все",9,1,0),
 ("Релиз","t21","Буфер, сдача","Все",10,1,0),
 ("Релиз","m3","Сдача проекта","",10,0,1),
]

# ---- mermaid
lines = ["gantt", "    title SquareRoot: 2 недели (10 рабочих дней)", "    dateFormat YYYY-MM-DD",
         "    axisFormat %d.%m", "    excludes weekends"]
sec = None
for s, i, name, who, d0, dur, ms in T:
    if s != sec:
        lines.append(f"    section {s}"); sec = s
    if ms:
        lines.append(f"    {name} :milestone, {i}, {day(d0)}, 0d")
    else:
        crit = "crit, " if i in ("t2","t5","t8","t12","t20") else ""
        lines.append(f"    {name} ({who}) :{crit}{i}, {day(d0)}, {dur}d")
print("\n".join(lines))  # Mermaid source for docs/ProjectManagement.md

# ---- png
colors = {"Старт":"#64748b","Ядро":"#0f766e","Интерфейс":"#7c3aed","Сборка":"#c2410c","Качество":"#2563eb","Документы":"#a16207","Релиз":"#be123c"}
fig, ax = plt.subplots(figsize=(11, 7.5), dpi=150)
rows = list(reversed(T))
for y, (s, i, name, who, d0, dur, ms) in enumerate(rows):
    label = f"{name}" + (f"  [{who}]" if who else "")
    if ms:
        ax.scatter(d0 - 0.02, y, marker="D", s=70, color="#111827", zorder=3)
    else:
        ax.barh(y, dur, left=d0 - 1, height=0.6, color=colors[s],
                edgecolor="#111827" if i in ("t2","t5","t8","t12","t20") else "none", linewidth=1.4)
    ax.text(-0.15, y, label, ha="right", va="center", fontsize=8.5)
ax.set_yticks([]); ax.set_xlim(0, 10.15); ax.set_ylim(-0.8, len(rows) - 0.2)
ax.set_xticks([k + 0.5 for k in range(10)])
ax.set_xticklabels([f"Д{k+1}\n{day(k+1).strftime('%d.%m')}" for k in range(10)], fontsize=8)
for k in range(11): ax.axvline(k, color="#e5e7eb", lw=0.8, zorder=0)
ax.axvline(5, color="#9ca3af", lw=1.2, ls="--", zorder=0)
for sp in ("top","right","left"): ax.spines[sp].set_visible(False)
ax.legend(handles=[Patch(color=c, label=k) for k, c in colors.items()] +
          [Patch(facecolor="white", edgecolor="#111827", label="критический путь")],
          loc="lower center", bbox_to_anchor=(0.3, -0.16), ncol=4, fontsize=7.5, frameon=False)
ax.set_title("SquareRoot — диаграмма Ганта (10 рабочих дней, ◆ — вехи)", fontsize=11, loc="left", x=-0.45)
plt.subplots_adjust(left=0.38, right=0.98, top=0.93, bottom=0.17)
plt.savefig("docs/img/gantt.png")
