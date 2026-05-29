import 'package:flutter/material.dart';
import '../models/signal_model.dart';
import '../services/api_service.dart';
import 'package:intl/intl.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  SignalResult? _result;
  bool _loading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchAnalysis();
  }

  Future<void> _fetchAnalysis() async {
    setState(() { _loading = true; _error = null; });
    try {
      final result = await ApiService.analyze();
      setState(() { _result = result; });
    } catch (e) {
      setState(() { _error = e.toString(); });
    } finally {
      setState(() { _loading = false; });
    }
  }

  Color get _signalColor {
    if (_result == null) return Colors.grey;
    if (_result!.isBuy) return const Color(0xFF4CAF50);
    if (_result!.isSell) return const Color(0xFFF44336);
    return const Color(0xFFFF9800);
  }

  IconData get _signalIcon {
    if (_result == null) return Icons.show_chart;
    if (_result!.isBuy) return Icons.trending_up;
    if (_result!.isSell) return Icons.trending_down;
    return Icons.trending_flat;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0D0D1A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0D0D1A),
        title: const Text('Zomet Stocks', style: TextStyle(fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loading ? null : _fetchAnalysis,
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? _buildError()
              : _result != null
                  ? _buildContent()
                  : const SizedBox(),
    );
  }

  Widget _buildError() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, color: Colors.red, size: 48),
            const SizedBox(height: 16),
            Text(_error!, textAlign: TextAlign.center, style: const TextStyle(color: Colors.red)),
            const SizedBox(height: 16),
            ElevatedButton(onPressed: _fetchAnalysis, child: const Text('Coba Lagi')),
          ],
        ),
      ),
    );
  }

  Widget _buildContent() {
    final r = _result!;
    final priceFormat = NumberFormat('#,###', 'id_ID');
    final timeFormat = DateFormat('dd MMM yyyy, HH:mm', 'id_ID');

    return RefreshIndicator(
      onRefresh: _fetchAnalysis,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Kartu Sinyal Utama
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: _signalColor.withOpacity(0.15),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: _signalColor.withOpacity(0.5), width: 1.5),
              ),
              child: Column(
                children: [
                  Icon(_signalIcon, color: _signalColor, size: 56),
                  const SizedBox(height: 12),
                  Text(
                    r.signal,
                    style: TextStyle(
                      fontSize: 36,
                      fontWeight: FontWeight.bold,
                      color: _signalColor,
                      letterSpacing: 4,
                    ),
                  ),
                  const SizedBox(height: 6),
                  _ConfidenceBadge(confidence: r.confidence),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Kartu Harga IHSG
            _InfoCard(
              title: 'IHSG',
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    priceFormat.format(r.ihsgPrice),
                    style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: r.ihsgChangePct >= 0
                          ? Colors.green.withOpacity(0.2)
                          : Colors.red.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      '${r.ihsgChangePct >= 0 ? '+' : ''}${r.ihsgChangePct.toStringAsFixed(2)}%',
                      style: TextStyle(
                        color: r.ihsgChangePct >= 0 ? Colors.green : Colors.red,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),

            // Alasan
            _InfoCard(
              title: 'Analisis AI',
              child: Text(r.reason, style: const TextStyle(fontSize: 14, height: 1.5)),
            ),
            const SizedBox(height: 12),

            // Risiko
            if (r.risk != null) ...[
              _InfoCard(
                title: 'Risiko',
                titleColor: Colors.orange,
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.warning_amber, color: Colors.orange, size: 18),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(r.risk!, style: const TextStyle(fontSize: 14, height: 1.5)),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
            ],

            // Footer
            Text(
              'Dianalisis: ${timeFormat.format(r.timestamp.toLocal())}',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.white.withOpacity(0.4), fontSize: 12),
            ),
            Text(
              'Provider: ${r.providerUsed}',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.white.withOpacity(0.4), fontSize: 12),
            ),
            const SizedBox(height: 24),

            // Disclaimer
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.05),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                'Disclaimer: Analisis ini hanya untuk referensi, bukan rekomendasi investasi. '
                'Keputusan investasi sepenuhnya tanggung jawab Anda.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.white.withOpacity(0.4), fontSize: 11),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  final String title;
  final Widget child;
  final Color? titleColor;

  const _InfoCard({required this.title, required this.child, this.titleColor});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.05),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              color: titleColor ?? Colors.white.withOpacity(0.5),
              fontSize: 12,
              fontWeight: FontWeight.w600,
              letterSpacing: 1,
            ),
          ),
          const SizedBox(height: 10),
          child,
        ],
      ),
    );
  }
}

class _ConfidenceBadge extends StatelessWidget {
  final String confidence;
  const _ConfidenceBadge({required this.confidence});

  Color get _color {
    switch (confidence) {
      case 'tinggi': return Colors.green;
      case 'sedang': return Colors.orange;
      default: return Colors.red;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      decoration: BoxDecoration(
        color: _color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _color.withOpacity(0.5)),
      ),
      child: Text(
        'Keyakinan: $confidence',
        style: TextStyle(color: _color, fontSize: 13),
      ),
    );
  }
}
