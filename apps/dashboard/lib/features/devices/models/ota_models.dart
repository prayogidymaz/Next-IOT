class FirmwareRelease {
  const FirmwareRelease({
    required this.id,
    required this.version,
    required this.targetDeviceCategory,
    required this.fileUrl,
    required this.checksumSha256,
    required this.status,
    required this.createdAt,
  });

  final String id;
  final String version;
  final String targetDeviceCategory;
  final String fileUrl;
  final String checksumSha256;
  final String status;
  final DateTime createdAt;

  bool get isActive => status == 'active';
  bool get isArchived => status == 'archived';

  factory FirmwareRelease.fromJson(Map<String, dynamic> json) {
    return FirmwareRelease(
      id: json['id'] as String,
      version: json['version'] as String,
      targetDeviceCategory: json['target_device_category'] as String,
      fileUrl: json['file_url'] as String,
      checksumSha256: json['checksum_sha256'] as String,
      status: json['status'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}

class OtaRolloutRow {
  const OtaRolloutRow({
    required this.id,
    required this.deviceId,
    required this.deviceName,
    required this.status,
    this.reportedAt,
    required this.createdAt,
  });

  final String id;
  final String deviceId;
  final String deviceName;
  final String status;
  final DateTime? reportedAt;
  final DateTime createdAt;

  factory OtaRolloutRow.fromJson(Map<String, dynamic> json) {
    return OtaRolloutRow(
      id: json['id'] as String,
      deviceId: json['device_id'] as String,
      deviceName: json['device_name'] as String,
      status: json['status'] as String,
      reportedAt: json['reported_at'] != null
          ? DateTime.parse(json['reported_at'] as String)
          : null,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}

class BulkImportResult {
  const BulkImportResult({
    required this.importedCount,
    required this.failedCount,
    required this.items,
    required this.errors,
  });

  final int importedCount;
  final int failedCount;
  final List<BulkImportItem> items;
  final List<BulkImportError> errors;

  factory BulkImportResult.fromJson(Map<String, dynamic> json) {
    return BulkImportResult(
      importedCount: json['imported_count'] as int,
      failedCount: json['failed_count'] as int,
      items: (json['items'] as List<dynamic>)
          .map((e) => BulkImportItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      errors: (json['errors'] as List<dynamic>)
          .map((e) => BulkImportError.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

class BulkImportItem {
  const BulkImportItem({
    required this.name,
    required this.deviceId,
    required this.provisioningToken,
  });

  final String name;
  final String deviceId;
  final String provisioningToken;

  factory BulkImportItem.fromJson(Map<String, dynamic> json) {
    return BulkImportItem(
      name: json['name'] as String,
      deviceId: json['device_id'] as String,
      provisioningToken: json['provisioning_token'] as String,
    );
  }
}

class BulkImportError {
  const BulkImportError({required this.row, this.name, required this.detail});

  final int row;
  final String? name;
  final String detail;

  factory BulkImportError.fromJson(Map<String, dynamic> json) {
    return BulkImportError(
      row: json['row'] as int,
      name: json['name'] as String?,
      detail: json['detail'] as String,
    );
  }
}
