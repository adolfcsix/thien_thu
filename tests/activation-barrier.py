"""Apply a deterministic worker activation barrier to the pinned F1.6 browser test.
No force-activation, cache mutation, test skipping or changes to shipped site.
"""
from pathlib import Path
import sys

path = Path(sys.argv[1])
old = """            page.close()
            page=ctx.new_page();page.goto(url)
            # Activation is asynchronous. Reload only after the new worker is active.
            page.wait_for_function('async()=>{const r=await navigator.serviceWorker.getRegistration();return !!r?.active&&!r.waiting&&!r.installing}',timeout=30000)
            page.reload();page.locator('#discover h2').wait_for();page.get_by_text('Sẵn sàng offline',exact=False).first.wait_for(timeout=30000)"""
new = """            # Observe activation from an out-of-scope, same-origin page. Reopening
            # /thien_thu/ too soon can keep the OLD worker alive in Chromium.
            (root/'activation-probe.html').write_text('<!doctype html><title>Activation observer</title>',encoding='utf-8')
            observer=ctx.new_page()
            observer.goto(f'http://127.0.0.1:{server.server_port}/activation-probe.html')
            assert observer.evaluate('navigator.serviceWorker.controller === null')
            page.close()
            observer.wait_for_function('''async url=>{
                const r=await navigator.serviceWorker.getRegistration(url);
                const keys=await caches.keys();
                return r?.active?.state==='activated' && !r.waiting && !r.installing
                    && keys.some(k=>k.startsWith('xi:'+url+':shell:'))
                    && !keys.some(k=>k.startsWith('thien-thu:'+url+':'));
            }''',arg=url,timeout=60000)
            # The new worker has naturally activated and cleaned the old cache.
            page=ctx.new_page();page.goto(url)
            observer.close()
            page.wait_for_function('navigator.serviceWorker.controller?.state === "activated"',timeout=30000)
            page.locator('#discover h2').wait_for(timeout=30000);page.get_by_text('Sẵn sàng offline',exact=False).first.wait_for(timeout=30000)
            print('PASS natural worker activation (out-of-scope observer)',flush=True)"""
source=path.read_text(encoding='utf-8')
if source.count(old)!=1:
    raise SystemExit('Pinned migration test differs; refusing to patch')
path.write_text(source.replace(old,new),encoding='utf-8')
compile(path.read_text(encoding='utf-8'),str(path),'exec')
print('Migration test activation barrier applied; all original acceptance assertions retained.')
