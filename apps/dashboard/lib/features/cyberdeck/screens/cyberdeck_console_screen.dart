import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/cyberdeck_provider.dart';
import '../theme/cyberdeck_theme.dart';
import '../widgets/cyberdeck_health_panel.dart';
import '../widgets/cyberdeck_mesh_panel.dart';
import '../widgets/cyberdeck_ptt_panel.dart';
import '../widgets/cyberdeck_text_dispatch_panel.dart';

class CyberdeckConsoleScreen extends ConsumerStatefulWidget {
  const CyberdeckConsoleScreen({super.key});

  @override
  ConsumerState<CyberdeckConsoleScreen> createState() => _CyberdeckConsoleScreenState();
}

class _CyberdeckConsoleScreenState extends ConsumerState<CyberdeckConsoleScreen> {
  final _textController = TextEditingController();

  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(cyberdeckProvider.notifier).load());
  }

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(cyberdeckProvider);
    final notifier = ref.read(cyberdeckProvider.notifier);

    return Theme(
      data: cyberdeckTheme(),
      child: Scaffold(
        backgroundColor: CyberdeckColors.background,
        appBar: AppBar(
          backgroundColor: CyberdeckColors.panel,
          title: const Text('CYBERDECK // LoRa PTT CONSOLE'),
          actions: [
            if (state.isLoading)
              const Padding(
                padding: EdgeInsets.all(16),
                child: SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)),
              ),
            IconButton(
              tooltip: 'Refresh mesh',
              onPressed: notifier.load,
              icon: const Icon(Icons.refresh, color: CyberdeckColors.green),
            ),
          ],
        ),
        body: LayoutBuilder(
          builder: (context, constraints) {
            final wide = constraints.maxWidth >= 960;
            final ptt = CyberdeckPttPanel(
              channel: state.channel,
              isTransmitting: state.isTransmitting,
              waveform: state.waveform,
              statusMessage: state.statusMessage,
              onChannelChanged: notifier.setChannel,
              onTransmitStart: notifier.startTransmit,
              onTransmitEnd: notifier.stopTransmit,
            );
            final mesh = CyberdeckMeshPanel(
              nodes: state.nodes,
              selectedNodeId: state.selectedNodeId,
              onSelect: notifier.selectNode,
              expand: wide,
            );
            final textPanel = CyberdeckTextDispatchPanel(
              controller: _textController,
              lastDispatch: state.lastDispatch,
              onSend: () async {
                await notifier.sendText(_textController.text);
                _textController.clear();
              },
              onBeacon: notifier.sendBeacon,
            );
            final health = CyberdeckHealthPanel(health: state.health);

            if (wide) {
              return Padding(
                padding: const EdgeInsets.all(12),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Expanded(flex: 5, child: Column(children: [Expanded(child: ptt), const SizedBox(height: 12), textPanel])),
                    const SizedBox(width: 12),
                    Expanded(flex: 4, child: Column(children: [Expanded(child: mesh), const SizedBox(height: 12), health])),
                  ],
                ),
              );
            }

            return ListView(
              padding: const EdgeInsets.all(12),
              children: [ptt, const SizedBox(height: 12), mesh, const SizedBox(height: 12), textPanel, const SizedBox(height: 12), health],
            );
          },
        ),
      ),
    );
  }
}
