"""Pinned QCEW 2025 annual ingestion; exact raw values plus a disclosure-aware view."""
from __future__ import annotations
import argparse,csv,datetime,decimal,hashlib,io,json,pathlib,re,shutil,urllib.request,zipfile
import duckdb
HERE=pathlib.Path(__file__).resolve().parent
SCHEMA=json.loads((HERE/'schema.json').read_text())
LOCK=json.loads((HERE/'source-lock.json').read_text())
PAIRS={'areas':('area_fips','area_title'),'ownerships':('own_code','own_title'),'industries':('industry_code','industry_title'),'aggregation_levels':('agglvl_code','agglvl_title'),'size_classes':('size_code','size_title')}
KEY=['area_fips','own_code','industry_code','agglvl_code','size_code','year','qtr']
FLAGS=['disclosure_code','lq_disclosure_code','oty_disclosure_code']
ESTABLISHMENTS={'annual_avg_estabs','lq_annual_avg_estabs','oty_annual_avg_estabs_chg','oty_annual_avg_estabs_pct_chg'}
def q(x):return '"'+x.replace('"','""')+'"'
def lit(x):return "'"+str(x).replace("'","''")+"'"
def require(condition,message):
 if not condition:raise ValueError(message)
def sha(path):
 h=hashlib.sha256()
 with pathlib.Path(path).open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()
def save(path,value):path.write_text(json.dumps(value,indent=2,default=str)+'\n')
def typed(value,column):
 name=column['name'];kind=column['type']
 if kind=='VARCHAR':
  require(value!='' or name in FLAGS,'Unexpected blank '+name)
  if name in FLAGS:require(value in ('','N'),'Unknown disclosure flag')
  return value
 if kind=='BIGINT':require(bool(re.fullmatch(r'-?[0-9]+',value)),'Invalid integer '+name);return int(value)
 scale=int(kind.split(',')[1][:-1]);require(bool(re.fullmatch(r'-?[0-9]+(?:\.[0-9]{1,'+str(scale)+r'})?',value)),'Invalid or overprecision decimal '+name)
 return decimal.Decimal(value)
def connection(path,readonly=False):
 return duckdb.connect(str(path),read_only=readonly,config={'memory_limit':'256MiB','threads':'1','max_temp_directory_size':'512MiB','preserve_insertion_order':'true'})
def verify_archive(path,record):
 require(path.stat().st_size==record['bytes'] and sha(path)==record['sha256'],'Archive size/SHA mismatch')
 with zipfile.ZipFile(path) as z:
  infos=z.infolist();require(len({i.filename for i in infos})==len(infos),'Duplicate ZIP names')
  require(sum(i.file_size for i in infos)<=800*1024**2,'Inflated singlefile archive over cap')
  require(len(infos)==1 and infos[0].filename==record['members'][0]['name'],'Unexpected ZIP member')
  require(infos[0].file_size==record['members'][0]['bytes'],'Member size mismatch')
def download(path):
 if path.exists():verify_archive(path,LOCK['archive']);return
 path.parent.mkdir(parents=True,exist_ok=True);partial=path.with_suffix('.partial')
 if partial.exists():raise FileExistsError('Retained partial source; inspect it and use a new --archive path')
 with urllib.request.urlopen(LOCK['archive']['url'],timeout=45) as res,partial.open('xb') as out:
  n=0
  while b:=res.read(1024*1024):
   n+=len(b);require(n<=LOCK['archive']['bytes'],'Download exceeds pinned size');out.write(b)
 verify_archive(partial,LOCK['archive']);partial.rename(path)
def view_sql():
 expressions=[]
 for c in SCHEMA['annual_raw']['columns']:
  name=c['name']
  if c['type']=='VARCHAR' or name in ESTABLISHMENTS:expressions.append('x.'+q(name));continue
  flag='lq_disclosure_code' if name.startswith('lq_') else 'oty_disclosure_code' if name.startswith('oty_') else 'disclosure_code'
  expressions.append(f"CASE WHEN x.{flag}='' THEN x.{q(name)} ELSE NULL END AS {q(name)}")
 joins=[]
 for table,(code,title) in PAIRS.items():
  expressions.append(table+'.'+q(title));joins.append(f'LEFT JOIN {table} USING({q(code)})')
 return 'SELECT '+','.join(expressions)+' FROM annual_raw x '+' '.join(joins)
