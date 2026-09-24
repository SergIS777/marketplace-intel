import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class Quest {
  final String title;
  final String desc;
  final int xp;
  bool done;
  Quest({required this.title, required this.desc, required this.xp, this.done = false});
}

class PathScreen extends StatefulWidget {
  const PathScreen({super.key});
  @override
  State<PathScreen> createState() => _PathScreenState();
}

class _PathScreenState extends State<PathScreen> {
  int _xp = 120;
  final List<Quest> _quests = [
    Quest(title: 'Анкета продавца', desc: 'Расскажи о целях и интересах — подберём нишу', xp: 20, done: true),
    Quest(title: 'Выбор ниши', desc: 'AI-рекомендация по 6 параметрам рынка', xp: 30, done: true),
    Quest(title: 'Регистрация WB Partners', desc: 'Создай профиль продавца по нашей карте', xp: 40),
    Quest(title: 'Первая карточка товара', desc: 'Собери карточку с AI-помощником', xp: 50),
    Quest(title: 'Первая поставка', desc: 'Посчитай юнит-экономику и отгрузи', xp: 60),
    Quest(title: 'Первая продажа', desc: 'Разбери событие вместе с тренером', xp: 100),
  ];

  int get _doneCount => _quests.where((q) => q.done).length;
  int get _level => (_xp / 100).floor() + 1;

  void _complete(int i) {
    setState(() {
      _xp += _quests[i].xp;
      _quests[i].done = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Путь продавца'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _xpCard(),
          const SizedBox(height: 16),
          ...List.generate(_quests.length, (i) => _questCard(_quests[i], i)),
        ],
      ),
    );
  }

  Widget _xpCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(colors: [AppColors.primary, AppColors.primaryDark]),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Уровень $_level', style: const TextStyle(color: AppColors.textPrimary, fontSize: 18, fontWeight: FontWeight.bold)),
              Text('$_xp XP', style: const TextStyle(color: AppColors.textPrimary, fontSize: 18, fontWeight: FontWeight.bold)),
            ],
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: _doneCount / _quests.length,
              minHeight: 10,
              backgroundColor: Colors.white24,
              valueColor: const AlwaysStoppedAnimation(AppColors.success),
            ),
          ),
          const SizedBox(height: 8),
          Text('$_doneCount из ${_quests.length} шагов START', style: TextStyle(color: AppColors.textPrimary.withOpacity(0.8), fontSize: 13)),
        ],
      ),
    );
  }

  Widget _questCard(Quest q, int i) {
    return InkWell(
      onTap: q.done ? null : () => _complete(i),
      borderRadius: BorderRadius.circular(16),
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(16),
          border: q.done ? Border.all(color: AppColors.success) : null,
        ),
        child: Row(
          children: [
            Icon(q.done ? Icons.check_circle : Icons.radio_button_unchecked,
                color: q.done ? AppColors.success : AppColors.textSecondary, size: 28),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(q.title, style: const TextStyle(color: AppColors.textPrimary, fontSize: 15, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 4),
                  Text(q.desc, style: TextStyle(color: AppColors.textSecondary, fontSize: 12)),
                ],
              ),
            ),
            Text(
              '+${q.xp} XP',
              style: TextStyle(
                color: q.done ? AppColors.textSecondary : AppColors.primary,
                fontSize: 14,
                fontWeight: q.done ? FontWeight.normal : FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}