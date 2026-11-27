"""Upgrade real installed F1.18 modules without discarding old caches or progress."""
import argparse, functools, http.server, json, shutil, tempfile, threading, zipfile
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
   b=getattr(pw,args.engine).launch();ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce');ctx.set_default_timeout(30000)
   page=ctx.new_page();page.goto(url);probe=ctx.new_page();probe.goto(f'http://127.0.0.1:{server.server_port}/probe.html');probe.wait_for_function("async url=>{const r=await navigator.serviceWorker.getRegistration(url);return r?.active?.state==='activated'&&!r.installing&&!r.waiting}",arg=url,timeout=60000);page.close();page=ctx.new_page();page.goto(url);probe.close();page.locator('#discover h2').wait_for()
   ids=['legacy','cubiq','block-nova','feather-fury'];versions=['9.2','1.2','1.2','12.2']
   for g in ids:assert rpc(page,'INSTALL',g)['ok']
   old=rpc(page,'DETAILS')['value'];assert all(old[g]['ready'] for g in ids)
   ff='xi:game:feather-fury:ff10-progress';newff='xi:game:feather-fury:ff12.2-progress'
   page.goto(url+'games/feather-fury/index.html');page.locator('#canvas').wait_for();page.locator('#menu').click();page.get_by_role('button',name='Về sảnh Xi',exact=True).click();page.get_by_role('button',name='Xác nhận về sảnh',exact=True).click();page.locator('#discover h2').wait_for()
   page.evaluate("""k=>{const v=JSON.parse(localStorage.getItem(k));v.coins=12345;v.feathers=567;v.stars[0]=3;v.best[0]=777;v.claimed[0]=true;v.birds[0].lv=5;v.open=1;localStorage.setItem(k,JSON.stringify(v))}""",ff)
   raw=page.evaluate('k=>localStorage.getItem(k)',ff);assert raw
   cache_names=page.evaluate("async()=> (await caches.keys()).filter(k=>k.includes(':game:')).sort()")
   shutil.rmtree(target);shutil.copytree(args.site,target);page.evaluate('async()=>{const r=await navigator.serviceWorker.getRegistration();await r.update()}');page.wait_for_function('async()=>!!(await navigator.serviceWorker.getRegistration()).waiting',timeout=60000)
   probe=ctx.new_page();probe.goto(f'http://127.0.0.1:{server.server_port}/probe.html');page.close();probe.wait_for_function("""async url=>{const r=await navigator.serviceWorker.getRegistration(url),k=await caches.keys();return r?.active?.state==='activated'&&!r.waiting&&!r.installing&&k.includes('xi:'+url+':shell:1.19.0')&&!k.includes('xi:'+url+':shell:1.18.0')}""",arg=url,timeout=60000)
   page=ctx.new_page();page.goto(url);probe.close();page.locator('#discover h2').wait_for()
   d=rpc(page,'DETAILS')['value'];assert all(d[g]['ready'] and d[g]['installedVersion']==old[g]['installedVersion'] and d[g]['availableVersion']==v and d[g]['updateAvailable'] for g,v in zip(ids,versions)),d
   assert page.evaluate("async()=> (await caches.keys()).filter(k=>k.includes(':game:')).sort()")==cache_names
   ctx.set_offline(True);assert not rpc(page,'UPDATE','feather-fury')['ok'];assert rpc(page,'DETAILS')['value']['feather-fury']['installedVersion']=='10.2';page.goto(url+'games/feather-fury/index.html');page.locator('#canvas').wait_for();assert page.locator('#xi-game-gesture-policy').count()==0;page.goto(url);page.locator('#discover h2').wait_for()
   assert page.evaluate('k=>localStorage.getItem(k)',ff)==raw
   ctx.set_offline(False)
   for g,v in zip(ids,versions):
    assert rpc(page,'UPDATE',g)['ok'];d=rpc(page,'DETAILS')['value'][g];assert d['installedVersion']==v and d['ready'] and not d['updateAvailable'] and d['backupBytes']>0,d
   assert page.evaluate('k=>localStorage.getItem(k)',ff)==raw
   ctx.set_offline(True)
   for g in ids:
    page.goto(url+'games/'+g+'/index.html');page.locator('#xi-game-gesture-policy').wait_for(state='attached')
    result=page.evaluate("""()=>{const t=document.createElement('button');document.body.append(t);const gesture=new Event('gesturestart',{cancelable:true,bubbles:true});const multi=new Event('touchmove',{cancelable:true,bubbles:true});Object.defineProperty(multi,'touches',{value:[{},{}]});const single=new Event('touchstart',{cancelable:true,bubbles:true});Object.defineProperty(single,'touches',{value:[{}]});const r=[!t.dispatchEvent(gesture),!t.dispatchEvent(multi),t.dispatchEvent(single),getComputedStyle(t).touchAction,getComputedStyle(document.querySelector('canvas')).touchAction,document.querySelector('meta[name=viewport]').content];t.remove();return r}""")
    assert result[:3]==[True,True,True] and set(result[3].split())=={'pan-x','pan-y'} and result[4]=='none' and 'maximum-scale=1' in result[5],(g,result)
    if args.engine=='chromium':
     session=ctx.new_cdp_session(page);page.evaluate("""()=>{const x=document.createElement('div');x.id='touchProbe';x.style.cssText='position:fixed;inset:0;z-index:2147483647';document.body.append(x)}""")
     session.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':150,'y':200,'id':0},{'x':240,'y':200,'id':1}]})
     for n in range(1,7):session.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':150-n*10,'y':200,'id':0},{'x':240+n*10,'y':200,'id':1}]})
     session.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});page.wait_for_timeout(350);assert abs(page.evaluate('visualViewport.scale')-1)<.01,g;page.evaluate('document.querySelector("#touchProbe").remove()');session.detach()
    if g!='feather-fury':page.goto(url);page.locator('#discover h2').wait_for()
   assert page.locator('#coins').inner_text()=='12345' and page.locator('#feathers').inner_text()=='567'
   page.locator('#menu').click();page.get_by_role('button',name='Chọn 8 chim ra trận',exact=True).click();assert page.locator('[data-r]').count()==12 and page.locator('[data-r][aria-pressed=true]').count()==8
   for w,h in [(280,650),(320,568),(390,844),(568,320),(844,390),(1024,768),(1280,800)]:
    page.set_viewport_size({'width':w,'height':h});panel=page.locator('.panel').bounding_box();assert panel['x']>=-1 and panel['y']>=-1 and panel['x']+panel['width']<=w+1 and panel['y']+panel['height']<=h+1,(w,h,panel)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
   page.set_viewport_size({'width':390,'height':844});page.locator('[data-r="0"]').click();page.locator('[data-r="8"]').click();page.locator('#saveFlock').click();page.get_by_role('button',name='Về sảnh Xi',exact=True).click();page.get_by_role('button',name='Xác nhận về sảnh',exact=True).click();page.locator('#discover h2').wait_for()
   v=json.loads(page.evaluate('k=>localStorage.getItem(k)',newff));assert (v['coins'],v['feathers'],v['stars'][0],v['best'][0],v['birds'][0]['lv'],len(v['birds']),len(v['flock']),v['open'])==(12345,567,3,777,5,12,8,1),v
   assert 8 in v['flock'] and 0 not in v['flock'];assert page.evaluate('k=>localStorage.getItem(k)',ff)==raw
   page.goto(url+'games/feather-fury/index.html');page.locator('#canvas').wait_for();assert page.locator('#coins').inner_text()=='12345';page.locator('#menu').click();page.get_by_role('button',name='Chọn 8 chim ra trận',exact=True).click();assert page.locator('[data-r="8"]').get_attribute('aria-pressed')=='true'
   print('PASS all four versioned game upgrades, failed offline update retains old cache, Feather 10.2 to 12.2 progress/roster migration, gesture policy and responsive panels',flush=True);b.close()
 finally:server.shutdown();server.server_close()