def checks(con):
 result={}
 def zero(name,sql):
  n=con.execute(sql).fetchone()[0];result[name]=n;require(n==0,f'{name}: {n} violations')
 for table,spec in SCHEMA.items():
  keys=KEY if table=='annual_raw' else [spec['columns'][0]['name']]
  zero(table+' duplicate keys',f'SELECT count(*) FROM (SELECT {",".join(map(q,keys))},count(*) n FROM {q(table)} GROUP BY ALL HAVING n<>1)')
  for col in spec['columns']:zero(table+' NULL '+col['name'],f'SELECT count(*) FROM {q(table)} WHERE {q(col["name"])} IS NULL')
  require(con.execute(f'SELECT count(*) FROM {q(table)}').fetchone()[0]==spec['rows'],'Source count '+table)
 for table,(code,title) in PAIRS.items():zero('reference '+code,f'SELECT count(*) FROM annual_raw x LEFT JOIN {table} d USING({q(code)}) WHERE d.{q(code)} IS NULL')
 for flag in FLAGS:zero(flag+' valid',f"SELECT count(*) FROM annual_raw WHERE {flag} NOT IN ('','N')")
 zero('year/quarter/size',"SELECT count(*) FROM annual_raw WHERE year<>'2025' OR qtr<>'A' OR size_code<>'0'")
 zero('area code length',"SELECT count(*) FROM annual_raw WHERE length(area_fips)<>5")
 zero('ownership code',"SELECT count(*) FROM annual_raw WHERE own_code NOT IN ('0','1','2','3','5','8','9')")
 levels=[c['name'] for c in SCHEMA['annual_raw']['columns'] if c['type']!='VARCHAR' and not c['name'].startswith('oty_')]
 zero('nonnegative levels',f'SELECT count(*) FROM annual_raw WHERE '+ ' OR '.join(q(n)+'<0' for n in levels))
 return result
