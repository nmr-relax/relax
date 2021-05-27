"""Script for determining the double pivot point motions of the CaM-IQ X-ray structure C-domain motions.

The reference for this analysis is:

    d’Auvergne, E. J. and Griesinger, C. (2019). The theory of frame ordering: observing motions in calmodulin complexes. Q. Rev. Biophys., 52, e3. (http://dx.doi.org/10.1017/S0033583519000015)

The aim is to iteratively find the focal point of all motions.  The Kabsch algorithm consists of a translation of one centroid onto the other, followed by a rotation to superimpose 3D structures.  However, by specifying one centroid location for all structures in the PDB frame, the translation is eliminated and only the rotation remains.  This is a pivoted rotation which, if the centroids are not located at the pivot point, causes the centroid positions to translate.

The RMSD between the superimposed models is calculated and adapted into a target function return value, whereby the parameters are simply the atomic [x, y, z] positions of the pivot being optimised.  This allows the motional pivot point to be optimisation via the Nelder-Mead simplex algorithm.  Once found, the structures are superimposed using this pivot point as the centroid position.  The algorithm has been implemented in the relax user function structure.find_pivot.

Combined with the motional pivot algorithm, the following relax script was used to determine the pivot position and the domain displacements.  This is for the example of the C-domain motions.  It is hard-coded for two iterations of the algorithm to find two pivots.
"""

# Python module imports.
from numpy import array
from pipe_control.structure.mass import pipe_centre_of_mass


