"""Read-only independent release checks, disclosure semantics and meaningful aggregates."""
import importlib.metadata,inspect,json,pathlib,platform,re,sys
import datapond_build
import qcew
def validate(con,report):
 checks={}
 def zero(name,sql):
  n=con.execute(sql).fetchone()[0];checks[name]=n;qcew.require(n==0,f'{name}: {n} violations')
 for table,spec in qcew.SCHEMA.items():
  qcew.require([(x[0],x[1]) for x in con.execute('DESCRIBE '+table).fetchall()]==[(c['name'],c['type']) for c in spec['columns']],'Schema mismatch '+table)
  expected=(spec['rows'],len(spec['columns']),spec['source_file'],spec['source_sha256'],qcew.LOCK['release'],'Public domain (U.S. Bureau of Labor Statistics)')
  qcew.require(con.execute('SELECT row_count,column_count,source_file,source_sha256,source_release,license FROM _metadata WHERE table_name=?',[table]).fetchone()==expected,'Metadata mismatch '+table)
  for col in spec['columns']:
   got=con.execute('SELECT data_type,source_file,null_pct,description,source_header FROM _columns WHERE table_name=? AND column_name=?',[table,col['name']]).fetchone()
   qcew.require(got==(col['type'],spec['source_file'],0.0,col['description'],col['source_header']),'Dictionary mismatch '+table+'.'+col['name'])
 qcew.require(con.execute('SELECT count(*) FROM annual').fetchone()[0]==3089813,'View join inflation/loss')
 # An independently listed disclosure mapping, checked across every actual row.
 base=['annual_avg_emplvl','total_annual_wages','taxable_annual_wages','annual_contributions','annual_avg_wkly_wage','avg_annual_pay']
 mappings=[('disclosure_code',base),('lq_disclosure_code',['lq_'+n for n in base]),('oty_disclosure_code',['oty_'+n+s for n in base for s in ['_chg','_pct_chg']])]
 for flag,columns in mappings:
  expressions=[f'a.{c} IS DISTINCT FROM CASE WHEN r.{flag}=\'\' THEN r.{c} ELSE NULL END' for c in columns]
  zero(flag+' correct analytic NULLs','SELECT count(*) FROM annual a JOIN annual_raw r USING('+','.join(qcew.KEY)+') WHERE '+' OR '.join(expressions))
 zero('establishment measures preserved', 'SELECT count(*) FROM annual a JOIN annual_raw r USING('+','.join(qcew.KEY)+') WHERE '+' OR '.join('a.'+c+' IS DISTINCT FROM r.'+c for c in sorted(qcew.ESTABLISHMENTS)))
 expected={'disclosure_code':1860359,'lq_disclosure_code':1872172,'oty_disclosure_code':1937791}
 for flag,n in expected.items():qcew.require(con.execute(f"SELECT count(*) FROM annual_raw WHERE {flag}='N'").fetchone()[0]==n,'Disclosure distribution changed '+flag)
 national=con.execute("SELECT annual_avg_estabs,annual_avg_emplvl,total_annual_wages,annual_avg_wkly_wage,avg_annual_pay FROM annual WHERE area_fips='US000' AND own_code='0' AND industry_code='10' AND agglvl_code='10'").fetchone()
 qcew.require(national==(12112924,155732363,12259226899972,1514,78720),'Locked original source-row regression value')
 partition=con.execute("SELECT sum(annual_avg_estabs),sum(annual_avg_emplvl),sum(total_annual_wages) FROM annual WHERE area_fips='US000' AND industry_code='10' AND own_code IN ('1','2','3','5') AND agglvl_code='11'").fetchone()
 qcew.require(abs(partition[0]-national[0])<=2 and abs(partition[1]-national[1])<=2 and partition[2]==national[2],'Disjoint national ownership partition')
 qcew.require(abs(national[2]/national[1]-national[4])<=1 and abs(national[2]/national[1]/52-national[3])<=1,'National average pay arithmetic')
 diagnostics={}
 for flag in qcew.FLAGS:
  diagnostics[flag]=con.execute(f'SELECT {flag},count(*) FROM annual_raw GROUP BY 1 ORDER BY 1').fetchall()
 diagnostics['published_establishments_on_suppressed_rows']=con.execute("SELECT count(*),sum(annual_avg_estabs),min(annual_avg_estabs),max(annual_avg_estabs) FROM annual WHERE disclosure_code='N'").fetchone()
 diagnostics['establishment_values_on_flagged_rows']={}
 for flag,columns in [('disclosure_code',['annual_avg_estabs']),('lq_disclosure_code',['lq_annual_avg_estabs']),('oty_disclosure_code',['oty_annual_avg_estabs_chg','oty_annual_avg_estabs_pct_chg'])]:
  for column in columns:
   diagnostics['establishment_values_on_flagged_rows'][column]=con.execute(f"SELECT count(*),count(*) FILTER(WHERE {column}<>0),min({column}),max({column}) FROM annual_raw WHERE {flag}='N'").fetchone()
 diagnostics['dc_source_labels']=con.execute("SELECT * FROM areas WHERE area_fips LIKE '11%' ORDER BY 1").fetchall()
 diagnostics['california_source_row']=con.execute("SELECT area_fips,area_title,annual_avg_estabs,annual_avg_emplvl FROM annual WHERE area_fips='06037' AND agglvl_code='74' AND own_code='5' AND industry_code='62'").fetchall()
 diagnostics['national_total']=national;diagnostics['disjoint_ownership_sum']=partition
 return checks,diagnostics
