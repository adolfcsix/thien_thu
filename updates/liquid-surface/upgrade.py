"""Real F1.10 -> F1.18: preserve caches and preferences, no forced activation."""
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
   probe.wait_for_function("""async url=>{const r=await navigator.serviceWorker.getRegistration(url),k=await caches.keys();return r?.active?.state==='activated'&&!r.waiting&&!r.installing&&k.includes('xi:'+url+':shell:1.18.0')&&!k.includes('xi:'+url+':shell:1.10.0')}""",arg=url,timeout=60000)
   page=ctx.new_page();page.goto(url);probe.close();page.locator('#discover h2').wait_for();assert page.locator('html').get_attribute('data-theme')=='jade';assert rpc(page,'DETAILS')['value']==old
   assert page.evaluate('(keys)=>Object.fromEntries(keys.map(k=>[k,localStorage.getItem(k)]))',list(saves))==saves
   assert page.evaluate("async()=> (await caches.keys()).filter(k=>k.includes(':game:')).sort()")==names
   ctx.set_offline(True);page.reload();page.locator('#discover h2').wait_for();page.get_by_role('button',name='Thư viện',exact=True).click();page.locator('[data-library-filter=ready]').click();page.wait_for_function("document.querySelectorAll('#libraryGames article').length===4");page.get_by_role('button',name='Hoạt động',exact=True).click();page.locator('#activityRecent').get_by_text('CUBIQ',exact=True).wait_for();page.get_by_role('button',name='Cài đặt',exact=True).click();assert page.locator('#themeChoices [data-theme=jade]').get_attribute('aria-pressed')=='true'
   print('PASS F1.10 -> F1.18: all game caches, save keys, preferences, recent play and secondary tabs offline',flush=True)
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
   ctx.close()
   fresh=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,service_workers='block')
   test=fresh.new_page();test.route('**/hub.js',lambda route:route.abort());test.goto(url);assert test.locator('#shell').is_hidden();assert test.locator('#intro').is_visible();assert test.get_by_text('Bỏ qua',exact=True).count()==0
   test.unroute('**/hub.js');test.reload();test.get_by_role('button',name='Vào sảnh Xi Universe').click();assert test.locator('#intro').is_hidden();assert test.locator('#shell').is_visible()
   print('PASS initial paint gate and tap-to-dismiss',flush=True);browser.close()
 finally:server.shutdown();server.server_close()
