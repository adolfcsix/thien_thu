"""Apply local-only private settings to an already built F1.7 candidate."""
import hashlib,json,re,subprocess,sys,zipfile
from pathlib import Path
root=Path(__file__).resolve().parent
out=Path(sys.argv[1]).resolve(); site=out/'site'
helper=(root/'dialog.js').read_text(encoding='utf-8')
def patch(path,old,new):
    p=out/path;s=p.read_text(encoding='utf-8');assert s.count(old)==1,(path,old,s.count(old));p.write_text(s.replace(old,new),encoding='utf-8')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Capture the exact F1.7 baseline for the catalog version guard.
meta=out/'integration/games.json'; data=json.loads(meta.read_text());assert data['hubVersion']=='1.7.0'
prior=[]
for g in data['games']:
    if g['status']=='released':prior.append({**{k:g[k] for k in ('id','version','entry','save')},'integrity':{p:digest(site/p) for p in g['files']}})
(out/'integration/release-baseline.json').write_text(json.dumps(prior,ensure_ascii=False,indent=2)+'\n')
# Existing game closures own their save/UI state. Only explicit Apply mutates it.
b='site/games/block-nova/index.html'
patch(b,'const btn=(a,t,p=false)',helper+'\nconst btn=(a,t,p=false)')
patch(b,"btn('help','Cách chơi')+btn('resume'","btn('help','Cách chơi')+btn('xi-private','?')+btn('resume'")
patch(b,"let a=e.target.dataset.a;if(a==='xi-hub')", """let a=e.target.dataset.a;if(a==='xi-private'){xiPrivateOptions([{id:'score',label:'Điểm ván hiện tại',value:state.score,min:0,max:1000000000},...(mode==='classic'?[{id:'best',label:'Kỷ lục Classic',value:best,min:0,max:1000000000}]:[])],v=>{if(mode==='classic'&&v.best<v.score)return 'Kỷ lục phải lớn hơn hoặc bằng điểm hiện tại.';const old=state.score,oldBest=best;state.score=v.score;if(mode==='classic')best=v.best;save();try{if(JSON.parse(localStorage.getItem('xi:game:block-nova:'+mode)).score!==v.score||(mode==='classic'&&JSON.parse(localStorage.getItem('xi:game:block-nova:best'))!==best))throw Error()}catch{state.score=old;best=oldBest;save();return 'Không thể lưu điểm.'}update();return true},'blue');return}if(a==='xi-hub')""")
# CUBIQ: unlock further levels without modifying records or current puzzle.
c='site/games/cubiq/index.html'
patch(c,'function menu(){',helper+'\nfunction menu(){')
patch(c,'<button data-act="xi-hub">Về sảnh Xi</button>','<button data-act="xi-private">?</button><button data-act="xi-hub">Về sảnh Xi</button>')
patch(c,"switch(b.dataset.act){case'xi-hub'", """switch(b.dataset.act){case'xi-private':xiPrivateOptions([{id:'unlocked',label:'Mở khóa đến màn',value:unlocked,min:unlocked,max:10000}],v=>{const old=unlocked;unlocked=v.unlocked;save();try{if(JSON.parse(localStorage.getItem(SAVE)).unlocked!==unlocked)throw Error()}catch{unlocked=old;save();return 'Không thể lưu màn đã mở.'}return true},'light');break;case'xi-hub'""")
# Feather Fury: offline wallet only, no campaign/statistics alterations.
f='site/games/feather-fury/index.html'
patch(f,'function settings(){',helper+'\nfunction settings(){')
patch(f,'<button id="importSave">Nhập sao lưu</button>','<button id="importSave">Nhập sao lưu</button><button id="xi-private-open">?</button>')
patch(f,"$('importSave').onclick=()=>$('import').click()", """$('importSave').onclick=()=>$('import').click();$('xi-private-open').onclick=()=>xiPrivateOptions([{id:'coins',label:'Vàng',value:sv.coins,min:0,max:1000000000},{id:'feathers',label:'Lông vũ',value:sv.feathers,min:0,max:1000000000}],v=>{const old=[sv.coins,sv.feathers];sv.coins=v.coins;sv.feathers=v.feathers;persist();if(!storage){[sv.coins,sv.feathers]=old;return 'Không thể lưu tài nguyên.'}hud();return true},'forest')""")
# Thiên Thủ: current battle gold; preserve engine, stars, medals and schema.
l='site/games/legacy/index.html';a='site/games/legacy/src/app.js'
patch(l,'<button id="closeSettings"','<button id="xi-private-open">?</button><button id="closeSettings"')
patch(a,'function settings(){',helper+'\nfunction settings(){')
patch(a,"$('settingsBtn').onclick=settings;", """$('xi-private-open').onclick=()=>{if(!s||s.result){notify('Cần có trận đấu chưa kết thúc để chỉnh vàng.');return}xiPrivateOptions([{id:'gold',label:'Vàng trận hiện tại',value:s.gold,min:0,max:100000000}],v=>{if(!s||s.result)return 'Không còn trận đấu hợp lệ.';const old=s.gold;s.gold=v.gold;if(!persist()){s.gold=old;return 'Không thể lưu vàng.'}if(screen==='battle')sync();return true})};$('settingsBtn').onclick=settings;""")
data['hubVersion']='1.8.0';versions={'legacy':'9.1','cubiq':'1.1','block-nova':'1.1','feather-fury':'10.2'}
for g in data['games']:
    if g['id'] in versions:g['version']=versions[g['id']]
meta.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Adapt version-sensitive tests; no weakening of actual catalog or worker assertions.
p=out/'tests/worker.test.js';s=p.read_text();s=s.replace("version='9.0'","version=game.version").replace(".replace('\"version\": \"9.0\"',", ".replace(`\"version\": \"${game.version}\"`,").replace("d.installedVersion,'9.0'","d.installedVersion,game.version").replace(".installedVersion,'9.0'",".installedVersion,game.version").replace("version:'9.1'","version:'9.2'").replace("d.installedVersion,'9.1'","d.installedVersion,'9.2'").replace(".installedVersion,'9.1'",".installedVersion,'9.2'").replace(":game:legacy:9.1:",":game:legacy:9.2:");p.write_text(s)
# Version-guard fixture must bump beyond the shipped 9.1.
patch('tests/integration.test.js',"input.games[0].version='9.1'","input.games[0].version='9.2'")
# Preflight pins new adapters, all other original V9 files remain checked byte-for-byte.
p=out/'tests/release-preflight.py';s=p.read_text()
for name in ('index.html','src/app.js'):
    pattern=r"('"+re.escape(name)+r"': ')[0-9a-f]{64}(')";s,n=re.subn(pattern,lambda m:m[1]+digest(site/'games/legacy'/name)+m[2],s);assert n==1
p.write_text(s)
subprocess.run(['node','tools/catalog.mjs','--write'],cwd=out,check=True)
with zipfile.ZipFile(out.parent/'candidate.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(out.rglob('*')):
        if p.is_file() and p.suffix not in ('.pyc','.png') or p.is_file() and 'site' in p.relative_to(out).parts:
            z.write(p,p.relative_to(out))
print('F1.8 private settings integrated; local save namespaces unchanged.')