class Pivot_finder:
    def __init__(self):
        """Find the pivot point."""

        # Results table and structures.
        self.results_file = open('double_displacements_multi_mechanics.txt', 'w')
        self.structs = ['CaM_A', 'CaM_B', 'CaM_C']

        # Atom selections.
        sele_bb = '@N,CA,C,O'
        sele_moving = ':82-144@N,CA,C,O'
        sele_displace = ':80-146,503,504,508,509,513,514'

        # Create a data pipe.
        pipe.create('double pivot', 'N-state')

        # Load the 2BE6 structures with peptide and metals and with MOLMOL attached protons (and hand editing to fix the mangled MOLMOL PDB file).
        structure.read_pdb('2BE6_H_fixed.pdb', dir='../..', set_mol_name=['CaM_A', 'CaM_B', 'CaM_C', 'IQ_D', 'IQ_E', 'IQ_F'], alt_loc='A')

        # Superimpose the N-domain (skipping mobile residues :2-4,42,56-57,76-80, identified from model-free order parameters), save the structure, and create the web-of-motion representation.
        structure.align(molecules=[self.structs], method='fit to mean', atom_id=':6-41,43-55,58-74@N,C,CA,O', displace_id=['#CaM_A,IQ_D', '#CaM_B,IQ_E', '#CaM_C,IQ_F'])
        structure.write_pdb('original.pdb', force=True)
        structure.web_of_motion(molecules=[self.structs], atom_id=sele_bb, file='web_original.pdb', force=True)
        structure.web_of_motion(molecules=[['IQ_D', 'IQ_E', 'IQ_F']], atom_id=sele_bb, file='web_original_IQ.pdb', force=True)

        # The current RMSD.
        structure.rmsd(molecules=[self.structs], atom_id=sele_moving)

        # Write out the original C-domain centroid displacements.
        structure.displacement(molecules=[self.structs], atom_id=sele_moving)
        self.results_file.write("\nOriginal X-ray C-domain displacements:\n")
        self.translations()
        self.rotations()

        # Find the pivot.
        pivot = array([13.120, -13.047, 12.167])    # The original pivot point.
        structure.find_pivot(molecules=[self.structs], atom_id=sele_moving, init_pos=pivot)

        # Create a visual representation.
        self.piv_com()

        # Calculate and write out the C-domain pivot displacements.
        structure.displacement(molecules=[self.structs], atom_id=sele_moving, centroid=cdp.structure.pivot)
        self.results_file.write("\n\nDisplacements from the 1st motional pivot:\n")
        self.translations()
        self.rotations()

        # Superimpose (fit-to-mean), save the structure, and create the web-of-motion representation.
        structure.align(molecules=[self.structs], method='fit to mean', atom_id=sele_moving, displace_id=sele_displace, centroid=cdp.structure.pivot)
        structure.write_pdb('pivot1_si.pdb', force=True)
        structure.web_of_motion(molecules=[self.structs], atom_id=sele_bb, file='web_pivot1_si.pdb', force=True)
        structure.web_of_motion(molecules=[['IQ_D', 'IQ_E', 'IQ_F']], atom_id=sele_bb, file='web_pivot1_si_IQ.pdb', force=True)

        # The current RMSD.
        structure.rmsd(molecules=[self.structs], atom_id=sele_moving)

        # Find the 2nd pivot.
        pivot = array([26.209, -18.539,   7.102])    # An educated guess for an initial optimisation starting position for the 2nd motional pivot.
        structure.find_pivot(molecules=[self.structs], atom_id=sele_moving, init_pos=pivot)

        # Calculate and write out the C-domain pivot displacements.
        structure.displacement(molecules=[self.structs], atom_id=sele_moving, centroid=cdp.structure.pivot)
        self.results_file.write("\n\nDisplacements from the 2nd motional pivot:\n")
        self.translations()
        self.rotations()

        # Superimpose (fit-to-mean), save the structure, and create the web-of-motion representation.
        structure.align(molecules=[self.structs], method='fit to mean', atom_id=sele_moving, displace_id=sele_displace, centroid=cdp.structure.pivot)
        structure.write_pdb('pivot2_si.pdb', force=True)
        structure.web_of_motion(molecules=[self.structs], atom_id=sele_bb, file='web_pivot2_si.pdb', force=True)
        structure.web_of_motion(molecules=[['IQ_D', 'IQ_E', 'IQ_F']], atom_id=sele_bb, file='web_pivot2_si_IQ.pdb', force=True)

        # The current RMSD.
        structure.rmsd(molecules=[self.structs], atom_id=sele_moving)

        # Write out the remaining C-domain centroid displacements.
        structure.displacement(molecules=[self.structs], atom_id=sele_moving)
        self.results_file.write("\n\nResidual displacements:\n")
        self.translations()
        self.rotations()

        # Centroid superimpose (fit-to-mean), save the structure, and create the web-of-motion representation.
        structure.align(molecules=[self.structs], method='fit to mean', atom_id=sele_moving, displace_id=sele_displace)
        structure.write_pdb('centroid_si.pdb', force=True)
        structure.web_of_motion(molecules=[self.structs], atom_id=sele_bb, file='web_centroid_si.pdb', force=True)
        structure.web_of_motion(molecules=[['IQ_D', 'IQ_E', 'IQ_F']], atom_id=sele_bb, file='web_centroid_si_IQ.pdb', force=True)

        # The final RMSD.
        structure.rmsd(molecules=[self.structs], atom_id=sele_moving)


    def piv_com(self):
        """Create a visual representation of the current mechanics as a PDB file."""

        # Store the pivot and original C-domain centres of mass.
        pivot = cdp.structure.pivot
        com = []
        com.append(pipe_centre_of_mass(atom_id='#CaM_A:82-144@N,CA,C,O'))
        com.append(pipe_centre_of_mass(atom_id='#CaM_B:82-144@N,CA,C,O'))
        com.append(pipe_centre_of_mass(atom_id='#CaM_C:82-144@N,CA,C,O'))

        # A new data pipe.
        pipe.create('rep', 'N-state')

        # Create a new structure.
        for i in range(3):
            # The pivot.
            structure.add_atom(atom_name='PIV', res_name='M%i'%i, res_num=i+1, pos=pivot, element='S')

            # The CoM
            structure.add_atom(atom_name='COM', res_name='M%i'%i, res_num=i+1, pos=com[i], element='S')

            # Connect.
            structure.connect_atom(index1=2*i, index2=2*i+1)

        # Save the structure.
        structure.write_pdb('piv_com.pdb', force=True)

        # Switch back to the original pipe.
        pipe.switch('double pivot')


    def rotations(self):
        """Write out the rotations between the structures."""

        # Title.
        self.results_file.write("\nRotations (deg):\n")

        # Header.
        self.results_file.write('%-4s ' % '')
        for struct in self.structs:
            self.results_file.write('%-6s ' % struct)
        for struct in self.structs:
            self.results_file.write('%-24s ' % struct)
        self.results_file.write('\n')

        # Values.
        for struct in self.structs:
            self.results_file.write('%-4s ' % struct)

            # The angle.
            for struct2 in self.structs:
                self.results_file.write('%6.3f ' % (cdp.structure.displacements._rotation_angle[struct][struct2] / 2.0 / pi * 360.0))

            # The axis.
            for struct2 in self.structs:
                axis = cdp.structure.displacements._rotation_axis[struct][struct2]
                self.results_file.write('[%6.3f, %6.3f, %6.3f] ' % (axis[0], axis[1], axis[2]))

            self.results_file.write('\n')


    def translations(self):
        """Write out the translations between the structures."""

        # Title.
        self.results_file.write("\nTranslations (Angstrom):\n")

        # Header.
        self.results_file.write('%-4s ' % '')
        for struct in self.structs:
            self.results_file.write('%-6s ' % struct)
        for struct in self.structs:
            self.results_file.write('%-24s ' % struct)
        self.results_file.write('\n')

        # Values.
        for struct in self.structs:
            self.results_file.write('%-4s ' % struct)

            # The distance.
            for struct2 in self.structs:
                self.results_file.write('%6.3f ' % cdp.structure.displacements._translation_distance[struct][struct2])

            # The vector.
            for struct2 in self.structs:
                vect = cdp.structure.displacements._translation_vector[struct][struct2]
                self.results_file.write('[%6.3f, %6.3f, %6.3f] ' % (vect[0], vect[1], vect[2]))

            self.results_file.write('\n')


# Find the pivot.
Pivot_finder()
