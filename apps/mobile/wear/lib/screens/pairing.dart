import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:mobile_scanner/mobile_scanner.dart";

import "../providers/mesh_connection.dart";
import "../services/auth_storage.dart";
import "../providers/sensor_provider.dart";
import "../theme/tactical_warm_cream.dart";

final authStorageProvider = Provider<AuthStorage>((ref) => AuthStorage());

class PairingScreen extends ConsumerStatefulWidget {
  const PairingScreen({super.key, required this.onPaired});

  final VoidCallback onPaired;

  @override
  ConsumerState<PairingScreen> createState() => _PairingScreenState();
}

class _PairingScreenState extends ConsumerState<PairingScreen> {
  bool _busy = false;
  String? _error;

  Future<void> _applyToken(String raw) async {
    setState(() {
      _busy = true;
      _error = null;
    });
    final token = raw.trim();
    if (token.length < 20) {
      setState(() {
        _error = "Invalid QR payload";
        _busy = false;
      });
      return;
    }
    await ref.read(authStorageProvider).saveJwt(token);
    ref.read(meshApiProvider).setJwt(token);
    await ref.read(meshApiProvider).registerFcmToken("wear-demo-token");
    ref.read(meshConnectionProvider.notifier).connectLive(token);
    widget.onPaired();
    if (mounted) {
      setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: TacticalWarmCream.base,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            children: [
              Text("Pair watch", style: Theme.of(context).textTheme.headlineSmall),
              const SizedBox(height: 8),
              const Text("Scan HQ claim QR or paste JWT", textAlign: TextAlign.center),
              Expanded(
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: MobileScanner(
                    onDetect: (capture) {
                      final raw = capture.barcodes.firstOrNull?.rawValue;
                      if (raw != null && !_busy) {
                        _applyToken(raw);
                      }
                    },
                  ),
                ),
              ),
              if (_error != null) Text(_error!, style: const TextStyle(color: TacticalWarmCream.critical)),
            ],
          ),
        ),
      ),
    );
  }
}
