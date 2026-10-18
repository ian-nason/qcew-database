"""Failure fixtures for disclosure, grain, numeric fidelity, and source integrity."""
import copy,decimal,json,pathlib,tempfile,unittest,zipfile
from unittest.mock import patch
import duckdb,qcew
class Values(unittest.TestCase):
 def column(self,name):return next(c for c in qcew.SCHEMA['annual_raw']['columns'] if c['name']==name)
 def test_area_leading_zero(self):self.assertEqual(qcew.typed('01001',self.column('area_fips')),'01001')
 def test_empty_disclosure_preserved(self):self.assertEqual(qcew.typed('',self.column('disclosure_code')),'')
 def test_unknown_disclosure_rejected(self):
  with self.assertRaisesRegex(ValueError,'Unknown disclosure'):qcew.typed('D',self.column('disclosure_code'))
 def test_blank_code_rejected(self):
  with self.assertRaisesRegex(ValueError,'Unexpected blank'):qcew.typed('',self.column('industry_code'))
 def test_blank_numeric_rejected(self):
  with self.assertRaisesRegex(ValueError,'Invalid integer'):qcew.typed('',self.column('total_annual_wages'))
 def test_wage_beyond_int32(self):self.assertEqual(qcew.typed('12345678901234',self.column('total_annual_wages')),12345678901234)
 def test_negative_change_valid(self):self.assertEqual(qcew.typed('-9876543210',self.column('oty_total_annual_wages_chg')),-9876543210)
 def test_no_fractional_employment(self):
  with self.assertRaisesRegex(ValueError,'Invalid integer'):qcew.typed('100.5',self.column('annual_avg_emplvl'))
 def test_exact_quotient(self):self.assertEqual(qcew.typed('0.01',self.column('lq_annual_avg_emplvl')),decimal.Decimal('0.01'))
 def test_excess_quotient_precision_rejected(self):
  with self.assertRaisesRegex(ValueError,'overprecision'):qcew.typed('0.001',self.column('lq_annual_avg_emplvl'))
 def test_excess_pct_precision_rejected(self):
  with self.assertRaisesRegex(ValueError,'overprecision'):qcew.typed('1.23',self.column('oty_total_annual_wages_pct_chg'))
 def test_nan_rejected(self):
  with self.assertRaisesRegex(ValueError,'Invalid'):qcew.typed('NaN',self.column('lq_annual_avg_emplvl'))
class Semantic(unittest.TestCase):
 def setUp(self):
  self.con=duckdb.connect(config={'memory_limit':'64MiB','threads':'1'});self.schema=copy.deepcopy(qcew.SCHEMA)
  for table,spec in self.schema.items():
   spec['rows']=1;self.con.execute('CREATE TABLE '+table+'('+','.join(c['name']+' '+c['type'] for c in spec['columns'])+')')
  self.row={c['name']:0 for c in self.schema['annual_raw']['columns']}
  self.row.update(area_fips='01001',own_code='5',industry_code='62',agglvl_code='74',size_code='0',year='2025',qtr='A',disclosure_code='',lq_disclosure_code='',oty_disclosure_code='',annual_avg_estabs=3,annual_avg_emplvl=100,total_annual_wages=5000000,lq_annual_avg_estabs=decimal.Decimal('1.23'),oty_annual_avg_estabs_chg=-1,oty_annual_avg_estabs_pct_chg=decimal.Decimal('-25.0'))
  self.con.execute('INSERT INTO annual_raw VALUES ('+','.join('?' for _ in self.row)+')',list(self.row.values()))
  for table,(code,title) in qcew.PAIRS.items():self.con.execute('INSERT INTO '+table+' VALUES (?,?)',[self.row[code],table+' fixture'])
  self.con.execute('CREATE VIEW annual AS '+qcew.view_sql())
 def tearDown(self):self.con.close()
 def checks(self):
  with patch.object(qcew,'SCHEMA',self.schema):return qcew.checks(self.con)
 def test_valid_fixture(self):self.checks()
 def test_suppressed_levels_null_establishments_retained(self):
  self.con.execute("UPDATE annual_raw SET disclosure_code='N',annual_avg_emplvl=0,total_annual_wages=0")
  self.assertEqual(self.con.execute('SELECT annual_avg_emplvl,total_annual_wages,annual_avg_estabs FROM annual').fetchone(),(None,None,3))
 def test_separate_lq_flag(self):
  self.con.execute("UPDATE annual_raw SET lq_disclosure_code='N'")
  self.assertEqual(self.con.execute('SELECT annual_avg_emplvl,lq_annual_avg_emplvl,lq_annual_avg_estabs FROM annual').fetchone(),(100,None,decimal.Decimal('1.23')))
 def test_separate_change_flag(self):
  self.con.execute("UPDATE annual_raw SET oty_disclosure_code='N'")
  self.assertEqual(self.con.execute('SELECT annual_avg_emplvl,oty_annual_avg_emplvl_chg,oty_annual_avg_estabs_chg,oty_annual_avg_estabs_pct_chg FROM annual').fetchone(),(100,None,-1,decimal.Decimal('-25.0')))
 def test_unsuppressed_zero_is_zero(self):self.assertEqual(self.con.execute('SELECT annual_contributions FROM annual').fetchone()[0],0)
 def test_duplicate_key_rejected(self):
  self.con.execute('INSERT INTO annual_raw SELECT * FROM annual_raw')
  with self.assertRaisesRegex(ValueError,'duplicate keys'):self.checks()
 def test_orphan_geography_rejected(self):
  self.con.execute("UPDATE annual_raw SET area_fips='99999'")
  with self.assertRaisesRegex(ValueError,'reference area_fips'):self.checks()
 def test_duplicate_label_join_inflation_rejected(self):
  self.con.execute('INSERT INTO industries SELECT * FROM industries');self.assertEqual(self.con.execute('SELECT count(*) FROM annual').fetchone()[0],2)
  with self.assertRaisesRegex(ValueError,'industries duplicate keys'):self.checks()
 def test_wrong_vintage_rejected(self):
  self.con.execute("UPDATE annual_raw SET year='2024'")
  with self.assertRaisesRegex(ValueError,'year/quarter'):self.checks()
 def test_unknown_flag_rejected_by_database_check(self):
  self.con.execute("UPDATE annual_raw SET disclosure_code='X'")
  with self.assertRaisesRegex(ValueError,'disclosure_code valid'):self.checks()
 def test_negative_level_rejected(self):
  self.con.execute('UPDATE annual_raw SET annual_avg_emplvl=-1')
  with self.assertRaisesRegex(ValueError,'nonnegative levels'):self.checks()
 def test_mutated_cell_detected(self):
  import csv,io
  self.con.execute('UPDATE annual_raw SET annual_avg_emplvl=101')
  f=io.StringIO();w=csv.writer(f);w.writerow(self.row);w.writerow(self.row.values());f.seek(0)
  with self.assertRaisesRegex(ValueError,'cell mismatch'):qcew.compare_rows(self.con,'annual_raw',csv.reader(f),self.schema['annual_raw'])
