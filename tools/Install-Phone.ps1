param([Parameter(Mandatory=$true)][string]$Serial)
$ErrorActionPreference='Stop'
$ffoRoot=(Split-Path $PSScriptRoot -Parent)
$ffoAdb='E:\LDPlayer\LDPlayer9\adb.exe'
if ($Serial -match '^emulator-|^127\.0\.0\.1:') { throw 'Use the USB phone serial, not an emulator.' }
function Invoke-FfoAdb {
    & $ffoAdb -s $Serial @args
    if ($LASTEXITCODE -ne 0) { throw "ADB failed: $args" }
}
foreach ($ffoApk in @('FFO-Hub.apk','FFO-Client.apk')) {
    $ffoPath=Join-Path $ffoRoot "dist/$ffoApk"
    if (-not (Test-Path -LiteralPath $ffoPath)) { throw "Build missing: $ffoPath" }
    Invoke-FfoAdb install -r $ffoPath
}
Invoke-FfoAdb shell pm grant com.cloud.ffo android.permission.POST_NOTIFICATIONS
Invoke-FfoAdb shell am start -n com.cloud.ffo/.MainActivity
Invoke-FfoAdb shell mkdir -p /sdcard/Android/data/com.cloud.ffo/files/runtime/assets
Invoke-FfoAdb push -a (Join-Path $ffoRoot 'assets/cache') /sdcard/Android/data/com.cloud.ffo/files/runtime/assets/
# The completion marker is installed only after every data push succeeds.
Invoke-FfoAdb push (Join-Path $ffoRoot 'dist/FFO-Data-Manifest.json') /sdcard/Android/data/com.cloud.ffo/files/runtime/data-manifest.json
Write-Output 'Installed. Open FF:O Hub, start the server, wait for Ready, then launch.'
