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

"""Sample script demonstrating the use of the N-state model of domain motions.

The N-state model uses alignment tensors as determined by RDC data to determine N-states in rotational space, each associated with a given probability or weight.
"""


# Create the data pipe.
pipe.create('test', 'N-state')

# Load the C-terminal alignment tensors.
align_tensor.init(tensor='110 t43L C-dom', params=(-1.0474e-04, 3.9223e-04, -3.7442e-05, 1.0529e-04, 4.0116e-05), param_types=1)
align_tensor.init(tensor='143 pk2 C-dom', params=(-1.4348e-05, -4.9444e-04, 5.1804e-05, 1.3307e-04, -1.0238e-04), param_types=1)
align_tensor.init(tensor='146 pk1 C-dom', params=(-2.4660e-04, -1.3212e-04, -3.1946e-04, 8.7208e-05, -8.4264e-05), param_types=1)
align_tensor.init(tensor='17 t43L C-dom', params=(8.5734e-06, -1.2820e-04, 5.3537e-05, -3.3512e-05, -4.1060e-05), param_types=1)
align_tensor.init(tensor='N60D Tb C-dom', params=(-4.8126e-05, -2.9930e-04, 4.3719e-04, 3.7058e-04, 1.2690e-04), param_types=1)
align_tensor.init(tensor='N60D Th C-dom', params=(-7.9627e-06, 2.7383e-04, -3.2579e-04, -2.9647e-04, -1.5191e-04), param_types=1)
align_tensor.init(tensor='146 pk2 C-dom', params=(-1.4930e-04, -2.9012e-04, -1.9983e-04, -2.0327e-05, -2.2792e-05), param_types=1)
align_tensor.init(tensor='146 t43D C-dom', params=(2.9713e-04, -9.4987e-05, -2.1837e-04, 2.1539e-05, 2.0522e-05), param_types=1)
align_tensor.init(tensor='146 t43L C-dom', params=(-1.6814e-04, -1.0235e-04, -2.3152e-04, -9.4095e-05, -2.9964e-05), param_types=1)

# Set the domain the tensors correspond to.
n_state_model.set_domain(tensor='110 t43L C-dom', domain='C')
n_state_model.set_domain(tensor='143 pk2 C-dom', domain='C')
n_state_model.set_domain(tensor='146 pk1 C-dom', domain='C')
n_state_model.set_domain(tensor='17 t43L C-dom', domain='C')
n_state_model.set_domain(tensor='N60D Tb C-dom', domain='C')
n_state_model.set_domain(tensor='N60D Th C-dom', domain='C')
n_state_model.set_domain(tensor='146 pk2 C-dom', domain='C')
n_state_model.set_domain(tensor='146 t43D C-dom', domain='C')
n_state_model.set_domain(tensor='146 t43L C-dom', domain='C')

# Set the tensor state (reduced or full).
n_state_model.set_type(tensor='110 t43L C-dom', red=False)
n_state_model.set_type(tensor='143 pk2 C-dom', red=False)
n_state_model.set_type(tensor='146 pk1 C-dom', red=False)
n_state_model.set_type(tensor='17 t43L C-dom', red=True)
n_state_model.set_type(tensor='N60D Tb C-dom', red=True)
n_state_model.set_type(tensor='N60D Th C-dom', red=True)
n_state_model.set_type(tensor='146 pk2 C-dom', red=False)
n_state_model.set_type(tensor='146 t43D C-dom', red=False)
n_state_model.set_type(tensor='146 t43L C-dom', red=False)

# List of C-dom tensors.
c_tensor_list = ['110 t43L C-dom', '143 pk2 C-dom', '146 pk1 C-dom', '17 t43L C-dom', 'N60D Tb C-dom', 'N60D Th C-dom', '146 pk2 C-dom', '146 t43D C-dom', '146 t43L C-dom']

# Calculate the singular values.
align_tensor.svd(basis_set=0, tensors=c_tensor_list)
align_tensor.svd(basis_set=1, tensors=c_tensor_list)

# Calculate the angles between the matrices.
align_tensor.matrix_angles(basis_set=0, tensors=c_tensor_list)
align_tensor.matrix_angles(basis_set=1, tensors=c_tensor_list)


