"""Add Pham Nhan Tu Tien as an offline, independent static game."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
root=Path(sys.argv[1]);site=root/'site';src=Path(__file__).resolve().parent
raw=(src/'original.html').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='e9ed8c2f290d6c624df12fdb137eb039b7af79d3aad52171618d7ce0bf85b895'
s=raw.decode('utf-8')
ns='xi:game:pham-nhan-tu-tien:'
key=ns+'vankiem-v1'
assert s.count("'vankiem-v1'")==2
s=s.replace("'vankiem-v1'",repr(key))
adapter='<script>(()=>{try{if(localStorage.getItem('+json.dumps(key)+')===null){const v=localStorage.getItem("vankiem-v1");if(v!==null)localStorage.setItem('+json.dumps(key)+',v)}}catch{}for(const e of ["gesturestart","gesturechange","gestureend"])document.addEventListener(e,x=>x.preventDefault(),{passive:false});document.addEventListener("touchmove",e=>{if(e.touches.length>1)e.preventDefault()},{passive:false})})();</script>'
style='<style>#xi-return{position:fixed;z-index:10000;bottom:max(8px,env(safe-area-inset-bottom));left:50%;transform:translateX(-50%);min-height:40px;padding:6px 12px;font-size:12px;white-space:nowrap}#xi-return:focus-visible{outline:2px solid #fff}</style>'
s=s.replace('</head>',adapter+style+'</head>',1)
s=s.replace('</body>','<button id="xi-return" type="button">Về sảnh Xi</button><script>document.getElementById("xi-return").onclick=()=>{if(!save()&&!confirm("Chưa lưu được tiến độ. Vẫn về sảnh Xi?"))return;location.assign("../../")};</script></body>',1)
entry='games/pham-nhan-tu-tien/index.html'
dest=site/entry;dest.parent.mkdir();dest.write_text(s,encoding='utf-8')
cover='assets/pham-nhan-tu-tien-cover.svg'
(site/cover).write_text('<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" viewBox="0 0 960 540"><defs><linearGradient id="a" x2="0" y2="1"><stop stop-color="#142b31"/><stop offset="1" stop-color="#71918a"/></linearGradient></defs><rect width="960" height="540" fill="url(#a)"/><circle cx="738" cy="150" r="85" fill="#e8d8ac"/><path d="M0 380L178 180 320 340 520 96 748 350 960 190V540H0Z" fill="#345b5a"/><path d="M0 450L200 280 450 460 690 260 960 430V540H0Z" fill="#193d3c"/><path d="M730 230L760 340 730 380 700 340Z" fill="#d8b975"/><path d="M620 345H840" stroke="#d8b975" stroke-width="3"/><text x="55" y="390" font-size="46" fill="#fff0c6" font-family="serif">PHÀM NHÂN TU TIÊN</text><text x="58" y="432" font-size="23" fill="#e5d9ba">THIÊN ĐỊA CHÍ BẢO</text></svg>',encoding='utf-8')
p=root/'integration/games.json';d=json.loads(p.read_text(encoding='utf-8'))
assert d['hubVersion']=='1.25.0';d['hubVersion']='1.26.0'
g={'id':'pham-nhan-tu-tien','title':'PHÀM NHÂN TU TIÊN','subtitle':'Thiên Địa Chí Bảo · Chơi thử','genre':'RPG · Tu tiên','description':'Thế giới mở chơi đơn, năm cảnh giới, công pháp, tông môn, trân thú và luyện chế pháp bảo.','status':'released','version':'0.7','offline':True,'runtime':'static-web','contract':1,'entry':entry,'returnToHub':'../../','cover':cover,'save':{'namespace':ns,'keys':[key]},'files':[entry]}
assert not any(x['id']==g['id'] for x in d['games'])
d['games'].insert(next((i for i,x in enumerate(d['games']) if x['status']=='planned'),len(d['games'])),g)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for i,code in enumerate(re.findall(r'<script>(.*?)</script>',s,re.S)):
    p=root/f'pn-check-{i}.js'
    try:p.write_text(code,encoding='utf-8');subprocess.run(['node','--check',str(p)],check=True)
    finally:p.unlink(missing_ok=True)
print('PASS Pham Nhan source hash, scoped save, offline catalog and JavaScript syntax')
