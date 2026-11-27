from pathlib import Path
import hashlib,json,subprocess,sys,zipfile
root=Path(sys.argv[1]);site=root/'site'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protected={p:digest(p) for p in [site/'manifest.webmanifest',*filter(Path.is_file,(site/'games').rglob('*'))]}
p=site/'hub.css';p.write_text(p.read_text()+'''
/* F1.12: intrinsic sizing, bounded controls and accessible safe-area navigation. */
*,*::before,*::after{box-sizing:border-box}
.shell,.content,.content>section,.featured,.detail,.panel,.game-row,.spotlight-body,.library-title,.activity-copy,.settings-profile>div,.switch-row>span,.section-heading>div,.browse-tools,.search-field,.theme-choice,.recent-info{min-inline-size:0;max-inline-size:100%}
.shell :is(h1,h2,h3,p,small,strong,.subtitle,.sub,.status,.lifecycle-note,.eyebrow,.catalog-count,.cover-label,.recent-info,.activity-stat,.settings-profile,.file-button){overflow-wrap:anywhere}
.shell :is(button,.file-button,select,input){max-inline-size:100%;min-inline-size:0}
.shell :is(button,.file-button){white-space:normal;overflow-wrap:anywhere;line-height:1.25}
.shell img{max-inline-size:100%}
.section-rule,.section-heading,.masthead,.browse-tools,.sort-label,footer{flex-wrap:wrap}
.section-rule>*,.section-heading>*,.browse-tools>*,.sort-label>*{min-inline-size:0}
.catalog-count,.connection{white-space:normal}.connection::before,.status::before{flex:none}
.cover-label{max-inline-size:calc(100% - 28px)}html[data-compact=true] .cover-label{max-inline-size:calc(100% - 14px)}
.detail .actions>button,.game-row .actions>button,#settings .actions>button{flex:1 1 auto;min-inline-size:0}
.search-field input{inline-size:100%;min-inline-size:0;font-size:16px}
.storage-panel{grid-template-columns:minmax(0,1fr) minmax(0,auto)}
.library-toolbar,.activity-summary,#libraryGames,#activityGames,#activityRecent{min-inline-size:0}
.activity-row{flex-wrap:wrap}.activity-copy{flex:1 1 120px}.activity-row button{margin-inline-start:auto;max-inline-size:100%}
.theme-choice>*{min-inline-size:0;max-inline-size:100%}.switch-row>span{flex:1 1 0}.switch-row input{flex:none}
.settings-help summary{line-height:1.4;padding-block:12px}.file-pick{max-inline-size:100%}.file-button{display:flex;align-items:center;justify-content:center;text-align:center;min-height:44px}
.shell nav button{flex:1 1 0;min-inline-size:0}.shell nav button span{white-space:normal;overflow-wrap:anywhere;text-align:center;line-height:1.2}.shell nav svg{flex:none}
html[data-glass=on] .shell nav::before{box-sizing:border-box}
@media(max-width:600px) and (orientation:portrait){
 .shell,html[data-glass=on] .shell{padding-bottom:max(calc(104px + var(--safe-bottom)),calc(var(--xi-nav-height,72px) + var(--safe-bottom) + 24px))}
 html{scroll-padding-bottom:max(calc(104px + var(--safe-bottom)),calc(var(--xi-nav-height,72px) + var(--safe-bottom) + 24px))}
 html[data-glass=on] .shell nav button{font-size:clamp(10px,2.8vw,12px)}
}
@media(max-width:340px){.shell{padding-inline:12px}.spotlight-body{max-width:100%;padding:16px}.storage-panel{grid-template-columns:minmax(0,1fr)}.theme-choices{grid-template-columns:repeat(2,minmax(0,1fr))}.activity-stat{padding:10px 6px}.activity-row button{flex:1 1 100%;margin:0}.settings-profile{flex-wrap:wrap}.settings-profile>img{flex:none}.detail .actions{display:grid;grid-template-columns:minmax(0,1fr)}html[data-compact=true] #featured{gap:8px}.game-thumb{width:56px;height:56px}}
@media(max-width:299px){html[data-compact=true] #featured{grid-template-columns:minmax(0,1fr)}.shell nav svg{width:18px;height:18px}.section-heading h2{font-size:30px}}
@media(max-height:450px) and (orientation:landscape){.shell{padding-top:10px}.masthead{padding-bottom:10px}nav{margin-block:8px 18px}.spotlight{min-height:180px}.spotlight-body{padding:16px}.recent-section{margin-block:16px}}
''')
p=site/'hub.js';p.write_text(p.read_text()+'''
// Reserve actual fixed-nav height, including when text wraps or rotation changes.
const layoutNav=document.querySelector('.shell nav');
function reserveNavSpace(){if(layoutNav)document.documentElement.style.setProperty('--xi-nav-height',Math.ceil(layoutNav.getBoundingClientRect().height)+'px')}
if(layoutNav&&typeof ResizeObserver==='function'){const navObserver=new ResizeObserver(reserveNavSpace);navObserver.observe(layoutNav)}
window.addEventListener('resize',reserveNavSpace,{passive:true});reserveNavSpace();
''')
p=root/'integration/games.json';d=json.loads(p.read_text());d['hubVersion']='1.12.0';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
subprocess.run(['node','tools/catalog.mjs','--write'],cwd=root,check=True)
assert all(digest(p)==h for p,h in protected.items()),'Game or app identity changed'
p=root/'tests/layout.py';p.write_text('\n'.join((root/'tests/ui.py').read_text().splitlines()[:14])+'\n'+'''with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None,args=['--no-sandbox','--disable-dev-shm-usage'])
 for w,h in [(280,650),(320,568),(390,844),(568,320),(600,800),(601,800),(750,600),(844,390),(1280,800)]:
  page=b.new_page(viewport={'width':w,'height':h},reduced_motion='reduce');errs=[];page.on('pageerror',lambda e:errs.append(str(e)));page.set_content(html.replace('<script>let ready=true;', '<script>const layoutStore={};Object.defineProperty(window,"localStorage",{value:{getItem(k){return layoutStore[k]??null},setItem(k,v){layoutStore[k]=String(v)},removeItem(k){delete layoutStore[k]}}});let ready=true;'))
  for glass in [True,False]:
   page.get_by_role('button',name='Cài đặt',exact=True).click();page.locator('#glassEnabled').set_checked(glass)
   for compact in [True,False]:
    page.get_by_role('button',name='Cài đặt',exact=True).click();page.locator('#compactCards').set_checked(compact)
    for name in ['Khám phá','Thư viện','Hoạt động','Cài đặt']:
     page.get_by_role('button',name=name,exact=True).click()
     page.evaluate("""()=>{const s=document.querySelector('.content>section:not([hidden])');for(const e of s.querySelectorAll('h3,.subtitle,.activity-stat small')){if(!e.dataset.stress){e.dataset.stress='1';e.textContent+=' · Phiên bản mở rộng dài hơn dự kiến'}}for(const e of s.querySelectorAll('button,.file-button,.switch-row small')){e.style.fontSize='16px'}}""")
     bad=page.evaluate("""()=>({width:document.documentElement.scrollWidth,overflow:[...document.querySelectorAll('.shell button,.panel,.game-row,.activity-stat,.featured,.detail,.settings-profile,.theme-choice,.library-title,.spotlight-body,.sort-label,.section-heading,.section-rule,.switch-row,.search-field,.browse-tools')].filter(e=>e.getClientRects().length&&e.clientWidth&&e.scrollWidth>e.clientWidth+2&&!e.closest('.collections,#libraryFilters,.recent-games')).map(e=>[e.className,e.textContent.slice(0,50),e.clientWidth,e.scrollWidth])})""")
     assert bad['width']<=w and not bad['overflow'],(w,h,glass,compact,name,bad)
     if w<=600 and h>w:
      page.evaluate('window.scrollTo(0,document.documentElement.scrollHeight)');nav=page.locator('nav').bounding_box();foot=page.locator('footer').bounding_box();assert foot['y']+foot['height']<=nav['y']+2,(w,glass,name,foot,nav)
   assert not errs,errs
  page.close();print(f'PASS {w}x{h}: 16 tab/layout/glass combinations; long labels and larger text',flush=True)
 b.close()
''')
with zipfile.ZipFile(root.parent/'candidate.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(root.rglob('*')):
  if p.is_file() and ('site' in p.relative_to(root).parts or p.suffix not in ('.pyc','.png')):z.write(p,p.relative_to(root))
