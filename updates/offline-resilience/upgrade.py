"""Real F1.16 -> F1.17: preserve caches and preferences, no forced activation."""
import argparse, functools, http.server, shutil, tempfile, threading, zipfile, json
from pathlib import Path
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--engine',choices=['chromium','webkit'],required=True);p.add_argument('--site',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);args=p.parse_args()
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
 def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
def rpc(page,kind,id=None):
 return page.evaluate("""async ([type,id])=>{const r=await navigator.serviceWorker.ready,c=new MessageChannel();return new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(Error('worker timeout')),30000);c.port1.onmessage=e=>{clearTimeout(t);c.port1.close();resolve(e.data)};(navigator.serviceWorker.controller||r.active).postMessage({type,id},[c.port2])})}""",[kind,id])
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);target=root/'thien_thu';target.mkdir()
 with zipfile.ZipFile(args.baseline) as z:
  for n in z.namelist():
   if n.startswith('site/') and not n.endswith('/'):
    f=target/n[5:];f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(z.read(n))
 (root/'probe.html').write_text('<!doctype html><title>Probe</title>')
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/thien_thu/'
 try:
  with sync_playwright() as pw:
   browser=getattr(pw,args.engine).launch();ctx=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce');ctx.set_default_timeout(30000);page=ctx.new_page();page.goto(url)
   probe=ctx.new_page();probe.goto(f'http://127.0.0.1:{server.server_port}/probe.html');probe.wait_for_function("async url=>{const r=await navigator.serviceWorker.getRegistration(url);return r?.active?.state==='activated'&&!r.installing&&!r.waiting}",arg=url,timeout=60000);page.close();page=ctx.new_page();page.goto(url);probe.close()
   page.wait_for_function('navigator.serviceWorker.controller?.state==="activated"');page.locator('#discover h2').wait_for()
   for g in ['legacy','cubiq','block-nova','feather-fury']:assert rpc(page,'INSTALL',g)['ok']
   old=rpc(page,'DETAILS')['value'];assert all(d['ready'] for d in old.values())
   saves={'thien-thu-v8':'legacy-fixture','xi:game:cubiq:save':'cubiq-fixture','xi:ui:appearance-v1':json.dumps({'theme':'jade','compact':True}),'xi:ui:recent-v1':'["cubiq"]'}
   page.evaluate('(s)=>Object.entries(s).forEach(([k,v])=>localStorage.setItem(k,v))',saves)
   names=page.evaluate("async()=> (await caches.keys()).filter(k=>k.includes(':game:')).sort()")
   shutil.rmtree(target);shutil.copytree(args.site,target);page.evaluate('async()=>{const r=await navigator.serviceWorker.getRegistration();await r.update()}');page.wait_for_function('async()=>!!(await navigator.serviceWorker.getRegistration()).waiting',timeout=60000)
   probe=ctx.new_page();probe.goto(f'http://127.0.0.1:{server.server_port}/probe.html');assert probe.evaluate('navigator.serviceWorker.controller===null');page.close()
   probe.wait_for_function("""async url=>{const r=await navigator.serviceWorker.getRegistration(url),k=await caches.keys();return r?.active?.state==='activated'&&!r.waiting&&!r.installing&&k.includes('xi:'+url+':shell:1.17.0')&&!k.includes('xi:'+url+':shell:1.16.0')}""",arg=url,timeout=60000)
   page=ctx.new_page();page.goto(url);probe.close();page.locator('#discover h2').wait_for();assert page.locator('html').get_attribute('data-theme')=='jade';assert rpc(page,'DETAILS')['value']==old
   assert page.evaluate('(keys)=>Object.fromEntries(keys.map(k=>[k,localStorage.getItem(k)]))',list(saves))==saves
   assert page.evaluate("async()=> (await caches.keys()).filter(k=>k.includes(':game:')).sort()")==names
   ctx.set_offline(True);page.reload();page.locator('#discover h2').wait_for();page.get_by_role('button',name='Thư viện',exact=True).click();page.locator('[data-library-filter=ready]').click();page.wait_for_function("document.querySelectorAll('#libraryGames article').length===4");page.get_by_role('button',name='Hoạt động',exact=True).click();page.locator('#activityRecent').get_by_text('CUBIQ',exact=True).wait_for();page.get_by_role('button',name='Cài đặt',exact=True).click();assert page.locator('#themeChoices [data-theme=jade]').get_attribute('aria-pressed')=='true'
   print('PASS F1.16 -> F1.17: all game caches, save keys, preferences, recent play and secondary tabs offline',flush=True)
   # Verify toggle persisted during reload and restored when enabled, while offline.
   assert page.locator('html').get_attribute('data-glass')=='on'
   page.locator('#glassEnabled').uncheck()
   assert page.locator('html').get_attribute('data-glass')=='off'
   assert page.evaluate("localStorage.getItem('xi:ui:glass-v1')")=='0'
   page.reload();page.locator('#discover h2').wait_for()
   assert page.locator('html').get_attribute('data-glass')=='off'
   page.get_by_role('button',name='Cài đặt',exact=True).click()
   assert not page.locator('#glassEnabled').is_checked()
   page.locator('#glassEnabled').check()
   assert page.locator('html').get_attribute('data-glass')=='on'
   assert page.locator('nav').evaluate("e=>getComputedStyle(e,'::before').transitionDuration")=='0s'
   assert page.evaluate("localStorage.getItem('xi:ui:glass-v1')")=='1'
   assert page.evaluate("document.documentElement.scrollWidth<=innerWidth")
   print('PASS offline glass preference persistence, reduced motion and nav layout',flush=True)
   page.locator('#glassOpacity').evaluate("e=>{e.value='20';e.dispatchEvent(new Event('input'));e.dispatchEvent(new Event('change'))}")
   page.locator('#wallStrength').evaluate("e=>{e.value='12';e.dispatchEvent(new Event('input'));e.dispatchEvent(new Event('change'))}")
   assert page.locator('#glassValue').inner_text()=='20%' and page.locator('#wallValue').inner_text()=='12%'
   for width,height in [(844,390),(1024,768),(768,1024),(390,844),(932,430),(430,932),(1366,768),(1920,1080)]:
    page.set_viewport_size({'width':width,'height':height})
    for label in ['Khám phá','Thư viện','Hoạt động','Cài đặt']:
     page.get_by_role('button',name=label,exact=True).click()
     assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,height,label)
     assert page.locator('nav button[aria-current=page]').inner_text()==label
     if width>=700 and width>height:
      nav=page.locator('nav').bounding_box();body=page.locator('.content').bounding_box();assert nav['x']+nav['width']<=body['x']+1,(width,height,nav,body)
   page.reload();page.locator('#discover h2').wait_for();page.get_by_role('button',name='Cài đặt',exact=True).click()
   assert page.locator('#glassValue').inner_text()=='20%' and page.locator('#wallValue').inner_text()=='12%'
   assert json.loads(page.evaluate("localStorage.getItem('xi:ui:surface-v1')"))=={'glass':20,'wall':12}
   assert rpc(page,'DETAILS')['value']==old
   assert page.evaluate('(keys)=>Object.fromEntries(keys.map(k=>[k,localStorage.getItem(k)]))',list(saves))==saves
   print('PASS real offline live rotation, surface tuning persistence and unchanged game saves',flush=True)
   page.locator('#motionEnabled').uncheck()
   assert page.locator('html').get_attribute('data-motion')=='off'
   assert page.evaluate("localStorage.getItem('xi:ui:motion-v1')")=='0'
   page.reload();page.locator('#discover h2').wait_for();assert page.locator('html').get_attribute('data-motion')=='off'
   page.get_by_role('button',name='Thư viện',exact=True).click()
   page.get_by_role('button',name='Gỡ tài nguyên',exact=True).first.click()
   dialog=page.locator('#resourceDialog');assert dialog.is_visible()
   for width,height in [(280,650),(844,320),(390,844),(1024,768)]:
    page.set_viewport_size({'width':width,'height':height});box=dialog.bounding_box()
    assert box['x']>=0 and box['y']>=0 and box['x']+box['width']<=width+1 and box['y']+box['height']<=height+1,(width,height,box)
   page.get_by_role('button',name='Hủy',exact=True).click();dialog.wait_for(state='hidden')
   assert rpc(page,'DETAILS')['value']==old
   assert page.evaluate('(keys)=>Object.fromEntries(keys.map(k=>[k,localStorage.getItem(k)]))',list(saves))==saves
   page.get_by_role('button',name='Cài đặt',exact=True).click();page.locator('#motionEnabled').check()
   assert page.evaluate("localStorage.getItem('xi:ui:motion-v1')")=='1'
   print('PASS offline modal cancellation, rotation and motion preference',flush=True)
   page.get_by_role('button',name='Khám phá',exact=True).click()
   page.locator('#featured [data-favorite=cubiq]').click()
   assert page.locator('#featured article h3').first.inner_text()=='CUBIQ'
   page.locator('[data-collection=favorite]').click();assert page.locator('#featured article').count()==1
   page.get_by_role('button',name='Cài đặt',exact=True).click()
   page.locator('#themeChoices [data-theme=jade]').click();page.locator('[data-performance=light]').click()
   page.locator('[data-save-slot="1"]').click();page.locator('#themeChoices [data-theme=pearl]').click();page.locator('[data-performance=premium]').click();page.locator('[data-save-slot="2"]').click()
   page.reload();page.locator('#discover h2').wait_for();assert page.locator('#featured article h3').first.inner_text()=='CUBIQ'
   page.get_by_role('button',name='Cài đặt',exact=True).click();page.locator('[data-load-slot="1"]').click()
   assert page.locator('html').get_attribute('data-theme')=='jade' and page.locator('html').get_attribute('data-glass')=='off'
   page.locator('[data-load-slot="2"]').click();assert page.locator('html').get_attribute('data-theme')=='pearl'
   assert rpc(page,'DETAILS')['value']==old
   assert page.evaluate('(keys)=>Object.fromEntries(keys.map(k=>[k,localStorage.getItem(k)]))',[k for k in saves if not k.startswith('xi:ui:')])=={k:v for k,v in saves.items() if not k.startswith('xi:ui:')}
   print('PASS offline favorites and two saved appearance profiles',flush=True)
   page.locator('#ambientEnabled').uncheck()
   assert page.locator('html').get_attribute('data-ambient')=='off'
   assert page.evaluate("localStorage.getItem('xi:ui:ambient-v1')")=='0'
   page.reload();page.locator('#discover h2').wait_for();assert page.locator('html').get_attribute('data-ambient')=='off'
   page.locator('[data-collection=recent]').click()
   assert page.locator('#featured article').count()==1
   page.locator('#featured article').first.get_by_role('button',name='Chi tiết',exact=True).click()
   d=page.locator('#gameDetail');assert d.is_visible();assert page.locator('#gameDetailTitle').inner_text()=='CUBIQ'
   for width,height in [(280,650),(844,320),(390,844),(1024,768)]:
    page.set_viewport_size({'width':width,'height':height});box=d.bounding_box()
    assert box['x']>=0 and box['y']>=0 and box['x']+box['width']<=width+1 and box['y']+box['height']<=height+1,(width,height,box)
   page.keyboard.press('Escape');d.wait_for(state='hidden')
   page.locator('[data-collection=updates]').click();assert page.locator('#featured article').count()==0
   assert rpc(page,'DETAILS')['value']==old
   assert page.evaluate('(keys)=>Object.fromEntries(keys.map(k=>[k,localStorage.getItem(k)]))',[k for k in saves if not k.startswith('xi:ui:')])=={k:v for k,v in saves.items() if not k.startswith('xi:ui:')}
   print('PASS offline detail, recent/update filters, rotation and ambient persistence',flush=True)
   ctx.close()
   fresh=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,service_workers='block')
   test=fresh.new_page();test.route('**/hub.js',lambda route:route.abort());test.goto(url);assert test.locator('#shell').is_hidden();assert test.locator('#intro').is_visible();assert test.get_by_text('Bỏ qua',exact=True).count()==0
   test.unroute('**/hub.js');test.reload();test.get_by_role('button',name='Vào sảnh Xi Universe').click();assert test.locator('#intro').is_hidden();assert test.locator('#shell').is_visible()
   print('PASS initial paint gate and tap-to-dismiss',flush=True);browser.close()
 finally:server.shutdown();server.server_close()
