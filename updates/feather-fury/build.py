"""Reproducible F1.7 overlay on the immutable, accepted F1.6 archive."""
import hashlib, json, shutil, subprocess, sys, zipfile
from pathlib import Path
root = Path(__file__).resolve().parent
repo = root.parents[1]
base = repo / 'Xi_Foundation_1_6_Release_Candidate.zip'
out = Path(sys.argv[1]).resolve()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(base) == 'd6c589a0990f005b27ec51c958ba2ec4588e320ed628640eabc4cdfbb87b2155'
assert sha(root/'original.html') == '8092426edb586209abd59a63c871484527205882f8518c416b40a503073d6115'
assert not out.exists(), 'Use a new output directory'
with zipfile.ZipFile(base) as z:
    assert z.testzip() is None
    z.extractall(out)
def patch(name, old, new):
    p=out/name; s=p.read_text(encoding='utf-8'); assert s.count(old)==1,(name,old,s.count(old)); p.write_text(s.replace(old,new),encoding='utf-8')
site=out/'site'; before={p.relative_to(site).as_posix():sha(p) for p in site.rglob('*') if p.is_file()}
source=(root/'original.html').read_text(encoding='utf-8')
for k in ('ff10-progress','ff9-progress','ff8-progress','ff7-progress'):
    source=source.replace("'"+k+"'", "'xi:game:feather-fury:"+k+"'")
old="['Màn mới nhất',()=>start(sv.open)]"
assert source.count(old)==1
source=source.replace(old,old+",['Về sảnh Xi',()=>{show('VỀ SẢNH XI','Tiến trình lâu dài được lưu. Chặng đang chơi sẽ bắt đầu lại khi quay lại.','','Quay lại',menu);const b=document.createElement('button');b.className='buy';b.textContent='Xác nhận về sảnh';b.onclick=()=>{persist();if(!storage){$('desc').textContent='Không thể lưu. Quay lại Cài đặt để xuất sao lưu.';return}location.assign('../../')};$('content').append(b)}]")
entry=site/'games/feather-fury/index.html';entry.parent.mkdir();entry.write_text(source,encoding='utf-8')
assert sha(entry)=='2e659a56e4ab362fd1c16b385b46ec39326f4f394d23c3607976c4c6717ade34', 'Integrated module differs from tested F1.7'
shutil.copyfile(root/'cover.svg',site/'assets/feather-fury-cover.svg')
p=out/'integration/games.json'; data=json.loads(p.read_text());data['hubVersion']='1.7.0';ids=['legacy','cubiq','block-nova','feather-fury']
g={'id':'feather-fury','title':'FEATHER FURY','subtitle':'Sky Islands · Stability Update','genre':'Kéo ná · Vật lý 2D','description':'100 màn, 200 chặng, tám chim và năm phép thuật.','status':'released','version':'10.1','offline':True,'runtime':'static-web','contract':1,'entry':'games/feather-fury/index.html','returnToHub':'../../','cover':'assets/feather-fury-cover.svg','save':{'namespace':'xi:game:feather-fury:','keys':['xi:game:feather-fury:'+k for k in ('ff10-progress','ff9-progress','ff8-progress','ff7-progress')]},'files':['games/feather-fury/index.html']}
data['games'].insert(3,g);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
patch('tests/foundation.test.js','["legacy","cubiq","block-nova"]','["legacy","cubiq","block-nova","feather-fury"]')
patch('tests/integration.test.js',"c.games.filter(g=>g.status==='released').length,4)","c.games.filter(g=>g.status==='released').length,5)")
patch('tests/integration.test.js',"c.games.filter(g=>g.status==='released').length,3)","c.games.filter(g=>g.status==='released').length,4)")
patch('tests/worker.test.js',"{legacy:true,cubiq:false,'block-nova':false}","{legacy:true,cubiq:false,'block-nova':false,'feather-fury':false}")
patch('tests/worker.test.js',"['cubiq','block-nova'])assert", "['cubiq','block-nova','feather-fury'])assert")
patch('tests/worker.test.js',"assert.equal(d.legacy,true)});","assert.equal(d.legacy,true);assert.equal(d['feather-fury'],true)});")
patch('tests/ui.py',"cat=(root/'catalog-data.js').read_text()","cat=(root/'catalog-data.js').read_text();cat=cat.replace('assets/feather-fury-cover.svg',data('assets/feather-fury-cover.svg','image/svg+xml'))")
patch('tests/ui.py',"locator('#featured article').count()==3","locator('#featured article').count()==4")
patch('tests/imported-ui.py',"['games/cubiq/index.html','games/block-nova/index.html']","['games/cubiq/index.html','games/block-nova/index.html','games/feather-fury/index.html']")
patch('tests/imported-ui.py',' assert not errors,errors', ''' pg.goto(base+'games/feather-fury/index.html');pg.locator('#canvas').wait_for();pg.locator('#menu').click();pg.get_by_role('button',name='Về sảnh Xi',exact=True).click();pg.get_by_role('button',name='Xác nhận về sảnh').click();pg.get_by_text('Hub fixture').wait_for();assert pg.evaluate("!!localStorage.getItem('xi:game:feather-fury:ff10-progress')");assert pg.evaluate("localStorage.getItem('xi:game:cubiq:save')")==saved
 assert not errors,errors''')