# Load the N-terminal alignment tensors.
align_tensor.init(tensor='110 t43L N-dom', params=(2.2127e-04, 5.2855e-05, 1.8433e-05, 3.0827e-05, 1.2017e-04), param_types=1)
align_tensor.init(tensor='143 pk2 N-dom', params=(3.1618e-05, 4.2658e-05, -8.7183e-06, -8.1250e-05, 4.8628e-05), param_types=1)
align_tensor.init(tensor='146 pk1 N-dom', params=(7.4553e-05, -9.6076e-05, 4.9363e-05, -6.0947e-05, -2.5628e-05), param_types=1)
align_tensor.init(tensor='17 t43L N-dom', params=(2.1506e-06, -2.0811e-04, -1.4169e-04, 6.1467e-05, -8.0616e-05), param_types=1)
align_tensor.init(tensor='N60D Tb N-dom', params=(1.0278e-03, -1.4860e-03, 8.4778e-04, 5.7108e-04, 3.6500e-04), param_types=1)
align_tensor.init(tensor='N60D Th N-dom', params=(-8.8394e-04, 1.5459e-03, -4.9095e-04, -5.4784e-04, -2.2704e-05), param_types=1)
align_tensor.init(tensor='146 pk2 N-dom', params=(-1.0566e-05, -7.7580e-05, -4.9425e-05, -5.2596e-06, -1.8736e-05), param_types=1)
align_tensor.init(tensor='146 t43D N-dom', params=(-3.0584e-05, -1.7438e-05, 5.5619e-05, 5.1900e-05, -2.6510e-05), param_types=1)
align_tensor.init(tensor='146 t43L N-dom', params=(3.1001e-05, -4.3433e-05, 1.7081e-05, 6.1744e-05, -2.8761e-05), param_types=1)

# Set the domain the tensors correspond to.
n_state_model.set_domain(tensor='110 t43L N-dom', domain='N')
n_state_model.set_domain(tensor='143 pk2 N-dom', domain='N')
n_state_model.set_domain(tensor='146 pk1 N-dom', domain='N')
n_state_model.set_domain(tensor='17 t43L N-dom', domain='N')
n_state_model.set_domain(tensor='N60D Tb N-dom', domain='N')
n_state_model.set_domain(tensor='N60D Th N-dom', domain='N')
n_state_model.set_domain(tensor='146 pk2 N-dom', domain='N')
n_state_model.set_domain(tensor='146 t43D N-dom', domain='N')
n_state_model.set_domain(tensor='146 t43L N-dom', domain='N')

# Set the tensor state (reduced or full).
n_state_model.set_type(tensor='110 t43L N-dom', red=True)
n_state_model.set_type(tensor='143 pk2 N-dom', red=True)
n_state_model.set_type(tensor='146 pk1 N-dom', red=True)
n_state_model.set_type(tensor='17 t43L N-dom', red=False)
n_state_model.set_type(tensor='N60D Tb N-dom', red=False)
n_state_model.set_type(tensor='N60D Th N-dom', red=False)
n_state_model.set_type(tensor='146 pk2 N-dom', red=True)
n_state_model.set_type(tensor='146 t43D N-dom', red=True)
n_state_model.set_type(tensor='146 t43L N-dom', red=True)

# List of N-dom tensors.
n_tensor_list = ['110 t43L N-dom', '143 pk2 N-dom', '146 pk1 N-dom', '17 t43L N-dom', 'N60D Tb N-dom', 'N60D Th N-dom', '146 pk2 N-dom', '146 t43D N-dom', '146 t43L N-dom']

# Calculate the singular values.
align_tensor.svd(basis_set=0, tensors=n_tensor_list)
align_tensor.svd(basis_set=1, tensors=n_tensor_list)

# Calculate the angles between the matrices.
align_tensor.matrix_angles(basis_set=0, tensors=n_tensor_list)
align_tensor.matrix_angles(basis_set=1, tensors=n_tensor_list)

# Set up the 5-state model (with the C domain as the reference frame).
n_state_model.model(N=5, ref='C')

