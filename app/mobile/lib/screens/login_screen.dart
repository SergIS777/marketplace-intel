import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import 'main_shell.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _email = TextEditingController(text: 'test@example.com');
  final _password = TextEditingController(text: 'test123');
  bool _loading = false;
  String? _error;

  Future<void> _login() async {
    setState(() { _loading = true; _error = null; });
    try {
      final data = await ApiService().login(_email.text, _password.text);
      if (!mounted) return;
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => MainShell(token: data['access_token'])),
      );
    } catch (e) {
      setState(() => _error = 'Не удалось войти. Проверь что backend запущен.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.rocket_launch, size: 64, color: AppColors.primary),
              const SizedBox(height: 16),
              const Text('Marketplace Intel', style: AppText.heroTitle),
              const SizedBox(height: 8),
              const Text('Твоя игра по запуску бизнеса на WB', style: AppText.subtitle),
              const SizedBox(height: 32),
              _field(_email, 'Email', false),
              const SizedBox(height: 12),
              _field(_password, 'Пароль', true),
              if (_error != null) ...[
                const SizedBox(height: 12),
                Text(_error!, style: AppText.error),
              ],
              const SizedBox(height: 24),
              FilledButton(
                onPressed: _loading ? null : _login,
                style: AppButtons.primary(),
                child: _loading
                    ? const SizedBox(width: 24, height: 24,
                        child: CircularProgressIndicator(color: Colors.white))
                    : const Text('Начать игру'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _field(TextEditingController c, String hint, bool obscure) {
    return TextField(
      controller: c,
      obscureText: obscure,
      style: const TextStyle(color: AppColors.textPrimary),
      decoration: InputDecoration(
        hintText: hint,
        hintStyle: TextStyle(color: AppColors.textSecondary.withOpacity(0.6)),
      ),
    );
  }
}