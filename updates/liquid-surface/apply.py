from pathlib import Path
import sys,json,subprocess,zipfile,hashlib
root=Path(sys.argv[1]);site=root/'site'
def patch(name,old,new):
 p=root/name;s=p.read_text();assert s.count(old)==1,(name,old,s.count(old));p.write_text(s.replace(old,new))
def hashes():return {str(p.relative_to(site)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (site/'games').rglob('*') if p.is_file()}
before=hashes();manifest=(site/'manifest.webmanifest').read_bytes()
patch('site/index.html','<article class="panel"><h3>Trải nghiệm</h3>','''<article class="panel"><h3>Trải nghiệm</h3><label class="switch-row glass-control"><span><strong>Hiệu ứng kính</strong><small>Ánh sáng mềm, nút bóng nước và thanh điều hướng chuyển động.</small></span><input id="glassEnabled" type="checkbox" checked></label><p id="glassStatus" class="small-note" role="status"></p>''')
patch('site/hub.js',"view=v;for(const id of ['discover','library','activity','settings'])","view=v;document.documentElement.dataset.tab=v;for(const id of ['discover','library','activity','settings'])")
patch('site/hub.js',';applyAppearance();startIntro();',''';applyAppearance();
const GLASS='xi:ui:glass-v1',glassControl=$('glassEnabled');let glass=readPref('localStorage',GLASS)!=='0';
function applyGlass(){docRoot.dataset.glass=glass?'on':'off';glassControl.checked=glass}
glassControl.addEventListener('change',()=>{const previous=glass;try{localStorage.setItem(GLASS,glassControl.checked?'1':'0');glass=glassControl.checked;$('glassStatus').textContent='Đã lưu hiệu ứng giao diện.'}catch{glass=previous;$('glassStatus').textContent='Không thể lưu hiệu ứng trên thiết bị.'}applyGlass()});
docRoot.dataset.tab=view;applyGlass();startIntro();''')
p=site/'hub.css';p.write_text(p.read_text()+'''
/* F1.11: Xi Liquid Surface. CSS-only lighting; one blur layer, no canvas or pointer loops. */
:root{--glass-curve:cubic-bezier(.22,.75,.22,1);--glass-duration:310ms;--glass-index:0}
:root[data-tab=library]{--glass-index:1}:root[data-tab=activity]{--glass-index:2}:root[data-tab=settings]{--glass-index:3}
html[data-glass=on] .shell nav{--glass-gap:5px;--glass-pad:7px;--glass-segment:calc((100% - 2 * var(--glass-pad) - 3 * var(--glass-gap))/4);position:relative;isolation:isolate;box-sizing:border-box;display:flex;gap:var(--glass-gap);padding:var(--glass-pad);border-radius:24px;border:1px solid var(--line);background:var(--nav-bg);box-shadow:0 8px 26px #0003,inset 0 1px 0 #fff2}
html[data-glass=on] .shell nav::before{content:'';position:absolute;inset-block:var(--glass-pad);left:var(--glass-pad);width:var(--glass-segment);border-radius:18px;background:var(--surface-raised);border:1px solid var(--line);box-shadow:inset 0 1px 1px #fff2,0 3px 8px #0002;transform:translateX(calc(var(--glass-index) * (100% + var(--glass-gap))));transition:transform var(--glass-duration) var(--glass-curve);pointer-events:none;z-index:0}
html[data-glass=on] .shell nav button{position:relative;z-index:1;flex:1 1 0;min-width:0;border-color:transparent;background:transparent;box-shadow:none;border-radius:18px;transition:color 160ms ease,transform 160ms var(--glass-curve)}
html[data-glass=on] .shell nav button[aria-current]{color:var(--gold);background:transparent;border-color:transparent}
html[data-glass=on] .shell nav button:active:not(:disabled){transform:scale(.96)}
html[data-glass=on] .shell :is(button.primary,button.secondary,.file-button){border-radius:15px;box-shadow:inset 0 1px 1px #fff3,0 3px 9px #0002;transition:transform 150ms var(--glass-curve),box-shadow 180ms ease,filter 180ms ease,border-color 180ms ease}
html[data-glass=on] .shell button.primary{background:linear-gradient(180deg,#fff4 0%,#fff0 52%,#0001 100%),var(--gold);color:var(--accent-ink);border-color:var(--gold);font-weight:750}
html[data-glass=on] .shell button.secondary,html[data-glass=on] .shell .file-button{background:linear-gradient(180deg,#fff1,transparent 58%),var(--surface-raised);border-color:var(--line);color:var(--ink)}
html[data-glass=on] .shell :is(button.primary,button.secondary):active:not(:disabled){transform:scale(.965);box-shadow:inset 0 2px 5px #0002,0 1px 2px #0002;filter:brightness(.97)}
html[data-glass=on] .shell :is(.collection-chip,[data-library-filter]){border-radius:999px;box-shadow:inset 0 1px 0 #fff2;transition:background-color 170ms ease,color 170ms ease,transform 150ms var(--glass-curve)}
html[data-glass=on] .shell :is(.panel,.game-row,.activity-stat,.settings-profile){box-shadow:inset 0 1px 0 #fff1,0 5px 18px #0002}
html[data-glass=on] .shell .switch-row input[type=checkbox]{appearance:none;-webkit-appearance:none;width:46px;height:28px;border-radius:30px;position:relative;background:var(--surface-raised);border:1px solid var(--line);margin:0;cursor:pointer;transition:background 180ms ease;box-shadow:inset 0 2px 4px #0002}
html[data-glass=on] .shell .switch-row input[type=checkbox]::after{content:'';position:absolute;left:3px;top:3px;width:20px;height:20px;border-radius:50%;background:linear-gradient(145deg,#fff,#dedbd5);box-shadow:0 2px 5px #0004;transition:transform 220ms var(--glass-curve)}
html[data-glass=on] .shell .switch-row input[type=checkbox]:checked{background:var(--gold);border-color:var(--gold)}
html[data-glass=on] .shell .switch-row input[type=checkbox]:checked::after{transform:translateX(18px)}
.glass-control{margin-bottom:12px}.glass-control+.small-note{margin:0;min-height:0}
@supports (background:color-mix(in srgb,white,black)){html[data-glass=on] .shell nav{background:color-mix(in srgb,var(--nav-bg) 87%,transparent)}html[data-glass=on] .shell nav::before{background:linear-gradient(145deg,color-mix(in srgb,var(--gold) 24%,var(--surface-raised)),color-mix(in srgb,var(--gold) 7%,var(--surface)));border-color:color-mix(in srgb,var(--gold) 35%,var(--line))}}
@supports ((backdrop-filter:blur(12px)) or (-webkit-backdrop-filter:blur(12px))){html[data-glass=on] .shell nav{-webkit-backdrop-filter:blur(12px) saturate(125%);backdrop-filter:blur(12px) saturate(125%)}}
@media(hover:hover) and (pointer:fine){html[data-glass=on] .shell :is(button.primary,button.secondary):hover:not(:disabled){filter:brightness(1.07);box-shadow:inset 0 1px 1px #fff4,0 5px 12px #0003}html[data-glass=on] .shell nav button:hover:not(:disabled){background:#ffffff0b}}
@media(max-width:600px) and (orientation:portrait){html[data-glass=on] .shell{padding-bottom:calc(104px + var(--safe-bottom))}html[data-glass=on] .shell nav{position:fixed;left:max(10px,env(safe-area-inset-left,0px));right:max(10px,env(safe-area-inset-right,0px));bottom:calc(8px + var(--safe-bottom));margin:0;max-width:none;--glass-pad:6px;border-radius:24px}html[data-glass=on] .shell nav button{min-height:54px;padding:5px 2px;font-size:10px;gap:3px}}
@media(prefers-reduced-motion:reduce){html[data-glass=on] .shell nav::before,html[data-glass=on] .shell button,html[data-glass=on] .shell .switch-row input::after{transition:none!important;animation:none!important}html[data-glass=on] .shell button:active:not(:disabled){transform:none}}
''')
p=root/'integration/games.json';d=json.loads(p.read_text());d['hubVersion']='1.11.0';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');subprocess.run(['node','tools/catalog.mjs','--write'],cwd=root,check=True)
assert before==hashes();assert manifest==(site/'manifest.webmanifest').read_bytes()
patch('tests/ui.py',' b.close()', ''' # Liquid Surface: persisted preference, active indicator and reduced-motion behavior.
 page=b.new_page(viewport={'width':390,'height':844},reduced_motion='reduce');page.set_content(html.replace('<script>let ready=true;', '<script>const glassStore={};Object.defineProperty(window,"localStorage",{value:{getItem(k){return glassStore[k]??null},setItem(k,v){glassStore[k]=String(v)},removeItem(k){delete glassStore[k]}}});let ready=true;'))
 assert page.locator('html').get_attribute('data-glass')=='on';assert page.locator('nav').evaluate("e=>getComputedStyle(e).position")=='fixed';assert page.locator('nav').evaluate("e=>getComputedStyle(e,'::before').transitionDuration")=='0s'
 page.get_by_role('button',name='Thư viện',exact=True).click();assert page.locator('html').get_attribute('data-tab')=='library';assert page.locator('nav').evaluate("e=>getComputedStyle(e,'::before').transform")!='matrix(1, 0, 0, 1, 0, 0)'
 page.get_by_role('button',name='Cài đặt',exact=True).click();page.locator('#glassEnabled').uncheck();assert page.locator('html').get_attribute('data-glass')=='off';assert page.evaluate("localStorage.getItem('xi:ui:glass-v1')")=='0';page.locator('#glassEnabled').check();assert page.locator('html').get_attribute('data-glass')=='on';assert page.evaluate("localStorage.getItem('xi:ui:glass-v1')")=='1'
 page.screenshot(path=str(root.parent/'glass-settings.png'),full_page=True);page.get_by_role('button',name='Khám phá',exact=True).click();page.screenshot(path=str(root.parent/'glass-hub.png'),full_page=True);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.close();print('PASS glass controls, nav indicator and reduced motion')
 b.close()''')
# Mock Cache API: serialize response bytes once instead of repeatedly teeing Node's Response streams.
patch('tests/worker.test.js',"function harness(", "const snapshots=new WeakMap();async function copyResponse(r){if(!r)return undefined;if(!snapshots.has(r))snapshots.set(r,r.arrayBuffer().then(bytes=>({bytes,status:r.status,statusText:r.statusText,headers:[...r.headers]})));const v=await snapshots.get(r);return new Response(v.bytes.slice(0),{status:v.status,statusText:v.statusText,headers:v.headers})}function harness(")
patch('tests/worker.test.js','return m.get(key(r))?.clone()','return copyResponse(m.get(key(r)))')
patch('tests/worker.test.js','m.set(key(r),v.clone())','m.set(key(r),await copyResponse(v))')
with zipfile.ZipFile(root.parent/'candidate.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(root.rglob('*')):
  if f.is_file() and ('site' in f.relative_to(root).parts or f.suffix not in ('.pyc','.png')):z.write(f,f.relative_to(root))
print('Xi F1.11 shell only; all game files and manifest verified')