# Set the initial parameter values to the actual values (the grid search is impossibly large).
value.set([  0.26685287,   0.07816268,   0.19105772,   0.23598687,   0.22793986], ['p0', 'p1', 'p2', 'p3', 'p4'])
value.set([ -0.43017117,   3.19650016,  -0.61738298,   0.80737988,   1.66687706], ['alpha0', 'alpha1', 'alpha2', 'alpha3', 'alpha4'])
value.set([  3.80965887,   0.68001535,   1.87238680,   1.48347412,   4.34470497], ['beta0', 'beta1', 'beta2', 'beta3', 'beta4'])
value.set([  0.43465176,   2.59328881,  -5.45779788,  -3.09774689,   0.86388922], ['gamma0', 'gamma1', 'gamma2', 'gamma3', 'gamma4'])

# Load the PDB file.
structure.read_pdb('1J7O.pdb', model=2)
structure.load_spins(spin_id='@N')
cdp.mol[0].name = None

# Minimise.
minimise('simplex', constraints=False)

# Print out.
print("\n\nResults\n")
print("%-16s  %12s  %12s  %12s  %12s  %12s" % ("Conformation", '1', '2', '3', '4', '5'))
print("%-16s [%12.8f, %12.8f, %12.8f, %12.8f, %12.8f]" % ("Probs", cdp.probs[0], cdp.probs[1], cdp.probs[2], cdp.probs[3], cdp.probs[4]))
print("%-16s [%12.8f, %12.8f, %12.8f, %12.8f, %12.8f]" % ("alpha", cdp.alpha[0], cdp.alpha[1], cdp.alpha[2], cdp.alpha[3], cdp.alpha[4]))
print("%-16s [%12.8f, %12.8f, %12.8f, %12.8f, %12.8f]" % ("beta", cdp.beta[0], cdp.beta[1], cdp.beta[2], cdp.beta[3], cdp.beta[4]))
print("%-16s [%12.8f, %12.8f, %12.8f, %12.8f, %12.8f]" % ("gamma", cdp.gamma[0], cdp.gamma[1], cdp.gamma[2], cdp.gamma[3], cdp.gamma[4]))
print("\n\n")
print("value.set([%12.8f, %12.8f, %12.8f, %12.8f, %12.8f], ['p0', 'p1', 'p2', 'p3', 'p4'])" % (cdp.probs[0], cdp.probs[1], cdp.probs[2], cdp.probs[3], cdp.probs[4]))
print("value.set([%12.8f, %12.8f, %12.8f, %12.8f, %12.8f], ['alpha0', 'alpha1', 'alpha2', 'alpha3', 'alpha4'])" % (cdp.alpha[0], cdp.alpha[1], cdp.alpha[2], cdp.alpha[3], cdp.alpha[4]))
print("value.set([%12.8f, %12.8f, %12.8f, %12.8f, %12.8f], ['beta0', 'beta1', 'beta2', 'beta3', 'beta4'])" % (cdp.beta[0], cdp.beta[1], cdp.beta[2], cdp.beta[3], cdp.beta[4]))
print("value.set([%12.8f, %12.8f, %12.8f, %12.8f, %12.8f], ['gamma0', 'gamma1', 'gamma2', 'gamma3', 'gamma4'])" % (cdp.gamma[0], cdp.gamma[1], cdp.gamma[2], cdp.gamma[3], cdp.gamma[4]))
print("# fk: %s" % cdp.chi2)

# Pivot point.
piv = [ 12.067,  14.313,  -3.2675]    # Ave between 1J70 AND 1J7P (model 2).

# Centre of mass analysis.
n_state_model.CoM(pivot_point=piv)

# Cone PDBs.
#n_state_model.cone_pdb(cone_type='diff on cone', file='diff_on_cone.pdb', force=True)
#n_state_model.cone_pdb(cone_type='diff in cone', file='diff_in_cone.pdb', force=True)

# PyMOL.
pymol.view()
pymol.cartoon()
pymol.cone_pdb(file='diff_on_cone.pdb')
pymol.cone_pdb(file='diff_in_cone.pdb')

# Finish.
state.save('save', force=True)
results.write(file='results', force=True)
