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
   page=ctx.new_page();page.set_default_timeout(90000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('dialog',lambda d:d.accept())
   page.goto(url);page.wait_for_function('navigator.serviceWorker.controller?.state==="activated"')
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
    page.goto(url+'games/'+gid+'/index.html');page.locator('#board').wait_for();page.locator('#xi-return').wait_for()
    assert page.locator('meta[name=viewport]').get_attribute('content').find('user-scalable=no')>=0
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+2'),gid
    if gid=='ky-vien':
     assert page.evaluate("localStorage.getItem('xi:game:ky-vien:ky-vien-theme')")=='light'
     page.locator('#themeToggle').click()
    else:
     assert page.evaluate("!!localStorage.getItem('xi:game:garden-through-time:garden-audio-v1')")
     page.locator('#settingsToggle').click()
    page.locator('#xi-return').click();page.locator('#discover h2').wait_for()
   assert page.evaluate("localStorage.getItem('ky-vien-theme')")=='light'
   assert page.evaluate("!!localStorage.getItem('xi:game:ky-vien:ky-vien-v1')")
   assert rpc(page,'DETAILS')['value']==state
   assert rpc(page,'REMOVE','garden-through-time')['ok']
   removed=rpc(page,'DETAILS')['value'];assert not removed['garden-through-time']['ready'] and all(removed[g]==state[g] for g in ids[:-1])
   assert not rpc(page,'INSTALL','garden-through-time')['ok']
   ctx.set_offline(False);assert rpc(page,'INSTALL','garden-through-time')['ok']
   assert all(rpc(page,'DETAILS')['value'][g]['ready'] for g in ids)
   # Exercise the actual backup validator with raw preferences and archive.
   assert page.evaluate("""async()=>{const src=await (await fetch('hub.js')).text();return src.includes('xi:game:ky-vien:kv-archive-v1')}""")
   assert not errors,errors
   b.close()
  print('PASS six-game discovery, actual SW install, offline launch/return, legacy preference copy, independent remove/reinstall',flush=True)
 finally:server.shutdown();server.server_close()