def compare_rows(con,table,reader,spec):
 require(next(reader)==[c['source_header'] for c in spec['columns']],'Header mismatch '+table)
 cursor=con.execute(f'SELECT * FROM {q(table)} ORDER BY rowid');n=0;h=hashlib.sha256();nulls=[0]*len(spec['columns']);samples=[]
 for batch in iter(lambda:cursor.fetchmany(1024),[]):
  for actual in batch:
   row=next(reader,None);require(row is not None and len(row)==len(spec['columns']),'CSV row width/count '+table)
   expected=tuple(typed(v,c) for v,c in zip(row,spec['columns']))
   require(actual==expected,f'Source-to-table cell mismatch {table} record {n+1}')
   n+=1;h.update(json.dumps(actual,ensure_ascii=False,default=str,separators=(',',':')).encode()+b'\n')
   nulls=[a+int(v is None) for a,v in zip(nulls,actual)]
   if n in [1,spec['rows']//2,spec['rows']]:samples.append({'source_record':n,'source':row,'typed':actual})
 require(next(reader,None) is None and n==spec['rows'],'Final count mismatch '+table)
 return {'rows':n,'all_cells_equal':True,'typed_rows_sha256':h.hexdigest(),'null_counts':dict(zip([c['name'] for c in spec['columns']],nulls)),'samples':samples}
def audit_source(con,archive):
 out={}
 with zipfile.ZipFile(archive) as z,z.open(LOCK['archive']['members'][0]['name']) as f:
  out['annual_raw']=compare_rows(con,'annual_raw',csv.reader(io.TextIOWrapper(f,encoding='utf-8-sig',newline=''),strict=True),SCHEMA['annual_raw'])
 for table,(key,title) in PAIRS.items():
  with (HERE/LOCK['derived_dictionaries'][key]['path']).open(newline='',encoding='utf-8') as f:out[table]=compare_rows(con,table,csv.reader(f,strict=True),SCHEMA[table])
 return out
def extract_cache(archive,raw):
 if raw.exists():
  require(sha(raw)==LOCK['archive']['members'][0]['sha256'],'Cached source hash mismatch; inspect and quarantine it before retrying')
  return
 partial=raw.with_name(raw.name+'.partial')
 if partial.exists():raise FileExistsError('Retained partial extraction; inspect and quarantine it before retrying')
 with zipfile.ZipFile(archive) as z,z.open(LOCK['archive']['members'][0]['name']) as src,partial.open('xb') as dst:shutil.copyfileobj(src,dst,1024*1024)
 require(sha(partial)==LOCK['archive']['members'][0]['sha256'],'Extracted member SHA mismatch; partial retained')
 partial.rename(raw)

def build(archive,out):
 from datapond_build import ensure_metadata,build_columns_table,export_dictionary
 if out.exists():raise FileExistsError('Use a new output directory; prior artifacts retained')
 require(out.resolve().is_relative_to(HERE.resolve()),'Output must stay inside the guarded repository')
 verify_archive(archive,LOCK['archive']);require(shutil.disk_usage(HERE).free>=10*1024**3,'Free disk below 10 GiB')
 for record in LOCK['derived_dictionaries'].values():require(sha(HERE/record['path'])==record['sha256'],'Derived dictionary hash mismatch')
 out.mkdir(parents=True);raw=HERE/'data/annual-source.csv'
 extract_cache(archive,raw)
 con=connection(out/'qcew.duckdb')
 try:
  for table,spec in SCHEMA.items():
   file=raw if table=='annual_raw' else HERE/spec['source_file']
   columns=','.join(lit(c['source_header'])+":'VARCHAR'" for c in spec['columns'])
   cast=','.join(f'CAST({q(c["source_header"])} AS {c["type"]}) AS {q(c["name"])}' for c in spec['columns'])
   preserved='['+','.join(lit(c['source_header']) for c in spec['columns'])+']'
   con.execute(f"CREATE TABLE {q(table)} AS SELECT {cast} FROM read_csv({lit(file)},columns={{{columns}}},header=true,nullstr='',force_not_null={preserved},strict_mode=true,ignore_errors=false,parallel=false)")
   print(table,con.execute(f'SELECT count(*) FROM {q(table)}').fetchone()[0],flush=True)
  validation=checks(con);proof=audit_source(con,archive);con.execute('CREATE VIEW annual AS '+view_sql())
  ensure_metadata(con,descriptions={t:s['description'] for t,s in SCHEMA.items()},tables=list(SCHEMA),source_url=LOCK['archive']['url'],license='Public domain (U.S. Bureau of Labor Statistics)',replace=True)
  for name in ['source_file','source_sha256','source_release']:con.execute(f'ALTER TABLE _metadata ADD COLUMN {name} VARCHAR')
  for table,spec in SCHEMA.items():con.execute('UPDATE _metadata SET source_file=?,source_sha256=?,source_release=? WHERE table_name=?',[spec['source_file'],spec['source_sha256'],LOCK['release'],table])
  hints={k:'Join '+table+' using the entire string code. Filter one aggregation/ownership/industry level before aggregating.' for table,(k,_) in PAIRS.items()}
  hints.update({flag:'Blank is published; N is not disclosed. Raw numeric zeros are retained; use the annual view for disclosure-aware values.' for flag in FLAGS})
  build_columns_table(con,tables=list(SCHEMA),join_hints=hints)
  con.execute('ALTER TABLE _columns ADD COLUMN description VARCHAR');con.execute('ALTER TABLE _columns ADD COLUMN source_header VARCHAR')
  for table,spec in SCHEMA.items():
   for col in spec['columns']:con.execute('UPDATE _columns SET description=?,source_header=? WHERE table_name=? AND column_name=?',[col['description'],col['source_header'],table,col['name']])
  export_dictionary(con,out/'DICTIONARY.md',title='QCEW 2025 annual data dictionary',tables=list(SCHEMA),intro=['Source: U.S. Bureau of Labor Statistics QCEW, public domain.','annual_raw preserves all source values; annual applies separate disclosure flags except for published establishment measures. See README for limitations and exact grain.'])
  with (out/'DICTIONARY.md').open('a') as f:
   f.write('\n## Exact field definitions\n\n')
   for table,spec in SCHEMA.items():
    f.write('### '+table+'\n\n| Column | Original header | Definition |\n|---|---|---|\n')
    for c in spec['columns']:f.write('| '+c['name']+' | '+c['source_header']+' | '+c['description'].replace('|','\\|')+' |\n')
    f.write('\n')
  con.execute('CHECKPOINT')
 finally:con.close()
 with connection(out/'qcew.duckdb',True) as con:
  validation.update(checks(con));persisted=audit_source(con,archive);require(persisted==proof,'Persisted values differ')
  meta=con.execute('SELECT count(*),sum(row_count),sum(column_count) FROM _metadata').fetchone()
  require(meta==(len(SCHEMA),sum(s['rows'] for s in SCHEMA.values()),sum(len(s['columns']) for s in SCHEMA.values())),'Metadata totals differ')
 report={'status':'validated_local_not_published','release':LOCK['release'],'built_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'duckdb':duckdb.__version__,'database_sha256':sha(out/'qcew.duckdb'),'database_bytes':(out/'qcew.duckdb').stat().st_size,'rows':meta[1],'data_tables':meta[0],'dictionary_columns':meta[2],'validation':validation,'source_comparison':persisted,'all_cells_reverified_after_read_only_reopen':True,'build_input_sha256':{n:sha(HERE/n) for n in ['qcew.py','schema.json','source-lock.json','pyproject.toml']}}
 save(out/'build-report.json',report);print(json.dumps({k:v for k,v in report.items() if k not in ['validation','source_comparison']},indent=2),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--archive',type=pathlib.Path,default=HERE/'data/2025_annual_singlefile.zip');p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--download',action='store_true');a=p.parse_args()
 if a.download:download(a.archive)
 build(a.archive,a.output)
