import 'dart:ui';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class NotificationService {
  static final _localNotifications = FlutterLocalNotificationsPlugin();
  static const _channelId = 'ihsg_signals';
  static const _channelName = 'Sinyal IHSG';

  static Future<void> init() async {
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    await _localNotifications.initialize(
      const InitializationSettings(android: androidSettings),
    );

    await FirebaseMessaging.instance.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    await FirebaseMessaging.instance.subscribeToTopic('ihsg_signals');

    FirebaseMessaging.onMessage.listen((message) {
      showNotification(message);
    });

    final token = await FirebaseMessaging.instance.getToken();
    // ignore: avoid_print
    print('[FCM Token] $token');
  }

  static Future<void> showNotification(RemoteMessage message) async {
    final notification = message.notification;
    if (notification == null) return;

    final signal = message.data['signal'] ?? 'HOLD';
    final color = signal == 'BELI'
        ? const Color(0xFF4CAF50)
        : signal == 'JUAL'
            ? const Color(0xFFF44336)
            : const Color(0xFFFF9800);

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
          color: color,
        ),
      ),
    );
  }
}
