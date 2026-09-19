import 'dart:convert';
import 'dart:io';

class ApiService {
  static const String baseUrl = 'http://10.187.8.19:8000/api/v1';

  Future<Map<String, dynamic>> login(String email, String password) async {
    final client = HttpClient();
    try {
      final request = await client.postUrl(Uri.parse('$baseUrl/auth/login'));
      request.headers.set(HttpHeaders.contentTypeHeader, 'application/json');
      request.write(jsonEncode({'email': email, 'password': password}));
      final response = await request.close();
      final body = await response.transform(utf8.decoder).join();
      if (response.statusCode == 200) return jsonDecode(body);
      throw Exception('Login failed: ${response.statusCode}');
    } finally {
      client.close();
    }
  }

  Future<List<dynamic>> getProducts() async {
    final client = HttpClient();
    try {
      final request = await client.getUrl(Uri.parse('$baseUrl/store/products'));
      final response = await request.close();
      final body = await response.transform(utf8.decoder).join();
      if (response.statusCode == 200) return jsonDecode(body);
      throw Exception('Products failed: ${response.statusCode}');
    } finally {
      client.close();
    }
  }
}
