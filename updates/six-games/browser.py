"""Actual F1.21 site: six titles, two independent downloads and offline return."""
import argparse,functools,http.server,threading,tempfile,shutil,json,zipfile
from pathlib import Path
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--engine',required=True,choices=['chromium','webkit']);p.add_argument('--site',type=Path,required=True);a=p.parse_args()
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
def rpc(page,kind,gid=None):
 return page.evaluate("""([type,id])=>new Promise((resolve,reject)=>{let c=new MessageChannel(),t=setTimeout(()=>reject(Error('worker timeout')),90000);c.port1.onmessage=e=>{clearTimeout(t);c.port1.close();resolve(e.data)};navigator.serviceWorker.controller.postMessage({type,id},[c.port2])})""",[kind,gid])
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);shutil.copytree(a.site,root/'thien_thu')
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=tmp));threading.Thread(target=server.serve_forever,daemon=True).start()
 url=f'http://127.0.0.1:{server.server_port}/thien_thu/'
 try:
  with sync_playwright() as pw:
   b=getattr(pw,a.engine).launch()
   ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce')
   ctx.set_default_timeout(90000);errors=[]
   ctx.on('page',lambda pg:pg.on('pageerror',lambda e:errors.append(str(e))))
   (root/'activation-probe.html').write_text('<!doctype html><title>Activation observer</title>',encoding='utf-8')
   page=ctx.new_page();page.goto(url,wait_until='domcontentloaded')
   observer=ctx.new_page();observer.goto(f'http://127.0.0.1:{server.server_port}/activation-probe.html')
   assert observer.evaluate('navigator.serviceWorker.controller===null')
   try:
    observer.wait_for_function("""async url=>{const r=await navigator.serviceWorker.getRegistration(url);const keys=await caches.keys();return r?.active?.state==='activated'&&!r.installing&&!r.waiting&&keys.includes('xi:'+url+':shell:1.21.0')}""",arg=url,timeout=90000)
   except Exception:
    print('WORKER DIAGNOSTICS',observer.evaluate("""async url=>{const r=await navigator.serviceWorker.getRegistration(url);return {active:r?.active?.state,installing:r?.installing?.state,waiting:r?.waiting?.state,caches:await caches.keys()}}""",url),errors,flush=True)
    raise
   page.close()
   page=ctx.new_page();page.on('dialog',lambda d:d.accept())
   page.goto(url,wait_until='domcontentloaded');observer.close()
   page.wait_for_function('navigator.serviceWorker.controller?.state==="activated"')
   page.wait_for_function("globalThis.XI_CATALOG?.HUB_VERSION==='1.21.0'")
   page.locator('#discover h2').wait_for()
   assert page.evaluate('XI_CATALOG.HUB_VERSION')=='1.21.0'
   ids=['legacy','cubiq','block-nova','feather-fury','ky-vien','garden-through-time']
   assert page.evaluate('XI_CATALOG.released.map(g=>g.id)')==ids
   assert page.locator('#featured article').count()==6
   for gid in ids: assert rpc(page,'INSTALL',gid)['ok'],gid
   state=rpc(page,'DETAILS')['value'];assert all(state[g]['ready'] for g in ids)
   assert state['ky-vien']['installedVersion']=='1.0' and state['garden-through-time']['installedVersion']=='0.79.2'
   page.evaluate("""()=>{localStorage.setItem('ky-vien-theme','light');localStorage.setItem('garden-audio-v1',JSON.stringify({music:0,effects:0,muted:true}))}""")
   ctx.set_offline(True)
   for gid in ids[-2:]:
    page.goto(url+'games/'+gid+'/index.html');page.locator('#xi-return').wait_for()
    if gid=='ky-vien':page.locator('#board').wait_for()
    else:page.locator('#continueAdventure').wait_for()
    assert page.locator('meta[name=viewport]').get_attribute('content').find('user-scalable=no')>=0
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+2'),gid
    if gid=='ky-vien':
     assert page.evaluate("localStorage.getItem('xi:game:ky-vien:ky-vien-theme')")=='light'
     page.locator('#themeToggle').click()
    else:
     assert page.evaluate("!!localStorage.getItem('xi:game:garden-through-time:garden-audio-v1')")
     page.locator('#settingsToggle').click();page.locator('#settingsPanel').wait_for()
     page.locator('#settingsToggle').click();page.locator('#settingsPanel').wait_for(state='hidden')
     page.locator('#continueAdventure').click();page.locator('#fight').click()
     page.locator('#board').wait_for()
     assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+2'),gid
    page.locator('#xi-return').click();page.locator('#discover h2').wait_for()
   assert page.evaluate("localStorage.getItem('ky-vien-theme')")=='light'
   assert page.evaluate("!!localStorage.getItem('xi:game:ky-vien:ky-vien-v1')")
   assert rpc(page,'DETAILS')['value']==state
   assert rpc(page,'REMOVE','garden-through-time')['ok']
   removed=rpc(page,'DETAILS')['value'];assert not removed['garden-through-time']['ready'] and all(removed[g]==state[g] for g in ids[:-1])
   assert not rpc(page,'INSTALL','garden-through-time')['ok']
   ctx.set_offline(False);assert rpc(page,'INSTALL','garden-through-time')['ok']
   assert all(rpc(page,'DETAILS')['value'][g]['ready'] for g in ids)
   # Exercise real import UI and verify rejected data cannot replace saved values.
   page.get_by_role('button',name='Cài đặt',exact=True).click()
   theme='xi:game:ky-vien:ky-vien-theme';archive='xi:game:ky-vien:kv-archive-v1'
   def import_saves(values):
    payload=json.dumps({'format':'xi-game-saves-v1','saves':values}).encode('utf-8')
    page.locator('#importSaves').set_input_files({'name':'fixture.json','mimeType':'application/json','buffer':payload})
   import_saves({theme:'light',archive:'[]'})
   page.get_by_text('Đã nhập bản lưu. Mở lại trò chơi để sử dụng.',exact=True).wait_for()
   assert page.evaluate('([a,b])=>[localStorage.getItem(a),localStorage.getItem(b)]',[theme,archive])==['light','[]']
   import_saves({theme:'invalid'})
   page.get_by_text('Không thể nhập bản lưu:',exact=False).wait_for()
   assert page.evaluate('(k)=>localStorage.getItem(k)',theme)=='light'
   assert not errors,errors
   b.close()
  print('PASS six-game discovery, actual SW install, offline launch/return, legacy preference copy, independent remove/reinstall',flush=True)
 finally:server.shutdown();server.server_close()
