import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Профиль'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(color: AppColors.surface, borderRadius: BorderRadius.circular(16)),
            child: Row(
              children: [
                CircleAvatar(radius: 30, backgroundColor: AppColors.primary,
                    child: const Icon(Icons.person, size: 32, color: AppColors.textPrimary)),
                const SizedBox(width: 16),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Тестовый продавец', style: TextStyle(color: AppColors.textPrimary, fontSize: 17, fontWeight: FontWeight.w600)),
                    const SizedBox(height: 4),
                    Text('test@example.com', style: TextStyle(color: AppColors.textSecondary, fontSize: 13)),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          _row(Icons.store, 'Магазин: LOWENGRASS'),
          _row(Icons.category, 'Тариф: START (бесплатно)'),
          _row(Icons.emoji_events, 'Наград получено: 2'),
          _row(Icons.card_giftcard, 'Реферальный код: LOWEN-2026'),
        ],
      ),
    );
  }

  Widget _row(IconData icon, String text) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(color: AppColors.surface, borderRadius: BorderRadius.circular(12)),
      child: Row(
        children: [
          Icon(icon, color: AppColors.primary, size: 20),
          const SizedBox(width: 12),
          Text(text, style: const TextStyle(color: AppColors.textPrimary, fontSize: 14)),
        ],
      ),
    );
  }
}