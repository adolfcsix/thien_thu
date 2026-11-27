# Integration acceptance test for same-origin V9.0 -> Xi upgrade.
from pathlib import Path
import tempfile, shutil, zipfile, threading, http.server, functools, json, time
from playwright.sync_api import sync_playwright

root=Path.cwd()
class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

with tempfile.TemporaryDirectory() as d:
    d=Path(d)
    target=d/'thien_thu'
    target.mkdir()
    with zipfile.ZipFile(root/'Thien_Thu_V9_0_Web_Deploy.zip') as z:
        z.extractall(target)
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(d)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    url=f'http://127.0.0.1:{server.server_port}/thien_thu/'
    with sync_playwright() as p:
        browser=p.chromium.launch()
        ctx=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
        page=ctx.new_page()
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(url)
        page.wait_for_function('!!navigator.serviceWorker.controller',timeout=30000)
        page.locator('#newBtn').click(timeout=12000)
        page.locator('[data-map="0"]').click()
        page.locator('#start').click()
        page.wait_for_timeout(300)
        page.locator('#homeBtn').click()
        before=page.evaluate("localStorage.getItem('thien-thu-v8')")
        assert json.loads(before)['game']['wave']==1
        shutil.rmtree(target)
        shutil.copytree(root/'site',target)
        page.evaluate('(async()=>{let r=await navigator.serviceWorker.getRegistration();await r.update()})()')
        page.wait_for_function('(async()=>!!(await navigator.serviceWorker.getRegistration()).waiting)()',timeout=30000)
        page.close()
        time.sleep(1)
        page=ctx.new_page()
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(url)
        page.wait_for_timeout(500)
        page.reload()
        page.get_by_text('Mỗi trò chơi,',exact=False).wait_for(timeout=30000)
        page.get_by_text('Sẵn sàng offline',exact=False).first.wait_for(timeout=30000)
        assert page.evaluate("localStorage.getItem('thien-thu-v8')")==before
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        ctx.set_offline(True)
        page.reload()
        page.get_by_role('button',name='Chơi ngay').first.click()
        page.locator('#continueBtn').click(timeout=12000)
        assert page.locator('#chapter').is_visible()
        page.locator('#hubBtn').click()
        page.get_by_text('Mỗi trò chơi,',exact=False).wait_for()
        page.get_by_role('button',name='Thư viện').click()
        page.on('dialog',lambda x:x.accept())
        page.get_by_role('button',name='Gỡ tài nguyên').click()
        page.get_by_text('Đã gỡ tài nguyên. Tiến trình vẫn còn.').wait_for()
        assert page.get_by_role('button',name='Chơi ngay').last.is_disabled()
        assert json.loads(page.evaluate("localStorage.getItem('thien-thu-v8')"))['game']['wave']==1
        assert not page.evaluate("(async()=> (await caches.keys()).some(k=>k.includes(':game:legacy:')))()")
        ctx.set_offline(False)
        page.get_by_role('button',name='Tải offline').click()
        page.get_by_text('Đã lưu đủ tài nguyên offline.').wait_for()
        ctx.set_offline(True)
        page.get_by_role('button',name='Chơi ngay').last.click()
        page.locator('#continueBtn').click(timeout=12000)
        page.locator('#hubBtn').click()
        assert not errors,errors
        print('PASS V9.0 migration, save, offline, remove/download, return to hub')
        browser.close()
    server.shutdown()
