"""F1.6 -> F1.7 natural activation and offline resource/save preservation."""
import argparse, functools, http.server, shutil, tempfile, threading, zipfile
from pathlib import Path
from playwright.sync_api import sync_playwright

p=argparse.ArgumentParser()
p.add_argument('--engine',choices=['chromium','webkit'],required=True)
p.add_argument('--site',type=Path,required=True)
p.add_argument('--baseline',type=Path,required=True)
args=p.parse_args()
class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
    def end_headers(self):
        self.send_header('Cache-Control','no-store')
        super().end_headers()

def rpc(page,kind,game=None):
    return page.evaluate("""async ([type,id])=>{const r=await navigator.serviceWorker.ready;
        const ch=new MessageChannel();return new Promise((resolve,reject)=>{
        const t=setTimeout(()=>reject(Error('worker timeout')),30000);
        ch.port1.onmessage=e=>{clearTimeout(t);ch.port1.close();resolve(e.data)};
        (navigator.serviceWorker.controller||r.active).postMessage({type,id},[ch.port2])})}""",[kind,game])

with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp); target=root/'thien_thu';target.mkdir()
    with zipfile.ZipFile(args.baseline) as z:
        for item in z.infolist():
            if item.filename.startswith('site/') and not item.is_dir():
                f=target/item.filename[5:];f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(z.read(item))
    (root/'probe.html').write_text('<!doctype html><title>Activation observer</title>')
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    url=f'http://127.0.0.1:{server.server_port}/thien_thu/'
    try:
        with sync_playwright() as pw:
            b=getattr(pw,args.engine).launch()
            ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce')
            ctx.set_default_timeout(30000)
            page=ctx.new_page();page.goto(url)
            page.wait_for_function('navigator.serviceWorker.controller?.state === "activated"',timeout=60000)
            page.locator('#discover h2').wait_for()
            old_ids=['legacy','cubiq','block-nova']
            for game in old_ids: assert rpc(page,'INSTALL',game)['ok']
            old_status=rpc(page,'DETAILS')['value']
            assert all(old_status[g]['ready'] for g in old_ids)
            # Synthetic storage sentinels are deliberately never loaded as game data.
            saves={'thien-thu-v8':'legacy-sentinel','thien-thu-v8-recovery':'recovery-sentinel','xi:game:cubiq:save':'cubiq-sentinel','xi:game:block-nova:classic':'nova-sentinel'}
            page.evaluate('(s)=>Object.entries(s).forEach(([k,v])=>localStorage.setItem(k,v))',saves)
            old_caches=page.evaluate("async()=> (await caches.keys()).filter(k=>k.includes(':game:')).sort()")
            shutil.rmtree(target);shutil.copytree(args.site,target)
            page.evaluate('async()=>{const r=await navigator.serviceWorker.getRegistration();await r.update()}')
            page.wait_for_function('async()=>!!(await navigator.serviceWorker.getRegistration()).waiting',timeout=60000)
            observer=ctx.new_page();observer.goto(f'http://127.0.0.1:{server.server_port}/probe.html')
            assert observer.evaluate('navigator.serviceWorker.controller === null')
            page.close()
            observer.wait_for_function("""async url=>{const r=await navigator.serviceWorker.getRegistration(url);const keys=await caches.keys();return r?.active?.state==='activated'&&!r.waiting&&!r.installing&&keys.includes('xi:'+url+':shell:1.7.0')&&!keys.includes('xi:'+url+':shell:1.6.0')}""",arg=url,timeout=60000)
            page=ctx.new_page();page.goto(url);observer.close()
            page.wait_for_function('navigator.serviceWorker.controller?.state === "activated"')
            page.locator('#discover h2').wait_for()
            assert page.locator('#featured article').count()==4
            assert page.evaluate('(keys)=>Object.fromEntries(keys.map(k=>[k,localStorage.getItem(k)]))',list(saves))==saves
            assert page.evaluate("async()=> (await caches.keys()).filter(k=>k.includes(':game:')).sort()")==old_caches
            new_status=rpc(page,'DETAILS')['value']
            assert all(new_status[g]==old_status[g] for g in old_ids)
            assert not new_status['feather-fury']['ready']
            assert rpc(page,'INSTALL','feather-fury')['ok']
            ctx.set_offline(True)
            page.goto(url+'games/feather-fury/index.html');page.locator('#canvas').wait_for()
            page.locator('#menu').click();page.get_by_role('button',name='Về sảnh Xi',exact=True).click();page.get_by_role('button',name='Xác nhận về sảnh').click()
            page.locator('#discover h2').wait_for()
            assert page.evaluate("!!localStorage.getItem('xi:game:feather-fury:ff10-progress')")
            assert page.evaluate('(keys)=>Object.fromEntries(keys.map(k=>[k,localStorage.getItem(k)]))',list(saves))==saves
            print('PASS F1.6 to F1.7: natural activation, unchanged three-game caches and save keys, Feather Fury offline',flush=True)
            b.close()
    finally:
        server.shutdown();server.server_close()
