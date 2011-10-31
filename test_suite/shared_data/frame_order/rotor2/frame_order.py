# Script for optimising the free rotor frame order test model of CaM.

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

        # The rotation matrix.
        R = zeros((3, 3), float64)
        euler_to_R_zyz(cdp.ave_pos_alpha, cdp.ave_pos_beta, cdp.ave_pos_gamma, R)
        print("Rotation matrix:\n%s\n" % R)
        R = transpose(R)
        print("Inverted rotation:\n%s\n" % R)

        # The pivot point.
        pivot = array([ 37.254, 0.5, 16.7465])

        # Load the original structure.
        self.original_structure()

        # Domain transformation.
        self.transform(R, pivot)

        # Display in pymol.
        self.pymol_display(pivot)

        # Save the state.
        state.save('frame_order', force=True)


    def optimisation(self):
        """Optimise the frame order model."""

        # The file paths.
        PATH_N_DOM = '..' + sep
        PATH_C_DOM = '.' + sep

        # Create the data pipe.
        pipe.create(pipe_name='frame order', pipe_type='frame order')

        # Load the tensors.
        script(PATH_N_DOM + 'tensors.py')
        script(PATH_C_DOM + 'tensors.py')

        # The tensor domains and reductions.
        full = ['Dy N-dom', 'Tb N-dom', 'Tm N-dom', 'Er N-dom']
        red =  ['Dy C-dom', 'Tb C-dom', 'Tm C-dom', 'Er C-dom']
        for i in range(len(full)):
            align_tensor.set_domain(tensor=full[i], domain='N')
            align_tensor.set_domain(tensor=red[i], domain='C')
            align_tensor.reduction(full_tensor=full[i], red_tensor=red[i])

        # Select the model.
        frame_order.select_model('rotor')

        # Set the reference domain.
        frame_order.ref_domain('N')

        # Optimise.
        grid_search(inc=11)
        minimise('simplex', constraints=False)


    def original_structure(self):
        """Load the original structure into a dedicated data pipe."""

        # Create a special data pipe for the original rigid body position.
        pipe.create(pipe_name='orig pos', pipe_type='frame order')

        # Load the structure.
        structure.read_pdb('1J7P_1st_NH.pdb', dir='..')


    def pymol_display(self, pivot):
        """Display the results in PyMOL."""

        # Switch back to the main data pipe.
        pipe.switch('frame order')

        # Load the PDBs of the 2 domains.
        structure.read_pdb('1J7O_1st_NH.pdb', dir='..')
        structure.read_pdb('1J7P_1st_NH_rot.pdb', dir='..')

        # Set the pivot point.
        frame_order.pivot(pivot)

        # Create the cone PDB file.
        frame_order.cone_pdb(file='cone.pdb', force=True)

        # Set the domains.
        frame_order.domain_to_pdb(domain='N', pdb='1J7O_1st_NH.pdb')
        frame_order.domain_to_pdb(domain='C', pdb='1J7P_1st_NH_rot.pdb')

        # PyMOL.
        pymol.view()
        pymol.command('show spheres')
        pymol.cone_pdb('cone.pdb')


    def transform(self, R, pivot):
        """Transform the domain to the average position."""

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
