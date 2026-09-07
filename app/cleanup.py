"""Гигиена: retention снапшотов + логи. Запуск раз в сутки."""
from pathlib import Path

DATA = Path('/app/data')

def cleanup():
    report = []
    for pattern, keep in [('wb_reviews_2', 14), ('wb_cards_2', 60), ('drafts_2', 10), ('competitors_2', 60)]:
        files = sorted(DATA.glob(f'{pattern}*.csv'))
        for f in files[:-keep]:
            f.unlink()
        report.append(f"{pattern}: оставлено {min(len(files), keep)}")
    for name in ['bot.log', 'sched.log', 'dash.log']:
        p = DATA / name
        if p.exists() and p.stat().st_size > 5 * 1024 * 1024:
            p.write_bytes(p.read_bytes()[-1024 * 1024:])
            report.append(f"{name}: обрезан")
    print(' | '.join(report))

if __name__ == '__main__':
    cleanup()
