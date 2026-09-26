import 'package:flutter/material.dart';
import 'tariff_selection_screen.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart' as theme;

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController(text: 'test@example.com');
  final _passwordController = TextEditingController(text: 'test123');
  bool _isLoading = false;
  String? _error;

  Future<void> _login() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final data = await ApiService().login(
        _emailController.text.trim(),
        _passwordController.text,
      );

      if (mounted) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => TariffSelectionScreen(token: data['access_token']),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Неверный email или пароль. Проверьте подключение.';
          _isLoading = false;
        });
      }
    }
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF5B21B6),
              Color(0xFF6D28D9),
              Color(0xFF4C1D95),
            ],
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Spacer(flex: 1),
                
                // ЛОГОТИП — иконка приложения
                Image.asset(
                  'assets/icon.png',
                  width: 140,
                  height: 140,
                  fit: BoxFit.contain,
                ),
                
                const SizedBox(height: 24),
                
                // НАЗВАНИЕ
                const Text(
                  'MY MARKET W',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 32,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 1.5,
                    shadows: [
                      Shadow(
                        color: Colors.black26,
                        offset: Offset(0, 2),
                        blurRadius: 4,
                      ),
                    ],
                  ),
                ),
                
                const SizedBox(height: 8),
                
                // ПОДПИСЬ
                Text(
                  'Интеллектуальная аналитика Wildberries',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.7),
                    fontSize: 14,
                    letterSpacing: 0.5,
                  ),
                  textAlign: TextAlign.center,
                ),
                
                const SizedBox(height: 40),
                
                // РАЗДЕЛИТЕЛЬНАЯ ЛИНИЯ (золотая)
                Container(
                  width: 80,
                  height: 4,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFFFFD700), Color(0xFFE6A817)],
                    ),
                    borderRadius: BorderRadius.circular(2),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFFFFD700).withOpacity(0.6),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                ),
                
                const SizedBox(height: 40),
                
                // EMAIL
                _buildInputLabel('Email'),
                const SizedBox(height: 8),
                _buildTextField(_emailController, 'test@example.com', false),
                
                const SizedBox(height: 20),
                
                // ПАРОЛЬ
                _buildInputLabel('Пароль'),
                const SizedBox(height: 8),
                _buildTextField(_passwordController, '••••••••', true),
                
                if (_error != null) ...[
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.red.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: Colors.red.withOpacity(0.5),
                      ),
                    ),
                    child: Text(
                      _error!,
                      style: const TextStyle(color: Colors.red),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ],
                
                const SizedBox(height: 32),
                
                // КНОПКА ВОЙТИ
                SizedBox(
                  width: double.infinity,
                  height: 56,
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _login,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFFE6A817),
                      foregroundColor: Colors.black,
                      elevation: 8,
                      shadowColor: const Color(0xFFE6A817).withOpacity(0.5),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: _isLoading
                        ? const SizedBox(
                            width: 24,
                            height: 24,
                            child: CircularProgressIndicator(
                              color: Colors.black,
                              strokeWidth: 3,
                            ),
                          )
                        : const Text(
                            'Войти в систему',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w700,
                              letterSpacing: 0.5,
                            ),
                          ),
                  ),
                ),
                
                const SizedBox(height: 16),
                
                // ЗАБЫЛИ ПАРОЛЬ
                TextButton(
                  onPressed: () {},
                  child: Text(
                    'Забыли пароль?',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.6),
                      fontSize: 14,
                    ),
                  ),
                ),
                
                const Spacer(flex: 1),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildInputLabel(String label) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Text(
        label,
        style: TextStyle(
          color: Colors.white.withOpacity(0.85),
          fontSize: 14,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Widget _buildTextField(TextEditingController controller, String hint, bool obscure) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.12),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Colors.white.withOpacity(0.15),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: TextField(
        controller: controller,
        style: const TextStyle(color: Colors.white, fontSize: 16),
        obscureText: obscure,
        decoration: InputDecoration(
          hintText: hint,
          hintStyle: TextStyle(
            color: Colors.white.withOpacity(0.4),
          ),
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 20,
            vertical: 16,
          ),
        ),
      ),
    );
  }
}