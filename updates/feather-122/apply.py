from pathlib import Path
import json,hashlib,subprocess,sys,zipfile,re
root=Path(sys.argv[1]);source=Path(sys.argv[2]);site=root/'site';target=site/'games/feather-fury/index.html';old=target.read_text();s=source.read_text();assert hashlib.sha256(source.read_bytes()).hexdigest()=='def37b93bf2a0938fa9b5c02a8c849e30184838719a6ec5541459cc760f03eed';protected={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in site.rglob('*') if p.is_file() and (p.relative_to(site).parts[0] in ('games','assets') or p.name=='manifest.webmanifest') and p not in set((site/'games').glob('*/index.html'))}
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
patch("function menu(){show('SKY ISLANDS'","function menu(){show('SKY ODYSSEY'")
# Apply the same touch policy to game entry pages only. Menus remain scrollable.
# Safari may ignore viewport scaling hints; cancel its proprietary gestures and
# multi-contact defaults, while leaving single-finger clicks/scrolling untouched.
guard='''<style id="xi-game-touch-policy">html,body{overscroll-behavior:none;-webkit-text-size-adjust:100%;text-size-adjust:100%}html *{touch-action:pan-x pan-y!important}html canvas,html #brandIntro{touch-action:none!important}</style><script id="xi-game-gesture-policy">(()=>{const cancel=e=>{if(e.cancelable)e.preventDefault()};for(const name of ['gesturestart','gesturechange','gestureend'])document.addEventListener(name,cancel,{capture:true,passive:false});for(const name of ['touchstart','touchmove'])document.addEventListener(name,e=>{if(e.touches.length>1)cancel(e)},{capture:true,passive:false})})();</script>'''
# Narrow/mobile landscape fixes, preserving the canvas aspect ratio and existing art.
feather_css='''<style id="xi-feather-layout">body{padding:env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left)}#game{min-width:0;min-height:calc(100dvh - env(safe-area-inset-top,0px) - env(safe-area-inset-bottom,0px))}.top,.wallet,.brand,.hud>div,.tabs,.bottom,.panel,.stage-dock{min-width:0}.wallet{flex-wrap:wrap;justify-content:flex-end}.hud>div{overflow-wrap:anywhere}.tabs{flex-wrap:wrap}.bottom{flex-wrap:wrap}.info{min-width:0;overflow-wrap:anywhere}.panel{max-height:calc(100dvh - 24px - env(safe-area-inset-top,0px) - env(safe-area-inset-bottom,0px));overflow:auto;overscroll-behavior:contain;overflow-wrap:anywhere}.overlay{padding:max(12px,env(safe-area-inset-top)) max(12px,env(safe-area-inset-right)) max(12px,env(safe-area-inset-bottom)) max(12px,env(safe-area-inset-left))}.panel .menu,.panel .grid,.panel .map{grid-template-columns:repeat(2,minmax(0,1fr))}.panel .grid{grid-template-columns:repeat(4,minmax(0,1fr))}.panel .map{grid-template-columns:repeat(5,minmax(0,1fr))}.panel button{min-width:0;overflow-wrap:anywhere}.panel .stage-dock{flex-wrap:wrap}.panel .stage-dock .buy{white-space:normal}.panel .bird-art{max-width:100%}.panel .mini{min-height:44px}.wallet button,.hud button,.tabs button{min-height:44px;min-width:44px}.arena canvas{height:auto;aspect-ratio:16/10}.deck{min-width:0}.card{min-width:0}@media(max-width:340px){.top{flex-wrap:wrap}.wallet{flex:1 1 100%;justify-content:flex-end}.hud{gap:3px;left:4px;right:4px}.hud>div{padding:3px 4px}.hud small{font-size:8px}.hud strong{font-size:13px}.panel .grid{grid-template-columns:repeat(3,minmax(0,1fr))}.panel .menu{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(orientation:landscape) and (max-height:600px){#game{min-height:0;grid-template-columns:minmax(0,1fr) minmax(150px,210px)}.arena canvas{width:min(100%,calc(max(100px,100dvh - 76px - env(safe-area-inset-top,0px) - env(safe-area-inset-bottom,0px))*1.6))}.deck{max-height:max(80px,calc(100dvh - 174px - env(safe-area-inset-top,0px) - env(safe-area-inset-bottom,0px)))}.top{grid-column:1/-1}.panel{max-height:calc(100dvh - 24px - env(safe-area-inset-top,0px) - env(safe-area-inset-bottom,0px))}}@media(orientation:landscape) and (max-width:540px){#game{display:block}.arena canvas{width:100%}.deck{display:flex;max-height:none;overflow-x:auto}.footer{display:block}}</style>'''
def lock_touch(text,extra=''):
 pattern=r'<meta name="viewport" content="[^"]+">'
 assert len(re.findall(pattern,text))==1
 return re.sub(pattern,lambda _: '<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">'+guard+extra,text,count=1)
