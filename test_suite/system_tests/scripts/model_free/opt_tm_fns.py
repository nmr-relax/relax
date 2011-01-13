###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

"""Functions for the local tm grid optimisation tests."""

# Python module imports.
from os import sep
from re import search

# relax module imports.
from prompt.interpreter import Interpreter
from status import Status; status = Status()


# Initialise the interpreter.
interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
interpreter.populate_self()
interpreter.on()


def create_sequence(num_res):
    """Generate the required sequence.

    @param num_res:     The total number of residues to create.
    @type num_res:      int
    """

    # Create the molecule.
    interpreter.molecule.create(mol_name='Polycarbonate')

    # Create the spins and residues.
    for i in range(num_res):
        interpreter.spin.create(spin_num=1, spin_name='C1', res_num=i+1, res_name='Bisphenol_A', mol_name='Polycarbonate')


def opt_and_check(spin=None, tm=None, tm_index=None):
    """Optimise the given model-free model, residue by residue.

    @keyword spin:      The spin container to validate.
    @type spin:         SpinContainer instance
    """

    # Default values for certain parameters.
    s2 = [1.0]
    s2_index = 0
    te = [0.0]
    te_index = 0

    # Select the spin.
    spin.select = True

    # Set up the diffusion tensor.
    if search('^m', cdp._model):
        if hasattr(cdp, 'diff_tensor'):
            interpreter.diffusion_tensor.delete()
        interpreter.diffusion_tensor.init(tm[tm_index])

    # Set up the initial model-free parameter values (bypass the grid search for speed).
    if search('^t', cdp._model):
        spin.local_tm = tm[tm_index] + 1e-11
    if cdp._model in ['tm2', 'm1', 'm2']:
        spin.s2 = 0.98
    if cdp._model in ['tm2', 'm2']:
        spin.te = 1e-12
    if cdp._model in ['m3']:
        spin.rex = 0.1 / (2.0 * pi * spin.frq[0])**2

    # Minimise.
    interpreter.minimise('newton', 'gmw', 'back', constraints=False)

    # Check the values.
    if cdp._model == 'm0':
        cdp._value_test(spin, chi2=0.0)
    elif cdp._model == 'm1':
        cdp._value_test(spin, s2=s2[s2_index], chi2=0.0)
    elif cdp._model == 'm2':
        cdp._value_test(spin, s2=s2[s2_index], te=te[te_index]*1e12, chi2=0.0)
    elif cdp._model == 'm3':
        cdp._value_test(spin, s2=s2[s2_index], rex=0.0, chi2=0.0)
    elif cdp._model == 'm4':
        cdp._value_test(spin, s2=s2[s2_index], te=te[te_index]*1e12, rex=0.0, chi2=0.0)
    elif cdp._model == 'tm2':
        cdp._value_test(spin, local_tm=tm[tm_index]*1e9, s2=s2[s2_index], te=te[te_index]*1e12, chi2=0.0)

    # Deselect the spin.
    spin.select = False


def setup_data():
    """Set up all the relevant data prior to optimisation."""

    # Path of the files.
    path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'tm0_grid'

    # The proton frequencies in MHz.
    frq = ['400', '500', '600', '700', '800', '900', '1000']

    # Load the relaxation data.
    for i in range(len(frq)):
        interpreter.relax_data.read('NOE', frq[i], float(frq[i])*1e6, 'noe.%s.out' % frq[i], dir=path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
        interpreter.relax_data.read('R1',  frq[i], float(frq[i])*1e6, 'r1.%s.out' % frq[i],  dir=path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
        interpreter.relax_data.read('R2',  frq[i], float(frq[i])*1e6, 'r2.%s.out' % frq[i],  dir=path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

    # Setup other values.
    interpreter.value.set(1.04 * 1e-10, 'bond_length')
    interpreter.value.set(-160 * 1e-6, 'csa')
    interpreter.value.set('15N', 'heteronucleus')
    interpreter.value.set('1H', 'proton')

    # Select the model-free model.
    interpreter.model_free.select_model(model=cdp._model)

    # Deselect all spins.
    interpreter.deselect.spin()
