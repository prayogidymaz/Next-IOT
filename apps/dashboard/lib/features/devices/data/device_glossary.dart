class IotGlossaryEntry {
  const IotGlossaryEntry({
    required this.term,
    required this.plainExplanation,
  });

  final String term;
  final String plainExplanation;
}

/// Plain-language IoT glossary for Device Management beginners.
const deviceIotGlossary = <IotGlossaryEntry>[
  IotGlossaryEntry(
    term: 'MAVLink',
    plainExplanation:
        'Protokol komunikasi standar untuk drone & robot. Dipakai mengirim perintah '
        'seperti ARM (siap terbang) atau RTL (kembali ke home).',
  ),
  IotGlossaryEntry(
    term: 'ARM / RTL / LAND',
    plainExplanation:
        'Perintah drone: ARM = aktifkan motor, RTL = Return To Launch (balik ke titik '
        'lepas landas), LAND = turun & mendarat.',
  ),
  IotGlossaryEntry(
    term: 'Geofence',
    plainExplanation:
        'Pagar virtual di peta. Jika perangkat keluar/masuk area, sistem memicu '
        'peringatan atau aksi otomatis.',
  ),
  IotGlossaryEntry(
    term: 'DO / Oksigen Terlarut',
    plainExplanation:
        'Dissolved Oxygen — kadar oksigen dalam air (budidaya ikan/kolam). '
        'Terlalu rendah = ikan stres atau mati.',
  ),
  IotGlossaryEntry(
    term: 'Modbus / RS485',
    plainExplanation:
        'Cara mesin industri saling kirim data via kabel. RS485 adalah media fisik; '
        'Modbus adalah "bahasa" datanya.',
  ),
  IotGlossaryEntry(
    term: 'LoRa / LoRaWAN',
    plainExplanation:
        'Teknologi radio jarak jauh & irit daya untuk sensor lapangan. Cocok untuk '
        'sawah, tambak, atau site tanpa Wi-Fi.',
  ),
  IotGlossaryEntry(
    term: 'RSSI',
    plainExplanation:
        'Received Signal Strength Indicator — seberapa kuat sinyal radio diterima. '
        'Semakin tinggi (kurang negatif), semakin stabil koneksinya.',
  ),
  IotGlossaryEntry(
    term: 'Telemetry',
    plainExplanation:
        'Data live dari perangkat — suhu, posisi GPS, baterai, kecepatan angin, dll.',
  ),
  IotGlossaryEntry(
    term: 'Provisioning',
    plainExplanation:
        'Proses pertama kali mendaftarkan perangkat ke platform dengan token '
        'sekali pakai sebelum bisa online.',
  ),
  IotGlossaryEntry(
    term: 'Online / Offline / Pending',
    plainExplanation:
        'Online = perangkat aktif kirim data. Offline = tidak terdengar. '
        'Pending = terdaftar tapi belum selesai setup.',
  ),
];
