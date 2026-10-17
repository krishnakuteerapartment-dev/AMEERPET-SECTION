// Copies index.html into www/ for the Android app and points the barcode and Excel
// libraries at local copies, so scanning and Excel import work without internet.
import { readFileSync, writeFileSync, mkdirSync, copyFileSync } from 'node:fs';

mkdirSync('www/vendor', { recursive: true });
copyFileSync('node_modules/@zxing/library/umd/index.min.js', 'www/vendor/zxing.min.js');
copyFileSync('node_modules/xlsx/dist/xlsx.full.min.js', 'www/vendor/xlsx.full.min.js');

let html = readFileSync('index.html', 'utf8');
const swaps = [
  ['https://cdn.jsdelivr.net/npm/@zxing/library@0.21.3/umd/index.min.js', 'vendor/zxing.min.js'],
  ['https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js', 'vendor/xlsx.full.min.js'],
];
for (const [from, to] of swaps) {
  if (!html.includes(from)) throw new Error('index.html no longer references ' + from);
  html = html.split(from).join(to);
}
writeFileSync('www/index.html', html);
console.log('www/ ready');
