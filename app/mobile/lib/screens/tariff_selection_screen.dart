import 'package:flutter/material.dart';
import '../theme/app_theme.dart' as theme;
import 'main_shell.dart';

class TariffSelectionScreen extends StatelessWidget {
  final String token;
  const TariffSelectionScreen({super.key, required this.token});

  void _selectTariff(BuildContext context, String tariff) {
    if (tariff == 'START') {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => MainShell(token: token, tariff: 'START')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Этот тариф станет доступен после успешного прохождения обучения в START 🚀'),
          backgroundColor: theme.AppColors.surface,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: theme.AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text('Выберите тариф', style: theme.AppText.screenTitle),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Инвестиция в ваш успех на Wildberries', style: theme.AppText.subtitle),
            const SizedBox(height: 20),
            
            _TariffCard(
              title: 'START',
              price: '5 000 ₽ / мес',
              subtitle: 'Идеально для новичков без магазина',
              // ЯРКАЯ БРОНЗА с переливом
              gradient: const LinearGradient(
                colors: [Color(0xFFFFD700), Color(0xFFE6A817), Color(0xFFCD7F32)],
                stops: [0.0, 0.5, 1.0],
              ),
              buttonColor: const Color(0xFFE6A817),
              iconColor: const Color(0xFFFFD700),
              icon: Icons.school,
              benefits: [
                'Научитесь запускать бизнес с нуля без риска',
                'Получите персонального AI-наставника 24/7',
                'Узнайте реальные цифры конкурентов до старта',
                'Пройдёте 6 шагов до первой регистрации',
              ],
              features: [
                'AI-консультант: отвечает на любые вопросы о WB',
                'Пошаговый план: от бюджета до первой закупки',
                'Анализ реальных магазинов конкурентов',
                'Доступ к данным рынка через API Wildberries',
                '6 практических заданий с проверкой',
              ],
              onTap: () => _selectTariff(context, 'START'),
            ),
            
            const SizedBox(height: 12),
            
            _TariffCard(
              title: 'PRO',
              price: '25 000 ₽ / мес',
              subtitle: 'Полная автоматизация вашего магазина',
              // ЯРКОЕ СЕРЕБРО с белым блеском
              gradient: const LinearGradient(
                colors: [Color(0xFFFFFFFF), Color(0xFFE8E8E8), Color(0xFFC0C0C0)],
                stops: [0.0, 0.5, 1.0],
              ),
              buttonColor: const Color(0xFFE8E8E8),
              iconColor: const Color(0xFFFFFFFF),
              icon: Icons.analytics,
              isLocked: true,
              benefits: [
                'Замените менеджера за 60-140 тысяч в месяц',
                'Работает 24/7 без выходных и больничных',
                'Видит ваших конкурентов и предупреждает об угрозах',
                'Отвечает покупателям вашим голосом',
              ],
              features: [
                'Авто-синхронизация с 1С каждые 15 минут',
                'AI отвечает на отзывы в вашем стиле',
                'Мониторинг конкурентов с мгновенными алертами',
                'Финансовые отчёты: прибыль, комиссии, налоги',
                'До 5 магазинов в одном приложении',
              ],
              onTap: () => _selectTariff(context, 'PRO'),
            ),
            
            const SizedBox(height: 12),
            
            _TariffCard(
              title: 'MAX',
              price: '40 000 ₽ / мес',
              subtitle: 'AI создаёт продающий контент за вас',
              // ЯРКОЕ ЗОЛОТО с оранжевым переливом
              gradient: const LinearGradient(
                colors: [Color(0xFFFFF700), Color(0xFFFFD700), Color(0xFFFFA500)],
                stops: [0.0, 0.5, 1.0],
              ),
              buttonColor: const Color(0xFFFFD700),
              iconColor: const Color(0xFFFFF700),
              icon: Icons.auto_awesome,
              isLocked: true,
              benefits: [
                'Забудьте о фотографах и дизайнерах',
                'Создавайте карточки быстрее конкурентов',
                'Тестируйте разные варианты и увеличивайте CTR',
                'Экономьте 15-30 тысяч в месяц на контенте',
              ],
              features: [
                'Всё из тарифа PRO',
                'Безлимитная генерация инфографики для карточек',
                'A/B-тесты главных фото для роста продаж',
                'Автозагрузка готовых фото в карточки WB',
                'Профессиональная нейросеть ComfyUI',
              ],
              onTap: () => _selectTariff(context, 'MAX'),
            ),
          ],
        ),
      ),
    );
  }
}

