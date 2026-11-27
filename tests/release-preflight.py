"""Verify exact F1.5 candidate before browser acceptance."""
import hashlib, json, stat, sys, zipfile
from pathlib import PurePosixPath

EXPECTED = {
    'index.html': 'ea0f3dacf1769e2fe2aa853d09769cd52eafef5e548c2e6cbf9d113912b67ea1',
    'style.css': '6240a4c5968f3780fe46f1bee51183bb622d5f44b0a76fdec0454d5f5b796312',
    'src/app.js': 'c2d5dff15893076cac32dd61f974f1d9db3499527760973fff2a2ba08ca4cfae',
}
def require(ok, message):
    if not ok: raise SystemExit(message)
def read_archive(path):
    with zipfile.ZipFile(path) as z:
        entries = z.infolist()
        require(z.testzip() is None, 'Invalid ZIP CRC')
        require(len({i.filename for i in entries}) == len(entries), 'Duplicate ZIP path')
        for i in entries:
            p = PurePosixPath(i.filename)
            require(not p.is_absolute() and '..' not in p.parts and '\\' not in i.filename and not stat.S_ISLNK(i.external_attr >> 16), 'Unsafe ZIP path: '+i.filename)
        return {i.filename:z.read(i) for i in entries if not i.is_dir()}
def sha(b): return hashlib.sha256(b).hexdigest()
baseline, candidate = map(read_archive, sys.argv[1:3])
site = {k[5:]:v for k,v in candidate.items() if k.startswith('site/')}
a,b = (json.loads(x['manifest.webmanifest']) for x in (baseline,site))
for key in ('id','scope','start_url','display','orientation'):
    require(a[key] == b[key], 'PWA identity changed: '+key)
for icon in a['icons']:
    p=icon['src']; require(baseline[p]==site[p], 'Original app icon changed: '+p)
legacy = {k[len('games/legacy/'):]:v for k,v in site.items() if k.startswith('games/legacy/')}
require(len(legacy)==15, 'Unexpected Legacy module size')
for k,v in legacy.items():
    require(k in baseline, 'Unexpected Legacy file: '+k)
    if k in EXPECTED: require(sha(v)==EXPECTED[k], 'Unapproved adapter change: '+k)
    else: require(v==baseline[k], 'Original game content changed: '+k)
require(EXPECTED.keys() <= legacy.keys(), 'Missing platform adapters')
games=json.loads(candidate['integration/games.json'])['games']
require([g['id'] for g in games if g['status']=='released']==['legacy'], 'Unapproved game released')
require(set(games[0]['save']['keys'])=={'thien-thu-v8','thien-thu-v8-recovery'}, 'Save identity changed')
require(set(games[0]['files'])=={'games/legacy/'+k for k in legacy}, 'Resource catalog mismatch')
print(json.dumps({'pwa_identity':'PASS','icons':'PASS','legacy_unchanged':12,'approved_adapters':3,'save_keys':'PASS','released_games':['legacy'],'site_files':len(site)},ensure_ascii=False,indent=2))
