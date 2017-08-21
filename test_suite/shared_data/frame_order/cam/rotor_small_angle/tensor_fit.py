###############################################################################
#                                                                             #
# Copyright (C) 2011-2012,2014 Edward d'Auvergne                              #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Script for calculating the RDC alignment tensors for the test model."""


# The tensor file for reading into relax.
out = open('tensors.py', 'w')

# Loop over the alignments.
ln = ['dy', 'tb', 'tm', 'er']
for i in range(len(ln)):
    # Create a new data pipe.
    pipe.create(ln[i], 'N-state')

    # Load the rotated C-domain.
    structure.read_pdb('1J7P_1st_NH_rot.pdb', dir='..')

    # Set up the 15N and 1H spins.
    structure.load_spins(spin_id='@N', ave_pos=False)
    structure.load_spins(spin_id='@H', ave_pos=False)
    spin.isotope(isotope='15N', spin_id='@N')
    spin.isotope(isotope='1H', spin_id='@H')

    # Define the magnetic dipole-dipole relaxation interaction.
    interatom.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
    interatom.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.041 * 1e-10)
    interatom.unit_vectors()

    # Load the RDCs.
    rdc.read(align_id=ln[i], file='rdc_%s.txt'%ln[i], spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4)

    # Set up the model.
    n_state_model.select_model(model='fixed')

    # Minimisation.
    minimise.grid_search(inc=5)
    minimise.execute('newton', constraints=True)

    # Monte Carlo simulations.
    monte_carlo.setup(number=1000)
    monte_carlo.create_data()
    monte_carlo.initial_values()
    minimise.execute('newton', constraints=False)
    monte_carlo.error_analysis()

    # Alias the tensor.
    A = cdp.align_tensors[0]

    # Write out the tensors.
    out.write("align_tensor.init(tensor='%s%s %s-dom', params=(%s, %s, %s, %s, %s), param_types=2)\n" % (ln[i][0].upper(), ln[i][1], 'C', A.Axx, A.Ayy, A.Axy, A.Axz, A.Ayz))
    out.write("align_tensor.init(tensor='%s%s %s-dom', params=(%s, %s, %s, %s, %s), param_types=2, errors=True)\n" % (ln[i][0].upper(), ln[i][1], 'C', A.Axx_err, A.Ayy_err, A.Axy_err, A.Axz_err, A.Ayz_err))
