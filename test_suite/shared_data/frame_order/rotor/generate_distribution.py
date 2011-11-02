# Script for generating the distribution of PDB structures.

# Python module imports.
from numpy import array, cross, dot, float64, zeros
from numpy.linalg import norm

# relax module imports.
from maths_fns.rotation_matrix import axis_angle_to_R


# The number of structures.
INC = 2
N = 60 / INC

# Create a data pipe.
pipe.create('generate', 'N-state')

# The axis for the rotations (the pivot point to CoM axis).
pivot = array([ 37.254, 0.5, 16.7465])
com = array([ 26.83678091, -12.37906417,  28.34154128])
axis = pivot - com
axis = axis / norm(axis)

# Init a rotation matrix.
R = zeros((3, 3), float64)

# Load N+1 copies of the original C-domain, rotating them about the rotation axis.
for i in range(N+1):
    # Load the PDB as a new model.
    structure.read_pdb('1J7P_1st_NH.pdb', dir='..', set_model_num=i)

    # The rotation angle.
    angle = (i - N/2) * INC / 360.0 * 2.0 * pi
    print("Rotation angle: %s" % angle)

    # The rotation matrix.
    axis_angle_to_R(axis, angle, R)
    print("Rotation matrix:\n%s\n" % R)

    # Rotate.
    structure.rotate(R=R, origin=pivot, model=i)

# Save the PDB file.
structure.write_pdb('distribution.pdb', compress_type=2, force=True)

# Create a PDB for the motional axis system.
end_pt = axis * norm(pivot - com) + pivot
structure.delete()
structure.add_atom(atom_name='C', res_name='AXE', res_num=1, pos=pivot, element='C')
structure.add_atom(atom_name='N', res_name='AXE', res_num=1, pos=end_pt, element='N')
structure.connect_atom(index1=0, index2=1)
structure.write_pdb('axis.pdb', compress_type=0, force=True)
