# Ameerpet sec-DTR verify: DTR Verification App

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
2. Use the **full APK** from the admin (data and Sheet link built in: it opens straight to the DTRs), or paste the Sheet link and tap **Get section data from Google Sheet** (after the admin has tapped **Put section data on Sheet** once), or tap **Load section data file (.json)** and choose `YRGuda_section_data.json`. The admin shares this file privately, never through GitHub.

**When a new Service Mapping Excel comes from EBS:**
- In the app, go to **Guide → Data on this phone → Load new mapping Excel**. Structures, feeders and areas are replaced, and the meter numbers already on the phone are kept.
- Then tap **Save data file** and share that file with the other staff phones.

**Rebuilding the data file from the EBS consumer master PDF** (for example when meters change):

```bash
pip install openpyxl          # pdftotext comes with poppler-utils
python3 tools/make_data.py CONSUMER_MASTER.pdf SERVICE_MAPPING.xlsx -o YRGuda_section_data.json
```

`.gitignore` blocks `*.json`, `*.xlsx`, `*.pdf` and `*.csv`, so data files cannot be committed by mistake.


## Google Sheet backup (and sharing between phones), no backup key

Every entry goes to a Google Sheet that you own. Several phones sync into the same Sheet and pull each other's entries, so the one-service-one-DTR check also works across phones.

**Setup (once, on a computer):**
1. Open your backup Google Sheet (or create one at `sheets.new`).
2. **Extensions → Apps Script**. Delete the old code, paste all of [`tools/Code.gs`](tools/Code.gs), and save.
3. **Deploy → New deployment → Web app**. *Execute as:* **Me**. *Who has access:* **Anyone**. Deploy, allow access, and copy the **Web app URL** (it ends in `/exec`).
4. Archive any old deployment (**Deploy → Manage deployments → Archive**). The old keyed link was in this public code, so the app ignores it.
5. The link is built into the full APK (never into this repository). Or, in the app as admin: **☰ → Google Sheet sync**, paste the URL, **Save and test**.

There is no backup key, so anyone who has the Web app URL can read and change the entries. Share the full APK and the link only with your staff.

**What goes into the Sheet:**

| Tab | Contents |
|---|---|
| Services | Every DTR verification: DTR, structure name, feeder, service no, UKSCNO, meter, consumer, result, source, who, when |
| Unknown meters | Meters scanned that are not in the master or the mapping |
| Feeder checks | Feeder-wise structure confirmations |
| Area checks | Area-code-wise structure confirmations |
| Backup log | Each backup: time, phone, user |
| Section master | All services with meter, structure, feeder and area (only when the admin taps **Copy section master to Sheet**) |
| App data | The section data file in parts, so a phone can download it with the link (when the admin taps **Put section data on Sheet**; staff then tap **Get latest data from Sheet**) |

- **How it updates:** each row is matched by its KEY, and the newest entry wins. Removed entries stay as `REMOVED`, so the removal reaches the other phones.
- **When it runs:** every 3 minutes, when the app is opened, shortly after each change, when the internet comes back, and when you pull down on a list or tap the badge at the top. Each sync first pulls other phones' entries, then sends this phone's.
- **Keep it private:** the web app URL alone gives access to the entries. Never put it in a public place.
- **Where it works:** in the Android app and the GitHub Pages version. The claude.ai preview cannot reach Google.

## Limits of this hosted version
- **Results are saved on each phone first.** With Google Sheet backup set up, phones share entries through the Sheet (pull on start, push after changes). Without it, results stay on the phone and you collect them through **Report → downloads**.
- **IR/IRDA is a demo.** Real reads need an optical probe (USB-OTG or Bluetooth) and a native Android app using DLMS/COSEM (IS 15959), plus TGSPDCL approval for meter passwords. See the Guide tab.
- **Live camera** scanning works here because GitHub Pages serves over HTTPS. Use Chrome on Android, or the APK below.


## Android app (APK): Ameerpet sec-DTR verify

The same app packaged as a native Android app with **Capacitor**:

- **Native scanner (Google ML Kit):** full-screen, continuous QR and barcode scanning with torch and zoom. Each meter's result appears in a bottom sheet over the camera, with a beep and a vibration.
- **Native feel:** haptics, splash screen, green status bar, Android back button, native confirm dialogs, keyboard-aware layout, screen kept on while scanning, offline badge.
- **Fast:** entries are saved per DTR in IndexedDB, lists update one row at a time, and fonts and libraries are bundled so nothing waits for the internet.
- **Safe:** a copy of all entries is written to `Documents/YRG DTR Verify/` on the phone, and it survives uninstalling. **Guide → Restore entries backup** brings it back.
- **Data built in:** the full APK (`Ameerpet-sec-DTR-verify-full.apk`, shared privately by the admin) carries the section data and the Sheet link, so the app opens straight to the DTRs after sign-in and syncs with no setup. A newer full APK also updates the data on phones that had older data.

### Download
**https://github.com/krishnakuteerapartment-dev/AMEERPET-SECTION/releases/download/apk/Ameerpet-sec-DTR-verify.apk**

This public download has no consumer data and no Sheet link. Staff should install the full APK from the admin.

Open the link in Chrome on the phone, download, tap the file, and allow "Install unknown apps" when Android asks.

**Updates install over the app and keep its entries.** Every APK is signed with the same permanent key (`yrg-dtr-release.jks`, kept by the admin, never in this repository). Never uninstall to update.

The first test builds were named *YRG DTR Verify* (`com.ameerpetsection.dtrverify`) and each was signed with a throwaway key. *Ameerpet sec-DTR verify* (first released as *DTR Verify*) is a separate app, so it installs next to them. To move entries over: in the old app sign in as admin, set the backup key and tap **Save and test**; then tap **Sync now** in DTR Verify; then uninstall the old app.

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
| App name | Ameerpet sec-DTR verify (APK file: Ameerpet-sec-DTR-verify.apk) |
| Capacitor | 8.5.2: ML Kit Barcode Scanning, Haptics, Splash Screen, Keyboard, Network, Device, Dialog, Keep Awake, Filesystem, Share, App |
| Android | min SDK 24 (Android 7.0), target SDK 36, portrait |
| Permissions | Internet, Camera, Vibrate, network state; storage only on Android 10 and older (for the backup file) |

## Files
- `index.html`: the whole app (no consumer data).
- `tools/Code.gs`: Apps Script for the Google Sheet backup and sync (no backup key).
- `tools/add-data.py`: makes the private full APK by adding `data.js` (section data + Sheet link) to the release APK; sign it afterwards with `tools/apksign.py`.
- `tools/merge_dtr_list.py`: takes DTR names, KVA and substation from the all-DTRs list Excel into the section data.
- `tools/make_data.py`: builds the private section data file from the consumer master PDF and the Service Mapping Excel.
- `package.json`, `capacitor.config.json`, `tools/build-www.mjs`: Capacitor setup. `npm run sync` copies `index.html` into `www/` with the scanning and Excel libraries bundled offline.
- `android/`: the Android Studio project.
- `.github/workflows/android-apk.yml`: builds the APKs and runs the emulator test on every push.
- `.github/workflows/publish-signed.yml`, `tools/apksign.py`: check and publish the APK signed with the permanent key.
- `tools/ci/`: emulator test (made-up data only).
