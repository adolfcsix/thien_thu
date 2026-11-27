from pathlib import Path
import json,hashlib,subprocess,sys,zipfile,re
root=Path(sys.argv[1]);source=Path(sys.argv[2]);site=root/'site';target=site/'games/feather-fury/index.html';old=target.read_text();s=source.read_text();protected={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in site.rglob('*') if p.is_file() and (p.relative_to(site).parts[0] in ('games','assets') or p.name=='manifest.webmanifest') and p!=target}
def patch(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
for key in ['ff12.2-progress','ff12.1-progress','ff10-progress','ff9-progress','ff8-progress','ff7-progress']:
 s=s.replace("'"+key+"'","'xi:game:feather-fury:"+key+"'")
# Keep original older saves; new game writes only its own versioned key.
helper=old[old.index('function xiPrivateOptions('):old.index('function settings(){')]
assert '040804' in helper
patch('function settings(){',helper+'function settings(){')
patch('<button id="importSave">Nhập sao lưu</button>','<button id="importSave">Nhập sao lưu</button><button id="xi-private-open">?</button>')
private=old[old.index(";$('xi-private-open').onclick="):old.index("},'forest')}",old.index(";$('xi-private-open').onclick="))+len("},'forest')")]
patch("$('importSave').onclick=()=>$('import').click()}","$('importSave').onclick=()=>$('import').click()"+private+"}")
ret=old[old.index(",['Về sảnh Xi',"):old.index("]]",old.index(",['Về sảnh Xi',"))+1]
patch("['Màn mới nhất',()=>start(sv.open)]]","['Màn mới nhất',()=>start(sv.open)]"+ret+"]")
target.write_text(s)
p=root/'integration/games.json';d=json.loads(p.read_text());g=next(g for g in d['games'] if g['id']=='feather-fury');g.update(version='12.2',subtitle='Sky Odyssey',description='100 màn, 200 chặng, 12 chim, đội hình 8 chim và năm phép thuật.');g['save']['keys'][:0]=['xi:game:feather-fury:ff12.2-progress','xi:game:feather-fury:ff12.1-progress'];d['hubVersion']='1.19.0';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
# Explicit additive save migration; preserve all old keys and compiler enforcement.
p=root/'integration/release-baseline.json';baseline=json.loads(p.read_text());b=next(x for x in baseline if x['id']=='feather-fury');assert b['save']['namespace']==g['save']['namespace'] and set(b['save']['keys'])<set(g['save']['keys']);b['save']['keys']=g['save']['keys'];p.write_text(json.dumps(baseline,ensure_ascii=False,indent=2)+'\n')
subprocess.run(['node','tools/catalog.mjs','--write'],cwd=root,check=True)
for file in ['browser.py','imported-ui.py','personalization-ui.py']:
 p=root/'tests'/file;p.write_text(p.read_text().replace('xi:game:feather-fury:ff10-progress','xi:game:feather-fury:ff12.2-progress'))
kit=site/'xi-offline-kit.zip'
with zipfile.ZipFile(kit) as z:readme=z.read('README.txt')
with zipfile.ZipFile(kit,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(site.rglob('*')):
  if not f.is_file() or f==kit:continue
  name='site/'+f.relative_to(site).as_posix()
  if f.name=='sw.js':z.writestr(name,f.read_text().replace(",'xi-offline-kit.zip'",''))
  else:z.write(f,name)
 z.writestr('README.txt',readme)
assert all(hashlib.sha256(f.read_bytes()).hexdigest()==h for f,h in protected.items())
print('Protected files unchanged:',len(protected));print('Source SHA256:',hashlib.sha256(source.read_bytes()).hexdigest());print('Integrated SHA256:',hashlib.sha256(target.read_bytes()).hexdigest())
with zipfile.ZipFile(root.parent/'candidate.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(root.rglob('*')):
  if f.is_file() and ('site' in f.relative_to(root).parts or f.suffix not in ('.pyc','.png')):z.write(f,f.relative_to(root))
