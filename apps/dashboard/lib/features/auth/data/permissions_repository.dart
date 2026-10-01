import '../../../core/network/api_client.dart';
import '../models/permissions_models.dart';

class PermissionsRepository {
  PermissionsRepository({ApiClient? apiClient})
      : _api = (apiClient ?? ApiClient()).dio;

  final _api;

  Future<UserPermissions> fetchMyPermissions() async {
    final response = await _api.get('/api/v1/auth/me');
    return UserPermissions.fromJson(response.data as Map<String, dynamic>);
  }
}
