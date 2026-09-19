import 'dart:convert';
import 'dart:html' as html;

class ApiService {
  static const String baseUrl = 'http://localhost:8000/api/v1';

  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await html.HttpRequest.request(
      '$baseUrl/auth/login',
      method: 'POST',
      requestHeaders: {'Content-Type': 'application/json'},
      sendData: jsonEncode({'email': email, 'password': password}),
    );
    if (response.status == 200) {
      return jsonDecode(response.responseText!);
    }
    throw Exception('Login failed: ${response.status}');
  }

  Future<List<dynamic>> getProducts() async {
    final response = await html.HttpRequest.request('$baseUrl/store/products');
    if (response.status == 200) {
      return jsonDecode(response.responseText!);
    }
    throw Exception('Products failed: ${response.status}');
  }
}