def main():
 db=pathlib.Path(sys.argv[1]);report=json.loads((db.parent/'build-report.json').read_text());qcew.require(qcew.sha(db)==report['database_sha256'],'Artifact hash mismatch')
 profile=json.loads((qcew.HERE/'evidence/source-profile.json').read_text())
 qcew.require(profile['singlefile_original_strings_sha256']==profile['byarea_original_strings_sha256_in_archive_order'],'Official archive record values/order disagree')
 qcew.require(profile['rows']==profile['byarea_rows']==3089813,'Official archive counts disagree')
 with qcew.connection(db,True) as con:
  checks,diagnostics=validate(con,report);examples=[]
  for sql in re.sub(r'--[^\n]*','',(qcew.HERE/'examples.sql').read_text()).split(';'):
   if not sql.strip():continue
   cursor=con.execute(sql);rows=cursor.fetchall();qcew.require(bool(rows),'Empty query example')
   examples.append({'sql':sql.strip(),'columns':[x[0] for x in cursor.description],'rows':rows})
 modules={};pin=json.loads((qcew.HERE/'helper-lock.json').read_text())
 for name in ['ensure_metadata','build_columns_table','export_dictionary']:
  path=pathlib.Path(inspect.getsourcefile(getattr(datapond_build,name)));modules[name]={'path':str(path),'sha256':qcew.sha(path)}
  qcew.require(modules[name]['sha256']==pin['metadata_py_sha256'],'Helper pin mismatch '+name)
 runtime={'python':platform.python_version(),'interpreter':sys.executable,'duckdb':qcew.duckdb.__version__,'datapond_build_version':importlib.metadata.version('datapond-build'),'datapond_build_install_origin':json.loads(importlib.metadata.distribution('datapond-build').read_text('direct_url.json')),'helper_source_pin':pin,'used_helpers':modules,'installed_packages':sorted([{'name':d.metadata['Name'],'version':d.version} for d in importlib.metadata.distributions()],key=lambda x:x['name'].lower())}
 qcew.save(qcew.HERE/'runtime.json',runtime)
 qcew.save(qcew.HERE/'evidence/source-agreement.json',{'status':'passed','rows':profile['rows'],'original_non_title_field_strings_identical_across_both_official_archives':True,'ordered_record_strings_sha256':profile['singlefile_original_strings_sha256'],'full_profile_sha256':qcew.sha(qcew.HERE/'evidence/source-profile.json'),'singlefile_zip_sha256':qcew.LOCK['archive']['sha256'],'label_zip_sha256':qcew.LOCK['label_archive']['sha256'],'derived_dictionary_identities':qcew.LOCK['derived_dictionaries']})
 proof={'status':'passed','artifact_sha256':qcew.sha(db),'checks':checks,'schema_metadata_dictionary_verified':True,'diagnostics':diagnostics}
 qcew.save(qcew.HERE/'evidence/release-audit.json',proof);qcew.save(qcew.HERE/'evidence/examples.json',{'artifact_sha256':qcew.sha(db),'queries':examples})
 print(json.dumps(proof,indent=2,default=str))
if __name__=='__main__':main()
