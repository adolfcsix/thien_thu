"""Integrate the exact user-supplied Huyen Anh v82 RC3 offline playtest."""
from pathlib import Path
import base64,gzip,hashlib,json,re,shutil,subprocess,sys
root=Path(sys.argv[1]);site=root/'site';src=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decode(name,expected):
    raw=gzip.decompress(base64.b64decode(''.join((src/name).read_text(encoding='ascii').split()),validate=True))
    assert hashlib.sha256(raw).hexdigest()==expected,(name,'source checksum')
    return raw
def once(s,a,b):
    assert s.count(a)==1,a[:120]
    return s.replace(a,b)
protected={p.relative_to(site):sha(p) for p in (site/'games').rglob('*') if p.is_file()}
original=decode('source.html.gz.b64','698f9f327ed16d9ab1977fc7a18fa84d5e4ec2e39fe5165694d9c14c715941a8')
cover=decode('cover.webp.gz.b64','f90eb7f9c96f79016c62539067fa1616bc8f27ea6a1edbc5d62463f53eb72bef')
s=original.decode('utf-8');ns='xi:game:huyen-anh:'
keys=['ha-world-v'+str(i) for i in range(29,36)]+['ha-world-v35-backup','ha-control62','ha-soft66','ha-sound67']
for key in sorted(keys,key=len,reverse=True):
    s,n=re.subn(r"(['\"])"+re.escape(key)+r"\1",lambda m:m[1]+ns+key+m[1],s)
    if key!='ha-world-v35-backup':assert n>0,key
assert "key29='xi:game:huyen-anh:ha-world-v35'" in s and "backupKey29=key29+'-backup'" in s
# Only copy legacy same-origin values once, and do not overwrite either original or namespaced saves.
migration=json.dumps([[k,ns+k] for k in keys])
adapter='<script>(()=>{try{const flag='+json.dumps(ns+'migration-v1')+';if(localStorage.getItem(flag)===null){for(const [a,b] of '+migration+'){if(localStorage.getItem(b)===null){const v=localStorage.getItem(a);if(v!==null)localStorage.setItem(b,v)}}localStorage.setItem(flag,"1")}}catch{}for(const type of ["gesturestart","gesturechange","gestureend"])document.addEventListener(type,e=>e.preventDefault(),{passive:false});document.addEventListener("touchmove",e=>{if(e.touches.length>1)e.preventDefault()},{passive:false})})();</script>'
s=once(s,'width=device-width, initial-scale=1, viewport-fit=cover','width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover')
s=once(s,'</head>',adapter+'<style id="xi-ha-layout">#xi-return{min-height:44px;white-space:nowrap;flex:none}html{overscroll-behavior:none}.playbar37{flex-wrap:wrap}@media(orientation:landscape) and (max-height:650px){.touch61.focus37 .playbar37{flex-wrap:wrap}}</style></head>')
exit_script="""<script>(()=>{const bar=document.querySelector('.playbar37');if(!bar)return;const button=document.createElement('button');button.id='xi-return';button.type='button';button.textContent='Về Xi';button.setAttribute('aria-label','Về sảnh Xi');bar.append(button);button.onclick=()=>{let ok=false;try{if(!worldMode)ok=true;else ok=save29()}catch{}if(!ok&&!confirm('Chưa lưu được hành trình. Vẫn về sảnh Xi?'))return;location.assign('../../')};})();</script>"""
s=once(s,'</body>',exit_script+'</body>')
dest=site/'games/huyen-anh';dest.mkdir()
(dest/'index.html').write_text(s,encoding='utf-8')
(site/'assets/huyen-anh-cover.webp').write_bytes(cover)
# Distribute the upstream notices with the actual offline game, not just the repository.
licenses=['LICENSE-PixelFX.txt','NOTICE-PixelFX.md','LICENSE-Hollow-Crown.txt','SOURCE-AND-QA.md']
for name in licenses:shutil.copyfile(src/name,dest/name)
p=root/'integration/games.json';d=json.loads(p.read_text(encoding='utf-8'))
assert d['hubVersion']=='1.24.0';d['hubVersion']='1.25.0'
g={'id':'huyen-anh','title':'HUYỀN ẢNH','subtitle':'Dragon World v82 RC3 · Chơi thử','genre':'RPG · Hành động','description':'Hành trình offline, 111 bản đồ, 6 chủng tộc, 60 kỹ năng, trang bị, đệ tử và Boss.','status':'released','version':'0.82.3','offline':True,'runtime':'static-web','contract':1,'entry':'games/huyen-anh/index.html','returnToHub':'../../','cover':'assets/huyen-anh-cover.webp','save':{'namespace':ns,'keys':[ns+k for k in keys]},'files':['games/huyen-anh/index.html']+['games/huyen-anh/'+name for name in licenses]}
assert not any(x['id']==g['id'] for x in d['games'])
d['games'].insert(next(i for i,x in enumerate(d['games']) if x['status']=='planned'),g)
# Avoid showing two identically named cards: the unreleased Shadow Blade remains separate.
for x in d['games']:
    if x['id']=='shadow-blade' and x['status']=='planned':x['title']='SHADOW BLADE'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=site/'hub.js';h=p.read_text(encoding='utf-8')
anchor="const enums={'xi:game:ky-vien:ky-vien-theme'"
extra="""if(k==='xi:game:huyen-anh:ha-soft66'){if(!['true','false'].includes(v))throw Error('Tùy chọn Huyền Ảnh không hợp lệ');continue}if(k==='xi:game:huyen-anh:ha-sound67'){let x;try{x=JSON.parse(v)}catch{}if(!x||Array.isArray(x)||typeof x.enabled!=='boolean'||['master','sfx','music','ambient'].some(f=>typeof x[f]!=='number'||!Number.isFinite(x[f])||x[f]<0||x[f]>1))throw Error('Âm thanh Huyền Ảnh không hợp lệ');continue}if(k.startsWith('xi:game:huyen-anh:ha-world-')){let x;try{x=JSON.parse(v)}catch{}if(!x||![29,30,31,32,33,34,35].includes(x.v)||!Array.isArray(x.clears)||!Array.isArray(x.owned))throw Error('Bản lưu Huyền Ảnh không hợp lệ');continue}const enums={'xi:game:huyen-anh:ha-control62':['touch','buttons'],'xi:game:ky-vien:ky-vien-theme'"""
h=once(h,anchor,extra);p.write_text(h,encoding='utf-8')
for i,code in enumerate(re.findall(r'<script>(.*?)</script>',s,re.S)):
    p=root/('ha-syntax-'+str(i)+'.js')
    try:p.write_text(code,encoding='utf-8');subprocess.run(['node','--check',str(p)],check=True)
    finally:p.unlink(missing_ok=True)
assert protected=={p:sha(site/p) for p in protected},'Existing six game bytes changed'
print('PASS exact Huyen Anh RC3 source, cover, scoped saves, syntax, six protected game modules and offline notices')
