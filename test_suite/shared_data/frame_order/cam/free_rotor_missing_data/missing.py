# relax module imports.
from pipe_control.mol_res_spin import return_spin
from pipe_control.interatomic import return_interatom


# Create a data pipe to load the data into.
pipe.create('missing', 'N-state')

# Set up the spins from the PDB file.
structure.read_pdb(file='1J7P_1st_NH.pdb', dir='..', set_mol_name='C-dom')
structure.load_spins(spin_id='@N')
structure.load_spins(spin_id='@H')
interatom.define(spin_id1='@N', spin_id2='@H', direct_bond=True)

# The data to delete.
missing_pcs = {
    'pcs_dy': [':86@N', ':92@H', ':93@N', ':93@H', ':94@N', ':94@H', ':99@H', ':100@N'],
    'pcs_dy_subset': [':119@H'],
    'pcs_er_subset': [],
    'pcs_er': [],
    'pcs_tb_subset': [],
    'pcs_tb': []
}
missing_rdc = {
    'rdc_dy': [
        ['#C-dom:86@N',      '#C-dom:86@H'],
    ],
    'rdc_tb': [
        ['#C-dom:84@N',      '#C-dom:84@H'],
        ['#C-dom:99@N',      '#C-dom:99@H'],
        ['#C-dom:100@N',     '#C-dom:100@H'],
        ['#C-dom:120@N',     '#C-dom:120@H'],
        ['#C-dom:121@N',     '#C-dom:121@H'],
        ['#C-dom:130@N',     '#C-dom:130@H'],
        ['#C-dom:131@N',     '#C-dom:131@H'],
        ['#C-dom:132@N',     '#C-dom:132@H'],
        ['#C-dom:133@N',     '#C-dom:133@H'],
        ['#C-dom:134@N',     '#C-dom:134@H'],
        ['#C-dom:135@N',     '#C-dom:135@H'],
        ['#C-dom:136@N',     '#C-dom:136@H'],
        ['#C-dom:137@N',     '#C-dom:137@H'],
        ['#C-dom:138@N',     '#C-dom:138@H'],
        ['#C-dom:139@N',     '#C-dom:139@H']
    ],
    'rdc_tm': [
        ['#C-dom:84@N',      '#C-dom:84@H'],
    ]
}

# The subset of files to load.
files = [
    'pcs_dy_subset',
    'pcs_dy',
    'pcs_er_subset',
    'pcs_er',
    'pcs_tb_subset',
    'pcs_tb',
    'rdc_dy',
    'rdc_tb',
    'rdc_tm'
]

# Loop over and load the original data.
for file in files:
    # PCS data.
    if file[:3] == 'pcs':
        # Load the original file.
        pcs.read(align_id=file, file='%s.txt'%file, dir='../free_rotor/', mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

        # Delete the data.
        for spin_id in missing_pcs[file]:
            # Get the container.
            spin = return_spin(spin_id)

            # Delete the data.
            del spin.pcs[file]

        # Write data to file.
        pcs.write(align_id=file, file='%s.txt'%file, dir='.', force=True)

    # RDC data.
    elif file[:3] == 'rdc':
        # Load the original file.
        rdc.read(align_id=file, file='%s.txt'%file, dir='../free_rotor/', data_col=3, error_col=4)

        # Delete the data.
        for spin_id1, spin_id2 in missing_rdc[file]:
            # Get the container.
            interatom = return_interatom(spin_id1, spin_id2)

            # Delete the data.
            del interatom.rdc[file]

        # Write data to file.
        rdc.write(align_id=file, file='%s.txt'%file, dir='.', force=True)
