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

## Limits of this hosted version
- **Results stay on each phone.** Verification results are saved in that phone's browser. Phones do not sync with each other here, so use **Report → downloads** to collect results. Sharing across staff in real time needs a small server (for example Cloudflare Workers + D1, or Firebase), which is the next step.
- **IR/IRDA is a demo.** Real reads need an optical probe (USB-OTG or Bluetooth) and a native Android app using DLMS/COSEM (IS 15959), plus TGSPDCL approval for meter passwords. See the Guide tab.
- **Live camera** scanning works here because GitHub Pages serves over HTTPS. Use Chrome on Android.

## Files
- `index.html`: the whole app (no consumer data).
- `tools/make_data.py`: builds the private section data file from the consumer master PDF and the Service Mapping Excel.
