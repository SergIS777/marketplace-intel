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
  bool _isSubmitting = false;
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

  void _openTrainerChat() {
    final currentQuest = _quests.firstWhere(
      (q) => !q.done,
      orElse: () => _quests.last,
    );

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: theme.AppColors.background,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) => _TrainerChatSheet(quest: currentQuest),
    );
  }

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
              if (_quests[i].feedback == null) ...[
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
              ] else ...[
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: theme.AppColors.background,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: theme.AppColors.success, width: 1.5),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.check_circle, color: theme.AppColors.success, size: 20),
                          const SizedBox(width: 8),
                          const Text('Тренер проверил:', style: theme.AppText.cardTitle),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(_quests[i].feedback!, style: theme.AppText.cardSecondary.copyWith(fontSize: 14)),
                    ],
                  ),
                ),
              ],
            ],
          ),
          actions: [
            if (_quests[i].feedback == null) ...[
              TextButton(
                onPressed: _isSubmitting ? null : Navigator.of(context).pop,
                child: const Text('Отмена', style: TextStyle(color: theme.AppColors.textSecondary)),
              ),
              ElevatedButton(
                onPressed: _isSubmitting
                    ? null
                    : () async {
                        if (controller.text.trim().length < 10) {
                          setDialogState(() => error = 'Минимум 10 символов');
                          return;
                        }
                        setDialogState(() {
                          _isSubmitting = true;
                          error = null;
                        });

                        try {
                          final result = await ApiService().submitQuestProof(
                            _quests[i].id,
                            controller.text.trim(),
                          );

                          setDialogState(() {
                            _isSubmitting = false;
                            _quests[i].feedback = result['feedback'];
                            _quests[i].done = result['is_approved'];
                            if (_quests[i].done) {
                              _xp += (result['xp_awarded'] as num).toInt();
                            }
                          });
                        } catch (e) {
                          setDialogState(() {
                            _isSubmitting = false;
                            error = 'Ошибка сети: ${e.toString()}';
                          });
                        }
                      },
                style: theme.AppButtons.primary(),
                child: _isSubmitting
                    ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                    : const Text('Отправить'),
              ),
            ] else ...[
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: Navigator.of(context).pop,
                  style: theme.AppButtons.primary(),
                  child: const Text('Отлично, понятно'),
                ),
              ),
            ],
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
      // ✅ ИСПРАВЛЕНИЕ 1: Неоновая голубая FAB кнопка
      floatingActionButton: FloatingActionButton.large(
        onPressed: _openTrainerChat,
        backgroundColor: const Color(0xFF00E5FF), // Неоновый голубой
        elevation: 8,
        child: const Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.school, color: Colors.white, size: 32),
            SizedBox(height: 2),
            Text('Тренер', style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.w600)),
          ],
        ),
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

// ✅ ИСПРАВЛЕНИЕ 2: Шторка чата с правильным поведением клавиатуры
class _TrainerChatSheet extends StatefulWidget {
  final Quest quest;
  const _TrainerChatSheet({required this.quest});

  @override
  State<_TrainerChatSheet> createState() => _TrainerChatSheetState();
}

class _TrainerChatSheetState extends State<_TrainerChatSheet> {
  final TextEditingController _controller = TextEditingController();
  final List<Map<String, String>> _messages = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _messages.add({
      'role': 'assistant',
      'content': 'Привет! Я твой AI-тренер. Помогу разобраться с заданием "${widget.quest.title}". Что хочешь узнать?',
    });
  }

  void _sendMessage() async {
    final text = _controller.text.trim();
    if (text.isEmpty) return;

    setState(() {
      _messages.add({'role': 'user', 'content': text});
      _isLoading = true;
    });
    _controller.clear();

    try {
      final response = await ApiService().chatWithTrainer(widget.quest.id, _messages);
      setState(() {
        _messages.add({'role': 'assistant', 'content': response['reply']});
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _messages.add({'role': 'assistant', 'content': 'Извини, произошла ошибка связи с тренером. Попробуй ещё раз.'});
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    // ✅ ИСПРАВЛЕНИЕ: Учитываем высоту клавиатуры
    final keyboardHeight = MediaQuery.of(context).viewInsets.bottom;
    
    return Container(
      height: MediaQuery.of(context).size.height * 0.85,
      decoration: BoxDecoration(
        color: theme.AppColors.background,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
      ),
      // ✅ Поднимаем весь контент на высоту клавиатуры
      padding: EdgeInsets.only(bottom: keyboardHeight),
      child: Column(
        children: [
          // Заголовок шторки
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: theme.AppColors.surface,
              borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('AI-Тренер', style: theme.AppText.cardTitle),
                      Text('Контекст: ${widget.quest.title}', style: theme.AppText.cardSecondary),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close, color: theme.AppColors.textSecondary),
                  onPressed: Navigator.of(context).pop,
                ),
              ],
            ),
          ),
          const Divider(height: 1, color: theme.AppColors.surface),
          
          // Список сообщений
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length + (_isLoading ? 1 : 0),
              itemBuilder: (context, index) {
                if (_isLoading && index == _messages.length) {
                  return const Padding(
                    padding: EdgeInsets.symmetric(vertical: 8),
                    child: Row(
                      children: [
                        CircleAvatar(
                          radius: 16,
                          backgroundColor: theme.AppColors.surface,
                          child: SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2)),
                        ),
                        SizedBox(width: 12),
                        Text('Тренер печатает...', style: theme.AppText.cardSecondary),
                      ],
                    ),
                  );
                }

                final msg = _messages[index];
                final isUser = msg['role'] == 'user';

                return Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: Row(
                    mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (!isUser) ...[
                        const CircleAvatar(
                          radius: 16,
                          backgroundColor: theme.AppColors.primarySoft,
                          child: Icon(Icons.school, color: theme.AppColors.primary, size: 16),
                        ),
                        const SizedBox(width: 8),
                      ],
                      Flexible(
                        child: Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: isUser ? theme.AppColors.primary : theme.AppColors.surface,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            msg['content']!,
                            style: TextStyle(
                              color: isUser ? Colors.white : theme.AppColors.textPrimary,
                              fontSize: 14,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
          
          // Поле ввода
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: theme.AppColors.surface,
              borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    maxLines: null,
                    style: const TextStyle(color: theme.AppColors.textPrimary),
                    decoration: InputDecoration(
                      hintText: 'Задай вопрос тренеру...',
                      hintStyle: const TextStyle(color: theme.AppColors.textSecondary),
                      filled: true,
                      fillColor: theme.AppColors.background,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(24),
                        borderSide: BorderSide.none,
                      ),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    ),
                    onSubmitted: (_) => _sendMessage(),
                  ),
                ),
                const SizedBox(width: 8),
                CircleAvatar(
                  backgroundColor: theme.AppColors.primary,
                  child: IconButton(
                    icon: const Icon(Icons.send, color: Colors.white, size: 20),
                    onPressed: _isLoading ? null : _sendMessage,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}