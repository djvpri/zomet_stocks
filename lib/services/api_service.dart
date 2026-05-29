import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/signal_model.dart';

class ApiService {
  // Ganti dengan IP server kamu saat development
  // Gunakan 10.0.2.2 untuk Android emulator (localhost)
  static const String baseUrl = 'http://10.0.2.2:8000';

  static Future<SignalResult> analyze() async {
    final response = await http
        .get(Uri.parse('$baseUrl/analyze'))
        .timeout(const Duration(seconds: 30));

    if (response.statusCode == 200) {
      return SignalResult.fromJson(jsonDecode(response.body));
    }
    throw Exception('Gagal mengambil analisis: ${response.statusCode}');
  }

  static Future<Map<String, dynamic>> getSettings() async {
    final response = await http
        .get(Uri.parse('$baseUrl/settings'))
        .timeout(const Duration(seconds: 10));

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Gagal mengambil settings');
  }
}
