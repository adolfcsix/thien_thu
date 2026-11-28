"""F1.21: add two original standalone games after the accepted F1.20 build."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys,zipfile
src=Path(__file__).resolve().parents[1]
old=Path(sys.argv[1]).resolve()
root=Path(sys.argv[2]).resolve()
assert not root.exists()
shutil.copytree(old,root)
site=root/'site'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protected={p.relative_to(site):sha(p) for p in site.rglob('*') if p.is_file() and (p.relative_to(site).parts[0] in ('games','assets') or p.name=='manifest.webmanifest')}
p=root/'integration/games.json';data=json.loads(p.read_text())
assert data['hubVersion']=='1.20.0'
data['hubVersion']='1.21.0'
games=[
 ('ky-vien','ky-vien-10','20948778b865d502fa739c5dfc4c1190024658c5d686537dc18b7ab33fa7f410','KỲ VIỆN','Imperial Jade','Cờ · Chiến thuật','Phòng cờ, đấu AI, học tập, kỳ phổ và hồ sơ kỳ thủ.','1.0',['ky-vien-v1','ky-vien-theme','kv-archive-v1','kv-learning-v1','kv-results-v1','kv-skin','kv-sound','kv-piece-skin'], '#203c30','#f1d79e','♞'),
 ('garden-through-time','garden-0792','c2ef48d4f82e637d02b5014195c1e1886abc4b96240ae1ac6e3be6130b8aff4b','Garden Through Time','Final Stability RC3','Thủ thành · Chiến thuật','Chiến dịch xuyên thời gian, cây phòng thủ, thử thách và cửa hàng.','0.79.2',['garden-time-v1','garden-audio-v1','garden-graphics-v1'],'#29492b','#e8d58b','✿')
]
for gid,folder,expected,title,subtitle,genre,desc,version,keys,bg,fg,symbol in games:
    source=src/folder/'original.html';assert sha(source)==expected,folder
    text=source.read_text(encoding='utf-8')
    ns='xi:game:'+gid+':'
    for key in keys:
        pattern=r"""(['"])"""+re.escape(key)+r"""\1"""
        text,n=re.subn(pattern,lambda m:m[1]+ns+key+m[1],text)
        assert n>0,key
    # Copy same-origin legacy values only when the new key is absent. No deletion.
    migration=json.dumps([[k,ns+k] for k in keys],ensure_ascii=False)
    adapter='<script>(()=>{try{const m='+migration+',flag='+json.dumps(ns+'migration-v1')+';if(localStorage.getItem(flag)===null){for(const [a,b] of m){const v=localStorage.getItem(a);if(v!==null&&localStorage.getItem(b)===null)localStorage.setItem(b,v)}localStorage.setItem(flag,"1")}}catch{}for(const e of ["gesturestart","gesturechange","gestureend"])document.addEventListener(e,x=>x.preventDefault(),{passive:false});document.addEventListener("touchmove",e=>{if(e.touches.length>1)e.preventDefault()},{passive:false})})();</script>'
    viewport='<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
    assert text.count(viewport)==1
    text=text.replace(viewport,'<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">'+adapter)
    style='<style id="xi-new-game-layout">html{touch-action:manipulation;overscroll-behavior:none}header{flex-wrap:wrap;gap:8px}header>div{min-width:0}#xi-return{min-height:44px;min-width:44px;white-space:nowrap;padding:8px 12px;border-radius:12px}body{padding-left:env(safe-area-inset-left,0px);padding-right:env(safe-area-inset-right,0px)}#board{touch-action:manipulation}input[type=range]{touch-action:pan-x}button{touch-action:manipulation}</style>'
    assert text.count('</head>')==1 and text.count('</header>')==1
    text=text.replace('</head>',style+'</head>').replace('</header>','<button id="xi-return" type="button">Về sảnh Xi</button></header>')
    handler="if(!save()&&!confirm('Không lưu được ván hiện tại. Vẫn về sảnh?'))return;" if gid=='ky-vien' else "if(g&&!confirm('Về sảnh sẽ kết thúc phiên chiến đấu hiện tại. Tiếp tục?'))return;pauseForPageExit();if(saveDirty&&!confirm('Chưa lưu được tiến độ. Vẫn về sảnh?'))return;"
    text=text.replace('</body>','<script>document.getElementById("xi-return").onclick=()=>{'+handler+'location.assign("../../")};</script></body>')
    entry='games/'+gid+'/index.html';dest=site/entry;dest.parent.mkdir()
    dest.write_text(text,encoding='utf-8')
    # Original HTML remains pinned; adapter changes only namespace, viewport and return.
    cover='assets/'+gid+'-cover.svg'
    (site/cover).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540"><defs><radialGradient id="g"><stop stop-color="{fg}" stop-opacity=".25"/><stop offset="1" stop-color="{bg}"/></radialGradient></defs><rect width="960" height="540" fill="{bg}"/><rect width="960" height="540" fill="url(#g)"/><g fill="none" stroke="{fg}" opacity=".25"><circle cx="725" cy="245" r="182"/><circle cx="725" cy="245" r="157"/><path d="M515 245h420M725 35v420"/></g><text x="725" y="340" font-size="230" text-anchor="middle" fill="{fg}" font-family="serif">{symbol}</text><path d="M50 470h430" stroke="{fg}" opacity=".5"/><text x="50" y="415" font-size="40" fill="{fg}" font-family="sans-serif">{title}</text></svg>',encoding='utf-8')
    g={'id':gid,'title':title,'subtitle':subtitle,'genre':genre,'description':desc,'status':'released','version':version,'offline':True,'runtime':'static-web','contract':1,'entry':entry,'returnToHub':'../../','cover':cover,'save':{'namespace':ns,'keys':[ns+k for k in keys]},'files':[entry]}
    assert not any(x['id']==gid for x in data['games'])
    data['games'].insert(next((i for i,x in enumerate(data['games']) if x['status']=='planned'),len(data['games'])),g)
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
# Existing hub backup accepts JSON objects by default. Kỳ Viện has raw enum preferences
# and an archive array. Restrict exceptions to precisely those registered save keys.
p=site/'hub.js';s=p.read_text()
a="for(const [k,v] of entries){let parsed;try{parsed=JSON.parse(v)}"
assert s.count(a)==1
s=s.replace(a,"for(const [k,v] of entries){const enums={'xi:game:ky-vien:ky-vien-theme':['dark','light'],'xi:game:ky-vien:kv-skin':['jade','walnut','slate'],'xi:game:ky-vien:kv-sound':['on','off'],'xi:game:ky-vien:kv-piece-skin':['heritage','classic','onyx']};if(Object.hasOwn(enums,k)){if(!enums[k].includes(v))throw Error('Tùy chọn bản lưu không hợp lệ: '+k);continue}if(k==='xi:game:ky-vien:kv-archive-v1'){let a;try{a=JSON.parse(v)}catch{}if(!Array.isArray(a)||a.length>30||a.some(x=>!x||typeof x!=='object'||!Array.isArray(x.history)||!Array.isArray(x.moves)))throw Error('Kỳ phổ không hợp lệ');continue}let parsed;try{parsed=JSON.parse(v)}")
p.write_text(s)
subprocess.run([sys.executable,str(src/'six-games'/'garden-sandbox.py'),str(root)],check=True)
# Replace hub artwork only; game bytes and existing non-art resources remain protected.
for gid in ('feather-fury','ky-vien','garden-through-time'):
    name=gid+'-cover.svg'
    shutil.copyfile(src/'six-games'/'art'/name,site/'assets'/name)
    protected.pop(Path('assets')/name,None)
# Bump the shell version to guarantee a new artwork cache even if F1.22 publishes first.
p=root/'integration/games.json';d=json.loads(p.read_text());assert d['hubVersion']=='1.22.0';d['hubVersion']='1.24.0';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
with (site/'hub.css').open('a',encoding='utf-8') as f:f.write('\n/* Per-game art focus, shared by discovery and spotlight. */\n.featured[data-game-id="feather-fury"] .cover,#spotlight[data-slide="feather-fury"]{background-position:64% 44%}.featured[data-game-id="ky-vien"] .cover,#spotlight[data-slide="ky-vien"]{background-position:70% 55%}.featured[data-game-id="garden-through-time"] .cover,#spotlight[data-slide="garden-through-time"]{background-position:69% 52%}\n')
# Use real image elements for card art; background CSS is not reliably
# observable during WebKit style/layout transitions. Spotlight remains a background.
p=site/'hub.js';s=p.read_text(encoding='utf-8')
anchor="cover.style.backgroundImage=\x60url('\x24{g.cover}')\x60;"
assert s.count(anchor)==1
s=s.replace(anchor,"const art=e('img','cover-art');art.src=g.cover;art.alt='';art.decoding='async';cover.append(art);")
p.write_text(s,encoding='utf-8')
with (site/'hub.css').open('a',encoding='utf-8') as f:
    f.write('\n/* Real image surfaces with the same native card layout and focus. */\n.featured .cover-art{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center;display:block;pointer-events:none}.featured .cover::after{z-index:1;pointer-events:none}.featured .cover-label{z-index:2}.featured[data-game-id="feather-fury"] .cover-art{object-position:64% 44%}.featured[data-game-id="ky-vien"] .cover-art{object-position:70% 55%}.featured[data-game-id="garden-through-time"] .cover-art{object-position:69% 52%}\n')
subprocess.run(['node','tools/catalog.mjs','--write'],cwd=root,check=True)
subprocess.run(['node','tools/catalog.mjs'],cwd=root,check=True)
subprocess.run(['node','--check','site/hub.js'],cwd=root,check=True)
for gid,*_ in games:
    p=site/'games'/gid/'index.html'
    for i,script in enumerate(re.findall(r'<script>(.*?)</script>',p.read_text(),re.S)):
        f=root/f'xi-check-{i}.js';f.write_text(script)
        subprocess.run(['node','--check',str(f)],check=True);f.unlink()
subprocess.run([sys.executable,str(src/'shell-stability'/'guard.py'),str(site)],check=True)
subprocess.run(['node','--check','site/sw.js'],cwd=root,check=True)
kit=site/'xi-offline-kit.zip'
with zipfile.ZipFile(kit) as z: readme=z.read('README.txt')
with zipfile.ZipFile(kit,'w',zipfile.ZIP_DEFLATED) as z:
    for f in sorted(site.rglob('*')):
        if not f.is_file() or f==kit:continue
        name='site/'+f.relative_to(site).as_posix()
        if f.name=='sw.js':z.writestr(name,f.read_text().replace(",'xi-offline-kit.zip'",''))
        else:z.write(f,name)
    z.writestr('README.txt',readme)
assert all(sha(site/p)==h for p,h in protected.items()),'Existing game or asset changed'
assert all((site/'games'/g[0]/'index.html').exists() for g in games)
with zipfile.ZipFile(root.parent/'release.zip','w',zipfile.ZIP_DEFLATED) as z:
    for f in sorted(root.rglob('*')):
        if f.is_file() and (f.relative_to(root).parts[0]=='site' or f.suffix not in ('.pyc','.png')):z.write(f,f.relative_to(root))
print('PASS F1.24 six-game catalog, original source hashes, JS syntax, unchanged previous modules and offline kit')
