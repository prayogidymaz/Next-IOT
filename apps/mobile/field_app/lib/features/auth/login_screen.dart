import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/theme/field_theme.dart';
import 'auth_controller.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _email = TextEditingController(text: 'admin@nextiot.com');
  final _password = TextEditingController();
  final _apiBase = TextEditingController(text: 'http://10.0.2.2:8000');

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    _apiBase.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authControllerProvider);

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      'Field Execution',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: FieldColors.ink,
                          ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Tactical Clean login — tokens stored in secure enclave.',
                      style: TextStyle(color: FieldColors.inkMuted),
                    ),
                    const SizedBox(height: 20),
                    TextField(
                      controller: _apiBase,
                      decoration: const InputDecoration(
                        labelText: 'API base URL',
                        border: OutlineInputBorder(),
                      ),
                      onSubmitted: (_) => _submit(),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _email,
                      decoration: const InputDecoration(labelText: 'Email', border: OutlineInputBorder()),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _password,
                      obscureText: true,
                      decoration: const InputDecoration(labelText: 'Password', border: OutlineInputBorder()),
                    ),
                    if (auth.error != null) ...[
                      const SizedBox(height: 12),
                      Text(auth.error!, style: const TextStyle(color: FieldColors.danger)),
                    ],
                    const SizedBox(height: 20),
                    FilledButton(
                      onPressed: auth.loading ? null : _submit,
                      child: auth.loading
                          ? const SizedBox(
                              height: 18,
                              width: 18,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Sign in'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _submit() async {
    await ref.read(tokenStorageProvider).saveApiBaseUrl(_apiBase.text.trim());
    await ref.read(authControllerProvider.notifier).login(_email.text.trim(), _password.text);
  }
}
