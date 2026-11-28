"""Add an opt-in Garden sandbox to Xi without touching normal progress."""
from pathlib import Path
import json,re,sys
root=Path(sys.argv[1]);site=root/'site';game=site/'games/garden-through-time/index.html'
NS='xi:game:garden-through-time:'
normal=NS+'garden-time-v1';sandbox=NS+'sandbox-progress-v1';options=NS+'sandbox-options-v1'
flags={'stages':'Mở mọi màn thường và khó','plants':'Mở khóa toàn bộ cây phù hợp địa hình','ranks':'Cấp cây tối đa, Mastery và trang phục','resources':'Xu và mảnh nâng cấp dồi dào','items':'99 vật phẩm mỗi loại trong cửa hàng','battle':'9.999 mặt trời và 3 Plant Food khi vào trận thường/khó'}
def once(text,a,b):
    assert text.count(a)==1,a[:100]
    return text.replace(a,b)
s=game.read_text(encoding='utf-8')
code='''const XI_SANDBOX=typeof location!=='undefined'&&new URLSearchParams(location.search).get('sandbox')==='1';
const XI_PROGRESS_KEY=XI_SANDBOX?%s:%s;
const XI_FLAGS=%s;
const XI_SANDBOX_OPTIONS=Object.fromEntries(XI_FLAGS.map(k=>[k,false]));
if(XI_SANDBOX){let stored=null;try{stored=JSON.parse(localStorage.getItem(%s))}catch{}for(const k of XI_FLAGS)XI_SANDBOX_OPTIONS[k]=stored?.[k]!==false;}
'''%(json.dumps(sandbox),json.dumps(normal),json.dumps(list(flags)),json.dumps(options))
s=once(s,'/* Original offline tower-defense simulation. No imported game assets. */','/* Original offline tower-defense simulation. No imported game assets. */\n'+code)
idx=s.index('function commitBackup(storage,progress)')
assert s[idx:].count("'"+normal+"'")==8,s[idx:].count("'"+normal+"'")
s=s[:idx]+s[idx:].replace("'"+normal+"'",'XI_PROGRESS_KEY')
s=once(s,"const SAVE_FORMAT='garden-through-time', SAVE_LIMIT=256*1024;","const SAVE_FORMAT=XI_SANDBOX?'garden-through-time-sandbox':'garden-through-time', SAVE_LIMIT=256*1024;")
# Bypass level gates only; retain native campaign and terrain restrictions.
a=s.index("this.available=['sun','pea','wall'");b=s.index('this.pool=[...this.available]',a);pool=s[a:b]
pool,n=re.subn(r'level>=([A-Za-z0-9]+)',r'(XI_SANDBOX_OPTIONS.plants||level>=\1)',pool);assert n>=15,n
pool=once(pool,'if(level===0)','if(level===0&&!XI_SANDBOX_OPTIONS.plants)')
pool=once(pool,"this.world.style==='egypt'&&level>0","this.world.style==='egypt'&&(XI_SANDBOX_OPTIONS.plants||level>0)")
s=s[:a]+pool+"if(XI_SANDBOX_OPTIONS.plants)this.available=[...new Set(this.available)];"+s[b:]
s=once(s,'plants:Object.keys(PLANTS).map(id=>entry(plants,id))','plants:Object.keys(PLANTS).map(id=>{const x=entry(plants,id);if(XI_SANDBOX_OPTIONS.plants&&x.first!==null)x.unlocked=true;return x})')
seed='''function xiSandboxGrant(){if(!XI_SANDBOX)return;for(const c of Object.keys(WORLDS)){
 if(XI_SANDBOX_OPTIONS.stages){save[c]=stageMax(c);save.completed[c]=stageMax(c)+1;save.hard[c]=stageMax(c);save.hard.completed[c]=stageMax(c)+1;}
 const w=economy[c];if(XI_SANDBOX_OPTIONS.resources)w.coins=Math.max(w.coins,10000000);
 if(XI_SANDBOX_OPTIONS.ranks||XI_SANDBOX_OPTIONS.resources)for(const id of Object.keys(PLANTS)){const p=w.plants[id]||(w.plants[id]={level:1,packets:0});if(XI_SANDBOX_OPTIONS.ranks){p.level=UPGRADE_RULES[c].max;if(c==='intl'&&masteryEligible(id))p.mastery=MASTERY_MAX;}if(XI_SANDBOX_OPTIONS.resources)p.packets=Math.max(p.packets,10000);}
 if(XI_SANDBOX_OPTIONS.items)for(const id of Object.keys(SHOP_ITEMS))shop[c].items[id]=99;
 }if(!saveBlocked&&!saveConflict)persist();}
'''
s=once(s,'function currentProgress(){return {...save,economy,shop,records};}', 'function currentProgress(){return {...save,economy,shop,records};}\n'+seed)
s=once(s,"g=new Game(campaign,l,Math.random,selected,economy[campaign],difficulty);if(items.length", "g=new Game(campaign,l,Math.random,selected,economy[campaign],difficulty);if(XI_SANDBOX_OPTIONS.battle){g.sun=Math.max(g.sun,9999);g.food=Math.max(g.food,3);}if(items.length")
s=once(s,'<button id="xi-return" type="button">Về sảnh Xi</button>','<span id="xi-sandbox-label" hidden style="padding:7px 10px;border:1px solid #f4d777;border-radius:10px;color:#f4d777;font-size:12px">SANDBOX · Bản lưu riêng</span><button id="xi-return" type="button">Về sảnh Xi</button>')
s=once(s,'}menu();requestAnimationFrame(frame);','}if(XI_SANDBOX){$(\'xi-sandbox-label\').hidden=false;xiSandboxGrant();}menu();requestAnimationFrame(frame);')
s=once(s,'<title>Garden Through Time 0.79.2 — Final Stability RC3</title>','<title>Garden Through Time 0.79.3 — Xi Sandbox</title>')
game.write_text(s,encoding='utf-8')
p=site/'index.html';h=p.read_text(encoding='utf-8');panel='<article class="panel" id="gardenSandbox"><div class="eyebrow">GARDEN THROUGH TIME</div><h3>Chế độ Sandbox</h3><p>Thử toàn bộ nội dung trong bản lưu riêng. Chế độ chơi thường không bị thay đổi.</p>'
for k,label in flags.items():panel+=f'<label class="switch-row"><span><strong>{label}</strong></span><input type="checkbox" data-garden-option="{k}" checked></label>'
panel+='<p class="small-note">Bỏ chọn không thu hồi nội dung đã mở. Đặt lại Sandbox để áp dụng từ đầu. Kỷ lục thử thách vẫn phải chơi để đạt.</p><div class="actions"><button id="gardenSandboxLaunch" class="primary" type="button">Chơi Sandbox</button><button id="gardenSandboxReset" class="secondary" type="button">Đặt lại Sandbox</button></div><p id="gardenSandboxStatus" class="small-note" role="status" aria-live="polite"></p></article>'
h=once(h,'<article class="panel"><h3>Tiến trình &amp; bộ nhớ</h3>',panel+'<article class="panel"><h3>Tiến trình &amp; bộ nhớ</h3>');p.write_text(h,encoding='utf-8')
p=site/'hub.js';h=p.read_text(encoding='utf-8');h=once(h,"function enterGame(g){if(!ensureSaveRecovery()){select('settings');return}recordLaunch(g);location.assign(g.entry)}","function enterGame(g,suffix=''){if(!ensureSaveRecovery()){select('settings');return}recordLaunch(g);location.assign(g.entry+suffix)}")
anchor='for(const [k,v] of entries){const enums='
h=once(h,anchor,'for(const [k,v] of entries){if(k==='+json.dumps(options)+'){let x;try{x=JSON.parse(v)}catch{}const flags='+json.dumps(list(flags))+';if(!x||typeof x!==\'object\'||Array.isArray(x)||Object.keys(x).length!==flags.length||flags.some(f=>typeof x[f]!==\'boolean\'))throw Error(\'Tùy chọn Sandbox không hợp lệ\');continue}const enums=')
h+='''
// Garden Sandbox: explicit entry selects an isolated progress key.
const gardenOptionsKey=%s,gardenSandboxKey=%s;
const gardenControls=[...document.querySelectorAll('[data-garden-option]')];
const gardenStatus=t=>$('gardenSandboxStatus').textContent=t;
try{const p=JSON.parse(localStorage.getItem(gardenOptionsKey));for(const c of gardenControls)c.checked=p?.[c.dataset.gardenOption]!==false}catch{}
function saveGardenOptions(){const value=JSON.stringify(Object.fromEntries(gardenControls.map(c=>[c.dataset.gardenOption,c.checked])));localStorage.setItem(gardenOptionsKey,value);if(localStorage.getItem(gardenOptionsKey)!==value)throw Error('Không lưu được tùy chọn Sandbox.');}
for(const c of gardenControls)c.onchange=()=>{try{saveGardenOptions();gardenStatus('Đã lưu tùy chọn Sandbox.')}catch{gardenStatus('Không lưu được tùy chọn.')}};
$('gardenSandboxLaunch').onclick=async()=>{const button=$('gardenSandboxLaunch'),g=getGame('garden-through-time');if(!g||busy||button.disabled)return;button.disabled=true;try{if(!ensureSaveRecovery())return;saveGardenOptions();await refresh();if(details[g.id]?.installedVersion!==g.version){if(!canDownload()||!workerReady){gardenStatus('Cần cập nhật Garden khi có mạng để chơi Sandbox.');return;}if(!await task(states[g.id]?'UPDATE':details[g.id]?.needsRepair?'REPAIR':'INSTALL',g))throw Error('Chưa tải được phiên bản Sandbox.');}if(details[g.id]?.installedVersion!==g.version)throw Error('Phiên bản Sandbox chưa sẵn sàng.');enterGame(g,'?sandbox=1');}catch(e){gardenStatus(e.message||'Không mở được Sandbox.')}finally{button.disabled=false;}};
$('gardenSandboxReset').onclick=()=>{if(!confirm('Xóa riêng tiến trình Sandbox? Bản lưu chơi thường không bị ảnh hưởng.'))return;try{if(!ensureSaveRecovery())return;localStorage.removeItem(gardenSandboxKey);if(localStorage.getItem(gardenSandboxKey)!==null)throw Error();gardenStatus('Đã đặt lại Sandbox. Tiến trình thường được giữ nguyên.')}catch{gardenStatus('Không thể đặt lại Sandbox.')}};
'''%(json.dumps(options),json.dumps(sandbox))
p.write_text(h,encoding='utf-8')
p=root/'integration/games.json';d=json.loads(p.read_text());d['hubVersion']='1.22.0';g=next(g for g in d['games'] if g['id']=='garden-through-time');g['version']='0.79.3';g['subtitle']='Final Stability RC3 · Xi Sandbox';g['save']['keys'] += [sandbox,options];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print('PASS Sandbox integration, separate save and explicit launch')
