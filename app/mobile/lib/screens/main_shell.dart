import 'package:flutter/material.dart';
import 'store_screen.dart';
import 'path_screen.dart';
import 'profile_screen.dart';

class MainShell extends StatefulWidget {
  final String token;
  const MainShell({super.key, required this.token});
  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    final screens = [
      StoreScreen(token: widget.token),
      const PathScreen(),
      const ProfileScreen(),
    ];
    return Scaffold(
      backgroundColor: const Color(0xFF0E1220),
      body: screens[_index],
      bottomNavigationBar: NavigationBar(
        backgroundColor: const Color(0xFF1A2035),
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.store, color: Colors.white54), selectedIcon: Icon(Icons.store, color: Color(0xFF6C5CE7)), label: 'Магазин'),
          NavigationDestination(icon: Icon(Icons.explore, color: Colors.white54), selectedIcon: Icon(Icons.explore, color: Color(0xFF6C5CE7)), label: 'Путь'),
          NavigationDestination(icon: Icon(Icons.person, color: Colors.white54), selectedIcon: Icon(Icons.person, color: Color(0xFF6C5CE7)), label: 'Профиль'),
        ],
      ),
    );
  }
}