patch('tests/browser.py',"for game in ('cubiq','block-nova'):","for game in ('cubiq','block-nova','feather-fury'):")
patch('tests/browser.py',"            print('PASS three independent offline games, remove/reinstall and saves',flush=True)",'''            page.goto(url+'games/feather-fury/index.html');page.locator('#canvas').wait_for();page.locator('#menu').click();page.get_by_role('button',name='Về sảnh Xi',exact=True).click();page.get_by_role('button',name='Xác nhận về sảnh').click();page.locator('#discover h2').wait_for();ff=page.evaluate("localStorage.getItem('xi:game:feather-fury:ff10-progress')");assert ff
            assert rpc(page,'REMOVE','feather-fury')['ok'];assert page.evaluate("localStorage.getItem('xi:game:feather-fury:ff10-progress')")==ff
            d=rpc(page,'DETAILS')['value'];assert not d['feather-fury']['ready'] and all(d[g]['ready'] for g in ('legacy','cubiq','block-nova'))
            ctx.set_offline(False);assert rpc(page,'INSTALL','feather-fury')['ok'];ctx.set_offline(True);page.goto(url+'games/feather-fury/index.html');page.locator('#canvas').wait_for();assert page.evaluate("localStorage.getItem('xi:game:feather-fury:ff10-progress')")==ff
            assert not errors,errors
            print('PASS four independent offline games, remove/reinstall and saves',flush=True)''')
p=out/'tests/release-preflight.py';s=p.read_text();assert s.count("['legacy','cubiq','block-nova']")==2;p.write_text(s.replace("['legacy','cubiq','block-nova']",repr(ids)),encoding='utf-8')
# Landscape cover art: verified original bytes, no gameplay or save changes.
art={'cubiq-cover.webp':'27af7af0f7c43d8638c633bb74fc3e4a1c282ecc35d3252589121638c5414920','block-nova-cover.webp':'892f87aedb4f6f0a83f37f162a20c2d04be8d98b5e422279e1e13bedd3538164'}
for name,h in art.items():
    assert sha(root/name)==h, 'Cover integrity: '+name
    shutil.copyfile(root/name,site/'assets'/name)
patch('site/hub.css','.featured:not(:first-child) .cover{background-size:contain;background-repeat:no-repeat;background-color:#201d1a}', '.featured .cover{background-size:cover;background-repeat:no-repeat;background-color:#201d1a}')
patch('tests/ui.py',"assert page.locator('#featured article').count()==4", "assert page.locator('#featured article').count()==4;assert page.locator('#featured .cover').evaluate_all(\"els=>els.every(e=>getComputedStyle(e).backgroundSize==='cover'&&e.clientWidth>0&&e.clientHeight>0)\");assert page.locator('#featured .cover').evaluate_all(\"els=>Promise.all(els.map(async e=>{const im=new Image();im.src=e.style.backgroundImage.slice(5,-2);await im.decode();return im.naturalWidth>0&&im.naturalHeight>0})).then(a=>a.every(Boolean))\")")
subprocess.run(['node','tools/catalog.mjs','--write'],cwd=out,check=True)
allowed={'catalog-data.js','hub.css','assets/cubiq-cover.webp','assets/block-nova-cover.webp'}
for name,h in before.items():
    if name not in allowed: assert sha(site/name)==h,name
# ZIP for existing preflight; generated only once per CI run.
with zipfile.ZipFile(out.parent/'candidate.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(out.rglob('*')):
        if p.is_file(): z.write(p,p.relative_to(out))
print('F1.7 source overlay built; existing F1.6 game files unchanged; catalog and approved cover art updated')
