#!/usr/bin/env python3
"""Build the private section data file used by the DTR verification app.

Inputs (keep these private, never commit them):
  1. EBS "Consumer Master Details" PDF for the section  -> meter no, phase, make, seal, last reading
  2. "Service Mapping" Excel for the section            -> structure, feeder, area, service no, UKSCNO

Output:
  YRGuda_section_data.json  (load it in the app: Guide > Data on this phone > Load section data file)

Usage:
  python3 tools/make_data.py MASTER.pdf SERVICE_MAPPING.xlsx [-o YRGuda_section_data.json]

Needs: pdftotext (poppler-utils) and openpyxl  (pip install openpyxl)
"""
import argparse, base64, datetime, gzip, json, re, subprocess, sys

F = ['s','u','m','dtr','n','a','ph','ct','ld','mk','r','rm','sl','st','mf','an','x']

# Two printed lines per service in the EBS consumer master
L1 = re.compile(r'^([A-Z0-9]{6,10})\s+(\S+)\s+(\d+\.\d+)\s+(.*?)\s+(\d{9})\s+(\S+)\s+(\d+)\s+(?:(.+?)\s+)?(OPEN|CONCEAL)\s+(NO DATE|\d\d/\d\d/\d\d)\s+(-?\d+(?:\.\d+)?)\s+(\d+\.\d+)\s*$')
L2 = re.compile(r'^(\S+)\s+(\S+)\s+(\S)\s+(\S+)\s+(\d+\.\d+)\s?(.*?)\s+(-?\d+)\s+([13])\s*(.*?)\s*(YES|NO)\s+(NO DATE|\d\d/\d\d/\d\d)\s+(\d\d/\d{4})(?:\s+(-?[\d.]+))?\s*$')

def num(v):
    v = float(v)
    return int(v) if v == int(v) else v

def parse_master(pdf):
    txt = subprocess.run(['pdftotext', '-layout', pdf, '-'], capture_output=True, text=True, check=True).stdout
    lines = txt.replace('\x0c', '').split('\n')
    recs, i = [], 0
    while i < len(lines):
        m = L1.match(lines[i])
        if not m:
            i += 1; continue
        g = m.groups()
        r = dict(s=g[0], ct=g[1], ld=float(g[2]), n=g[3].strip(), u=g[4], m=g[5], dtr=g[6], sl=g[7] or '',
                 r=float(g[10]), mf=float(g[11]), a='', mk='', ph=1, st='', rm='')
        j = i + 1
        while j < len(lines) and not lines[j].strip(): j += 1
        m2 = L2.match(lines[j]) if j < len(lines) else None
        if m2:
            h = m2.groups()
            parts = re.split(r'\s{2,}', h[5].strip())
            r.update(st=h[1], ph=int(h[7]), rm=h[11])
            if len(parts) >= 2: r['a'], r['mk'] = ' '.join(parts[:-1]), parts[-1]
            else: r['a'] = h[5].strip()
            i = j + 1
        else:
            i += 1
        recs.append(r)
    # split address and meter make where they were printed with a single space
    makes = sorted({r['mk'] for r in recs if r['mk']}, key=len, reverse=True)
    for r in recs:
        if not r['mk']:
            for k in makes:
                if len(k) >= 3 and r['a'].endswith(k):
                    r['mk'], r['a'] = k, r['a'][:-len(k)].strip(); break
    return recs

def parse_mapping(xlsx):
    import openpyxl
    ws = openpyxl.load_workbook(xlsx, read_only=True).worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    hdr = [str(c or '').strip().upper() for c in rows[0]]
    return [dict(zip(hdr, r)) for r in rows[1:]]

def clean(v):
    return re.sub(r'[\t\r\n]+', ' ', str(v if v is not None else '')).strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('master_pdf'); ap.add_argument('mapping_xlsx')
    ap.add_argument('-o', '--out', default='YRGuda_section_data.json')
    a = ap.parse_args()

    old = {r['u']: r for r in parse_master(a.master_pdf)}
    rows = parse_mapping(a.mapping_xlsx)
    print(f'consumer master: {len(old)} services · mapping: {len(rows)} rows', file=sys.stderr)

    out, structs, areas, seen = [], {}, {}, set()
    for m in rows:
        u = clean(m['UKSCNO']).removesuffix('.0')
        if not u or u in seen: continue
        seen.add(u)
        o = old.get(u, {})
        code = clean(m['STRUCTURE CODE']).removesuffix('.0')
        structs.setdefault(code, [clean(m.get('STRUCTURE NAME')), clean(m.get('STRUCTURE TYPE')), clean(m.get('FEEDER NAME')), clean(m.get('FEEDER CODE')).removesuffix('.0')])
        ac = clean(m.get('AREA CODE')).removesuffix('.0'); an = clean(m.get('AREA NAME'))
        if ac:
            areas.setdefault(ac, [an, {}]); areas[ac][1][code] = areas[ac][1].get(code, 0) + 1
        addr = clean(m.get('ADDRESS'))
        if not re.sub(r'[\W_]+', '', addr): addr = o.get('a', '')
        out.append([clean(m['SERVICE NO']), u, o.get('m', '0'), code, clean(m.get('CONSUMER NAME')) or o.get('n', ''), addr,
                    o.get('ph', 1), o.get('ct', ''), num(o.get('ld', 0)), o.get('mk', ''), num(o.get('r', 0)), o.get('rm', ''),
                    o.get('sl', ''), o.get('st', ''), num(o.get('mf', 1)), an, 0])
    legacy = 0
    for u, o in old.items():  # in the consumer master but not in the mapping: kept for scanning, flagged
        if u in seen: continue
        legacy += 1
        out.append([o['s'], u, o['m'], o['dtr'], o['n'], o['a'], o['ph'], o['ct'], num(o['ld']), o['mk'], num(o['r']), o['rm'], o['sl'], o['st'], num(o['mf']), '', 1])

    txt = '\n'.join('\t'.join(str(c) for c in r) for r in out)
    today = datetime.date.today().strftime('%d-%b-%Y')
    data = {'app': 'yrguda-dtr', 'v': 1,
            'meta': {'mapOn': today, 'masterOn': today},
            'records': base64.b64encode(gzip.compress(txt.encode(), 9)).decode(),
            'structs': structs, 'areas': areas}
    with open(a.out, 'w', encoding='utf-8') as f:
        json.dump(data, f, separators=(',', ':'), ensure_ascii=False)
    nometer = sum(1 for r in out if not r[16] and r[2] in ('0', ''))
    print(f'wrote {a.out}: {len(seen)} mapped services, {legacy} only in master, {len(structs)} structures, '
          f'{len(areas)} areas, {nometer} mapped services without meter no', file=sys.stderr)

if __name__ == '__main__':
    main()
