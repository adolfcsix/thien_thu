"""Consolidate the built release without modifying shipped runtime bytes."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,zipfile
root=Path(sys.argv[1]).resolve()
repo=Path(__file__).resolve().parents[2]
expected={'legacy':'9.2','cubiq':'1.2','block-nova':'1.2','feather-fury':'14.1','ky-vien':'1.0','garden-through-time':'0.79.3','huyen-anh':'0.82.3','pham-nhan-tu-tien':'0.7'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def patch(path,old,new):
    p=root/path
    text=p.read_text(encoding='utf-8')
    assert text.count(old)==1,(path,old)
    p.write_text(text.replace(old,new),encoding='utf-8')
site=root/'site'
runtime={p.relative_to(site).as_posix():sha(p) for p in site.rglob('*') if p.is_file()}
baseline=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import('./site/catalog.js').then(({released})=>console.log(JSON.stringify(released.map(({id,version,entry,save,integrity})=>({id,version,entry,save,integrity})),null,2)))"],cwd=root,text=True))
assert {g['id']:g['version'] for g in baseline}==expected
(root/'integration/release-baseline.json').write_text(json.dumps(baseline,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
patch('tests/foundation.test.js','three approved games; future titles have no launch entry','eight approved games; future titles have no launch entry')
patch('tests/foundation.test.js','["legacy","cubiq","block-nova","feather-fury"]','["legacy","cubiq","block-nova","feather-fury","ky-vien","garden-through-time","huyen-anh","pham-nhan-tu-tien"]')
patch('tests/integration.test.js',"c.games.filter(g=>g.status==='released').length,4)","c.games.filter(g=>g.status==='released').length,8)")
patch('tests/integration.test.js',"c.games.filter(g=>g.status==='released').length,5)","c.games.filter(g=>g.status==='released').length,9)")
patch('tests/worker.test.js',"{legacy:true,cubiq:false,'block-nova':false,'feather-fury':false}","Object.fromEntries(released.map(g=>[g.id,g.id==='legacy']))")
patch('tests/worker.test.js',"for(const id of ['cubiq','block-nova','feather-fury'])","for(const {id} of released.filter(g=>g.id!=='legacy'))")
patch('tests/worker.test.js',"assert.equal(d['block-nova'],true);assert.equal(d.legacy,true);assert.equal(d['feather-fury'],true)","for(const g of released.filter(g=>g.id!=='cubiq'))assert.equal(d[g.id],true)")
patch('tests/worker.test.js',"'?xi-release=1.20.0'","'?xi-release='+globalThis.XI_CATALOG.HUB_VERSION")
# Historical UI tests remain in the four-game candidate and mandatory CI jobs.
for p in (root/'tests').glob('*.py'):p.unlink()
shutil.copyfile(repo/'updates/six-games/browser.py',root/'tests/browser.py')
shutil.copyfile(repo/'updates/six-games/verify-source.py',root/'tools/verify-source.py')
(root/'README.md').write_text("""# Xi Universe F1.26 — consolidated source candidate
Run Node 22+ and Python 3.12+.
- npm test — catalog, integrity and unit tests.
- npm start — local web server on port 8000.
- python tools/verify-source.py . — verify snapshot inventory.
- python -m pip install playwright
- python -m playwright install chromium webkit
- python tests/browser.py --engine chromium --site site
- python tests/browser.py --engine webkit --site site

Maintain site/ and integration/ directly. For subsequent releases, increment affected versions, regenerate catalog, worker integrity and offline kit, and refresh the snapshot manifest after testing. Historical V9 and four-game migration suites remain in the parent repository. This candidate requires all browser and deployment gates.
""",encoding='utf-8')
assert runtime=={p.relative_to(site).as_posix():sha(p) for p in site.rglob('*') if p.is_file()}
subprocess.run(['npm','test'],cwd=root,check=True)
lock={'format':'xi-source-lock-v1','hubVersion':'1.26.0','games':expected,'files':{p.relative_to(root).as_posix():sha(p) for p in sorted(root.rglob('*')) if p.is_file() and p.name!='source-lock.json'}}
(root/'source-lock.json').write_text(json.dumps(lock,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
subprocess.run([sys.executable,'tools/verify-source.py','.'],cwd=root,check=True)
with zipfile.ZipFile(root.parent/'release.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(root.rglob('*')):
        if p.is_file():
            info=zipfile.ZipInfo(p.relative_to(root).as_posix(),date_time=(2020,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
print('PASS consolidated source, final unit suite, unchanged runtime')
