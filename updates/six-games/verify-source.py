"""Verify the exact source snapshot before browser acceptance or packaging."""
from pathlib import Path
import hashlib,json,sys
root=Path(sys.argv[1]).resolve()
lock=json.loads((root/'source-lock.json').read_text(encoding='utf-8'))
assert lock['format']=='xi-source-lock-v1'
assert lock['hubVersion']=='1.26.0'
assert lock['games']=={'legacy':'9.2','cubiq':'1.2','block-nova':'1.2','feather-fury':'14.1','ky-vien':'1.0','garden-through-time':'0.79.3','huyen-anh':'0.82.3','pham-nhan-tu-tien':'0.7'}
assert not any(p.is_symlink() for p in root.rglob('*'))
actual={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file() and p.name!='source-lock.json'}
assert actual==lock['files'],{'missing':sorted(set(lock['files'])-set(actual)),'extra':sorted(set(actual)-set(lock['files'])),'changed':sorted(k for k in set(actual)&set(lock['files']) if actual[k]!=lock['files'][k])}
print('PASS exact consolidated source',len(actual),'files')
