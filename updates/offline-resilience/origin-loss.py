"""Real browser acceptance for a vanished host and cached recovery kit."""
import argparse,functools,http.server,threading,tempfile,shutil,json,hashlib,zipfile
from pathlib import Path
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--engine',choices=['chromium','webkit'],required=True);p.add_argument('--site',type=Path,required=True);args=p.parse_args()
class Handler(http.server.SimpleHTTPRequestHandler):
 gone=False
 def log_message(self,*a):pass
 def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
 def do_GET(self):
  if type(self).gone:self.send_error(404,'Origin removed');return
  super().do_GET()
def rpc(page,kind,id=None):
 return page.evaluate("""async ([type,id])=>{const r=await navigator.serviceWorker.ready,c=new MessageChannel();return new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(Error('worker timeout')),30000);c.port1.onmessage=e=>{clearTimeout(t);c.port1.close();resolve(e.data)};(navigator.serviceWorker.controller||r.active).postMessage({type,id},[c.port2])})}""",[kind,id])
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);target=root/'thien_thu';shutil.copytree(args.site,target);(root/'probe.html').write_text('<!doctype html><title>Probe</title>')
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/thien_thu/'
 try:
  with sync_playwright() as pw:
   b=getattr(pw,args.engine).launch();ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce',accept_downloads=True);ctx.set_default_timeout(30000)
   page=ctx.new_page();page.goto(url)
   probe=ctx.new_page();probe.goto(f'http://127.0.0.1:{server.server_port}/probe.html');probe.wait_for_function("async url=>{const r=await navigator.serviceWorker.getRegistration(url);return r?.active?.state==='activated'&&!r.installing&&!r.waiting}",arg=url,timeout=60000);page.close();page=ctx.new_page();page.goto(url);probe.close()
   page.wait_for_function('navigator.serviceWorker.controller?.state==="activated"');page.locator('#discover h2').wait_for()
   page.get_by_role('button',name='Cài đặt',exact=True).click();page.locator('#downloadAll').click();page.get_by_text('Tất cả game hiện có đã sẵn sàng offline.',exact=True).wait_for()
   before=rpc(page,'DETAILS')['value'];assert len(before)==4 and all(x['ready'] for x in before.values()),before
   page.goto(url+'games/cubiq/index.html');page.locator('[data-act=menu]').click();page.locator('[data-act=sound]').click();page.get_by_role('button',name='Về sảnh Xi').click();page.locator('#discover h2').wait_for()
   saved=page.evaluate("localStorage.getItem('xi:game:cubiq:save')");assert isinstance(json.loads(saved),dict)
   # Server remains reachable but every request, including SW update, returns 404.
   Handler.gone=True;page.evaluate("async()=>{try{await (await navigator.serviceWorker.getRegistration()).update()}catch{}}")
   page.close();page=ctx.new_page();page.goto(url);page.locator('#discover h2').wait_for();assert rpc(page,'DETAILS')['value']==before
   assert page.evaluate("localStorage.getItem('xi:game:cubiq:save')")==saved
   # Test actual target and focus, not just tab selection.
   page.get_by_role('button',name='Hoạt động',exact=True).click();page.locator('#activityGames article').filter(has=page.get_by_role('heading',name='FEATHER FURY',exact=True)).get_by_role('button',name='Quản lý',exact=True).click();page.wait_for_function("document.activeElement.dataset.gameId==='feather-fury'")
   assert page.locator('#libraryGames [data-game-id=feather-fury]').evaluate("e=>e.classList.contains('managed-game')")
   # Airplane mode after host deletion; all games launch from verified caches.
   ctx.set_offline(True)
   for path,selector in [('legacy','#newBtn'),('cubiq','canvas'),('block-nova','#board'),('feather-fury','#canvas')]:
    page.goto(url+'games/'+path+'/index.html');page.locator(selector).wait_for()
    assert page.locator('#xi-game-gesture-policy').count()==1
    result=page.evaluate("""()=>{const t=document.createElement('button');document.body.append(t);const event=new Event('gesturestart',{cancelable:true,bubbles:true});const multi=new Event('touchmove',{cancelable:true,bubbles:true});Object.defineProperty(multi,'touches',{value:[{},{}]});const single=new Event('touchstart',{cancelable:true,bubbles:true});Object.defineProperty(single,'touches',{value:[{}]});const result=[!t.dispatchEvent(event),!t.dispatchEvent(multi),t.dispatchEvent(single),getComputedStyle(document.querySelector('canvas')).touchAction,document.querySelector('meta[name=viewport]').content];t.remove();return result}""")
    assert result[:4]==[True,True,True,'none'] and 'maximum-scale=1' in result[4] and 'user-scalable=no' in result[4],(path,result)
    assert abs(page.evaluate('visualViewport.scale')-1)<.01
    page.evaluate("""()=>{const p=document.createElement('div');p.id='xiTestTouchProbe';p.style.cssText='position:fixed;inset:0;z-index:2147483647;background:transparent';document.body.append(p)}""")
    page.touchscreen.tap(190,200);page.touchscreen.tap(190,200);page.wait_for_timeout(350);assert abs(page.evaluate('visualViewport.scale')-1)<.01,(path,'double tap')
    if args.engine=='chromium':
     session=ctx.new_cdp_session(page);session.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':150,'y':200,'id':0},{'x':240,'y':200,'id':1}]})
     for n in range(1,7):session.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':150-n*10,'y':200,'id':0},{'x':240+n*10,'y':200,'id':1}]})
     session.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});page.wait_for_timeout(350);assert abs(page.evaluate('visualViewport.scale')-1)<.01,(path,'pinch');session.detach()
    page.evaluate("document.querySelector('#xiTestTouchProbe').remove()")
    print('PASS',path,'offline touch policy, single touch and double tap; Chromium actual pinch',flush=True)
   # Emulate status bar and home-indicator safe-area geometry; physical iPhone still required.
   page.goto(url+'games/feather-fury/index.html');page.locator('#canvas').wait_for();assert page.locator('#xi-feather-safe-area').count()==1
   page.evaluate("document.documentElement.setAttribute('data-xi-ios-standalone','')")
   for w,h,t,r,bt,l in [(428,926,62,0,34,0),(390,844,47,0,34,0),(320,568,20,0,0,0),(280,650,0,0,0,0),(844,390,0,47,21,47),(926,428,0,59,21,59),(1024,768,0,0,0,0)]:
    page.set_viewport_size({'width':w,'height':h});page.evaluate("""([t,r,b,l])=>{const s=document.documentElement.style;for(const [k,v] of Object.entries({top:t,right:r,bottom:b,left:l}))s.setProperty('--xi-safe-'+k,v+'px');window.scrollTo(0,0)}""",[t,r,bt,l])
    q=page.evaluate("""()=>{const rect=s=>{const r=document.querySelector(s).getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,b:r.bottom,right:r.right}};return {head:rect('.top'),wallet:rect('.wallet'),canvas:rect('canvas'),hud:rect('.hud'),power:rect('#power'),sw:document.documentElement.scrollWidth,scale:visualViewport.scale,cols:getComputedStyle(document.querySelector('.deck')).gridTemplateColumns}}""")
    assert q['head']['y']>=t-1 and q['head']['x']>=l-1 and q['head']['right']<=w-r+1 and q['wallet']['right']<=w-r+1 and q['sw']<=w+1,(w,h,q)
    assert abs(q['canvas']['w']/q['canvas']['h']-1.6)<.02 and abs(q['scale']-1)<.01,(w,h,q)
    if h>w:assert q['head']['y']>=59 and q['hud']['b']<=q['canvas']['y']+1,(w,h,q)
    if h>=844 and w>=340:assert q['cols'].count('px')==4 and q['power']['b']<=h-bt+1,(w,h,q)
    page.locator('#menu').click();panel=page.locator('.panel').bounding_box();assert panel['y']>=t-1 and panel['x']>=l-1 and panel['x']+panel['width']<=w-r+1 and panel['y']+panel['height']<=h-bt+1,(w,h,panel)
    page.locator('#go').click();assert not page.locator('#game').evaluate('e=>e.inert')
   print('PASS 7 Feather safe-area geometries, portrait HUD, card grid and canvas ratio',flush=True)
   for game,head,canvas,menu,panel,close,ratio in [('legacy','header','#field','#settingsBtn','#settings','#closeSettings',5/3),('cubiq','.top','canvas','[data-act=menu]','.panel','[data-act=resume]',None),('block-nova','header','#board','#settings','.panel',None,360/440)]:
    page.goto(url+'games/'+game+'/index.html');page.locator(head).first.wait_for()
    if game=='legacy':
     page.locator('#brandIntro').wait_for(state='hidden',timeout=12000);page.locator('#newBtn').click();page.locator('#mapList button').first.click();page.locator('#field').wait_for()
    for w,h,t,r,bt,l in [(428,926,62,0,34,0),(390,844,47,0,34,0),(320,568,20,0,0,0),(280,650,0,0,0,0),(844,390,0,47,21,47),(926,428,0,59,21,59),(568,320,0,30,21,30),(1024,768,0,0,0,0)]:
     page.set_viewport_size({'width':w,'height':h});page.evaluate("""([t,r,b,l])=>{const root=document.documentElement;root.setAttribute('data-xi-ios-standalone','');for(const [k,v] of Object.entries({top:t,right:r,bottom:b,left:l}))root.style.setProperty('--xi-safe-'+k,v+'px');window.scrollTo(0,0)}""",[t,r,bt,l]);page.wait_for_timeout(100)
     q=page.evaluate("""([head,canvas])=>{const rect=s=>{const r=document.querySelector(s).getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right}};return {head:rect(head),cv:rect(canvas),sw:document.documentElement.scrollWidth,scale:visualViewport.scale}}""",[head,canvas])
     assert q['head']['y']>=t-1 and q['head']['x']>=l-1 and q['head']['right']<=w-r+1 and q['sw']<=w+1,(game,w,h,q)
     assert q['cv']['x']>=l-1 and q['cv']['right']<=w-r+1 and abs(q['scale']-1)<.01,(game,w,h,q)
     if ratio:assert abs(q['cv']['w']/q['cv']['h']-ratio)<.03,(game,w,h,q)
     page.locator(menu).click();d=page.locator(panel).first;d.wait_for();z=d.bounding_box();assert z['x']>=l-1 and z['y']>=t-1 and z['x']+z['width']<=w-r+1 and z['y']+z['height']<=h-bt+1,(game,w,h,z)
     if close:page.locator(close).click()
     else:page.evaluate("document.querySelector('#overlay').hidden=true")
    print('PASS',game,'8 offline safe-area geometries and responsive menus',flush=True)

   page.set_viewport_size({'width':390,'height':844})
   page.goto(url);page.locator('#discover h2').wait_for();assert rpc(page,'DETAILS')['value']==before
   page.get_by_role('button',name='Cài đặt',exact=True).click()
   # Verify ZIP bytes against the exact release kit while the original site is unavailable.
   digest=page.evaluate("""async()=>{const r=await fetch('xi-offline-kit.zip');if(!r.ok)throw Error('kit unavailable');return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',await r.arrayBuffer())),x=>x.toString(16).padStart(2,'0')).join('')}""")
   kit=args.site/'xi-offline-kit.zip';assert digest==hashlib.sha256(kit.read_bytes()).hexdigest()
   with zipfile.ZipFile(kit) as z:
    assert z.testzip() is None and 'site/sw.js' in z.namelist() and 'site/xi-offline-kit.zip' not in z.namelist()
    for f in (args.site/'games').rglob('*'):
     if f.is_file():assert z.read('site/'+f.relative_to(args.site).as_posix())==f.read_bytes()
   # Real backup download and restore; remove only the test profile's generated save.
   with page.expect_download() as d:page.locator('#exportSaves').click()
   file=root/'save.json';d.value.save_as(file);payload=json.loads(file.read_text());assert payload['format']=='xi-game-saves-v1';assert payload['saves']['xi:game:cubiq:save']==page.evaluate("localStorage.getItem('xi:game:cubiq:save')")
   page.evaluate("localStorage.removeItem('xi:game:cubiq:save')");page.on('dialog',lambda d:d.accept());page.locator('#importSaves').set_input_files(str(file));page.get_by_text('Đã nhập bản lưu. Mở lại trò chơi để sử dụng.',exact=True).wait_for();assert page.evaluate("localStorage.getItem('xi:game:cubiq:save')")==payload['saves']['xi:game:cubiq:save']
   assert rpc(page,'DETAILS')['value']==before
   # Simulate a process termination after a partial write, then reopen offline.
   page.evaluate("""()=>{const a='xi:game:cubiq:save',b='xi:game:block-nova:best';localStorage.setItem('xi:recovery:import-v1',JSON.stringify({format:'xi-import-rollback-v1',previous:[[a,localStorage.getItem(a)],[b,localStorage.getItem(b)]]}));localStorage.setItem(a,'{"level":999}');localStorage.setItem(b,'12345')}""")
   page.close();page=ctx.new_page();page.goto(url);page.locator('#discover h2').wait_for()
   assert page.evaluate("localStorage.getItem('xi:recovery:import-v1')") is None
   assert page.evaluate("localStorage.getItem('xi:game:cubiq:save')")==payload['saves']['xi:game:cubiq:save']
   assert page.evaluate("localStorage.getItem('xi:game:block-nova:best')")==payload['saves'].get('xi:game:block-nova:best')
   assert rpc(page,'DETAILS')['value']==before
   print('PASS interrupted import journal recovery on offline reopen',flush=True)
   print('PASS origin HTTP 404, reopen, airplane-mode launches, cached ZIP byte integrity, correct-game navigation and save export/import',flush=True);b.close()
 finally:server.shutdown();server.server_close()
