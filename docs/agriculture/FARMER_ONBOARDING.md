# Farmer Onboarding

1. Daftar tenant di Next-IoT Web → buka **Smart Agriculture**.
2. **Tambah kebun** (nama, jenis tanaman, koordinat, WhatsApp pemilik).
3. Pasang **LoRa gateway** di titik tertinggi kebun; commission via super admin atau self-service API.
4. Commission **sensor tanah** per blok (DevEUI + AppKey dari label device).
5. Atur **ambang irigasi** dan jadwal valve; aktifkan notifikasi Fonnte.
6. Pantau **peringatan hama** dan kalender panen dari dashboard.

Demo: `docker compose exec api python scripts/seed_agriculture_demo.py`
