# FF:O Android Hub

The Hub runs the Python gateway in an Android foreground service. The client
connects to `127.0.0.1:11880` on the same phone, including native CRI downloads.
No PC gateway, ADB reverse tunnel or root access is required while playing.

## Build and install

From the project root, run `python tools/build_phone_hub.py` and
`python tools/build_phone_client.py`. The client build uses the locally retained
APKEditor, Apktool and Frida Gadget artifacts. Outputs are `dist/FFO-Hub.apk`
and `dist/FFO-Client.apk`. Both use the local Android debug signing key; retain
that key to install future updates without erasing app data.

Connect the phone with USB debugging and run
`tools/Install-Phone.ps1 -Serial <USB serial>`. This installs both APKs and
transfers the recovered data separately. The data manifest is copied last;
the server checks every file size before starting. Allow approximately 8 GB
for the initial installation plus space for the client's downloaded cache.

Open **FF:O Hub → Start server**, wait for **Local server is ready**, then
choose **Launch FF:O**. Leave the foreground notification active while playing.
Return to Hub and choose **Stop server** when finished. Saves live in Hub's
private app data; uninstalling Hub erases that save and its external data.

This remains a restoration test build. Story and Vortex placeholder limitations
are unchanged by Android packaging. Installation does not establish complete
native story or event playability.
