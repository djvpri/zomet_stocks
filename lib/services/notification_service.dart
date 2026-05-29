import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class NotificationService {
  static final _localNotifications = FlutterLocalNotificationsPlugin();
  static const _channelId = 'ihsg_signals';
  static const _channelName = 'Sinyal IHSG';

  static Future<void> init() async {
    // Setup local notifications
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    await _localNotifications.initialize(
      const InitializationSettings(android: androidSettings),
    );

    // Minta izin notifikasi
    await FirebaseMessaging.instance.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    // Subscribe ke topic sinyal IHSG
    await FirebaseMessaging.instance.subscribeToTopic('ihsg_signals');

    // Handle notifikasi saat app di foreground
    FirebaseMessaging.onMessage.listen((message) {
      showNotification(message);
    });

    // Print FCM token untuk keperluan testing
    final token = await FirebaseMessaging.instance.getToken();
    print('[FCM Token] $token');
  }

  static Future<void> showNotification(RemoteMessage message) async {
    final notification = message.notification;
    if (notification == null) return;

    final data = message.data;
    final signal = data['signal'] ?? 'HOLD';
    final color = signal == 'BELI'
        ? const Color(0xFF4CAF50).value
        : signal == 'JUAL'
            ? const Color(0xFFF44336).value
            : const Color(0xFFFF9800).value;

    await _localNotifications.show(
      notification.hashCode,
      notification.title,
      notification.body,
      NotificationDetails(
        android: AndroidNotificationDetails(
          _channelId,
          _channelName,
          importance: Importance.high,
          priority: Priority.high,
          color: Color(color),
        ),
      ),
    );
  }
}

// Dummy Color class untuk background isolate
class Color {
  final int value;
  const Color(this.value);
}
