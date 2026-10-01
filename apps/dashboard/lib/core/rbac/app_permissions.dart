/// Permission strings aligned with `apps/api/app/auth/permissions.py`.
abstract final class AppPermissions {
  static const devicesRead = 'devices.read';
  static const devicesRegister = 'devices.register';
  static const devicesDelete = 'devices.delete';
  static const otaUpload = 'ota.upload';
  static const commandsSend = 'commands.send';
  static const alertsManage = 'alerts.manage';
  static const alertsAck = 'alerts.ack';
  static const settingsManage = 'settings.manage';
  static const tenantManage = 'tenant.manage';
  static const membersManage = 'members.manage';
  static const automationRead = 'automation.read';
  static const automationManage = 'automation.manage';
  static const automationRun = 'automation.run';
  static const auditRead = 'audit.read';

  static const all = {
    devicesRead,
    devicesRegister,
    devicesDelete,
    otaUpload,
    commandsSend,
    alertsManage,
    alertsAck,
    settingsManage,
    tenantManage,
    membersManage,
    automationRead,
    automationManage,
    automationRun,
    auditRead,
  };
}
