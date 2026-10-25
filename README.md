# FF:O

FINAL FANTASY BRAVE EXVIUS, running with a local Android server.
Built and restored by **Cloud** for preservation and hands-on testing.

## Android tester build

Download **FFO-Hub.apk** and **FFO-Client.apk** from the
[tester release](https://github.com/CloudyCodez/FF-O/releases/tag/v0.1.0),
then install both on an ARM64 Android phone (Android 8 or newer).

1. Open **FF:O Hub** and enter the tester password supplied by Cloud.
2. Choose **Download / repair game data**. Keep Hub open for the initial download.
   The eight data parts total about 6.9 GB; Hub downloads and extracts them
   directly and verifies each part. Keep at least 10 GB free before setup.
3. Choose **Start server** and wait for **Local server is ready**.
4. Choose **Launch FF:O**. Keep the server notification active while playing.
5. Return to Hub and choose **Stop server** when finished.

The server runs on the phone. USB, a PC server and root are not required while
playing. The first data download needs internet access. A failed download can
be retried from Hub; a completion marker is written only after verification.
Keep both apps installed to preserve your save and downloaded data.

The password is a shared tester-access gate, not individual licensing or
protection against modification. The release does not contain personal saves.

## What is restored

Guest login, persistent units and parties, local Premium / Collaboration /
Standard summons, story battle handlers, basic town transitions, mail, battle
EXP and offline Vortex listings. Test currencies are supplied locally.

All 2,732 story mission rows have handlers. Only 77 encounters currently have
individually authored formations; the rest use provisional encounters. This
includes 132 temporary battle replacements for zero-wave scenes/explorations.
Vortex covers 14,612 mission IDs using standard offline battles. Those listings
do **not** restore historical raids, event exchanges or unique event mechanics.
Summon pools use local uniform draws rather than historical banner rates.

This is an early testing release, not a complete or faithful game restoration.
The desktop gateway has automated progression coverage; Android native startup
and full playthrough verification remain in progress. Report the stage ID,
visible error and action that caused a failure.

## Development

Server implementation is under `server/`; Android Hub is under `AndroidHub/`.
The target client is Global 9.1.0, build 9101. Current Android runtime uses
Python 3.12 and PyCryptodome 3.21.0; the desktop dependency is in requirements.txt.

Rebuild scripts are under `tools/`. They require the preserved game packages,
master data and local Android SDK/JDK/Gradle installation described in
[AndroidHub/README.md](AndroidHub/README.md). Large game data, personal saves,
local tool binaries and analysis workspaces are excluded from Git history.
Automated tests require the corresponding recovered master data.

## Sources and credits

- Original Global package and data-cache preservation: [Internet Archive gacha-archive](https://archive.org/download/gacha-archive/Online/Final%20Fantasy%20-%20Brave%20Exvius/).
- Historical protocol documentation: [shalzuth/BraveHaxvius](https://github.com/shalzuth/BraveHaxvius), MIT licensed. Its older mappings are references, not assumed compatible with build9101. No upstream source has been copied into the server.
- Supplemental asset lead: [DaddyRaegen/ffbe_asset_dump](https://github.com/DaddyRaegen/ffbe_asset_dump).
- Separate fan Memorial project: [Luminest](https://ffbe.luminest.io/downloads/). This has useful preservation context but is not FF:O's original Global client target.

FINAL FANTASY BRAVE EXVIUS and its game content belong to their respective rights holders. FF:O is an unofficial preservation project.


Additional tooling: [Frida](https://frida.re),
[Apktool](https://apktool.org), [APKEditor](https://github.com/REAndroid/APKEditor),
[Chaquopy](https://chaquo.com/chaquopy), REA and Ghidra.
