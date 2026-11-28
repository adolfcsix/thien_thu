"""Real-browser F1.7 -> F1.20 migration, independent module updates and settings persistence."""
import argparse, functools, http.server, shutil, tempfile, threading, zipfile, json
from pathlib import Path
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--engine',choices=['chromium','webkit'],required=True);p.add_argument('--site',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);args=p.parse_args()
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
def rpc(page,kind,id=None):
 return page.evaluate("""async ([type,id])=>{const r=await navigator.serviceWorker.ready;const c=new MessageChannel();return new Promise((res,rej)=>{const t=setTimeout(()=>rej(Error('worker timeout')),30000);c.port1.onmessage=e=>{clearTimeout(t);c.port1.close();res(e.data)};(navigator.serviceWorker.controller||r.active).postMessage({type,id},[c.port2])})}""",[kind,id])
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);target=root/'thien_thu';target.mkdir()
 with zipfile.ZipFile(args.baseline) as z:
  for n in z.namelist():
   if n.startswith('site/') and not n.endswith('/'):
    f=target/n[5:];f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(z.read(n))
 (root/'probe.html').write_text('<!doctype html><title>Activation observer</title>')
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/thien_thu/'
 try:
  with sync_playwright() as pw:
   b=getattr(pw,args.engine).launch();ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce');ctx.set_default_timeout(30000);page=ctx.new_page();page.goto(url)
   # Observe first install from an unscoped page, avoiding competing reloads
   # from hub.js controllerchange and Playwright's explicit page.reload().
   initial=ctx.new_page();initial.goto(f'http://127.0.0.1:{server.server_port}/probe.html')
   initial.wait_for_function("async url=>{const r=await navigator.serviceWorker.getRegistration(url);return r?.active?.state==='activated'&&!r.installing&&!r.waiting}",arg=url,timeout=60000)
   page.close();page=ctx.new_page();page.goto(url);initial.close()
   page.wait_for_function('navigator.serviceWorker.controller?.state === "activated"',timeout=60000);page.locator('#discover h2').wait_for()
   ids=['legacy','cubiq','block-nova','feather-fury'];old=['9.0','1.0','1.0','10.1'];new=['9.2','1.2','1.2','14.1']
   for g in ids:assert rpc(page,'INSTALL',g)['ok']
   saves={'thien-thu-v8':'legacy-sentinel','thien-thu-v8-recovery':'recovery-sentinel','xi:game:cubiq:save':'cubiq-sentinel','xi:game:block-nova:classic':'nova-sentinel','xi:game:feather-fury:ff10-progress':'feather-sentinel'}
   page.evaluate('(s)=>Object.entries(s).forEach(([k,v])=>localStorage.setItem(k,v))',saves)
   def check_saves():assert page.evaluate('(keys)=>Object.fromEntries(keys.map(k=>[k,localStorage.getItem(k)]))',list(saves))==saves
   shutil.rmtree(target);shutil.copytree(args.site,target);page.evaluate('async()=>{const r=await navigator.serviceWorker.getRegistration();await r.update()}');page.wait_for_function('async()=>!!(await navigator.serviceWorker.getRegistration()).waiting',timeout=60000)
   probe=ctx.new_page();probe.goto(f'http://127.0.0.1:{server.server_port}/probe.html');assert probe.evaluate('navigator.serviceWorker.controller===null');page.close()
   probe.wait_for_function("""async url=>{const r=await navigator.serviceWorker.getRegistration(url),k=await caches.keys();return r?.active?.state==='activated'&&!r.waiting&&!r.installing&&k.includes('xi:'+url+':shell:1.20.0')&&!k.includes('xi:'+url+':shell:1.7.0')}""",arg=url,timeout=60000)
   page=ctx.new_page();page.goto(url);probe.close();page.wait_for_function('navigator.serviceWorker.controller?.state==="activated"');page.locator('#discover h2').wait_for();check_saves();d=rpc(page,'DETAILS')['value']
   assert all(d[g]['ready'] and d[g]['installedVersion']==o and d[g]['availableVersion']==n and d[g]['updateAvailable'] for g,o,n in zip(ids,old,new)),d
   # Failure while offline must not discard previous playable resources.
   ctx.set_offline(True);assert not rpc(page,'UPDATE','cubiq')['ok'];check_saves();assert rpc(page,'DETAILS')['value']['cubiq']['installedVersion']=='1.0';ctx.set_offline(False)
   for g,n in zip(ids,new):
    assert rpc(page,'UPDATE',g)['ok'];check_saves();d=rpc(page,'DETAILS')['value'][g];assert d['installedVersion']==n and d['backupBytes']>0 and not d['updateAvailable'],d
   # The fixture values are intentionally non-game sentinel data; remove only these test keys before testing real saves.
   page.evaluate('(keys)=>keys.forEach(k=>localStorage.removeItem(k))',list(saves))
   page.get_by_role('button',name='Cài đặt',exact=True).click();page.locator('#themeChoices [data-theme=jade]').click();page.locator('#compactCards').check();page.reload();page.locator('html[data-theme=jade]').wait_for(state='attached');assert page.locator('html').get_attribute('data-theme')=='jade';assert page.locator('html').get_attribute('data-compact')=='true'
   page.get_by_role('button',name='Khám phá',exact=True).click();ctx.set_offline(True);page.locator('#featured article').filter(has=page.locator('h3',has_text='CUBIQ')).get_by_role('button',name='Chơi ngay',exact=True).click();page.wait_for_url('**/games/cubiq/index.html');page.locator('[data-act=menu]').click();page.get_by_role('button',name='?',exact=True).click();page.locator('#xi-private-pin').fill('040804');page.get_by_role('button',name='Mở khóa',exact=True).click();page.locator('#xi-private-unlocked').fill('40');page.locator('#xi-private-jump').fill('20');page.locator('#xi-private-assist').fill('1');page.get_by_role('button',name='Áp dụng').click();assert page.locator('[data-el=level]').inner_text()=='Màn 20';assert page.locator('[data-el=hearts]').inner_text()=='∞';page.locator('[data-act=menu]').click();page.get_by_role('button',name='Về sảnh Xi').click();page.locator('#discover h2').wait_for();page.locator('html[data-theme=jade]').wait_for(state='attached');assert page.locator('html').get_attribute('data-theme')=='jade';assert page.locator('#recentGames .recent-tile').first.get_by_text('CUBIQ',exact=True).is_visible();assert json.loads(page.evaluate("localStorage.getItem('xi:ui:recent-v1')"))[0]=='cubiq'
   assert json.loads(page.evaluate("localStorage.getItem('xi:game:cubiq:save')"))['level']==20
   print('PASS F1.7 to F1.20 natural activation, four versioned updates, failed offline update, unchanged save keys, real offline CUBIQ and persistent appearance',flush=True);b.close()
 finally:server.shutdown();server.server_close()
