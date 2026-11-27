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
   print('PASS origin HTTP 404, reopen, airplane-mode launches, cached ZIP byte integrity, correct-game navigation and save export/import',flush=True);b.close()
 finally:server.shutdown();server.server_close()
