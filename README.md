# Ameerpet Section: DTR Verification App

A phone app (one HTML page) for **Section 10 Yella Reddy Guda, ERO 11 Banjara Hills (TGSPDCL)**. Staff use it to verify services DTR-wise, structures feeder-wise, and structures area-code-wise in the field.

**Open the app:** https://krishnakuteerapartment-dev.github.io/AMEERPET-SECTION/

## What it does

| Tab | Purpose |
|---|---|
| **Services** | Pick a DTR structure code (1607010001–1607010800). Scan each meter's QR code or barcode, or use IR/IRDA (demo), or type the number. The app shows the **Service No and UKSCNO** and tells you whether the service belongs to this DTR. |
| **Feeders** | Pick a feeder. Confirm each structure the mapping puts on it, by scanning a DTR tag, typing the code or name, or ticking it from the list. |
| **Areas** | Pick an area code. Confirm each structure that has services in that area. |
| **Service** | Type a service no, UKSCNO or meter no: details, **master structure code**, whether and when it was verified (and by whom), **move it to another DTR** from a searchable list of all DTRs with a remark, and the history of moves with remarks. Part of a name lists matches. |
| **Report** | Summary, DTR-wise, feeder-wise and area-wise reports, plus conflicts. Everything can be downloaded as CSV. |
| **Guide** | How to use the app, and the data on this phone. |

### Protection against wrong mapping
- **One service, one DTR.** A meter already recorded on another DTR is held, not saved. Staff can cancel or send it to AE review.
- **One structure, one feeder.** Same rule for feeders.
- A scan that disagrees with the master asks for confirmation before saving.
- Every entry records when and how it was made (scan, IRDA, typed, manual).

## Consumer data is NOT in this repository

This repository is public, so it holds **code only**. Consumer names, addresses and meter numbers are loaded on each phone from a private file and stay in that phone's browser.

**First time on a phone:**
1. Open the app (or the Android app) and sign in.
2. Either type the backup key and tap **Get section data from Google Sheet** (after the admin has tapped **Put section data on Sheet** once), or tap **Load section data file (.json)** and choose `YRGuda_section_data.json`. The admin shares this file privately, never through GitHub.

**When a new Service Mapping Excel comes from EBS:**
- In the app, go to **Guide → Data on this phone → Load new mapping Excel**. Structures, feeders and areas are replaced, and the meter numbers already on the phone are kept.
- Then tap **Save data file** and share that file with the other staff phones.

**Rebuilding the data file from the EBS consumer master PDF** (for example when meters change):

```bash
pip install openpyxl          # pdftotext comes with poppler-utils
python3 tools/make_data.py CONSUMER_MASTER.pdf SERVICE_MAPPING.xlsx -o YRGuda_section_data.json
```

`.gitignore` blocks `*.json`, `*.xlsx`, `*.pdf` and `*.csv`, so data files cannot be committed by mistake.


## Google Sheet backup (and sharing between phones)

Every entry can be backed up to a Google Sheet that you own. Several phones can back up into the same Sheet and pull each other's entries, so the one-service-one-DTR check also works across phones.

**Setup (once, on a computer, about 5 minutes):**
1. Create a new Google Sheet (open `sheets.new`) and name it, for example, "YRG DTR Backup".
2. **Extensions → Apps Script**. Delete the sample code and paste all of [`tools/google-sheet-backup.gs`](tools/google-sheet-backup.gs).
3. Change `BACKUP_KEY` at the top to your own secret (8+ characters) and save.
4. **Deploy → New deployment → Web app**. Set *Execute as* to **Me** and *Who has access* to **Anyone**. Deploy, allow access, and copy the **Web app URL** (it ends in `/exec`).
5. In the app, sign in as admin: **Guide → Google Sheet backup**. Paste the URL and the key, then tap **Save and test**.
6. Tap **Save data file**. The file now carries the Sheet settings, so staff phones that load it back up automatically.

**What goes into the Sheet:**

| Tab | Contents |
|---|---|
| Services | Every DTR verification: DTR, structure name, feeder, service no, UKSCNO, meter, consumer, result, source, who, when |
| Unknown meters | Meters scanned that are not in the master or the mapping |
| Feeder checks | Feeder-wise structure confirmations |
| Area checks | Area-code-wise structure confirmations |
| Backup log | Each backup: time, phone, user |
| Section master | All services with meter, structure, feeder and area (only when the admin taps **Copy section master to Sheet**) |
| App data | The section data file in parts, so a new phone can download it with the key (only when the admin taps **Put section data on Sheet**) |

- **How it updates:** each row is matched by its KEY, and the newest entry wins. Removed entries stay as `REMOVED`, so the removal reaches the other phones.
- **When it runs:** every 3 minutes, when the app is opened, shortly after each change, when the internet comes back, and when you pull down on a list or tap the badge at the top. Each sync first pulls other phones' entries, then sends this phone's.
- **Keep it private:** the web app URL plus the key give access to the data. Share them only through the data file, never in a public place.
- **Where it works:** in the Android app and the GitHub Pages version. The claude.ai preview cannot reach Google.

