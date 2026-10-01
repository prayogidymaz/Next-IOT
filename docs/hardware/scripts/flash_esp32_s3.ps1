# Flash ESP32-S3 PTT firmware via esptool (Windows)
param(
  [Parameter(Mandatory = $true)][string]$Port,
  [Parameter(Mandatory = $true)][string]$BuildDir
)

$boot = Join-Path $BuildDir "bootloader.bin"
$part = Join-Path $BuildDir "partitions.bin"
$app  = Join-Path $BuildDir "firmware.bin"

foreach ($f in @($boot, $part, $app)) {
  if (-not (Test-Path $f)) { throw "Missing $f" }
}

python -m esptool --chip esp32s3 --port $Port --baud 921600 `
  write_flash -z 0x0 $boot 0x8000 $part 0x10000 $app

Write-Host "Flash complete on $Port"
