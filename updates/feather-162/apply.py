"""F1.26: reconstruct exact user-supplied 16.2 and adapt only Xi integration."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,zipfile,base64,gzip
root=Path(sys.argv[1]).resolve();site=root/'site';target=site/'games/feather-fury/index.html'
src=Path(__file__).resolve().parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
old_raw=target.read_bytes()
assert sha(old_raw)=='083f61d8f7121e7bfb57064bb4363699c1cc9b5d8bd1ae7f3a518b4288e2b63a'
parts=sorted((src/'source').glob('*.b64'))
assert len(parts)==13 and [p.name for p in parts]==[f'{i:02d}.b64' for i in range(13)]
encoded=b''.join(p.read_bytes() for p in parts)
assert len(encoded)==6087976 and sha(encoded)=='8d4bd87e9d237c9c12c6595c79641b75755190b2feb4f7d39c3d550e3cb12671'
delta=gzip.decompress(base64.b64decode(encoded,validate=True))
assert sha(delta)=='b3ea243cbde6121e669df5752c61b3312a46a40a66420b3ce19fcc260709e02a'
pattern=rb'data:image/[^;,]+;base64,[A-Za-z0-9+/=]+'
assets={sha(x).encode():x for x in re.findall(pattern,old_raw)}
raw=re.sub(rb'@@XI_ASSET:([0-9a-f]{64})@@',lambda m:assets[m[1]],delta)
assert len(raw)==21894085 and sha(raw)=='a5cc92a07aced1ef5c28c775d0c1683e4fa91533d4bf27d54feaa33e5cabd764'
s=raw.decode('utf-8');old=old_raw.decode('utf-8');ns='xi:game:feather-fury:'
protected={p:sha(p.read_bytes()) for p in (site/'games').rglob('*') if p.is_file() and p!=target}
def replace(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
replace("KEY='ff12.2-progress'", "KEY='"+ns+"ff16.2-progress'")
replace("[KEY,BACKUP_KEY,'ff12.1-progress'", "[KEY,BACKUP_KEY,'"+ns+"ff14.1-progress','"+ns+"ff14.1-progress-backup','"+ns+"ff12.2-progress','"+ns+"ff12.2-progress-backup','ff12.1-progress'")
for k in ['ff12.1-progress','ff10-progress','ff9-progress','ff8-progress','ff7-progress']:s=s.replace("'"+k+"'","'"+ns+k+"'")
replace('width=device-width,initial-scale=1,viewport-fit=cover','width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover')
replace('</head>','<script id="xi-gesture-162">for(const type of ["gesturestart","gesturechange","gestureend"])document.addEventListener(type,e=>e.preventDefault(),{passive:false});document.addEventListener("touchmove",e=>{if(e.touches.length>1)e.preventDefault()},{passive:false});</script></head>')
private=old[old.index('function xiPrivateOptions('):old.index('function settings()',old.index('function xiPrivateOptions('))]
replace('function settings(){',private+'function settings(){')
replace('<button id="importSave">Nhập sao lưu</button>','<button id="importSave">Nhập sao lưu</button><button id="xi-private-open" aria-label="Tùy chỉnh riêng">?</button>')
callback=old[old.index(";$(\'xi-private-open\').onclick="):old.index("}\n$('import').onchange",old.index(";$(\'xi-private-open\').onclick="))]
replace("$('importSave').onclick=()=>$('import').click()}","$('importSave').onclick=()=>$('import').click()"+callback+'}')
ret=old[old.index(",['Về sảnh Xi',"):old.index(']]',old.index(",['Về sảnh Xi',"))+1]
ret=ret.replace('persist();if(!storage)', 'if(!persist())')
replace("['Màn mới nhất',()=>start(sv.open)]]","['Màn mới nhất',()=>start(sv.open)]"+ret+"]")
assert re.findall(pattern,s.encode())==re.findall(pattern,raw)
# Seed a verified recovery copy even when the migrated save has not changed.
replace(" if(previous&&previous!==next){try{normalize(JSON.parse(previous));localStorage.setItem(BACKUP_KEY,previous)}catch(e){/* Current save remains authoritative. */}}"," // Seed a verified backup on first save or repair a missing/invalid backup.\n // Never replace a valid backup with an invalid previous primary.\n let fallback=null;\n if(previous&&previous!==next){try{normalize(JSON.parse(previous));fallback=previous}catch(e){}}\n if(fallback===null&&backup){try{normalize(JSON.parse(backup));fallback=backup}catch(e){}}\n if(fallback===null){normalize(JSON.parse(next));fallback=next}\n if(fallback!==backup){try{localStorage.setItem(BACKUP_KEY,fallback)}catch(e){storage=false;pendingSave=true}}")
assert sha(s.encode())=='87a1835924a5c66d01f3b5ff6ab41a15aa41c7d8b01786670dcd413133802101'
target.write_text(s,encoding='utf-8')
for i,code in enumerate(re.findall(r'<script[^>]*>(.*?)</script>',s,re.S)):
 p=root/f'ff162-syntax-{i}.js'
 try:p.write_text(code,encoding='utf-8');subprocess.run(['node','--check',str(p)],check=True)
 finally:p.unlink(missing_ok=True)
p=root/'integration/games.json';d=json.loads(p.read_text());assert d['hubVersion']=='1.25.0';d['hubVersion']='1.26.0'
g=next(x for x in d['games'] if x['id']=='feather-fury');assert g['version']=='14.1'
g.update(version='16.2',subtitle='Save Integrity & Stability',description='210 màn, 420 chặng, 24 chim, 8 chim ra trận, chiến dịch không gian và thử thách đặc biệt.')
g['save']['keys'][:0]=[ns+'ff16.2-progress',ns+'ff16.2-progress-backup'];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=root/'integration/release-baseline.json';d=json.loads(p.read_text());b=next(x for x in d if x['id']=='feather-fury');assert set(b['save']['keys'])<set(g['save']['keys']);b['save']['keys']=g['save']['keys'];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
subprocess.run(['node','tools/catalog.mjs','--write'],cwd=root,check=True)
subprocess.run([sys.executable,str(src.parent/'shell-stability'/'guard.py'),str(site)],check=True)
kit=site/'xi-offline-kit.zip'
with zipfile.ZipFile(kit) as z:readme=z.read('README.txt')
with zipfile.ZipFile(kit,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(site.rglob('*')):
  if not f.is_file() or f==kit:continue
  name='site/'+f.relative_to(site).as_posix()
  if f.name=='sw.js':z.writestr(name,f.read_text().replace(",'xi-offline-kit.zip'",''))
  else:z.write(f,name)
 z.writestr('README.txt',readme)
assert all(sha(p.read_bytes())==h for p,h in protected.items())
print('PASS 16.2 exact original and adapter SHA-256, all artwork, six unchanged games and offline kit')