## Limits of this hosted version
- **Results are saved on each phone first.** With Google Sheet backup set up, phones share entries through the Sheet (pull on start, push after changes). Without it, results stay on the phone and you collect them through **Report → downloads**.
- **IR/IRDA is a demo.** Real reads need an optical probe (USB-OTG or Bluetooth) and a native Android app using DLMS/COSEM (IS 15959), plus TGSPDCL approval for meter passwords. See the Guide tab.
- **Live camera** scanning works here because GitHub Pages serves over HTTPS. Use Chrome on Android, or the APK below.


## Android app (APK): DTR Verify

The same app packaged as a native Android app with **Capacitor**:

- **Native scanner (Google ML Kit):** full-screen, continuous QR and barcode scanning with torch and zoom. Each meter's result appears in a bottom sheet over the camera, with a beep and a vibration.
- **Native feel:** haptics, splash screen, green status bar, Android back button, native confirm dialogs, keyboard-aware layout, screen kept on while scanning, offline badge.
- **Fast:** entries are saved per DTR in IndexedDB, lists update one row at a time, and fonts and libraries are bundled so nothing waits for the internet.
- **Safe:** a copy of all entries is written to `Documents/YRG DTR Verify/` on the phone, and it survives uninstalling. **Guide → Restore entries backup** brings it back.
- **New phone in one step:** sign in as admin, type the backup key, tap **Get section data from Google Sheet**. The admin puts the section data on the Sheet once with **Guide → Put section data on Sheet**.

### Download
**https://github.com/krishnakuteerapartment-dev/AMEERPET-SECTION/releases/download/apk/DTR-Verify.apk**

Open the link in Chrome on the phone, download, tap the file, and allow "Install unknown apps" when Android asks.

**Updates install over the app and keep its entries.** Every APK is signed with the same permanent key (`yrg-dtr-release.jks`, kept by the admin, never in this repository). Never uninstall to update.

The first test builds were named *YRG DTR Verify* (`com.ameerpetsection.dtrverify`) and each was signed with a throwaway key. *DTR Verify* is a separate app, so it installs next to them. To move entries over: in the old app sign in as admin, set the backup key and tap **Save and test**; then tap **Sync now** in DTR Verify; then uninstall the old app.

### How builds are signed
- `.github/workflows/android-apk.yml` builds an unsigned release APK and a debug APK on every push to `main`, and runs the debug APK on an Android emulator with made-up data (screenshots go to the `ci-screens` release).
- The release APK is signed with the permanent key using `tools/apksign.py` (APK Signature Scheme v2) and pushed to the `signed-apk` branch. `.github/workflows/publish-signed.yml` installs it on an emulator and publishes it to the `apk` release.
- Optional: add repository secrets `ANDROID_KEYSTORE_B64` (the keystore, base64), `ANDROID_KEYSTORE_PASSWORD` and `ANDROID_KEY_ALIAS` (`yrgdtr`). CI then signs and publishes every build by itself.

### Build it yourself in Android Studio (Windows)
1. Install **Node.js 22 LTS**, **Git** and the latest **Android Studio** (it includes the JDK and Android SDK; let it install SDK Platform 36).
2. In PowerShell:
   ```powershell
   git clone https://github.com/krishnakuteerapartment-dev/AMEERPET-SECTION.git
   cd AMEERPET-SECTION
   npm install
   npm run sync          # copies index.html into the Android project
   npx cap open android  # opens the android folder in Android Studio
   ```
3. **Build → Generate Signed Bundle / APK → APK**, choose `yrg-dtr-release.jks` (alias `yrgdtr`), build type **release**. An APK signed with any other key will not install over the staff phones' app.

After changing `index.html`, run `npm run sync` again before building.

| Setting | Value |
|---|---|
| App ID | `com.ameerpetsection.yrgdtr` |
| App name | DTR Verify |
| Capacitor | 8.5.2: ML Kit Barcode Scanning, Haptics, Splash Screen, Keyboard, Network, Device, Dialog, Keep Awake, Filesystem, Share, App |
| Android | min SDK 24 (Android 7.0), target SDK 36, portrait |
| Permissions | Internet, Camera, Vibrate, network state; storage only on Android 10 and older (for the backup file) |

## Files
- `index.html`: the whole app (no consumer data).
- `tools/google-sheet-backup.gs`: Apps Script for the Google Sheet backup.
- `tools/make_data.py`: builds the private section data file from the consumer master PDF and the Service Mapping Excel.
- `package.json`, `capacitor.config.json`, `tools/build-www.mjs`: Capacitor setup. `npm run sync` copies `index.html` into `www/` with the scanning and Excel libraries bundled offline.
- `android/`: the Android Studio project.
- `.github/workflows/android-apk.yml`: builds the APKs and runs the emulator test on every push.
- `.github/workflows/publish-signed.yml`, `tools/apksign.py`: check and publish the APK signed with the permanent key.
- `tools/ci/`: emulator test (made-up data only).
