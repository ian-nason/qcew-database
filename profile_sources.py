"""Acquire version-matched official labels and independently profile original CSVs."""
import collections,csv,datetime,hashlib,io,json,pathlib,urllib.request,zipfile
R=pathlib.Path(__file__).resolve().parent
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()
lock=json.loads((R/'source-lock.json').read_text());path=R/'data/2025_annual_by_area.zip'
url='https://data.bls.gov/cew/data/files/2025/csv/2025_annual_by_area.zip'
if not path.exists():
 partial=path.with_suffix('.partial');n=0
 with urllib.request.urlopen(url,timeout=45) as res,partial.open('xb') as out:
  headers={k:res.headers.get(k) for k in ['Last-Modified','ETag','Content-Length']}
  while b:=res.read(512*1024):
   n+=len(b)
   if n>114997862:raise ValueError('By-area archive exceeds verified size')
   out.write(b)
 if n!=114997862:raise ValueError('By-area size mismatch')
 if 'label_archive' in lock:
  if sha(partial)!=lock['label_archive']['sha256']:raise ValueError('New download differs from pinned label archive; partial retained')
 partial.rename(path)
 if 'label_archive' not in lock:lock['label_archive']={'url':url,'bytes':n,'sha256':sha(path),'headers':headers,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'path':'data/'+path.name}
 (R/'source-lock.json').write_text(json.dumps(lock,indent=2)+'\n')
if path.stat().st_size!=lock['label_archive']['bytes'] or sha(path)!=lock['label_archive']['sha256']:raise ValueError('Label archive mismatch')
pairs=[('area_fips','area_title'),('own_code','own_title'),('industry_code','industry_title'),('agglvl_code','agglvl_title'),('size_code','size_title')]
maps={key:{} for key,title in pairs};byarea_rows=0;members=[];byarea_hash=hashlib.sha256()
with zipfile.ZipFile(path) as z:
 infos=z.infolist()
 if len({i.filename for i in infos})!=len(infos) or sum(i.file_size for i in infos)>2*1024**3:raise ValueError('Duplicate/oversize label archive')
 for info in infos:
  if info.is_dir():continue
  if not info.filename.endswith('.csv'):raise ValueError('Unexpected member')
  member_rows=0
  with z.open(info) as f:
   reader=csv.DictReader(io.TextIOWrapper(f,encoding='utf-8-sig',newline=''),restkey='EXTRA',restval=None)
   for row in reader:
    if 'EXTRA' in row or None in row.values():raise ValueError('Ragged label row')
    for key,title in pairs:
     if row[key] in maps[key] and maps[key][row[key]]!=row[title]:raise ValueError('Conflicting versioned label '+key+' '+row[key])
     maps[key][row[key]]=row[title]
    byarea_hash.update(json.dumps([v for k,v in row.items() if k not in {t for _,t in pairs}],separators=(',',':')).encode()+b'\n')
    member_rows+=1
  byarea_rows+=member_rows;members.append({'name':info.filename,'bytes':info.file_size,'crc32':info.CRC,'rows':member_rows})
 print('Streamed label archive:',byarea_rows,'records; dictionaries:',{k:len(v) for k,v in maps.items()},flush=True)
for key,title in pairs:
 f=io.StringIO(newline='');w=csv.writer(f);w.writerow([key,title]);w.writerows(sorted(maps[key].items()))
 data=f.getvalue().encode();target=R/'data'/(key+'_labels.csv')
 if target.exists():
  if target.read_bytes()!=data:raise ValueError('Rebuilt labels differ; existing dictionary retained')
 else:
  with target.open('xb') as out:out.write(data)
counts={};blank=collections.Counter();maxlen=collections.Counter();numeric_digits=collections.Counter();n=0;header=None;single_hash=hashlib.sha256();sample=[]
if sha(R/lock['archive']['path'])!=lock['archive']['sha256']:raise ValueError('Annual singlefile SHA mismatch')
with zipfile.ZipFile(R/lock['archive']['path']) as z,z.open(lock['archive']['members'][0]['name']) as raw:
 reader=csv.reader(io.TextIOWrapper(raw,encoding='utf-8-sig',newline=''),strict=True);header=next(reader)
 counts={h:collections.Counter() for h in header[:8]+['lq_disclosure_code','oty_disclosure_code']}
 for row in reader:
  if len(row)!=len(header):raise ValueError('Singlefile width mismatch')
  n+=1;single_hash.update(json.dumps(row,separators=(',',':')).encode()+b'\n')
  for h,v in zip(header,row):
   blank[h]+=v=='';maxlen[h]=max(maxlen[h],len(v))
   if h in counts:counts[h][v]+=1
   if '.' in v:numeric_digits[h]=max(numeric_digits[h],len(v.rsplit('.',1)[1]))
  if n<4 or (row[0]=='US000' and row[2]=='10'):sample.append(row)
 if n!=byarea_rows:raise ValueError('Annual single/by-area record counts differ')
report={'rows':n,'header':header,'blank_counts':blank,'max_token_length':maxlen,'max_fraction_digits':numeric_digits,'codes':counts,'samples':sample,'byarea_rows':byarea_rows,'label_counts':{k:len(v) for k,v in maps.items()},'singlefile_original_strings_sha256':single_hash.hexdigest(),'byarea_original_strings_sha256_in_archive_order':byarea_hash.hexdigest(),'label_archive_members':members}
(R/'evidence/source-profile.json').write_text(json.dumps(report,indent=2)+'\n')
lock['derived_dictionaries']={key:{'path':'data/'+key+'_labels.csv','rows':len(maps[key]),'sha256':sha(R/'data'/(key+'_labels.csv')),'bytes':(R/'data'/(key+'_labels.csv')).stat().st_size,'source':'label_archive; distinct exact code/title pairs; sorted by code'} for key,_ in pairs}
(R/'source-lock.json').write_text(json.dumps(lock,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['codes','label_archive_members']},indent=2),flush=True)
