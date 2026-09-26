import 'package:flutter/material.dart';

/// Дизайн-гайдлайны Marketplace Intel: единственная точка правды для стилей.
abstract class AppColors {
  static const Color background = Color(0xFF0B101A);
  static const Color surface = Color(0xFF1A2130);
  static const Color surfaceNav = Color(0xFF161B26);

  static const Color primary = Color(0xFF6C5CE7);
  static const Color primaryDark = Color(0xFF5A4BD8);
  static const Color primarySoft = Color(0xFFE4DEFB);
  static const Color primaryText = Color(0xFF8B7CF7);

  static const Color success = Color(0xFF2DD4A7);
  static const Color error = Color(0xFFE57373);

  static const Color textPrimary = Color(0xFFF5F7FA);
  static const Color textSecondary = Color(0xFF8A94A6);

  // ============================================
  // ЭКРАН ВХОДА (login_screen.dart)
  // ============================================
  static const Color loginBgStart = Color(0xFF5B21B6); // Глубокий фиолетовый
  static const Color loginBgMid = Color(0xFF6D28D9);   // Фиолетовый Wildberries
  static const Color loginBgEnd = Color(0xFF4C1D95);   // Тёмный фиолетовый
  static const Color loginButton = Color(0xFFE6A817);  // Золотая кнопка "Войти"

  // ============================================
  // ЭКРАН ТАРИФОВ (tariff_selection_screen.dart)
  // ============================================
  // START (Бронза)
  static const Color startBronzeLight = Color(0xFFFFD700);
  static const Color startBronzeMid = Color(0xFFE6A817);
  static const Color startBronzeDark = Color(0xFFCD7F32);
  
  // PRO (Серебро)
  static const Color proSilverLight = Color(0xFFFFFFFF);
  static const Color proSilverMid = Color(0xFFE8E8E8);
  static const Color proSilverDark = Color(0xFFC0C0C0);
  
  // MAX (Золото)
  static const Color maxGoldLight = Color(0xFFFFF700);
  static const Color maxGoldMid = Color(0xFFFFD700);
  static const Color maxGoldDark = Color(0xFFFFA500);

  // ============================================
  // ПУТЬ ПРОДАВЦА (path_screen.dart)
  // ============================================
  static const Color trainerFAB = Color(0xFF00E5FF); // Неоновая голубая кнопка тренера
}

abstract class AppRadii {
  static const double card = 16;
  static const double button = 16;
  static const double field = 12;
  static const double pill = 999;
}

abstract class AppText {
  static const TextStyle heroTitle = TextStyle(
      color: AppColors.textPrimary, fontSize: 32, fontWeight: FontWeight.w700);
  static const TextStyle screenTitle = TextStyle(
      color: AppColors.textPrimary, fontSize: 28, fontWeight: FontWeight.w600);
  static const TextStyle progressTitle = TextStyle(
      color: Colors.white, fontSize: 22, fontWeight: FontWeight.w700);
  static const TextStyle subtitle =
      TextStyle(color: AppColors.textSecondary, fontSize: 15);
  static const TextStyle cardTitle = TextStyle(
      color: AppColors.textPrimary, fontSize: 17, fontWeight: FontWeight.w600);
  static const TextStyle cardSecondary =
      TextStyle(color: AppColors.textSecondary, fontSize: 13.5);
  static const TextStyle price = TextStyle(
      color: AppColors.success, fontSize: 18, fontWeight: FontWeight.w700);
  static const TextStyle rating =
      TextStyle(color: AppColors.textSecondary, fontSize: 14);
  static const TextStyle xp = TextStyle(
      color: AppColors.primaryText, fontSize: 15, fontWeight: FontWeight.w700);
  static const TextStyle xpDone = TextStyle(
      color: AppColors.textSecondary, fontSize: 15, fontWeight: FontWeight.w600);
  static const TextStyle button = TextStyle(
      color: Colors.white, fontSize: 17, fontWeight: FontWeight.w600);
  static const TextStyle error =
      TextStyle(color: AppColors.error, fontSize: 14.5);
}

enum StepState { done, notDone }

abstract class AppCards {
  static BoxDecoration base({StepState state = StepState.notDone}) =>
      BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppRadii.card),
        border: Border.all(
          color: state == StepState.done ? AppColors.success : Colors.transparent,
          width: 1.5,
        ),
      );

  static BoxDecoration progressHeader() => BoxDecoration(
        borderRadius: BorderRadius.circular(AppRadii.card),
        gradient: const LinearGradient(
            colors: [AppColors.primary, AppColors.primaryDark]),
      );
}

abstract class AppButtons {
  static ButtonStyle primary() => ElevatedButton.styleFrom(
        backgroundColor: AppColors.primary,
        disabledBackgroundColor: AppColors.surface,
        foregroundColor: Colors.white,
        disabledForegroundColor: AppColors.textSecondary,
        textStyle: AppText.button,
        minimumSize: const Size.fromHeight(56),
        shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppRadii.button)),
      );
}

abstract class AppTheme {
  static ThemeData get dark => ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        scaffoldBackgroundColor: AppColors.background,
        colorScheme: const ColorScheme.dark(
          primary: AppColors.primary,
          secondary: AppColors.success,
          error: AppColors.error,
          surface: AppColors.surface,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: AppColors.background,
          foregroundColor: AppColors.textPrimary,
          elevation: 0,
          titleTextStyle: AppText.screenTitle,
        ),
        navigationBarTheme: NavigationBarThemeData(
          backgroundColor: AppColors.surfaceNav,
          indicatorColor: AppColors.primarySoft,
          iconTheme: WidgetStateProperty.resolveWith((states) {
            return IconThemeData(
              color: states.contains(WidgetState.selected)
                  ? AppColors.primary
                  : AppColors.textSecondary,
            );
          }),
          labelTextStyle: WidgetStateProperty.resolveWith(
            (states) => states.contains(WidgetState.selected)
                ? AppText.cardSecondary.copyWith(color: AppColors.textPrimary)
                : AppText.cardSecondary,
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: AppColors.surface,
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AppRadii.field),
            borderSide: BorderSide.none,
          ),
        ),
      );
}

// ============================================
// ГРАДИЕНТЫ (AppGradients)
// ============================================
class AppGradients {
  static const LinearGradient loginBackground = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [AppColors.loginBgStart, AppColors.loginBgMid, AppColors.loginBgEnd],
  );

  static const LinearGradient tariffStart = LinearGradient(
    colors: [AppColors.startBronzeLight, AppColors.startBronzeMid, AppColors.startBronzeDark],
    stops: [0.0, 0.5, 1.0],
  );

  static const LinearGradient tariffPro = LinearGradient(
    colors: [AppColors.proSilverLight, AppColors.proSilverMid, AppColors.proSilverDark],
    stops: [0.0, 0.5, 1.0],
  );

  static const LinearGradient tariffMax = LinearGradient(
    colors: [AppColors.maxGoldLight, AppColors.maxGoldMid, AppColors.maxGoldDark],
    stops: [0.0, 0.5, 1.0],
  );
  
  static const LinearGradient goldAccent = LinearGradient(
    colors: [AppColors.startBronzeLight, AppColors.startBronzeMid],
  );
}