class _TariffCard extends StatelessWidget {
  final String title;
  final String price;
  final String subtitle;
  final Gradient gradient;
  final Color buttonColor;
  final Color iconColor;
  final IconData icon;
  final List<String> benefits;
  final List<String> features;
  final bool isLocked;
  final VoidCallback onTap;

  const _TariffCard({
    required this.title,
    required this.price,
    required this.subtitle,
    required this.gradient,
    required this.buttonColor,
    required this.iconColor,
    required this.icon,
    required this.benefits,
    required this.features,
    this.isLocked = false,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: theme.AppColors.surface,
        borderRadius: BorderRadius.circular(theme.AppRadii.card),
        border: Border.all(
          color: theme.AppColors.textSecondary.withOpacity(0.15),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: buttonColor.withOpacity(0.3),
            blurRadius: 15,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  gradient: gradient,
                  borderRadius: BorderRadius.circular(10),
                  boxShadow: [
                    BoxShadow(
                      color: iconColor.withOpacity(0.6),
                      blurRadius: 10,
                      offset: const Offset(0, 3),
                    ),
                  ],
                ),
                child: Icon(icon, color: Colors.white, size: 20),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(title, style: theme.AppText.cardTitle.copyWith(fontSize: 20, fontWeight: FontWeight.w700)),
                        if (isLocked)
                          Icon(Icons.lock_outline, color: theme.AppColors.textSecondary.withOpacity(0.5), size: 18),
                      ],
                    ),
                    Text(subtitle, style: theme.AppText.cardSecondary.copyWith(fontSize: 12)),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(price, style: theme.AppText.price.copyWith(fontSize: 18, fontWeight: FontWeight.w700)),
          const SizedBox(height: 12),
          
          Text('Что вы получите:', style: theme.AppText.cardTitle.copyWith(fontSize: 14, fontWeight: FontWeight.w600)),
          const SizedBox(height: 6),
          ...benefits.map((f) => Padding(
            padding: const EdgeInsets.only(bottom: 5),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  margin: const EdgeInsets.only(top: 2),
                  padding: const EdgeInsets.all(2),
                  decoration: BoxDecoration(
                    gradient: gradient,
                    borderRadius: BorderRadius.circular(3),
                    boxShadow: [
                      BoxShadow(
                        color: iconColor.withOpacity(0.4),
                        blurRadius: 4,
                        offset: const Offset(0, 1),
                      ),
                    ],
                  ),
                  child: Icon(Icons.star, color: Colors.white, size: 10),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    f,
                    style: theme.AppText.cardSecondary.copyWith(
                      fontSize: 13,
                      color: isLocked ? theme.AppColors.textSecondary.withOpacity(0.7) : theme.AppColors.textPrimary,
                      height: 1.3,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          )).toList(),
          
          const SizedBox(height: 10),
          
          Text('Что входит:', style: theme.AppText.cardSecondary.copyWith(fontSize: 13, fontWeight: FontWeight.w600)),
          const SizedBox(height: 6),
          ...features.map((f) => Padding(
            padding: const EdgeInsets.only(bottom: 5),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  margin: const EdgeInsets.only(top: 2),
                  padding: const EdgeInsets.all(2),
                  decoration: BoxDecoration(
                    gradient: gradient,
                    borderRadius: BorderRadius.circular(3),
                    boxShadow: [
                      BoxShadow(
                        color: iconColor.withOpacity(0.4),
                        blurRadius: 4,
                        offset: const Offset(0, 1),
                      ),
                    ],
                  ),
                  child: Icon(Icons.check, color: Colors.white, size: 10),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    f,
                    style: theme.AppText.cardSecondary.copyWith(
                      fontSize: 12,
                      color: isLocked ? theme.AppColors.textSecondary.withOpacity(0.7) : theme.AppColors.textPrimary,
                      height: 1.3,
                    ),
                  ),
                ),
              ],
            ),
          )).toList(),
          
          const SizedBox(height: 12),
          
          SizedBox(
            width: double.infinity,
            height: 46,
            child: ElevatedButton(
              onPressed: onTap,
              style: ElevatedButton.styleFrom(
                backgroundColor: buttonColor,
                foregroundColor: Colors.black,
                elevation: 3,
                shadowColor: buttonColor.withOpacity(0.6),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(theme.AppRadii.button),
                ),
                padding: const EdgeInsets.symmetric(vertical: 10),
              ),
              child: Text(
                isLocked ? 'Скоро' : 'Начать обучение',
                style: const TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: Colors.black,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}