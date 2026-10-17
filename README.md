# Ameerpet Section: DTR Verification App

A phone app (one HTML page) for **Section 10 Yella Reddy Guda, ERO 11 Banjara Hills (TGSPDCL)**. Staff use it to verify services DTR-wise, structures feeder-wise, and structures area-code-wise in the field.

**Open the app:** https://krishnakuteerapartment-dev.github.io/AMEERPET-SECTION/

## What it does

| Tab | Purpose |
|---|---|
| **Services** | Pick a DTR structure code (1607010001–1607010800). Scan each meter's QR code or barcode, or use IR/IRDA (demo), or type the number. The app shows the **Service No and UKSCNO** and tells you whether the service belongs to this DTR. |
| **Feeders** | Pick a feeder. Confirm each structure the mapping puts on it, by scanning a DTR tag, typing the code or name, or ticking it from the list. |
| **Areas** | Pick an area code. Confirm each structure that has services in that area. |
| **Search** | Find any service by service no, UKSCNO, meter no or name. |
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
1. Open the app link.
2. Tap **Load section data file (.json)** and choose `YRGuda_section_data.json`. The AE shares this file privately, never through GitHub.

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

- **How it updates:** each row is matched by its KEY, and the newest entry wins. Removed entries stay as `REMOVED`, so the removal reaches the other phones.
- **When it runs:** changes back up automatically within a minute when online. On start, the app first pulls new entries from the Sheet, then sends its own.
- **Keep it private:** the web app URL plus the key give access to the data. Share them only through the data file, never in a public place.
- **Where it works:** in the Android app and the GitHub Pages version. The claude.ai preview cannot reach Google.

## Limits of this hosted version
- **Results are saved on each phone first.** With Google Sheet backup set up, phones share entries through the Sheet (pull on start, push after changes). Without it, results stay on the phone and you collect them through **Report → downloads**.
- **IR/IRDA is a demo.** Real reads need an optical probe (USB-OTG or Bluetooth) and a native Android app using DLMS/COSEM (IS 15959), plus TGSPDCL approval for meter passwords. See the Guide tab.
- **Live camera** scanning works here because GitHub Pages serves over HTTPS. Use Chrome on Android, or the APK below.


## Android app (APK)

The same app is packaged as an Android app with **Capacitor**. Inside the APK, scanning uses the phone camera directly, scanning and Excel import work without internet, and CSV and data files are shared through WhatsApp, Drive or Files.

### Download the ready APK
Every push to `main` builds a new APK on GitHub:
**https://github.com/krishnakuteerapartment-dev/AMEERPET-SECTION/releases/download/apk/YRG-DTR-Verify.apk**

To install it on a phone: open the link in Chrome, download, tap the file, and allow "Install unknown apps" for Chrome when Android asks. On first open, load `YRGuda_section_data.json`.

### Build it yourself in Android Studio (Windows)
1. Install **Node.js 22 LTS**, **Git** and the latest **Android Studio**. Android Studio includes the JDK and the Android SDK; let it install SDK Platform 36 when it asks.
2. In a terminal (PowerShell):
   ```powershell
   git clone https://github.com/krishnakuteerapartment-dev/AMEERPET-SECTION.git
   cd AMEERPET-SECTION
   npm install
   npm run sync          # copies index.html into the Android project
   npx cap open android  # opens the android folder in Android Studio
   ```
3. In Android Studio, wait for **Gradle sync** to finish, then use **Build → Build App Bundle(s) / APK(s) → Build APK(s)**. Click **locate** in the popup to find `app-debug.apk` (in `android\app\build\outputs\apk\debug\`).
4. To run it directly, connect a phone with **USB debugging** on and press **Run ▶**.

After changing `index.html`, run `npm run sync` again before building.

**For a signed release APK** (needed to update the app without uninstalling, or for Play Store): **Build → Generate Signed Bundle / APK → APK**, then create a keystore and keep it safe. Never commit the keystore; `.gitignore` blocks `*.jks` and `*.keystore`.

| Setting | Value |
|---|---|
| App ID | `com.ameerpetsection.dtrverify` |
| App name | YRG DTR Verify |
| Capacitor | 8.5.2 (Filesystem, Share, App plugins) |
| Android | min SDK 24 (Android 7.0), target SDK 36 |
| Permissions | Internet, Camera |

## Files
- `index.html`: the whole app (no consumer data).
- `tools/google-sheet-backup.gs`: Apps Script for the Google Sheet backup.
- `tools/make_data.py`: builds the private section data file from the consumer master PDF and the Service Mapping Excel.
- `package.json`, `capacitor.config.json`, `tools/build-www.mjs`: Capacitor setup. `npm run sync` copies `index.html` into `www/` with the scanning and Excel libraries bundled offline.
- `android/`: the Android Studio project.
- `.github/workflows/android-apk.yml`: builds the APK on every push.
