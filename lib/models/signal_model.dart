class SignalResult {
  final DateTime timestamp;
  final double ihsgPrice;
  final double ihsgChangePct;
  final String signal;
  final String confidence;
  final String reason;
  final String? risk;
  final String providerUsed;

  SignalResult({
    required this.timestamp,
    required this.ihsgPrice,
    required this.ihsgChangePct,
    required this.signal,
    required this.confidence,
    required this.reason,
    this.risk,
    required this.providerUsed,
  });

  factory SignalResult.fromJson(Map<String, dynamic> json) {
    return SignalResult(
      timestamp: DateTime.parse(json['timestamp']),
      ihsgPrice: (json['ihsg_price'] as num).toDouble(),
      ihsgChangePct: (json['ihsg_change_pct'] as num).toDouble(),
      signal: json['signal'] ?? 'HOLD',
      confidence: json['confidence'] ?? 'rendah',
      reason: json['reason'] ?? '',
      risk: json['risk'],
      providerUsed: json['provider_used'] ?? '',
    );
  }

  bool get isBuy => signal == 'BELI';
  bool get isSell => signal == 'JUAL';
}
