# DESIGN GUIDELINES — Marketplace Intel (Фаза 2)

Принцип: приложение — личная игра, а не серый кабинет. Тёмная сцена, один акцент,
состояния читаются без подписей.

## Палитра
| Токен | Hex | Применение |
|---|---|---|
| background | #0B101A | фон экрана |
| surface | #1A2130 | карточки, поля ввода |
| surfaceNav | #161B26 | нижняя навигация |
| primary | #6C5CE7 | кнопки, иконки, аватар, градиент начала |
| primaryDark | #5A4BD8 | конец градиента прогресс-карточки |
| primarySoft | #E4DEFB | pill активного таба |
| primaryText | #8B7CF7 | XP и акцентный текст |
| success | #2DD4A7 | выполнено, прогресс-бар, цены |
| error | #E57373 | ошибки |
| textPrimary | #F5F7FA | основной текст |
| textSecondary | #8A94A6 | вторичный текст, рейтинги |

## Типографика (scale)
heroTitle 32/w700 · screenTitle 28/w600 · progressTitle 22/w700 ·
cardTitle 17-18/w600 · body 15 · cardSecondary 13.5 · price 18-20/w700 ·
button 17/w600 · error 14.5

## Скругления и отступы
card 16 · button 16 · field 12 · pill full · паддинги экрана 20-24 · зазор между карточками 12-16

## Состояния
- Шаг квеста: done = рамка success 1.5 + галка success; not_done = без рамки, круг-контур textSecondary; XP у done = textSecondary, у not_done = primaryText
- Кнопка: normal primary / pressed primaryDark / disabled surface + textSecondary
- Навигация: активный таб = pill primarySoft + иконка primary + label textPrimary; неактивный = иконка/label textSecondary

## Иконки (Material, фикс-набор)
storefront (магазин/магазин-строка), explore (путь), person (профиль/аватар),
check_circle (done), radio_button_unchecked (not_done), trophy (награды),
card_giftcard (рефералка), category (тариф), star (рейтинг)

## Правила
1. Экраны не пишут hex и TextStyle напрямую — только AppColors/AppText/AppCards/AppButtons.
2. Новый компонент = сначала токен в app_theme.dart, потом виджет.
3. Рефактор экрана на токены = отдельный коммит.