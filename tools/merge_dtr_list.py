"""Take DTR names (and KVA, substation; type/feeder for DTRs without services) from the section's all-DTRs Excel.
usage: merge_dtr_list.py structs.json ALL_DTRS.xlsx"""
import json, sys, re, openpyxl
sp, xp = sys.argv[1:3]
S = json.load(open(sp))
cl = lambda v: re.sub(r'\s+', ' ', str('' if v is None else v)).strip()
code = lambda v: re.sub(r'\.0+$', '', cl(v))
rows = list(openpyxl.load_workbook(xp, read_only=True).worksheets[0].iter_rows(values_only=True))
hdr = [cl(h).upper() for h in rows[0]]; ix = {h: i for i, h in enumerate(hdr)}
g = lambda r, k: r[ix[k]]
seen = {}; renamed = added = 0
for r in rows[1:]:
    c = code(g(r, 'STRUCTURE CODE'))
    if not c: continue
    kva = code(g(r, 'CAPACITY'))
    if c in seen:  # second DTR on the same structure
        if kva: S[c][4] = (S[c][4] + '+' if S[c][4] else '') + kva
        continue
    seen[c] = 1
    name, ss = cl(g(r, 'FUNC. LOC. TEXT')), cl(g(r, 'SUBSTATION NAME'))
    if c in S:
        s = S[c] + [''] * (6 - len(S[c]))
        if name and name != s[0]: renamed += 1
        S[c] = [name or s[0], s[1] or cl(g(r, 'FL TYPE')), s[2] or cl(g(r, 'FEEDER NAME')), s[3] or code(g(r, 'FEEDER CODE')), kva, ss]
    else:
        S[c] = [name, cl(g(r, 'FL TYPE')), cl(g(r, 'FEEDER NAME')), code(g(r, 'FEEDER CODE')), kva, ss]; added += 1
json.dump(S, open(sp, 'w'), separators=(',', ':'), ensure_ascii=False)
print(f'DTR list: {len(seen)} structure codes; names updated {renamed}; added (no services) {added}; structures now {len(S)}')
