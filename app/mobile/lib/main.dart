import 'package:flutter/material.dart';
import 'screens/login_screen.dart';

void main() {
  runApp(const MarketplaceIntelApp());
}

class MarketplaceIntelApp extends StatelessWidget {
  const MarketplaceIntelApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Marketplace Intel',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF6C5CE7)),
        useMaterial3: true,
        navigationBarTheme: NavigationBarThemeData(
          labelTextStyle: MaterialStatePropertyAll(
            TextStyle(color: Colors.white.withOpacity(0.72), fontSize: 12),
          ),
        ),
      ),
      home: const LoginScreen(),
    );
  }
}

