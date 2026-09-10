import json

import pytest

from app.hardware.lora_crypto import (
    LoRaCipherMode,
    decrypt_aes128_cbc,
    decrypt_aes128_gcm,
    decrypt_serial_line,
    encrypt_aes128_cbc,
    encrypt_aes128_gcm,
    encrypt_serial_payload,
    maybe_decrypt_serial_line,
)
from app.hardware.parser import packet_to_metrics, parse_serial_line

TEST_KEY = bytes.fromhex("00112233445566778899aabbccddeeff")
SAMPLE_JSON = (
    '{"node_id":"DRONE-01","lat":3.595,"lon":98.665,"alt":60,"rssi":-85,"snr":9.5}'
)


def test_aes128_cbc_round_trip():
    plain = SAMPLE_JSON.encode("utf-8")
    encrypted = encrypt_aes128_cbc(plain, TEST_KEY)
    decrypted = decrypt_aes128_cbc(encrypted, TEST_KEY)
    assert decrypted == plain


def test_aes128_gcm_round_trip():
    plain = SAMPLE_JSON.encode("utf-8")
    encrypted = encrypt_aes128_gcm(plain, TEST_KEY)
    decrypted = decrypt_aes128_gcm(encrypted, TEST_KEY)
    assert decrypted == plain


def test_encrypt_decrypt_serial_line_cbc():
    encrypted_line = encrypt_serial_payload(SAMPLE_JSON, TEST_KEY, mode=LoRaCipherMode.CBC)
    assert encrypted_line.startswith("ENC:")
    decrypted = decrypt_serial_line(encrypted_line, TEST_KEY)
    assert json.loads(decrypted) == json.loads(SAMPLE_JSON)


def test_encrypt_decrypt_serial_line_gcm():
    encrypted_line = encrypt_serial_payload(SAMPLE_JSON, TEST_KEY, mode=LoRaCipherMode.GCM)
    assert encrypted_line.startswith("AESGCM:")
    decrypted = decrypt_serial_line(encrypted_line, TEST_KEY)
    assert json.loads(decrypted) == json.loads(SAMPLE_JSON)


def test_plain_json_encrypt_decrypt_parse_flow():
    encrypted_line = encrypt_serial_payload(SAMPLE_JSON, TEST_KEY, mode=LoRaCipherMode.CBC)
    decrypted_line = maybe_decrypt_serial_line(encrypted_line, TEST_KEY)
    packet = parse_serial_line(decrypted_line, encryption_key=TEST_KEY)
    assert packet is not None
    assert packet.node_id == "DRONE-01"
    assert packet.latitude == 3.595
    metrics = packet_to_metrics(packet)
    assert metrics["altitude_m"] == 60.0


def test_parse_serial_line_decrypts_encrypted_payload():
    encrypted_line = encrypt_serial_payload(SAMPLE_JSON, TEST_KEY, mode=LoRaCipherMode.CBC)
    packet = parse_serial_line(encrypted_line, encryption_key=TEST_KEY)
    assert packet is not None
    assert packet.node_id == "DRONE-01"


def test_encrypted_line_without_key_raises():
    encrypted_line = encrypt_serial_payload(SAMPLE_JSON, TEST_KEY, mode=LoRaCipherMode.CBC)
    with pytest.raises(ValueError, match="LORA_ENCRYPTION_KEY"):
        maybe_decrypt_serial_line(encrypted_line, None)
