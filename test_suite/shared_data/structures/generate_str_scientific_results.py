pipe.create('str', 'mf')
structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir='test_suite/shared_data/structures', parser='scientific')
results.write('str_scientific', dir='test_suite/shared_data/structures', force=True)
