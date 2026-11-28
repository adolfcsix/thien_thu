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
                    && keys.includes('xi:'+url+':shell:1.20.0')
                    && !keys.some(k=>k.startsWith('thien-thu:'+url+':'));
            }''',arg=url,timeout=60000)
            # The new worker has naturally activated and cleaned the old cache.
            # Read the exact new shell independently before testing navigation.
            import hashlib
            cached=observer.evaluate('''async url=>{const c=await caches.open('xi:'+url+':shell:1.20.0');const r=await c.match(new URL('index.html',url).href);if(!r)return null;return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',await r.arrayBuffer())),x=>x.toString(16).padStart(2,'0')).join('')}''',url)
            assert cached==hashlib.sha256((args.site/'index.html').read_bytes()).hexdigest(),('cached shell hash',cached)
            # Verify the active worker's actual code version via a read-only
            # message, not merely its state or the presence of a cache name.
            worker_version = '''async ([scope,controlled])=>{
                const r=await navigator.serviceWorker.getRegistration(scope);
                const w=controlled?navigator.serviceWorker.controller:r?.active;
                if(!w||w.state!=='activated')return null;
                const ch=new MessageChannel();
                return new Promise(resolve=>{
                    const timeout=setTimeout(()=>{ch.port1.close();resolve(null)},5000);
                    ch.port1.onmessage=e=>{clearTimeout(timeout);ch.port1.close();resolve(e.data?.ok?e.data.value:null)};
                    w.postMessage({type:'VERSION'},[ch.port2]);
                });
            }'''
            expected_worker={'version':'1.20.0','scope':url,'shell':'xi:'+url+':shell:1.20.0'}
            # Poll through the Python API; avoid depending on the browser's
            # JSHandle serialization of a wait_for_function predicate.
            def require_worker(target,controlled):
                import time
                deadline=time.monotonic()+45
                reply=None
                while time.monotonic()<deadline:
                    reply=target.evaluate(worker_version,[url,controlled])
                    if isinstance(reply,dict) and all(reply.get(k)==v for k,v in expected_worker.items()):
                        return reply
                    target.wait_for_timeout(500)
                print('WORKER HANDSHAKE DIAGNOSTICS',target.evaluate('''async url=>{const r=await navigator.serviceWorker.getRegistration(url);return {scope:r?.scope,script:r?.active?.scriptURL,state:r?.active?.state,controller:navigator.serviceWorker.controller?.scriptURL,caches:await caches.keys()}}''',url),'last reply:',reply,flush=True)
                raise AssertionError(('worker identity mismatch',expected_worker,reply))
            print('PASS active release handshake',require_worker(observer,False),flush=True)
            # Check the network directory switch independently of service-worker routing.
            network_hash=observer.evaluate('''async url=>{const r=await fetch(url+'index.html?xi-network-check=1.20.0',{cache:'no-store'});if(!r.ok)return null;return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',await r.arrayBuffer())),x=>x.toString(16).padStart(2,'0')).join('')}''',url)
            assert network_hash==cached,('network shell hash',network_hash)
            # The initial online navigation may be supplied by the network while
            # control is being assigned. Require exact bytes, then prove the
            # controlling worker serves the canonical root without any network.
            page=ctx.new_page()
            response=page.goto(url+'index.html?xi-release=1.20.0',wait_until='domcontentloaded')
            observer.close()
            assert response and response.ok
            assert hashlib.sha256(response.body()).hexdigest()==cached,('first online shell',page.title(),response.status,response.header_value('x-xi-shell-version'))
            page.wait_for_function('navigator.serviceWorker.controller?.state === "activated"',timeout=30000)
            print('PASS controlling release handshake',require_worker(page,True),flush=True)
            ctx.set_offline(True)
            try:
                response=page.goto(url,wait_until='domcontentloaded')
                assert response and response.ok and response.header_value('x-xi-shell-version')=='1.20.0',('offline navigation response',response.status if response else None,response.all_headers() if response else None)
                assert hashlib.sha256(response.body()).hexdigest()==cached
                print('PASS offline controlling release handshake',require_worker(page,True),flush=True)
            finally:
                ctx.set_offline(False)
            try:
                page.wait_for_function("globalThis.XI_CATALOG?.HUB_VERSION === '1.20.0'",timeout=30000)
                page.locator('#discover h2').wait_for(timeout=30000);page.get_by_text('Sẵn sàng offline',exact=False).first.wait_for(timeout=30000)
            except Exception:
                print('STARTUP DIAGNOSTICS',page.evaluate("()=>({url:location.href,title:document.title,version:globalThis.XI_CATALOG?.HUB_VERSION,startup:document.documentElement.dataset.startup,controller:navigator.serviceWorker.controller?.state,notice:document.getElementById('notice')?.textContent})"),flush=True)
                raise
            print('PASS natural worker activation (out-of-scope observer)',flush=True)"""
source=path.read_text(encoding='utf-8')
if source.count(old)!=1:
    raise SystemExit('Pinned migration test differs; refusing to patch')
path.write_text(source.replace(old,new),encoding='utf-8')
compile(path.read_text(encoding='utf-8'),str(path),'exec')
print('Migration test activation barrier applied; all original acceptance assertions retained.')
