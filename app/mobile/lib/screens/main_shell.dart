import 'package:flutter/material.dart';
import 'store_screen.dart';
import 'path_screen.dart';
import 'profile_screen.dart';

class MainShell extends StatefulWidget {
  final String token;
  final String tariff;
  const MainShell({super.key, required this.token, required this.tariff});
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
      body: screens[_index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.store), selectedIcon: Icon(Icons.store), label: 'Магазин'),
          NavigationDestination(icon: Icon(Icons.explore), selectedIcon: Icon(Icons.explore), label: 'Путь'),
          NavigationDestination(icon: Icon(Icons.person), selectedIcon: Icon(Icons.person), label: 'Профиль'),
        ],
      ),
    );
  }
}