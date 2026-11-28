"""Pin shell assets to the actual build and serve canonical navigation responses."""
import hashlib,json,re,sys
from pathlib import Path
site=Path(sys.argv[1])
worker=site/'sw.js'
s=worker.read_text(encoding='utf-8')
pins={p:hashlib.sha256((site/p).read_bytes()).hexdigest() for p in ('index.html','hub.css','hub.js','catalog.js','catalog-data.js','manifest.webmanifest')}
line='const XI_SHELL_INTEGRITY='+json.dumps(pins,separators=(',',':'))+';'
if 'const XI_SHELL_INTEGRITY=' in s:
    s,n=re.subn(r'^const XI_SHELL_INTEGRITY=.*?;$',lambda _:line,s,flags=re.M)
    assert n==1
else:
    def patch(old,new):
        global s
        assert s.count(old)==1,old
        s=s.replace(old,new)
    patch("const requests=files=>files.map(p=>new Request(url(p),{cache:'reload'}));",line+"\nconst requests=files=>files.map(p=>new Request(url(p),{cache:'no-store'}));")
    anchor="async function verify(c,g)"
    patch(anchor,"async function verifyShell(c){for(const [p,expected] of Object.entries(XI_SHELL_INTEGRITY)){const r=await c.match(url(p));if(!r?.ok||await digest(await r.arrayBuffer())!==expected)throw Error('Shell integrity mismatch: '+p)}}\n"+anchor)
    patch("await c.addAll(requests(shellFiles));if(!previousFoundation)","await c.addAll(requests(shellFiles));await verifyShell(c);if(!previousFoundation)")
    patch("const c=await existing(shell);return await c?.match(url(path))||fetch(req)","const c=await existing(shell);const r=await c?.match(url(path));if(path==='index.html'&&req.mode==='navigate'){if(!r?.ok)return new Response('Xi shell unavailable. Please reconnect and retry.',{status:503,headers:{'Content-Type':'text/plain; charset=utf-8','Cache-Control':'no-store'}});return new Response(await r.arrayBuffer(),{headers:{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store','X-Xi-Shell-Version':globalThis.XI_CATALOG.HUB_VERSION}})}return r||fetch(req)")
# An activated registration alone is not proof that a new navigation is
# controlled by that exact release. Expose a read-only version handshake.
if "type==='VERSION'" not in s:
    anchor="if(type==='STATUS'||type==='DETAILS')"
    assert s.count(anchor)==1
    s=s.replace(anchor,"if(type==='VERSION'){value={version:globalThis.XI_CATALOG.HUB_VERSION,scope,shell}}else "+anchor)
worker.write_text(s,encoding='utf-8')
print('Pinned shell assets:',len(pins))
