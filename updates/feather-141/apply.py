"""Xi F1.20: lossless 14.1 source, additive save migration and existing Xi UI contract."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,zipfile
root=Path(sys.argv[1]);site=root/'site';target=site/'games/feather-fury/index.html'
source=Path(sys.argv[2]) if len(sys.argv)>2 else None
raw=source.read_bytes() if source else b''.join(f.read_bytes() for f in sorted(Path(__file__).with_name('source').glob('*.part')))
assert hashlib.sha256(raw).hexdigest()=='9d53c91aff9b9ce38d8f442e7cc58f4c68f756c3f804266550c5a4a7e8ccac80'
s=raw.decode('utf-8');old=target.read_text();kit=site/'xi-offline-kit.zip';protected={f:hashlib.sha256(f.read_bytes()).hexdigest() for f in site.rglob('*') if f.is_file() and (f.relative_to(site).parts[0] in ('games','assets') or f.name=='manifest.webmanifest') and f!=target}
def patch(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
ns='xi:game:feather-fury:'
patch("KEY='ff12.2-progress'", "KEY='"+ns+"ff14.1-progress'")
patch("[KEY,BACKUP_KEY,'ff12.1-progress'", "[KEY,BACKUP_KEY,'"+ns+"ff12.2-progress','"+ns+"ff12.2-progress-backup','ff12.1-progress'")
for k in ('ff12.1-progress','ff10-progress','ff9-progress','ff8-progress','ff7-progress'):
 s=s.replace("'"+k+"'","'"+ns+k+"'")
# Reuse the previously accepted adapter rather than changing game logic or artwork.
private=old[old.index('function xiPrivateOptions('):old.index('function settings()',old.index('function xiPrivateOptions('))]
patch('function settings(){',private+'function settings(){')
patch('<button id="importSave">Nhập sao lưu</button>','<button id="importSave">Nhập sao lưu</button><button id="xi-private-open">?</button>')
callback=old[old.index(";$('xi-private-open').onclick="):old.index("}\n$('import').onchange",old.index(";$('xi-private-open').onclick="))]
patch("$('importSave').onclick=()=>$('import').click()}","$('importSave').onclick=()=>$('import').click()"+callback+'}')
ret=old[old.index(",['Về sảnh Xi',"):old.index(']]',old.index(",['Về sảnh Xi',"))+1]
patch("['Màn mới nhất',()=>start(sv.open)]]","['Màn mới nhất',()=>start(sv.open)]"+ret+"]")
# Reuse viewport policy and responsive adapter; preserve the source's visual language.
policy=old[old.index('<meta name="viewport"'):old.index('<title>')]
patch('<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">',policy)
layouts=old[old.index('<style id="xi-feather-layout">'):old.index('</head>')]
extra='''<style id="xi-feather-141-layout">#game{padding:0}html .panel input[type=range]{touch-action:pan-x!important}html .deck{touch-action:pan-x pan-y!important}@media(orientation:portrait){#game{height:auto;overflow:visible;padding:0;min-height:calc(100dvh - max(var(--xi-safe-top),var(--xi-fallback-top)) - max(var(--xi-safe-bottom),var(--xi-fallback-bottom)))}.top{padding-top:5px}.arena{min-height:0;overflow:hidden;flex:none}.arena canvas{width:100%;height:auto;aspect-ratio:16/10;object-fit:contain}.room-track{position:relative;inset:auto;order:-1;margin:0 auto}.hud{background:transparent}.wallet button,.hud button,.tabs button,.gold{min-height:44px}.deck .card{min-height:60px}.footer{margin-top:auto}}@media(orientation:landscape) and (max-height:600px){#game{padding:0}.arena canvas{height:auto;aspect-ratio:16/10;object-fit:contain}.tabs button{min-height:44px}}.panel{max-width:100%;overflow-wrap:anywhere}.hero-card,.wardrobe-grid .mini{min-width:0}</style>'''
patch('</head>',layouts+extra+'</head>')
assert re.findall(r'data:image/[^;,]+;base64,[A-Za-z0-9+/=]+',s)==re.findall(r'data:image/[^;,]+;base64,[A-Za-z0-9+/=]+',raw.decode('utf-8'))
target.write_text(s)
p=root/'integration/games.json';d=json.loads(p.read_text());g=next(x for x in d['games'] if x['id']=='feather-fury');g.update(version='14.1',subtitle='Stability Update',description='100 màn, 200 chặng, 12 chim, đội hình 8 chim và năm phép thuật.');g['save']['keys'][:0]=[ns+'ff14.1-progress',ns+'ff14.1-progress-backup',ns+'ff12.2-progress-backup'];d['hubVersion']='1.20.0';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=root/'integration/release-baseline.json';baseline=json.loads(p.read_text());b=next(x for x in baseline if x['id']=='feather-fury');assert set(b['save']['keys'])<set(g['save']['keys']);b['save']['keys']=g['save']['keys'];p.write_text(json.dumps(baseline,ensure_ascii=False,indent=2)+'\n')
subprocess.run(['node','tools/catalog.mjs','--write'],cwd=root,check=True)
for name in ('browser.py','imported-ui.py','personalization-ui.py'):
 p=root/'tests'/name;p.write_text(p.read_text().replace(ns+'ff12.2-progress',ns+'ff14.1-progress'))
# A real navigation destroys the previous JS realm; set_content does not. Use a new
# page before the hub mock so old game animation callbacks cannot read hub markup.
p=root/'tests/personalization-ui.py';t=p.read_text();a=' hub(s);page.get_by_role';assert t.count(a)==1;t=t.replace(a,' page.close();page=b.new_page(viewport={"width":390,"height":844},is_mobile=True,has_touch=True,reduced_motion="reduce");page.set_default_timeout(5000);page.on("pageerror",lambda e:errors.append(str(e)))\n hub(s);page.get_by_role');p.write_text(t)
# A first controller claim already controls this document; reloading during startup
# can interrupt the ES-module graph. Keep reloads for actual worker replacement.
hub=site/'hub.js';h=hub.read_text()
before="navigator.serviceWorker.addEventListener('controllerchange',()=>{if(!busy)location.reload();else refresh()});"
after="let previousController=navigator.serviceWorker.controller;navigator.serviceWorker.addEventListener('controllerchange',()=>{const next=navigator.serviceWorker.controller,prior=previousController;previousController=next;if(!next)return;if(prior&&prior!==next&&!busy)location.reload();else refresh()});"
assert h.count(before)==1,'controllerchange anchor'
h=h.replace(before,after)
before="if(intro.hidden)return;intro.hidden=true;shell.inert=false;"
after="if(intro.hidden&&!document.documentElement.hasAttribute('data-startup'))return;intro.hidden=true;shell.inert=false;"
assert h.count(before)==1,'startup gate anchor'
hub.write_text(h.replace(before,after))
subprocess.run(['node','--check','site/hub.js'],cwd=root,check=True)
subprocess.run([sys.executable,str(Path(__file__).resolve().parents[1]/'shell-stability'/'guard.py'),str(site)],check=True)
subprocess.run(['node','--check','site/sw.js'],cwd=root,check=True)
with (root/'tests/worker.test.js').open('a') as test:
 test.write("""\ntest('reject stale shell before activation, retain previous cache',async()=>{const h=harness();h.setWrong('index.html');await assert.rejects(h.event('install'),/Shell integrity mismatch/);assert(h.maps.has(old));assert(!h.maps.has(shellName(scope)));assert(!h.claimed())});\ntest('canonical navigation uses exact shell bytes and no-store version header',async()=>{const h=harness();await h.event('install');await h.event('activate');h.setOnline(false);for(const path of ['', 'index.html','?xi-release=1.20.0']){const r=await h.event('fetch',{request:{method:'GET',url:scope+path,mode:'navigate'}});assert.equal(r.status,200);assert.equal(r.headers.get('X-Xi-Shell-Version'),globalThis.XI_CATALOG.HUB_VERSION);assert.equal(r.headers.get('Cache-Control'),'no-store');assert.equal(await r.text(),readFileSync(new URL('../site/index.html',import.meta.url),'utf8'))}});\n""")
with zipfile.ZipFile(kit) as z:readme=z.read('README.txt')
with zipfile.ZipFile(kit,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(site.rglob('*')):
  if not f.is_file() or f==kit:continue
  name='site/'+f.relative_to(site).as_posix()
  if f.name=='sw.js':z.writestr(name,f.read_text().replace(",'xi-offline-kit.zip'",''))
  else:z.write(f,name)
 z.writestr('README.txt',readme)
assert all(hashlib.sha256(f.read_bytes()).hexdigest()==h for f,h in protected.items())
print('Protected files unchanged:',len(protected),'14.1 adapter SHA256:',hashlib.sha256(target.read_bytes()).hexdigest())
with zipfile.ZipFile(root.parent/'candidate.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(root.rglob('*')):
  if f.is_file() and ('site' in f.relative_to(root).parts or f.suffix not in ('.pyc','.png')):z.write(f,f.relative_to(root))