legacy=site/'games/legacy/index.html';old_legacy=hashlib.sha256(legacy.read_bytes()).hexdigest();assert old_legacy=='57c9451e4ee811db95135ca6069dfd42ea0469ef43120ff2bcec57a0fffbe8bd'
for f in sorted((site/'games').glob('*/index.html')):
 text=s if f==target else f.read_text();f.write_text(lock_touch(text.replace('</head>',feather_css+Path(__file__).with_name('safe-area.html').read_text()+'</head>',1) if f==target else text))
new_legacy=hashlib.sha256(legacy.read_bytes()).hexdigest()
# Pin the exact approved adapter delta without weakening the original engine audit.
preflight=root/'tests/release-preflight.py';old_preflight=preflight.read_text();assert old_preflight.count(old_legacy)==1;preflight.write_text(old_preflight.replace(old_legacy,new_legacy))
p=root/'integration/games.json';d=json.loads(p.read_text());g=next(g for g in d['games'] if g['id']=='feather-fury');g.update(version='12.2',subtitle='Sky Odyssey',description='100 màn, 200 chặng, 12 chim, đội hình 8 chim và năm phép thuật.');g['save']['keys'][:0]=['xi:game:feather-fury:ff12.2-progress','xi:game:feather-fury:ff12.1-progress'];d['hubVersion']='1.19.0';versions={'legacy':'9.2','cubiq':'1.2','block-nova':'1.2'};
for item in d['games']:
 if item['id'] in versions:item['version']=versions[item['id']]
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
# Worker tests simulate a future Legacy update, which must now be newer than 9.2.
for name in ('worker.test.js','integration.test.js'):
 f=root/'tests'/name;f.write_text(f.read_text().replace('9.2','9.3'))
# Explicit additive save migration; preserve all old keys and compiler enforcement.
p=root/'integration/release-baseline.json';baseline=json.loads(p.read_text());b=next(x for x in baseline if x['id']=='feather-fury');assert b['save']['namespace']==g['save']['namespace'] and set(b['save']['keys'])<set(g['save']['keys']);b['save']['keys']=g['save']['keys'];p.write_text(json.dumps(baseline,ensure_ascii=False,indent=2)+'\n')
subprocess.run(['node','tools/catalog.mjs','--write'],cwd=root,check=True)
# Expose installed vs available version truthfully during a staged module update.
hub=site/'hub.js';text=hub.read_text();a='`V${g.version} · ${d?.updateAvailable?';b='`V${d?.installedVersion||g.version} · ${d?.updateAvailable?';assert text.count(a)==1;text=text.replace(a,b);a="$('gameDetailStatus').textContent='V'+g.version+' · '+(d?.updateAvailable?'Có bản cập nhật'";b="$('gameDetailStatus').textContent='V'+(d?.installedVersion||g.version)+' · '+(d?.updateAvailable?'Có bản V'+g.version";assert text.count(a)==1;text=text.replace(a,b);hub.write_text(text);subprocess.run(['node','--check','site/hub.js'],cwd=root,check=True)

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
