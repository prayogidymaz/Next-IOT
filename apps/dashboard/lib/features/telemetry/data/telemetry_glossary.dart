import '../../devices/data/device_glossary.dart';

String? telemetryGlossaryMessage(String label) {
  switch (label.toUpperCase()) {
    case 'BATT':
      return 'Persentase baterai perangkat. Di bawah 20% sering memicu peringatan RTL.';
    case 'SPEED':
      return 'Kecepatan ground speed dari GPS atau sensor onboard (meter/detik).';
    case 'ROLL':
    case 'PITCH':
    case 'YAW':
      return _findGlossary('MAVLink') ??
          'Orientasi perangkat dalam derajat (attitude).';
    case 'DO':
      return _findGlossary('DO / Oksigen Terlarut');
    case 'PH':
      return 'Tingkat keasaman air (0–14). Ideal budidaya ikan ~6.5–8.5.';
    case 'RSSI':
      return _findGlossary('RSSI');
    case 'GPS':
      return 'Koordinat posisi dari satelit GNSS (latitude/longitude).';
    case 'ALT':
      return 'Ketinggian di atas permukaan laut (MSL) dalam meter.';
    case 'MAVLINK':
      return _findGlossary('MAVLink');
    default:
      return null;
  }
}

String? _findGlossary(String termPrefix) {
  for (final entry in deviceIotGlossary) {
    if (entry.term.startsWith(termPrefix) ||
        entry.term.toUpperCase().contains(termPrefix.toUpperCase())) {
      return entry.plainExplanation;
    }
  }
  return null;
}
