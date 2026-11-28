"""Actual F1.24 site: six titles, two independent downloads and offline return."""
import argparse,functools,http.server,threading,tempfile,shutil,json,hashlib
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
    observer.wait_for_function("""async url=>{const r=await navigator.serviceWorker.getRegistration(url);const keys=await caches.keys();return r?.active?.state==='activated'&&!r.installing&&!r.waiting&&keys.includes('xi:'+url+':shell:1.24.0')}""",arg=url,timeout=90000)
   except Exception:
    print('WORKER DIAGNOSTICS',observer.evaluate("""async url=>{const r=await navigator.serviceWorker.getRegistration(url);return {active:r?.active?.state,installing:r?.installing?.state,waiting:r?.waiting?.state,caches:await caches.keys()}}""",url),errors,flush=True)
    raise
   # First online navigation may be supplied by the network.
   expected_hash=hashlib.sha256((a.site/'index.html').read_bytes()).hexdigest()
   expected_worker={'version':'1.24.0','scope':url,'shell':'xi:'+url+':shell:1.24.0'}
   page.close()
   page=ctx.new_page();page.on('dialog',lambda d:d.accept())
   response=page.goto(url+'index.html?xi-release=1.24.0',wait_until='domcontentloaded');observer.close()
   assert response and response.ok
   assert hashlib.sha256(response.body()).hexdigest()==expected_hash,('online shell',page.title())
   page.wait_for_function('navigator.serviceWorker.controller?.state==="activated"')
   assert rpc(page,'VERSION')['value']==expected_worker
   ctx.set_offline(True)
   try:
    response=page.goto(url,wait_until='domcontentloaded')
    assert response and response.ok and response.header_value('x-xi-shell-version')=='1.24.0',('offline shell',response.all_headers() if response else None)
    assert hashlib.sha256(response.body()).hexdigest()==expected_hash
    assert rpc(page,'VERSION')['value']==expected_worker
    page.wait_for_function("globalThis.XI_CATALOG?.HUB_VERSION==='1.24.0'")
   finally:
    ctx.set_offline(False)
   page.locator('#intro').wait_for(state='hidden')
   page.locator('#discover h2').wait_for()
   assert page.evaluate('XI_CATALOG.HUB_VERSION')=='1.24.0'
   ids=['legacy','cubiq','block-nova','feather-fury','ky-vien','garden-through-time']
   assert page.evaluate('XI_CATALOG.released.map(g=>g.id)')==ids
   assert page.locator('#featured article').count()==6
   # Local cover assets are versioned shell resources and remain readable offline.
   ctx.set_offline(True)
   try:
    for gid in ('feather-fury','ky-vien','garden-through-time'):
     cover='assets/'+gid+'-cover.svg'
     image=page.locator(f'#featured article[data-game-id="{gid}"] .cover img.cover-art')
     image.scroll_into_view_if_needed()
     assert image.get_attribute('src')==cover
     assert image.evaluate('''async el=>{await el.decode();return el.complete&&el.naturalWidth===960&&el.naturalHeight===540&&el.getBoundingClientRect().width>0}'''),gid
     actual=page.evaluate('''async p=>{const r=await fetch(p);if(!r.ok)throw Error('cover '+r.status);return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',await r.arrayBuffer())),x=>x.toString(16).padStart(2,'0')).join('')}''',cover)
     assert actual==hashlib.sha256((a.site/cover).read_bytes()).hexdigest(),gid
   finally:ctx.set_offline(False)
   print('PASS three versioned offline cover artworks',flush=True)
   for gid in ids: assert rpc(page,'INSTALL',gid)['ok'],gid
   state=rpc(page,'DETAILS')['value'];assert all(state[g]['ready'] for g in ids)
   assert state['ky-vien']['installedVersion']=='1.0' and state['garden-through-time']['installedVersion']=='0.79.3'
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
     page.locator('#continueAdventure').click()
     page.locator('#levels button[aria-current=step]').click()
     page.locator('#prepare').wait_for()
     page.locator('#autoDeck').click()
     assert page.locator('#fight').is_enabled()
     page.locator('#fight').click()
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
   # Launch Sandbox through lobby settings, even offline. Keep the normal save exact.
   ns='xi:game:garden-through-time:'
   normal_key=ns+'garden-time-v1';sandbox_key=ns+'sandbox-progress-v1'
   normal_save=json.dumps({'intl':0,'china':0,'economy':{'intl':{'coins':123,'plants':{}},'china':{'coins':456,'plants':{}}}},separators=(',',':'))
   page.evaluate('([k,v])=>localStorage.setItem(k,v)',[normal_key,normal_save])
   page.get_by_role('button',name='Cài đặt',exact=True).click()
   page.locator('#gardenSandbox').wait_for()
   assert page.locator('[data-garden-option]').count()==6
   ctx.set_offline(True)
   page.locator('#gardenSandboxLaunch').click()
   page.wait_for_url('**/games/garden-through-time/index.html?sandbox=1')
   page.locator('#xi-sandbox-label').wait_for()
   assert page.evaluate('''()=>Object.keys(WORLDS).every(c=>save.completed[c]===stageMax(c)+1&&save.hard.completed[c]===stageMax(c)+1&&economy[c].coins>=10000000&&Object.keys(PLANTS).every(id=>plantRank(economy[c],id)===UPGRADE_RULES[c].max&&economy[c].plants[id].packets>=10000)&&Object.keys(SHOP_ITEMS).every(id=>shop[c].items[id]===99))''')
   assert page.evaluate("masteryRank(economy.intl,'pea')===MASTERY_MAX")
   assert page.evaluate("new Game('intl',0).pool.includes('laser')")
   assert page.evaluate("SAVE_FORMAT==='garden-through-time-sandbox'")
   assert page.evaluate('(k)=>localStorage.getItem(k)',normal_key)==normal_save
   assert page.evaluate('(k)=>!!localStorage.getItem(k)',sandbox_key)
   page.locator('#levels button').first.click();page.locator('#autoDeck').click();page.locator('#fight').click();page.locator('#board').wait_for()
   assert page.evaluate('g.sun>=9999&&g.food>=3')
   page.locator('#xi-return').click();page.locator('#discover h2').wait_for()
   assert page.evaluate('(k)=>localStorage.getItem(k)',normal_key)==normal_save
   page.goto(url+'games/garden-through-time/index.html');page.locator('#continueAdventure').wait_for()
   assert page.evaluate("!XI_SANDBOX&&economy.intl.coins===123&&plantRank(economy.intl,'pea')===1&&save.intl===0")
   assert page.locator('#xi-sandbox-label').is_hidden()
   page.locator('#xi-return').click();page.locator('#discover h2').wait_for()
   page.get_by_role('button',name='Cài đặt',exact=True).click()
   page.locator('#gardenSandboxReset').click()
   assert page.evaluate('(k)=>localStorage.getItem(k)',sandbox_key) is None
   for box in page.locator('[data-garden-option]').all():box.uncheck()
   page.locator('#gardenSandboxLaunch').click();page.wait_for_url('**/games/garden-through-time/index.html?sandbox=1')
   page.locator('#xi-sandbox-label').wait_for()
   assert page.evaluate("XI_SANDBOX&&save.intl===0&&economy.intl.coins===0&&plantRank(economy.intl,'pea')===1")
   assert page.evaluate('(k)=>localStorage.getItem(k)',normal_key)==normal_save
   page.locator('#xi-return').click();page.locator('#discover h2').wait_for()
   ctx.set_offline(False)
   print('PASS Garden Sandbox full unlock, independent normal save, reset, options-off and offline launch',flush=True)
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
