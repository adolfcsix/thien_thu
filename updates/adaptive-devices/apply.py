from pathlib import Path
import hashlib,json,subprocess,sys,zipfile
root=Path(sys.argv[1]);site=root/'site'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protected={p:sha(p) for p in [site/'manifest.webmanifest',*filter(Path.is_file,(site/'games').rglob('*')),*filter(Path.is_file,(site/'assets').rglob('*'))]}
def patch(path,old,new):
 p=root/path;s=p.read_text();assert s.count(old)==1,(path,old);p.write_text(s.replace(old,new))
patch('site/index.html','<p id="glassStatus" class="small-note" role="status"></p>','''<p id="glassStatus" class="small-note" role="status"></p><div class="surface-tuning"><label for="glassOpacity">Độ trong của kính <output id="glassValue">13%</output></label><input id="glassOpacity" type="range" min="0" max="22" step="1" value="13"><label for="wallStrength">Mức hiện ảnh nền <output id="wallValue">18%</output></label><input id="wallStrength" type="range" min="0" max="24" step="1" value="18"><button class="secondary" id="surfaceReset">Khôi phục hiệu ứng</button><p class="small-note" id="surfaceStatus" role="status"></p></div>''')
patch('site/hub.js','docRoot.dataset.tab=view;applyGlass();startIntro();','''const SURFACE_PREF='xi:ui:surface-v1';let surface={glass:13,wall:18};
function bounded(v,max,def){return typeof v==='number'&&Number.isFinite(v)?Math.max(0,Math.min(max,Math.round(v))):def}
try{const p=JSON.parse(readPref('localStorage',SURFACE_PREF)||'null');if(p)surface={glass:bounded(p.glass,22,13),wall:bounded(p.wall,24,18)}}catch{}
function applySurface(){docRoot.style.setProperty('--xi-glass-solid',(100-surface.glass)+'%');docRoot.style.setProperty('--xi-wall-solid',(100-surface.wall)+'%');$('glassOpacity').value=surface.glass;$('wallStrength').value=surface.wall;$('glassValue').textContent=surface.glass+'%';$('wallValue').textContent=surface.wall+'%'}
function saveSurface(next){try{localStorage.setItem(SURFACE_PREF,JSON.stringify(next));surface=next;$('surfaceStatus').textContent='Đã lưu hiệu ứng.'}catch{$('surfaceStatus').textContent='Không thể lưu trên thiết bị.'}applySurface()}
for(const [id,key,max] of [['glassOpacity','glass',22],['wallStrength','wall',24]]){$(id).oninput=()=>{const n=bounded(Number($(id).value),max,surface[key]);docRoot.style.setProperty(key==='glass'?'--xi-glass-solid':'--xi-wall-solid',(100-n)+'%');$(key==='glass'?'glassValue':'wallValue').textContent=n+'%'};$(id).onchange=()=>saveSurface({...surface,[key]:bounded(Number($(id).value),max,surface[key])})}
$('surfaceReset').onclick=()=>saveSurface({glass:13,wall:18});applySurface();docRoot.dataset.tab=view;applyGlass();startIntro();''')
p=site/'hub.css';p.write_text(p.read_text()+'''
/* F1.13: adaptive device shell, live rotation and bounded surface tuning. */
:root{--xi-glass-solid:87%;--xi-wall-solid:82%}
.surface-tuning{display:grid;gap:8px;padding-block:12px;border-top:1px solid var(--line);margin-block:12px;min-inline-size:0}.surface-tuning label{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;color:var(--ink);font-size:13px;font-weight:650}.surface-tuning output{color:var(--gold);font-variant-numeric:tabular-nums}.surface-tuning input[type=range]{width:100%;min-height:44px;margin:0;accent-color:var(--gold)}.surface-tuning button{justify-self:start}.surface-tuning p{margin:0}
@supports (background:color-mix(in srgb,white,black)){html[data-glass=on] .shell nav{background:color-mix(in srgb,var(--nav-bg) var(--xi-glass-solid),transparent)}html[data-wallpaper=true] body::before{background-image:linear-gradient(color-mix(in srgb,var(--bg) var(--xi-wall-solid),transparent),color-mix(in srgb,var(--bg) var(--xi-wall-solid),transparent)),var(--wallpaper)}}
/* Use both dimensions: a short landscape phone is not a desktop. */
@media (min-width:700px) and (orientation:landscape){
 .shell,html[data-glass=on] .shell{display:grid;grid-template-columns:clamp(120px,16vw,190px) minmax(0,1fr);column-gap:clamp(12px,2vw,26px);padding-inline-start:max(clamp(14px,2.5vw,34px),env(safe-area-inset-left,0px));padding-inline-end:max(clamp(14px,2.5vw,34px),env(safe-area-inset-right,0px));padding-bottom:max(16px,env(safe-area-inset-bottom,0px));align-items:start}
 .shell .masthead,.shell #updateNotice{grid-column:1/-1}.shell .content{grid-column:2;grid-row:3;min-width:0}.shell nav,html[data-glass=on] .shell nav{grid-column:1;grid-row:3;position:sticky;top:max(10px,env(safe-area-inset-top,0px));align-self:start;flex-direction:column;max-width:none;width:100%;margin:0;gap:5px;padding:7px;border-radius:20px;--glass-gap:5px;--glass-pad:7px;--glass-segment:52px}
 .shell nav button,html[data-glass=on] .shell nav button{flex:0 0 52px;min-height:52px;justify-content:flex-start;padding:6px 8px;font-size:12px;gap:7px;text-align:left}.shell nav button span{text-align:left}.shell nav svg{width:19px;height:19px}
 html[data-glass=on] .shell nav::before{inset:auto;top:var(--glass-pad);left:var(--glass-pad);width:calc(100% - 2 * var(--glass-pad));height:var(--glass-segment);transform:translateY(calc(var(--glass-index) * (100% + var(--glass-gap))))}
 .shell .section-heading h2{font-size:clamp(30px,4vw,48px)}.shell .theme-choices{grid-template-columns:repeat(3,minmax(0,1fr))}.shell .spotlight{min-height:clamp(180px,29vw,340px)}
 html[data-compact=false] .featured{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}html[data-compact=false] .featured .detail{padding:16px}.shell .recent-games{grid-auto-columns:minmax(135px,32%)}
}
@media(min-width:1050px){.shell{max-width:1440px}.shell #libraryGames{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.shell #libraryGames .game-row{margin:0}.shell .theme-choices{grid-template-columns:repeat(6,minmax(0,1fr))}.shell .recent-games{grid-auto-columns:minmax(145px,24%)}}
@media(min-width:700px) and (orientation:landscape) and (max-height:340px){.shell nav,html[data-glass=on] .shell nav{position:relative;top:auto}.shell nav button,html[data-glass=on] .shell nav button{flex-basis:44px;min-height:44px}.shell nav,html[data-glass=on] .shell nav{--glass-segment:44px}}
@media(min-width:601px) and (orientation:portrait){.shell nav,html[data-glass=on] .shell nav{max-width:none}.shell .theme-choices{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(prefers-reduced-motion:no-preference){html[data-glass=on] .shell .content>section:not([hidden]){animation:xi-enter 150ms ease-out}@keyframes xi-enter{from{opacity:.84;transform:translateY(3px)}to{opacity:1;transform:none}}}
''')
p=root/'integration/games.json';d=json.loads(p.read_text());d['hubVersion']='1.13.0';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
subprocess.run(['node','tools/catalog.mjs','--write'],cwd=root,check=True)
assert all(sha(p)==h for p,h in protected.items())
p=root/'tests/layout.py';s=p.read_text();s=s.replace(' b.close()',''' # Exercise actual viewport changes in a single page, without resetting preferences.
 page=b.new_page(viewport={'width':390,'height':844},reduced_motion='reduce');errs=[];page.on('pageerror',lambda e:errs.append(str(e)));page.set_content(html.replace('<script>let ready=true;', '<script>const layoutStore={};Object.defineProperty(window,"localStorage",{value:{getItem(k){return layoutStore[k]??null},setItem(k,v){layoutStore[k]=String(v)},removeItem(k){delete layoutStore[k]}}});let ready=true;'))
 page.get_by_role('button',name='Cài đặt',exact=True).click();page.locator('#glassOpacity').fill('20');page.locator('#glassOpacity').dispatch_event('change');page.locator('#wallStrength').fill('12');page.locator('#wallStrength').dispatch_event('change');assert page.locator('#glassValue').inner_text()=='20%';assert page.locator('#wallValue').inner_text()=='12%'
 assert page.evaluate("JSON.parse(localStorage.getItem('xi:ui:surface-v1'))")=={'glass':20,'wall':12}
 for w,h in [(844,390),(1024,768),(768,1024),(390,844),(932,430),(430,932),(1366,768),(1920,1080)]:
  page.set_viewport_size({'width':w,'height':h})
  for name in ['Khám phá','Thư viện','Hoạt động','Cài đặt']:
   page.get_by_role('button',name=name,exact=True).click();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(w,h,name)
   assert page.locator('nav button[aria-current=page]').inner_text()==name
   assert page.locator('#glassValue').inner_text()=='20%'
   if w>=700 and w>h:
    nav=page.locator('nav').bounding_box();body=page.locator('.content').bounding_box();assert nav['x']+nav['width']<=body['x']+1,(w,h,nav,body)
   elif w<=600 and h>w:assert page.locator('nav').evaluate('e=>getComputedStyle(e).position')=='fixed'
  print(f'PASS live rotation / resize {w}x{h}: all four tabs',flush=True)
 page.locator('#surfaceReset').click();assert page.locator('#glassValue').inner_text()=='13%';assert page.locator('#wallValue').inner_text()=='18%';assert not errs,errs;page.close()
 b.close()''');p.write_text(s)
with zipfile.ZipFile(root.parent/'candidate.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(root.rglob('*')):
  if p.is_file() and ('site' in p.relative_to(root).parts or p.suffix not in ('.pyc','.png')):z.write(p,p.relative_to(root))
