"""F1.19 -> F1.20: real independent update, cache rollback and 12.2 save migration."""
import argparse,functools,http.server,threading,tempfile,shutil,zipfile,json
from pathlib import Path
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--engine',choices=['chromium','webkit'],required=True);p.add_argument('--site',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);args=p.parse_args()
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
 def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
def rpc(page,kind,id=None):
 return page.evaluate("""async ([type,id])=>{const r=await navigator.serviceWorker.ready,c=new MessageChannel();return new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(Error('worker timeout')),90000);c.port1.onmessage=e=>{clearTimeout(t);c.port1.close();resolve(e.data)};(navigator.serviceWorker.controller||r.active).postMessage({type,id},[c.port2])})}""",[kind,id])
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
   b=getattr(pw,args.engine).launch();ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce');ctx.set_default_timeout(90000)
   page=ctx.new_page();page.goto(url)
   probe=ctx.new_page();probe.goto(f'http://127.0.0.1:{server.server_port}/probe.html');probe.wait_for_function("async url=>{const r=await navigator.serviceWorker.getRegistration(url);return r?.active?.state==='activated'&&!r.installing&&!r.waiting}",arg=url,timeout=90000);page.close();page=ctx.new_page();page.goto(url);probe.close()
   page.wait_for_function('navigator.serviceWorker.controller?.state==="activated"');page.locator('#discover h2').wait_for()
   for gid in ['legacy','cubiq','block-nova','feather-fury']:assert rpc(page,'INSTALL',gid)['ok']
   gameurl=url+'games/feather-fury/index.html';oldkey='xi:game:feather-fury:ff12.2-progress';newkey='xi:game:feather-fury:ff14.1-progress'
   page.goto(gameurl);page.locator('#canvas').wait_for();page.locator('#menu').click();page.get_by_role('button',name='Về sảnh Xi',exact=True).click();page.get_by_role('button',name='Xác nhận về sảnh',exact=True).click();page.locator('#discover h2').wait_for()
   fixture=json.loads(page.evaluate('(k)=>localStorage.getItem(k)',oldkey));fixture.update(coins=12345,feathers=567);fixture['stars'][0]=3;fixture['best'][0]=777;fixture['birds'][0]['lv']=5;fixture['flock']=[0,1,2,3,4,5,6,7];oldsave=json.dumps(fixture);page.evaluate('([k,v])=>localStorage.setItem(k,v)',[oldkey,oldsave])
   old=rpc(page,'DETAILS')['value'];assert all(x['ready'] for x in old.values()) and old['feather-fury']['installedVersion']=='12.2'
   names=page.evaluate("async()=> (await caches.keys()).filter(k=>k.includes(':game:')).sort()")
   shutil.rmtree(target);shutil.copytree(args.site,target);page.evaluate('async()=>{const r=await navigator.serviceWorker.getRegistration();await r.update()}');page.wait_for_function('async()=>!!(await navigator.serviceWorker.getRegistration()).waiting',timeout=90000)
   probe=ctx.new_page();probe.goto(f'http://127.0.0.1:{server.server_port}/probe.html');assert probe.evaluate('navigator.serviceWorker.controller===null');page.close()
   probe.wait_for_function("""async url=>{const r=await navigator.serviceWorker.getRegistration(url),k=await caches.keys();return r?.active?.state==='activated'&&!r.waiting&&!r.installing&&k.includes('xi:'+url+':shell:1.20.0')&&!k.includes('xi:'+url+':shell:1.19.0')}""",arg=url,timeout=90000)
   page=ctx.new_page();page.goto(url);probe.close();page.locator('#discover h2').wait_for();old['feather-fury']['availableVersion']='14.1';old['feather-fury']['updateAvailable']=True
   assert rpc(page,'DETAILS')['value']==old;assert page.evaluate("async()=> (await caches.keys()).filter(k=>k.includes(':game:')).sort()")==names
   ctx.set_offline(True);assert not rpc(page,'UPDATE','feather-fury')['ok'];assert rpc(page,'DETAILS')['value']==old
   page.goto(gameurl);page.locator('#canvas').wait_for();assert page.locator('#xi-feather-141-layout').count()==0;assert page.locator('#coins').inner_text()=='12345';page.locator('#menu').click();page.get_by_role('button',name='Về sảnh Xi',exact=True).click();page.get_by_role('button',name='Xác nhận về sảnh',exact=True).click();page.locator('#discover h2').wait_for();preserved=page.evaluate('(k)=>localStorage.getItem(k)',oldkey)
   ctx.set_offline(False);assert rpc(page,'UPDATE','feather-fury')['ok'];now=rpc(page,'DETAILS')['value'];assert all(now[g]==old[g] for g in ['legacy','cubiq','block-nova']);assert now['feather-fury']['installedVersion']=='14.1' and not now['feather-fury']['updateAvailable'] and now['feather-fury']['backupBytes']>0
   ctx.set_offline(True);page.goto(gameurl);page.locator('#canvas').wait_for();assert page.locator('#xi-feather-141-layout').count()==1;assert page.locator('#coins').inner_text()=='12345' and page.locator('#feathers').inner_text()=='567'
   page.locator('#menu').click();page.get_by_role('button',name='Chọn 8 chim ra trận',exact=True).click();assert page.locator('[data-r]').count()==12;page.locator('[data-r="0"]').click();page.locator('[data-r="8"]').click();page.locator('#saveFlock').click();page.get_by_role('button',name='Về sảnh Xi',exact=True).click();page.get_by_role('button',name='Xác nhận về sảnh',exact=True).click();page.locator('#discover h2').wait_for()
   assert page.evaluate('(k)=>localStorage.getItem(k)',oldkey)==preserved;v=json.loads(page.evaluate('(k)=>localStorage.getItem(k)',newkey));assert v['coins']==12345 and v['feathers']==567 and v['stars'][0]==3 and v['best'][0]==777 and v['birds'][0]['lv']==5 and 8 in v['flock']
   assert page.evaluate("(k)=>!!localStorage.getItem(k)",newkey+'-backup')
   print('PASS 12.2 old offline cache, independent verified 14.1 update, migrated save and previous version preserved',flush=True);b.close()
 finally:server.shutdown();server.server_close()
