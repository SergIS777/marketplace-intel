import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart' as theme;

class Quest {
  final String id;
  final String title;
  final String desc;
  final int xp;
  bool done;
  String? feedback;

  Quest({
    required this.id,
    required this.title,
    required this.desc,
    required this.xp,
    this.done = false,
    this.feedback,
  });
}

class PathScreen extends StatefulWidget {
  const PathScreen({super.key});

  @override
  State<PathScreen> createState() => _PathScreenState();
}

class _PathScreenState extends State<PathScreen> {
  int _xp = 120;
  bool _isLoading = false;
  final List<Quest> _quests = [
    Quest(id: 'quest_1', title: 'Анкета продавца', desc: 'Расскажи о целях и интересах — подберём нишу', xp: 20, done: true),
    Quest(id: 'quest_2', title: 'Выбор ниши', desc: 'AI-рекомендация по 6 параметрам рынка', xp: 30, done: true),
    Quest(id: 'quest_3', title: 'Регистрация WB Partners', desc: 'Создай профиль продавца по нашей карте', xp: 40),
    Quest(id: 'quest_4', title: 'Первая карточка товара', desc: 'Собери карточку с AI-помощником', xp: 50),
    Quest(id: 'quest_5', title: 'Первая поставка', desc: 'Посчитай юнит-экономику и отгрузи', xp: 60),
    Quest(id: 'quest_6', title: 'Первая продажа', desc: 'Разбери событие вместе с тренером', xp: 100),
  ];

  int get _doneCount => _quests.where((q) => q.done).length;
  int get _level => (_xp / 100).floor() + 1;

  Future<void> _submitProof(int i) async {
    final controller = TextEditingController();
    String? error;

    await showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          backgroundColor: theme.AppColors.surface,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(theme.AppRadii.card)),
          title: const Text('Сдать доказательство', style: theme.AppText.cardTitle),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(_quests[i].desc, style: theme.AppText.cardSecondary),
              const SizedBox(height: 16),
              TextField(
                controller: controller,
                maxLines: 4,
                style: const TextStyle(color: theme.AppColors.textPrimary),
                decoration: const InputDecoration(
                  hintText: 'Опиши, что ты сделал...',
                  hintStyle: TextStyle(color: theme.AppColors.textSecondary),
                  filled: true,
                  fillColor: theme.AppColors.background,
                ),
              ),
              if (error != null) ...[
                const SizedBox(height: 8),
                Text(error!, style: theme.AppText.error),
              ],
              if (_quests[i].feedback != null) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: theme.AppColors.background,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: theme.AppColors.primarySoft),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('💬 Ответ тренера:', style: theme.AppText.cardSecondary),
                      const SizedBox(height: 4),
                      Text(_quests[i].feedback!, style: theme.AppText.cardTitle.copyWith(fontSize: 14)),
                    ],
                  ),
                ),
              ],
            ],
          ),
          actions: [
            TextButton(
              onPressed: _isLoading ? null : Navigator.of(context).pop,
              child: const Text('Отмена', style: TextStyle(color: theme.AppColors.textSecondary)),
            ),
            ElevatedButton(
              onPressed: _isLoading
                  ? null
                  : () async {
                      if (controller.text.trim().length < 10) {
                        setDialogState(() => error = 'Минимум 10 символов');
                        return;
                      }
                      setDialogState(() {
                        _isLoading = true;
                        error = null;
                      });

                      try {
                        print("🚀 Пытаемся отправить доказательство для: ${_quests[i].id}");
                        final result = await ApiService().submitQuestProof(
                          _quests[i].id,
                          controller.text.trim(),
                        );
                        print("✅ Ответ от бэкенда получен: $result");

                        setDialogState(() {
                          _isLoading = false;
                          _quests[i].feedback = result['feedback'];
                          _quests[i].done = result['is_approved'];
                          if (_quests[i].done) {
                            _xp += (result['xp_awarded'] as num).toInt();
                          }
                        });
                      } catch (e, stackTrace) {
                        print("❌ КРИТИЧЕСКАЯ ОШИБКА Flutter: $e");
                        print("Stack trace: $stackTrace");
                        setDialogState(() {
                          _isLoading = false;
                          error = 'Ошибка: ${e.toString()}';
                        });
                      }
                    },
              style: theme.AppButtons.primary(),
              child: _isLoading
                  ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                  : const Text('Отправить'),
            ),
          ],
        ),
      ),
    );
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Путь продавца')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _xpCard(),
          const SizedBox(height: 16),
          const Text('Текущие квесты', style: theme.AppText.subtitle),
          const SizedBox(height: 12),
          ...List.generate(_quests.length, (i) => _questCard(_quests[i], i)),
        ],
      ),
    );
  }

  Widget _xpCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: theme.AppCards.progressHeader(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Уровень $_level', style: theme.AppText.progressTitle),
              Text('$_xp XP', style: theme.AppText.progressTitle),
            ],
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: _doneCount / _quests.length,
              minHeight: 10,
              backgroundColor: Colors.white24,
              valueColor: const AlwaysStoppedAnimation(theme.AppColors.success),
            ),
          ),
          const SizedBox(height: 8),
          Text('$_doneCount из ${_quests.length} шагов START',
              style: TextStyle(color: theme.AppColors.textPrimary.withOpacity(0.8), fontSize: 13)),
        ],
      ),
    );
  }

  Widget _questCard(Quest q, int i) {
    return InkWell(
      onTap: q.done ? null : () => _submitProof(i),
      borderRadius: BorderRadius.circular(16),
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: theme.AppCards.base(state: q.done ? theme.StepState.done : theme.StepState.notDone),
        child: Row(
          children: [
            Icon(
              q.done ? Icons.check_circle : Icons.radio_button_unchecked,
              color: q.done ? theme.AppColors.success : theme.AppColors.textSecondary,
              size: 28,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(q.title, style: theme.AppText.cardTitle),
                  const SizedBox(height: 4),
                  Text(q.desc, style: theme.AppText.cardSecondary),
                ],
              ),
            ),
            Text(
              '+${q.xp} XP',
              style: TextStyle(
                color: q.done ? theme.AppColors.textSecondary : theme.AppColors.primaryText,
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