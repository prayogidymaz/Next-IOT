import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/domain_storage.dart';
import '../models/domain_navigation_profile.dart';
import '../models/operational_domain.dart';

final domainStorageProvider = Provider<DomainStorage>((ref) => DomainStorage());

class DomainContextState {
  const DomainContextState({
    this.domain,
    this.segment,
    this.isLoading = false,
  });

  final OperationalDomain? domain;
  final EnterpriseSegment? segment;
  final bool isLoading;

  bool get hasSelection => domain != null && segment != null;

  DomainNavigationProfile? get profile {
    if (domain == null || segment == null) return null;
    return navigationProfileFor(domain: domain!, segment: segment!);
  }

  DomainContextState copyWith({
    OperationalDomain? domain,
    EnterpriseSegment? segment,
    bool? isLoading,
    bool clear = false,
  }) {
    if (clear) return const DomainContextState();
    return DomainContextState(
      domain: domain ?? this.domain,
      segment: segment ?? this.segment,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class DomainContextNotifier extends StateNotifier<DomainContextState> {
  DomainContextNotifier(this._storage) : super(const DomainContextState(isLoading: true));

  final DomainStorage _storage;

  Future<void> bootstrap() async {
    state = state.copyWith(isLoading: true);
    try {
      final domain = await _storage.readDomain();
      final segment = await _storage.readSegment();
      state = DomainContextState(domain: domain, segment: segment);
    } catch (_) {
      state = const DomainContextState();
    }
  }

  Future<void> select({
    required OperationalDomain domain,
    required EnterpriseSegment segment,
  }) async {
    await _storage.save(domain: domain, segment: segment);
    state = DomainContextState(domain: domain, segment: segment);
  }

  Future<void> clear() async {
    await _storage.clear();
    state = const DomainContextState();
  }
}

final domainContextProvider =
    StateNotifierProvider<DomainContextNotifier, DomainContextState>((ref) {
  return DomainContextNotifier(ref.watch(domainStorageProvider));
});

final domainNavigationProfileProvider = Provider<DomainNavigationProfile?>((ref) {
  return ref.watch(domainContextProvider).profile;
});
