# Script for optimising the isotropic cone frame order test model of CaM.

# Python module imports.
from numpy import array, float64, transpose, zeros
from os import sep

# relax module imports.
from maths_fns.rotation_matrix import euler_to_R_zyz


class Analysis:
    def __init__(self):
        """Execute the frame order analysis."""

        # Optimise.
        self.optimisation()

        # Load the original structure.
        self.original_structure()

        # Domain transformation.
        self.transform()

        # Display in pymol.
        self.pymol_display()

        # Save the state.
        state.save('frame_order', force=True)


    def optimisation(self):
        """Optimise the frame order model."""

        # Create the data pipe.
        pipe.create(pipe_name='frame order', pipe_type='frame order')

        # Read the structures.
        structure.read_pdb('1J7O_1st_NH.pdb', dir='..', set_mol_name='N-dom')
        structure.read_pdb('1J7P_1st_NH_rot.pdb', dir='..', set_mol_name='C-dom')

        # Load the spins.
        structure.load_spins('@N')
        structure.load_spins('@H')

        # Load the NH vectors.
        structure.vectors(spin_id='@N', attached='H', ave=False)

        # Set the values needed to calculate the dipolar constant.
        value.set(1.041 * 1e-10, 'bond_length', spin_id="@N")
        value.set('15N', 'heteronucleus', spin_id="@N")
        value.set('1H', 'proton', spin_id="@N")

        # Loop over the alignments.
        ln = ['dy', 'tb', 'tm', 'er']
        for i in range(len(ln)):
            # Load the RDCs.
            rdc.read(align_id=ln[i], file='rdc_%s.txt'%ln[i], res_num_col=2, spin_name_col=5, data_col=6, error_col=7)

            # The PCS.
            pcs.read(align_id=ln[i], file='pcs_%s.txt'%ln[i], res_num_col=2, spin_name_col=5, data_col=6, error_col=7)

            # The temperature and field strength.
            temperature(id=ln[i], temp=303)
            frq.set(id=ln[i], frq=900e6)

        # Load the N-domain tensors (the full tensors).
        script('../tensors.py')

        # Define the domains.
        domain(id='N', spin_id=":1-78")
        domain(id='C', spin_id=":80-144")

        # The tensor domains and reductions.
        full = ['Dy N-dom', 'Tb N-dom', 'Tm N-dom', 'Er N-dom']
        red =  ['Dy C-dom', 'Tb C-dom', 'Tm C-dom', 'Er C-dom']
        for i in range(len(full)):
            # Initalise the reduced tensor.
            align_tensor.init(tensor=red[i], params=(0,0,0,0,0))

            # Set the domain info.
            align_tensor.set_domain(tensor=full[i], domain='N')
            align_tensor.set_domain(tensor=red[i], domain='C')

            # Specify which tensor is reduced.
            align_tensor.reduction(full_tensor=full[i], red_tensor=red[i])

        # Select the model.
        frame_order.select_model('pseudo-ellipse, free rotor')

        # Set the reference domain.
        frame_order.ref_domain('N')

        # Set the initial pivot point.
        pivot = array([ 37.254, 0.5, 16.7465])
        frame_order.pivot(pivot, fix=True)

        # Set the paramagnetic centre.
        paramag.centre(pos=[35.934, 12.194, -4.206])

        # Check the minimum.
        cdp.ave_pos_alpha = 4.3434999280669997
        cdp.ave_pos_beta = 0.43544332764249905
        cdp.ave_pos_gamma = 3.8013235235956007
        cdp.eigen_alpha = 3.1415926535897931
        cdp.eigen_beta = 0.96007997859534311
        cdp.eigen_gamma = 4.0322755062196229
        cdp.cone_theta_x = 0.5
        cdp.cone_theta_y = 0.1
        calc()
        print cdp.chi2

        # Optimise.
        #grid_search(inc=5)
        minimise('simplex', constraints=False)

        # Test Monte Carlo simulations.
        monte_carlo.setup(number=5)
        monte_carlo.create_data()
        monte_carlo.initial_values()
        minimise('simplex', constraints=False)
        eliminate()
        monte_carlo.error_analysis()


    def original_structure(self):
        """Load the original structure into a dedicated data pipe."""

        # Create a special data pipe for the original rigid body position.
        pipe.create(pipe_name='orig pos', pipe_type='frame order')

        # Load the structure.
        structure.read_pdb('1J7P_1st_NH_rot.pdb', dir='..')


    def pymol_display(self):
        """Display the results in PyMOL."""

        # Switch back to the main data pipe.
        pipe.switch('frame order')

        # Load the PDBs of the 2 domains.
        structure.read_pdb('1J7O_1st_NH.pdb', dir='..')
        structure.read_pdb('1J7P_1st_NH_rot.pdb', dir='..')

        # Create the cone PDB file.
        frame_order.cone_pdb(file='cone.pdb', force=True)

        # Set the domains.
        frame_order.domain_to_pdb(domain='N', pdb='1J7O_1st_NH.pdb')
        frame_order.domain_to_pdb(domain='C', pdb='1J7P_1st_NH_rot.pdb')

        # PyMOL.
        pymol.view()
        pymol.command('show spheres')
        pymol.cone_pdb('cone.pdb')


    def transform(self):
        """Transform the domain to the average position."""

        # Switch back to the main data pipe.
        pipe.switch('frame order')

        # The rotation matrix.
        R = zeros((3, 3), float64)
        euler_to_R_zyz(0.0, cdp.ave_pos_beta, cdp.ave_pos_gamma, R)
        print("Rotation matrix:\n%s\n" % R)
        R = transpose(R)
        print("Inverted rotation:\n%s\n" % R)
        pivot = cdp.pivot

        # Create a special data pipe for the average rigid body position.
        pipe.create(pipe_name='ave pos', pipe_type='frame order')

        # Load the structure.
        structure.read_pdb('1J7P_1st_NH_rot.pdb', dir='..')

        # Rotate all atoms.
        structure.rotate(R=R, origin=pivot)

        # Write out the new PDB.
        structure.write_pdb('ave_pos', force=True)


# Execute the analysis.
Analysis()
