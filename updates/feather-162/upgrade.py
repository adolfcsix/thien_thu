"""F1.25 -> F1.26: real independent update, offline fallback and 14.1 save migration."""
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
   def acquire(page,version):
    import time
    expected={'version':version,'scope':url,'shell':'xi:'+url+':shell:'+version};deadline=time.monotonic()+120;next_nav=time.monotonic()+5
    while time.monotonic()<deadline:
     result=page.evaluate('''()=>{const w=navigator.serviceWorker.controller;if(!w)return null;return new Promise(resolve=>{const c=new MessageChannel(),t=setTimeout(()=>{c.port1.close();resolve(null)},5000);c.port1.onmessage=e=>{clearTimeout(t);c.port1.close();resolve(e.data?.ok?e.data.value:null)};w.postMessage({type:'VERSION'},[c.port2])})}''')
     if result==expected:return
     active=page.evaluate('''async()=>{const r=await navigator.serviceWorker.getRegistration();return r?.active?.state==='activated'&&!r.waiting&&!r.installing}''')
     if active and time.monotonic()>=next_nav:page.goto(url+'index.html?xi-release='+version,wait_until='domcontentloaded');next_nav=time.monotonic()+10
     page.wait_for_timeout(500)
    raise AssertionError(('no exact controlling worker',version,result))
   page=ctx.new_page();page.bring_to_front();page.goto(url,wait_until='domcontentloaded');acquire(page,'1.25.0');page.locator('#discover h2').wait_for()
   for gid in ['legacy','cubiq','block-nova','feather-fury','ky-vien','garden-through-time','huyen-anh']:assert rpc(page,'INSTALL',gid)['ok']
   gameurl=url+'games/feather-fury/index.html';oldkey='xi:game:feather-fury:ff14.1-progress';newkey='xi:game:feather-fury:ff16.2-progress'
   page.goto(gameurl);page.locator('#canvas').wait_for();page.locator('#menu').click();page.get_by_role('button',name='Về sảnh Xi',exact=True).click();page.get_by_role('button',name='Xác nhận về sảnh',exact=True).click();page.locator('#discover h2').wait_for()
   fixture=json.loads(page.evaluate('(k)=>localStorage.getItem(k)',oldkey));fixture.update(coins=12345,feathers=567);fixture['stars'][0]=3;fixture['best'][0]=777;fixture['birds'][0]['lv']=5;fixture['flock']=[0,1,2,3,4,5,6,7];oldsave=json.dumps(fixture);page.evaluate('([k,v])=>localStorage.setItem(k,v)',[oldkey,oldsave])
   old=rpc(page,'DETAILS')['value'];assert all(x['ready'] for x in old.values()) and old['feather-fury']['installedVersion']=='14.1'
   names=page.evaluate("async()=> (await caches.keys()).filter(k=>k.includes(':game:')).sort()")
   shutil.rmtree(target);shutil.copytree(args.site,target);page.evaluate('async()=>{const r=await navigator.serviceWorker.getRegistration();await r.update()}');page.wait_for_function('async()=>!!(await navigator.serviceWorker.getRegistration()).waiting',timeout=90000)
   probe=ctx.new_page();probe.goto(f'http://127.0.0.1:{server.server_port}/probe.html');assert probe.evaluate('navigator.serviceWorker.controller===null');page.close()
   probe.wait_for_function("""async url=>{const r=await navigator.serviceWorker.getRegistration(url),k=await caches.keys();return r?.active?.state==='activated'&&!r.waiting&&!r.installing&&k.includes('xi:'+url+':shell:1.26.0')&&!k.includes('xi:'+url+':shell:1.25.0')}""",arg=url,timeout=90000)
   page=ctx.new_page();page.bring_to_front();page.goto(url,wait_until='domcontentloaded');probe.close();acquire(page,'1.26.0');page.locator('#discover h2').wait_for();old['feather-fury']['availableVersion']='16.2';old['feather-fury']['updateAvailable']=True
   assert rpc(page,'DETAILS')['value']==old;assert page.evaluate("async()=> (await caches.keys()).filter(k=>k.includes(':game:')).sort()")==names
   ctx.set_offline(True);assert not rpc(page,'UPDATE','feather-fury')['ok'];assert rpc(page,'DETAILS')['value']==old
   page.goto(gameurl);page.locator('#canvas').wait_for();assert page.locator('#xi-gesture-162').count()==0;assert page.locator('#coins').inner_text()=='12345';page.locator('#menu').click();page.get_by_role('button',name='Về sảnh Xi',exact=True).click();page.get_by_role('button',name='Xác nhận về sảnh',exact=True).click();page.locator('#discover h2').wait_for();preserved=page.evaluate('(k)=>localStorage.getItem(k)',oldkey)
   ctx.set_offline(False);assert rpc(page,'UPDATE','feather-fury')['ok'];now=rpc(page,'DETAILS')['value'];assert all(now[g]==old[g] for g in ['legacy','cubiq','block-nova','ky-vien','garden-through-time','huyen-anh']);assert now['feather-fury']['installedVersion']=='16.2' and not now['feather-fury']['updateAvailable'] and now['feather-fury']['backupBytes']>0
   ctx.set_offline(True);page.goto(gameurl);page.locator('#canvas').wait_for();assert page.locator('#xi-gesture-162').count()==1;assert page.locator('#coins').inner_text()=='12345' and page.locator('#feathers').inner_text()=='567'
   page.locator('#menu').click();page.get_by_role('button',name='Chọn 8 chim ra trận',exact=True).click();assert page.locator('[data-r]').count()==24;page.locator('[data-r="0"]').click();page.locator('[data-r="8"]').click();page.locator('#saveFlock').click();page.get_by_role('button',name='Về sảnh Xi',exact=True).click();page.get_by_role('button',name='Xác nhận về sảnh',exact=True).click();page.locator('#discover h2').wait_for()
   assert page.evaluate('(k)=>localStorage.getItem(k)',oldkey)==preserved;v=json.loads(page.evaluate('(k)=>localStorage.getItem(k)',newkey));assert v['schema']==18 and len(v['birds'])==24 and len(v['stars'])==210 and v['coins']==12345 and v['feathers']==567 and v['stars'][0]==3 and v['best'][0]==777 and v['birds'][0]['lv']==5 and 8 in v['flock']
   backup=page.evaluate('(k)=>localStorage.getItem(k)',newkey+'-backup')
   assert backup, '16.2 must seed a backup during the first migration/save'
   recovered=json.loads(backup)
   assert recovered['schema']==18 and recovered['coins']==12345 and recovered['feathers']==567 and recovered['stars'][0]==3 and recovered['birds'][0]['lv']==5
   # Corrupt the test profile's primary; verify actual offline recovery without
   # touching the previous release's save or the six other games.
   page.evaluate('(k)=>localStorage.setItem(k,\'{"schema":18}\')',newkey)
   page.goto(gameurl);page.locator('#canvas').wait_for()
   assert page.locator('#coins').inner_text()=='12345' and page.locator('#feathers').inner_text()=='567'
   page.locator('#menu').click();page.get_by_role('button',name='Về sảnh Xi',exact=True).click();page.get_by_role('button',name='Xác nhận về sảnh',exact=True).click();page.locator('#discover h2').wait_for()
   assert json.loads(page.evaluate('(k)=>localStorage.getItem(k)',newkey))['coins']==12345
   assert page.evaluate('(k)=>localStorage.getItem(k)',newkey+'-backup')==backup
   assert page.evaluate('(k)=>localStorage.getItem(k)',oldkey)==preserved
   assert rpc(page,'DETAILS')['value']==now
   print('PASS first-save backup, valid recovery copy and offline corrupt-primary recovery',flush=True)
   print('PASS 14.1 old offline cache, independent verified 16.2 update, migrated save and previous version preserved',flush=True);b.close()
 finally:server.shutdown();server.server_close()
