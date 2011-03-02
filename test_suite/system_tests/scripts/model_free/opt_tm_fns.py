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
from math import pi
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


def opt_and_check(spin=None, tm=None, s2=None, s2f=None, s2s=None, te=None, tf=None, ts=None, rex=None):
    """Optimise the given model-free model, residue by residue.

    @keyword spin:      The spin container to validate.
    @type spin:         SpinContainer instance
    """

    # Precision for significance checking.
    epsilon = 1e-7

    # Default tm value.
    tm_scaled = None
    if 'local_tm' in spin.params and tm != None:
        tm_scaled = tm * 1e9

    # Default S2 value.
    if 'S2' in spin.params and s2 == None:
        s2 = 1.0

    # Default S2f value.
    if 'S2f' in spin.params and s2f == None:
        s2f = 1.0

    # Default S2s value.
    if 'S2s' in spin.params:
        if s2s == None:
            s2s = 1.0
    else:
        if 'S2f' in spin.params:
            s2s = s2 / s2f

    # Default te value.
    if 'te' in spin.params and te == None:
        te = 0.0
    te_scaled = 'skip'
    if te and abs(s2 - 1.0) > epsilon:
        te_scaled = te * 1e12

    # Default tf value.
    if 'tf' in spin.params and tf == None:
        tf = 0.0
    tf_scaled = 'skip'
    if tf and abs(s2f - 1.0) > epsilon:
        tf_scaled = tf * 1e12

    # Default ts value.
    if 'ts' in spin.params and ts == None:
        ts = 0.0
    ts_scaled = 'skip'
    if ts and abs(s2/s2f - 1.0) > epsilon:
        ts_scaled = ts * 1e12

    # Default Rex value.
    if 'rex' in spin.params and rex == None:
        rex = 0.0
    rex_scaled = 'skip'
    if rex:
        rex_scaled = rex / (2.0 * pi * cdp.frq[cdp.ri_ids[0]])**2

    # Select the spin.
    spin.select = True

    # Set up the diffusion tensor.
    if search('^m', cdp._model):
        if hasattr(cdp, 'diff_tensor'):
            interpreter.diffusion_tensor.delete()
        interpreter.diffusion_tensor.init(tm)

    # Set up the initial model-free parameter values (bypass the grid search for speed).
    if search('^t', cdp._model):
        spin.local_tm = tm
    if 'S2' in spin.params:
        spin.s2 = s2
    if 'S2f' in spin.params:
        spin.s2f = s2f
    if 'S2s' in spin.params:
        spin.s2s = s2s
    if 'te' in spin.params:
        spin.te = te
    if 'tf' in spin.params:
        spin.tf = tf
    if 'ts' in spin.params:
        spin.ts = ts
    if 'rex' in spin.params:
        spin.rex = rex

    # Minimise.
    interpreter.minimise('newton', 'gmw', 'back', constraints=False)

    # Check the values.
    cdp._value_test(spin, local_tm=tm_scaled, s2=s2, s2f=s2f, s2s=s2s, te=te_scaled, tf=tf_scaled, ts=ts_scaled, rex=rex_scaled, chi2=0.0)

    # Deselect the spin.
    spin.select = False


def setup_data(dir=None):
    """Set up all the relevant data prior to optimisation."""

    # Path of the files.
    path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+dir

    # The proton frequencies in MHz.
    frq = ['400', '500', '600', '700', '800', '900', '1000']

    # Load the relaxation data.
    for i in range(len(frq)):
        interpreter.relax_data.read(ri_id='NOE_%s'%frq[i], ri_type='NOE', frq=float(frq[i])*1e6, file='noe.%s.out'%frq[i], dir=path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
        interpreter.relax_data.read(ri_id='R1_%s'%frq[i],  ri_type='R1',  frq=float(frq[i])*1e6, file='r1.%s.out'%frq[i],  dir=path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
        interpreter.relax_data.read(ri_id='R2_%s'%frq[i],  ri_type='R2',  frq=float(frq[i])*1e6, file='r2.%s.out'%frq[i],  dir=path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

    # Setup other values.
    interpreter.value.set(1.20 * 1e-10, 'bond_length')
    interpreter.value.set(200 * 1e-6, 'csa')
    interpreter.value.set('13C', 'heteronucleus')
    interpreter.value.set('1H', 'proton')

    # Select the model-free model.
    interpreter.model_free.select_model(model=cdp._model)

    # Deselect all spins.
    interpreter.deselect.spin()
