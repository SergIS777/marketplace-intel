import 'dart:convert';
import 'dart:io';

class ApiService {
  static const String baseUrl = 'http://localhost:8000/api/v1';

  Future<Map<String, dynamic>> login(String email, String password) async {
    final client = HttpClient();
    try {
      final request = await client.postUrl(Uri.parse('$baseUrl/auth/login'));
      request.headers.set(HttpHeaders.contentTypeHeader, 'application/json; charset=utf-8');
      // Используем utf8.encode для корректной передачи кириллицы (если в email/password будут спецсимволы)
      request.add(utf8.encode(jsonEncode({'email': email, 'password': password})));
      
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

  Future<Map<String, dynamic>> submitQuestProof(String questId, String proofText) async {
    print("📡 [ApiService] Вызов submitQuestProof: $questId");
    final client = HttpClient();
    try {
      final url = '$baseUrl/quest/submit';
      print("📡 [ApiService] URL запроса: $url");
      
      final request = await client.postUrl(Uri.parse(url));
      request.headers.set(HttpHeaders.contentTypeHeader, 'application/json; charset=utf-8');
      
      final body = jsonEncode({
        'quest_id': questId,
        'proof_text': proofText,
      });
      
      // ✅ КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: utf8.encode вместо request.write()
      request.add(utf8.encode(body));
      
      print("📡 [ApiService] Отправляем запрос...");
      final response = await request.close();
      print("📡 [ApiService] Статус ответа: ${response.statusCode}");
      
      final responseBody = await response.transform(utf8.decoder).join();
      if (response.statusCode == 200) return jsonDecode(responseBody);
      throw Exception('Submit failed: ${response.statusCode} - $responseBody');
    } finally {
      client.close();
    }
  }

  Future<Map<String, dynamic>> chatWithTrainer(String questId, List<Map<String, String>> messages) async {
    final client = HttpClient();
    try {
      final request = await client.postUrl(Uri.parse('$baseUrl/chat'));
      request.headers.set(HttpHeaders.contentTypeHeader, 'application/json; charset=utf-8');
      
      final body = jsonEncode({
        'quest_id': questId,
        'messages': messages,
      });
      
      // ✅ КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: utf8.encode вместо request.write()
      request.add(utf8.encode(body));
      
      final response = await request.close();
      final responseBody = await response.transform(utf8.decoder).join();
      if (response.statusCode == 200) return jsonDecode(responseBody);
      throw Exception('Chat failed: ${response.statusCode} - $responseBody');
    } finally {
      client.close();
    }
  }
}