class Archives(unittest.TestCase):
 def test_csv_empty_flag_retained_as_string(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'flags.csv';p.write_text('flag\n""\n"N"\n')
   with duckdb.connect(config={'memory_limit':'32MiB','threads':'1'}) as con:
    self.assertEqual(con.execute("SELECT * FROM read_csv(?,columns={'flag':'VARCHAR'},header=true,nullstr='',force_not_null=['flag'])",[str(p)]).fetchall(),[('',),('N',)])
 def test_existing_output_refused(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(FileExistsError):qcew.build(pathlib.Path('unused'),pathlib.Path(d))
 def test_archive_hash_mismatch(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'test.zip';p.write_bytes(b'bad')
   with self.assertRaisesRegex(ValueError,'Archive size/SHA'):qcew.verify_archive(p,{'bytes':3,'sha256':'0'*64})
 def test_duplicate_member_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'test.zip'
   with zipfile.ZipFile(p,'w') as z:z.writestr('x','1');z.writestr('x','1')
   with self.assertRaisesRegex(ValueError,'Duplicate ZIP'):qcew.verify_archive(p,{'bytes':p.stat().st_size,'sha256':qcew.sha(p)})
 def test_unknown_member_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'test.zip'
   with zipfile.ZipFile(p,'w') as z:z.writestr('other','1')
   with self.assertRaisesRegex(ValueError,'Unexpected ZIP'):qcew.verify_archive(p,{'bytes':p.stat().st_size,'sha256':qcew.sha(p),'members':[{'name':'x','bytes':1}]})
class ExtractionSafety(unittest.TestCase):
 def test_partial_extraction_is_not_reused(self):
  with tempfile.TemporaryDirectory() as d:
   raw=pathlib.Path(d)/'raw.csv';raw.with_name('raw.csv.partial').write_bytes(b'interrupted')
   with self.assertRaisesRegex(FileExistsError,'partial extraction'):qcew.extract_cache(pathlib.Path('unused'),raw)
   self.assertFalse(raw.exists())
 def test_bad_extraction_retains_partial_not_final(self):
  with tempfile.TemporaryDirectory() as d:
   raw=pathlib.Path(d)/'raw.csv';archive=pathlib.Path(d)/'a.zip'
   with zipfile.ZipFile(archive,'w') as z:z.writestr(qcew.LOCK['archive']['members'][0]['name'],'bad')
   with self.assertRaisesRegex(ValueError,'Extracted member SHA mismatch'):qcew.extract_cache(archive,raw)
   self.assertFalse(raw.exists());self.assertEqual(raw.with_name('raw.csv.partial').read_bytes(),b'bad')
 def test_output_outside_guarded_repository_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(ValueError,'guarded repository'):qcew.build(pathlib.Path('unused'),pathlib.Path(d)/'new-output')
if __name__=='__main__':unittest.main(verbosity=2)
