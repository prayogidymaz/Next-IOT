import '../../../core/auth/token_storage.dart';
import '../../../core/network/api_client.dart';
import '../../auth/models/auth_models.dart';
import '../models/tenant_models.dart';

class TenantRepository {
  TenantRepository({ApiClient? apiClient, TokenStorage? tokenStorage})
      : _api = (apiClient ?? ApiClient()).dio,
        _tokenStorage = tokenStorage ?? TokenStorage();

  final _api;
  final TokenStorage _tokenStorage;

  Future<List<TenantSummary>> listTenants() async {
    final response = await _api.get('/api/v1/tenants');
    final data = response.data as List<dynamic>;
    return data
        .map((e) => TenantSummary.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<TenantSummary> createTenant({
    required String name,
    required String slug,
  }) async {
    final response = await _api.post(
      '/api/v1/tenants',
      data: {'name': name, 'slug': slug},
    );
    return TenantSummary.fromJson(response.data as Map<String, dynamic>);
  }

  Future<TokenPair> switchTenant(String tenantId) async {
    final response = await _api.post(
      '/api/v1/tenants/switch',
      data: {'tenant_id': tenantId},
    );
    final tokens = TokenPair.fromJson(response.data as Map<String, dynamic>);
    await _tokenStorage.saveTokens(
      accessToken: tokens.accessToken,
      refreshToken: tokens.refreshToken,
      tenantId: tenantId,
    );
    await _tokenStorage.saveActiveTenantId(tenantId);
    return tokens;
  }

  Future<List<TenantMember>> listMembers(String tenantId) async {
    final response = await _api.get('/api/v1/tenants/$tenantId/members');
    final data = response.data as List<dynamic>;
    return data
        .map((e) => TenantMember.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<TenantMember> inviteMember({
    required String tenantId,
    required String email,
    required String password,
    required String role,
  }) async {
    final response = await _api.post(
      '/api/v1/tenants/$tenantId/members',
      data: {
        'email': email,
        'password': password,
        'role': role,
      },
    );
    return TenantMember.fromJson(response.data as Map<String, dynamic>);
  }
}
