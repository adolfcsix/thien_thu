from pathlib import Path
import hashlib,json,subprocess,sys,zipfile
root=Path(sys.argv[1]);site=root/'site';p=site/'hub.js'
protected={f:hashlib.sha256(f.read_bytes()).hexdigest() for f in site.rglob('*') if f.is_file() and (f.relative_to(site).parts[0] in ('games','assets') or f.name=='manifest.webmanifest')}
def patch(p,a,b):
 s=p.read_text();assert s.count(a)==1,(p,a,s.count(a));p.write_text(s.replace(a,b))
patch(p,"function enterGame(g){recordLaunch(g);location.assign(g.entry)}","function enterGame(g){if(!ensureSaveRecovery()){select('settings');return}recordLaunch(g);location.assign(g.entry)}")
patch(p,"function collectSaves(){",'''// Write-ahead rollback journal: the removal of this key is the commit point.
const SAVE_JOURNAL='xi:recovery:import-v1';
function rollbackImport(storage){const raw=storage.getItem(SAVE_JOURNAL);if(raw===null)return false;const j=JSON.parse(raw);if(j?.format!=='xi-import-rollback-v1'||!Array.isArray(j.previous)||!j.previous.length||j.previous.length>allowedSaves.size||new Set(j.previous.map(x=>x?.[0])).size!==j.previous.length||j.previous.some(x=>!Array.isArray(x)||x.length!==2||!allowedSaves.has(x[0])||!(x[1]===null||typeof x[1]==='string')))throw Error('Nhật ký phục hồi không hợp lệ.');for(const [k,v] of j.previous){if(v===null)storage.removeItem(k);else storage.setItem(k,v);if(storage.getItem(k)!==v)throw Error('Không thể xác minh bản lưu cũ.')}storage.removeItem(SAVE_JOURNAL);if(storage.getItem(SAVE_JOURNAL)!==null)throw Error('Không thể hoàn tất phục hồi.');return true}
function commitImport(entries,storage){rollbackImport(storage);const previous=entries.map(([k])=>[k,storage.getItem(k)]),raw=JSON.stringify({format:'xi-import-rollback-v1',previous});storage.setItem(SAVE_JOURNAL,raw);if(storage.getItem(SAVE_JOURNAL)!==raw)throw Error('Không thể lưu nhật ký an toàn.');try{for(const [k,v] of entries){storage.setItem(k,v);if(storage.getItem(k)!==v)throw Error('Không thể xác minh dữ liệu mới.')}storage.removeItem(SAVE_JOURNAL);if(storage.getItem(SAVE_JOURNAL)!==null)throw Error('Không thể hoàn tất nhập bản lưu.')}catch(err){try{rollbackImport(storage)}catch{throw Error('Còn nhật ký phục hồi. Mở lại Xi trước khi chơi.')}throw Error('Nhập thất bại; đã khôi phục dữ liệu trước đó.')}}
function ensureSaveRecovery(){let raw;try{raw=localStorage.getItem(SAVE_JOURNAL)}catch{return true}if(raw===null)return true;try{rollbackImport(localStorage);resilienceNote('Đã khôi phục bản lưu trước lần nhập bị gián đoạn.');return true}catch{resilienceNote('Chưa thể phục hồi bản lưu. Không mở game hoặc nhập thêm; giữ nguyên dữ liệu và thử mở lại Xi.');return false}}
function collectSaves(){''')
patch(p,"const data=collectSaves();","if(!ensureSaveRecovery())return;const data=collectSaves();")
patch(p,"if(!file)return;try{if(file.size", "if(!file||!ensureSaveRecovery())return;try{if(file.size")
patch(p,"Hãy xuất bản lưu hiện tại trước.","Hãy xuất bản lưu hiện tại và đóng các tab game khác trước.")
patch(p,"const previous=entries.map(([k])=>[k,localStorage.getItem(k)]);try{for(const [k,v] of entries)localStorage.setItem(k,v)}catch(err){for(const [k,v] of previous){try{v===null?localStorage.removeItem(k):localStorage.setItem(k,v)}catch{}}throw err}","commitImport(entries,localStorage);")
with p.open('a') as f:f.write('\nensureSaveRecovery();\n')
# Do not change any game bytes or save keys; keep the existing recovery archive in sync.
p=root/'integration/games.json';d=json.loads(p.read_text());d['hubVersion']='1.18.0';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');subprocess.run(['node','tools/catalog.mjs','--write'],cwd=root,check=True)
kit=site/'xi-offline-kit.zip'
with zipfile.ZipFile(kit) as z:old_readme=z.read('README.txt')
with zipfile.ZipFile(kit,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(site.rglob('*')):
  if not f.is_file() or f==kit:continue
  name='site/'+f.relative_to(site).as_posix()
  if f.name=='sw.js':z.writestr(name,f.read_text().replace(",'xi-offline-kit.zip'",''))
  else:z.write(f,name)
 z.writestr('README.txt',old_readme)
assert all(hashlib.sha256(f.read_bytes()).hexdigest()==h for f,h in protected.items())
subprocess.run(['node','--check','site/hub.js'],cwd=root,check=True)
patch(root/'tests/ui.py',' b.close()', ''' # Recovery: inject storage failures, verify rollback and crash recovery, no unrelated key changes.
 page=b.new_page(viewport={'width':390,'height':844},reduced_motion='reduce');page.set_content(html);page.locator('#discover h2').wait_for()
 result=page.evaluate("""()=>{const a='xi:game:cubiq:save',b='xi:game:block-nova:best',old='{"level":2}',next='{"level":3}',key=SAVE_JOURNAL;const values=new Map([[a,old],['unrelated','keep']]);let fail=false,quota=false;const store={getItem:k=>values.get(k)??null,setItem(k,v){if(quota&&k===key)throw Error('quota');if(fail&&k===b){fail=false;throw Error('write')}values.set(k,String(v))},removeItem:k=>values.delete(k)};quota=true;try{commitImport([[a,next],[b,'50']],store);return 'quota accepted'}catch{}if(values.get(a)!==old||values.has(b)||values.has(key))return 'quota changed saves';quota=false;fail=true;try{commitImport([[a,next],[b,'50']],store);return 'failure accepted'}catch{}if(values.get(a)!==old||values.has(b)||values.has(key))return 'rollback failed';values.set(key,JSON.stringify({format:'xi-import-rollback-v1',previous:[[a,old],[b,null]]}));values.set(a,next);values.set(b,'50');if(!rollbackImport(store)||values.get(a)!==old||values.has(b)||values.has(key))return 'crash rollback failed';commitImport([[a,next],[b,'50']],store);if(values.get(a)!==next||values.get(b)!=='50'||values.has(key)||values.get('unrelated')!=='keep')return 'commit failed';return 'ok'}""");assert result=='ok',result;page.close();print('PASS save journal quota refusal, failed write rollback, interrupted import recovery and commit')
 b.close()''')
with zipfile.ZipFile(root.parent/'candidate.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(root.rglob('*')):
  if f.is_file() and ('site' in f.relative_to(root).parts or f.suffix not in ('.pyc','.png')):z.write(f,f.relative_to(root))
