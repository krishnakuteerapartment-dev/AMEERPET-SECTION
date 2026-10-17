/**
 * YRG DTR Verify: Google Sheet backup
 *
 * Setup (once, on a computer):
 *   1. Create a new Google Sheet (sheets.new) and name it, e.g. "YRG DTR Backup".
 *   2. Extensions > Apps Script. Delete the sample code and paste this whole file.
 *   3. Change BACKUP_KEY below to your own secret (at least 8 characters). Save.
 *   4. Deploy > New deployment > Select type: Web app
 *        Execute as: Me
 *        Who has access: Anyone
 *      Deploy, allow access when Google asks, and copy the Web app URL (ends in /exec).
 *   5. In the app: Guide > Google Sheet backup > paste the URL and the same key > Save and test.
 *
 * The app sends entries as JSON. Each tab is keyed on its first column (KEY);
 * an incoming row replaces the stored one only if its T_MS (time in ms) is newer or equal.
 * Removed entries arrive with STATUS_CODE "del", so removals reach the other phones too.
 */
const BACKUP_KEY = 'CHANGE-THIS-KEY';

function doPost(e) {
  let body;
  try { body = JSON.parse(e.postData.contents); } catch (err) { return json_({ ok: false, error: 'Request was not valid JSON' }); }
  if (!keyOk_(body && body.key)) return json_({ ok: false, error: 'Wrong backup key' });
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const result = {};
    Object.keys(body.sheets || {}).forEach(function (name) {
      const part = body.sheets[name];
      result[name] = (part.mode === 'replace' || part.mode === 'append') ? writeAll_(ss, name, part) : upsert_(ss, name, part);
    });
    log_(ss, body, result);
    return json_({ ok: true, result: result, at: new Date().toISOString() });
  } finally {
    lock.releaseLock();
  }
}

function doGet(e) {
  const p = (e && e.parameter) || {};
  if (!keyOk_(p.key)) return json_({ ok: false, error: 'Wrong backup key' });
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  if (p.ping) return json_({ ok: true, sheet: ss.getName() });
  const names = String(p.sheets || 'Services,Unknown meters,Feeder checks,Area checks').split(',');
  const sheets = {};
  names.forEach(function (n) {
    const sh = ss.getSheetByName(n);
    if (!sh || sh.getLastRow() < 1) { sheets[n] = { header: [], rows: [] }; return; }
    const v = sh.getDataRange().getDisplayValues();
    sheets[n] = { header: v[0], rows: v.slice(1) };
  });
  return json_({ ok: true, sheets: sheets });
}

function keyOk_(k) {
  return BACKUP_KEY !== 'CHANGE-THIS-KEY' && String(k || '') === BACKUP_KEY;
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

function sheetFor_(ss, name, header) {
  let sh = ss.getSheetByName(name);
  if (!sh) sh = ss.insertSheet(name);
  // keep every cell as plain text so meter numbers keep their leading zeros
  const cols = Math.max(header.length, 1);
  if (sh.getMaxColumns() < cols) sh.insertColumnsAfter(sh.getMaxColumns(), cols - sh.getMaxColumns());
  sh.getRange(1, 1, sh.getMaxRows(), cols).setNumberFormat('@');
  sh.getRange(1, 1, 1, header.length).setValues([header]).setFontWeight('bold');
  sh.setFrozenRows(1);
  return sh;
}

function ensureRows_(sh, lastRowNeeded) {
  const max = sh.getMaxRows();
  if (lastRowNeeded > max) sh.insertRowsAfter(max, lastRowNeeded - max);
}

function upsert_(ss, name, part) {
  const header = part.header || [], rows = part.rows || [];
  if (!rows.length) return { added: 0, updated: 0 };
  const sh = sheetFor_(ss, name, header);
  const width = header.length, lastRow = sh.getLastRow();
  const existing = lastRow > 1 ? sh.getRange(2, 1, lastRow - 1, width).getValues() : [];
  const tCol = header.indexOf('T_MS');
  const index = {};
  existing.forEach(function (r, i) { index[String(r[0])] = i; });
  const extra = [];
  let added = 0, updated = 0, changed = false;
  rows.forEach(function (r) {
    r = r.slice(0, width); while (r.length < width) r.push('');
    r = r.map(function (c) { return c == null ? '' : String(c); });
    const k = r[0], i = index[k];
    const newer = function (old) { return tCol < 0 || Number(r[tCol]) >= Number(old[tCol]); };
    if (i === undefined) { index[k] = existing.length + extra.length; extra.push(r); added++; }
    else if (i < existing.length) { if (newer(existing[i])) { existing[i] = r; updated++; changed = true; } }
    else if (newer(extra[i - existing.length])) { extra[i - existing.length] = r; }
  });
  if (changed) sh.getRange(2, 1, existing.length, width).setValues(existing);
  if (extra.length) {
    const start = existing.length + 2;
    ensureRows_(sh, start + extra.length - 1);
    sh.getRange(start, 1, extra.length, width).setNumberFormat('@').setValues(extra);
  }
  return { added: added, updated: updated };
}

function writeAll_(ss, name, part) {
  const header = part.header || [], rows = (part.rows || []).map(function (r) { return r.map(function (c) { return c == null ? '' : String(c); }); });
  let sh = ss.getSheetByName(name);
  if (part.mode === 'replace' && sh) sh.clear();
  sh = sheetFor_(ss, name, header);
  if (!rows.length) return { written: 0 };
  const start = sh.getLastRow() + 1;
  ensureRows_(sh, start + rows.length - 1);
  sh.getRange(start, 1, rows.length, header.length).setNumberFormat('@').setValues(rows);
  return { written: rows.length };
}

function log_(ss, body, result) {
  const header = ['TIME', 'DEVICE', 'USER', 'APP_VERSION', 'RESULT'];
  let sh = ss.getSheetByName('Backup log');
  if (!sh) { sh = ss.insertSheet('Backup log'); sh.getRange(1, 1, 1, header.length).setValues([header]).setFontWeight('bold'); sh.setFrozenRows(1); }
  sh.appendRow([new Date(), body.device || '', body.user || '', body.app || '', JSON.stringify(result)]);
}
