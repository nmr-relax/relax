###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
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
"""The diffusion_tensor user function definitions."""

# relax module imports.
from graphics import WIZARD_IMAGE_PATH
from pipe_control import diffusion_tensor, pipes
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('diffusion_tensor')
uf_class.title = "Class for manipulating the diffusion tensor."
uf_class.menu_text = "&diffusion_tensor"
uf_class.gui_icon = "relax.diff_tensor"


# The diffusion_tensor.copy user function.
uf = uf_info.add_uf('diffusion_tensor.copy')
uf.title = "Copy diffusion tensor data from one data pipe to another."
uf.title_short = "Diffusion tensor data copying."
uf.add_keyarg(
    name = "pipe_from",
    py_type = "str",
    desc_short = "source data pipe",
    desc = "The name of the data pipe to copy the diffusion tensor data from.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "pipe_to",
    py_type = "str",
    desc_short = "destination data pipe",
    desc = "The name of the data pipe to copy the diffusion tensor data to.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will copy the diffusion tensor data between data pipes.  The destination data pipe must not contain any diffusion tensor data.  If the source or destination data pipes are not supplied, then both will default to the current data pipe (hence specifying at least one is essential).")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To copy the diffusion tensor from the data pipe 'm1' to the current data pipe, type:")
uf.desc[-1].add_prompt("relax> diffusion_tensor.copy('m1')")
uf.desc[-1].add_prompt("relax> diffusion_tensor.copy(pipe_from='m1')")
uf.desc[-1].add_paragraph("To copy the diffusion tensor from the current data pipe to the data pipe 'm9', type:")
uf.desc[-1].add_prompt("relax> diffusion_tensor.copy(pipe_to='m9')")
uf.desc[-1].add_paragraph("To copy the diffusion tensor from the data pipe 'm1' to 'm2', type:")
uf.desc[-1].add_prompt("relax> diffusion_tensor.copy('m1', 'm2')")
uf.desc[-1].add_prompt("relax> diffusion_tensor.copy(pipe_from='m1', pipe_to='m2')")
uf.backend = diffusion_tensor.copy
uf.menu_text = "&copy"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_size = (700, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'diff_tensor.png'


# The diffusion_tensor.delete user function.
uf = uf_info.add_uf('diffusion_tensor.delete')
uf.title = "Delete the diffusion tensor data from the relax data store."
uf.title_short = "Diffusion tensor data deletion."
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will delete all diffusion tensor data from the current data pipe.")
uf.backend = diffusion_tensor.delete
uf.menu_text = "&delete"
uf.gui_icon = "oxygen.actions.list-remove"
uf.wizard_size = (600, 400)
uf.wizard_image = WIZARD_IMAGE_PATH + 'diff_tensor.png'


# The diffusion_tensor.display user function.
uf = uf_info.add_uf('diffusion_tensor.display')
uf.title = "Display the diffusion tensor information."
uf.title_short = "Diffusion tensor data display."
uf.display = True
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will display all of the diffusion tensor information of the current data pipe.")
uf.backend = diffusion_tensor.display
uf.menu_text = "dis&play"
uf.gui_icon = "oxygen.actions.document-preview"
uf.wizard_size = (600, 400)
uf.wizard_image = WIZARD_IMAGE_PATH + 'diff_tensor.png'


# The diffusion_tensor.init user function.
uf = uf_info.add_uf('diffusion_tensor.init')
uf.title = "Initialise the diffusion tensor."
uf.title_short = "Diffusion tensor set up."
uf.add_keyarg(
    name = "params",
    py_type = "num_or_num_tuple",
    dim = [4, 6],
    desc_short = "diffusion tensor parameters",
    desc = "The diffusion tensor data."
)
uf.add_keyarg(
    name = "time_scale",
    default = 1.0,
    py_type = "num",
    desc_short = "time scale",
    desc = "The correlation time scaling value."
)
uf.add_keyarg(
    name = "d_scale",
    default = 1.0,
    py_type = "num",
    desc_short = "D scale",
    desc = "The diffusion tensor eigenvalue scaling value."
)
uf.add_keyarg(
    name = "angle_units",
    default = "deg",
    py_type = "str",
    desc_short = "angle units",
    desc = "The units for the angle parameters."
)
uf.add_keyarg(
    name = "param_types",
    default = 0,
    py_type = "int",
    desc_short = "parameter types",
    desc = "A flag to select different parameter combinations."
)
uf.add_keyarg(
    name = "spheroid_type",
    py_type = "str",
    desc_short = "spheroid type",
    desc = "A string which, if supplied together with spheroid parameters, will restrict the tensor to either being 'oblate' or 'prolate'.",
    can_be_none = True
)
uf.add_keyarg(
    name = "fixed",
    default = True,
    py_type = "bool",
    desc_short = "fixed flag",
    desc = "A flag specifying whether the diffusion tensor is fixed or can be optimised."
)
# The sphere (isotropic diffusion).
uf.desc.append(Desc_container("The sphere (isotropic diffusion)"))
uf.desc[-1].add_paragraph("When the molecule diffuses as a sphere, all three eigenvalues of the diffusion tensor are equal, Dx = Dy = Dz.  In this case, the orientation of the XH bond vector within the diffusion frame is inconsequential to relaxation, hence, the spherical or Euler angles are undefined.  Therefore solely a single geometric parameter, either tm or Diso, can fully and sufficiently parameterise the diffusion tensor.  The correlation function for the global rotational diffusion is")
uf.desc[-1].add_verbatim("""
             1   - tau / tm
    C(tau) = - e            ,
             5
""")
uf.desc[-1].add_paragraph("To select isotropic diffusion, the parameter should be a single floating point number.  The number is the value of the isotropic global correlation time, tm, in seconds. To specify the time in nanoseconds, set the time scale to 1e-9.  Alternative parameters can be used by changing the 'param_types' flag to the following integers")
uf.desc[-1].add_item_list_element("0", "{tm}   (Default),")
uf.desc[-1].add_item_list_element("1", "{Diso},")
uf.desc[-1].add_paragraph("where")
uf.desc[-1].add_item_list_element(None, "1 / tm = 6Diso.")
# The spheroid (axially symmetric diffusion).
uf.desc.append(Desc_container("The spheroid (axially symmetric diffusion)"))
uf.desc[-1].add_paragraph("When two of the three eigenvalues of the diffusion tensor are equal, the molecule diffuses as a spheroid.  Four pieces of information are required to specify this tensor, the two geometric parameters, Diso and Da, and the two orientational parameters, the polar angle theta and the azimuthal angle phi describing the orientation of the axis of symmetry.  The correlation function of the global diffusion is")
uf.desc[-1].add_verbatim("""
               _1_
             1 \          - tau / tau_i
    C(tau) = -  >  ci . e              ,
             5 /__
               i=-1
""")
uf.desc[-1].add_paragraph("where")
uf.desc[-1].add_item_list_element(None, "c-1 = 1/4 (3 dz^2 - 1)^2,")
uf.desc[-1].add_item_list_element(None, "c0  = 3 dz^2 (1 - dz^2),")
uf.desc[-1].add_item_list_element(None, "c1  = 3/4 (dz^2 - 1)^2,")
uf.desc[-1].add_paragraph("and")
uf.desc[-1].add_item_list_element(None, "1 / tau -1 = 6Diso - 2Da,")
uf.desc[-1].add_item_list_element(None, "1 / tau 0  = 6Diso - Da,")
uf.desc[-1].add_item_list_element(None, "1 / tau 1  = 6Diso + 2Da.")
uf.desc[-1].add_paragraph("The direction cosine dz is defined as the cosine of the angle alpha between the XH bond vector and the unique axis of the diffusion tensor.")
uf.desc[-1].add_paragraph("To select axially symmetric anisotropic diffusion, the parameters should be a tuple of floating point numbers of length four.  A tuple is a type of data structure enclosed in round brackets, the elements of which are separated by commas.  Alternative sets of parameters, 'param_types', are")
uf.desc[-1].add_item_list_element("0", "{tm, Da, theta, phi}   (Default),")
uf.desc[-1].add_item_list_element("1", "{Diso, Da, theta, phi},")
uf.desc[-1].add_item_list_element("2", "{tm, Dratio, theta, phi},")
uf.desc[-1].add_item_list_element("3", "{Dpar, Dper, theta, phi},")
uf.desc[-1].add_item_list_element("4", "{Diso, Dratio, theta, phi},")
uf.desc[-1].add_paragraph("where")
uf.desc[-1].add_item_list_element(None, "tm = 1 / 6Diso,")
uf.desc[-1].add_item_list_element(None, "Diso = 1/3 (Dpar + 2Dper),")
uf.desc[-1].add_item_list_element(None, "Da = Dpar - Dper,")
uf.desc[-1].add_item_list_element(None, "Dratio = Dpar / Dper.")
uf.desc[-1].add_paragraph("The spherical angles {theta, phi} orienting the unique axis of the diffusion tensor within the PDB frame are defined between")
uf.desc[-1].add_item_list_element(None, "0 <= theta <= pi,")
uf.desc[-1].add_item_list_element(None, "0 <= phi <= 2pi,")
uf.desc[-1].add_paragraph("while the angle alpha which is the angle between this axis and the given XH bond vector is defined between")
uf.desc[-1].add_item_list_element(None, "0 <= alpha <= 2pi.")
uf.desc[-1].add_paragraph("The spheroid type should be 'oblate', 'prolate', or None.  This will be ignored if the diffusion tensor is not axially symmetric.  If 'oblate' is given, then the constraint Da <= 0 is used while if 'prolate' is given, then the constraint Da >= 0 is used.  If nothing is supplied, then Da will be allowed to have any values.  To prevent minimisation of diffusion tensor parameters in a space with two minima, it is recommended to specify which tensor is to be minimised, thereby partitioning the two minima into the two subspaces along the boundary Da = 0.")
# The ellipsoid (rhombic diffusion).
uf.desc.append(Desc_container("The ellipsoid (rhombic diffusion)"))
uf.desc[-1].add_paragraph("When all three eigenvalues of the diffusion tensor are different, the molecule diffuses as an ellipsoid.  This diffusion is also known as fully anisotropic, asymmetric, or rhombic. The full tensor is specified by six pieces of information, the three geometric parameters Diso, Da, and Dr representing the isotropic, anisotropic, and rhombic components of the tensor, and the three Euler angles alpha, beta, and gamma orienting the tensor within the PDB frame.  The correlation function is")
uf.desc[-1].add_verbatim("""
               _2_
             1 \          - tau / tau_i
    C(tau) = -  >  ci . e              ,
             5 /__
               i=-2
""")
uf.desc[-1].add_paragraph("where the weights on the exponentials are")
uf.desc[-1].add_item_list_element(None, "c-2 = 1/4 (d + e),")
uf.desc[-1].add_item_list_element(None, "c-1 = 3 dy^2 dz^2,")
uf.desc[-1].add_item_list_element(None, "c0  = 3 dx^2 dz^2,")
uf.desc[-1].add_item_list_element(None, "c1  = 3 dx^2 dy^2,")
uf.desc[-1].add_item_list_element(None, "c2  = 1/4 (d + e).")
uf.desc[-1].add_paragraph("Let")
uf.desc[-1].add_item_list_element(None, "R = sqrt(1 + 3Dr),")
uf.desc[-1].add_paragraph("then")
uf.desc[-1].add_item_list_element(None, "d = 3 (dx^4 + dy^4 + dz^4) - 1,")
uf.desc[-1].add_item_list_element(None, "e = - 1 / R ((1 + 3Dr)(dx^4 + 2dy^2 dz^2) + (1 - 3Dr)(dy^4 + 2dx^2 dz^2) - 2(dz^4 + 2dx^2 dy^2)).")
uf.desc[-1].add_paragraph("The correlation times are")
uf.desc[-1].add_item_list_element(None, "1 / tau -2 = 6Diso - 2Da . R,")
uf.desc[-1].add_item_list_element(None, "1 / tau -1 = 6Diso - Da (1 + 3Dr),")
uf.desc[-1].add_item_list_element(None, "1 / tau 0  = 6Diso - Da (1 - 3Dr),")
uf.desc[-1].add_item_list_element(None, "1 / tau 1  = 6Diso + 2Da,")
uf.desc[-1].add_item_list_element(None, "1 / tau 1  = 6Diso + 2Da . R.")
uf.desc[-1].add_paragraph("The three direction cosines dx, dy, and dz are the coordinates of a unit vector parallel to the XH bond vector.  Hence the unit vector is [dx, dy, dz].")
uf.desc[-1].add_paragraph("To select fully anisotropic diffusion, the parameters should be a tuple of length six.  A tuple is a type of data structure enclosed in round brackets, the elements of which are separated by commas.  Alternative sets of parameters, 'param_types', are")
uf.desc[-1].add_item_list_element("0", "{tm, Da, Dr, alpha, beta, gamma}   (Default),")
uf.desc[-1].add_item_list_element("1", "{Diso, Da, Dr, alpha, beta, gamma},")
uf.desc[-1].add_item_list_element("2", "{Dx, Dy, Dz, alpha, beta, gamma},")
uf.desc[-1].add_item_list_element("3", "{Dxx, Dyy, Dzz, Dxy, Dxz, Dyz},")
uf.desc[-1].add_paragraph("where")
uf.desc[-1].add_item_list_element(None, "tm = 1 / 6Diso,")
uf.desc[-1].add_item_list_element(None, "Diso = 1/3 (Dx + Dy + Dz),")
uf.desc[-1].add_item_list_element(None, "Da = Dz - (Dx + Dy)/2,")
uf.desc[-1].add_item_list_element(None, "Dr = (Dy - Dx)/2Da.")
uf.desc[-1].add_paragraph("The angles alpha, beta, and gamma are the Euler angles describing the diffusion tensor within the PDB frame.  These angles are defined using the z-y-z axis rotation notation where alpha is the initial rotation angle around the z-axis, beta is the rotation angle around the y-axis, and gamma is the final rotation around the z-axis again.  The angles are defined between")
uf.desc[-1].add_item_list_element(None, "0 <= alpha <= 2pi,")
uf.desc[-1].add_item_list_element(None, "0 <= beta <= pi,")
uf.desc[-1].add_item_list_element(None, "0 <= gamma <= 2pi.")
uf.desc[-1].add_paragraph("Within the PDB frame, the XH bond vector is described using the spherical angles theta and phi where theta is the polar angle and phi is the azimuthal angle defined between")
uf.desc[-1].add_item_list_element(None, "0 <= theta <= pi,")
uf.desc[-1].add_item_list_element(None, "0 <= phi <= 2pi.")
uf.desc[-1].add_paragraph("When param_types is set to 3, then the elements of the diffusion tensor matrix defined within the PDB frame can be supplied.")
# Units.
uf.desc.append(Desc_container("Units"))
uf.desc[-1].add_paragraph("The correlation time scaling value should be a floating point number.  The only parameter affected by this value is tm.")
uf.desc[-1].add_paragraph("The diffusion tensor eigenvalue scaling value should also be a floating point number.  Parameters affected by this value are Diso, Dpar, Dper, Da, Dx, Dy, and Dz.  Significantly, Dr is not affected.")
uf.desc[-1].add_paragraph("The  units for the angle parameters should be either 'deg' or 'rad'.  Parameters affected are theta, phi, alpha, beta, and gamma.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To set an isotropic diffusion tensor with a correlation time of 10 ns, type:")
uf.desc[-1].add_prompt("relax> diffusion_tensor.init(10e-9)")
uf.desc[-1].add_prompt("relax> diffusion_tensor.init(params=10e-9)")
uf.desc[-1].add_prompt("relax> diffusion_tensor.init(10.0, 1e-9)")
uf.desc[-1].add_prompt("relax> diffusion_tensor.init(params=10.0, time_scale=1e-9, fixed=True)")
uf.desc[-1].add_paragraph("To select axially symmetric diffusion with a tm value of 8.5 ns, Dratio of 1.1, theta value of 20 degrees, and phi value of 20 degrees, type:")
uf.desc[-1].add_prompt("relax> diffusion_tensor.init((8.5e-9, 1.1, 20.0, 20.0), param_types=2)")
uf.desc[-1].add_paragraph("To select a spheroid diffusion tensor with a Dpar value of 1.698e7, Dper value of 1.417e7, theta value of 67.174 degrees, and phi value of -83.718 degrees, type one of:")
uf.desc[-1].add_prompt("relax> diffusion_tensor.init((1.698e7, 1.417e7, 67.174, -83.718), param_types=3)")
uf.desc[-1].add_prompt("relax> diffusion_tensor.init(params=(1.698e7, 1.417e7, 67.174, -83.718), param_types=3)")
uf.desc[-1].add_prompt("relax> diffusion_tensor.init((1.698e-1, 1.417e-1, 67.174, -83.718), param_types=3, d_scale=1e8)")
uf.desc[-1].add_prompt("relax> diffusion_tensor.init(params=(1.698e-1, 1.417e-1, 67.174, -83.718), param_types=3, d_scale=1e8)")
uf.desc[-1].add_prompt("relax> diffusion_tensor.init((1.698e-1, 1.417e-1, 1.1724, -1.4612), param_types=3, d_scale=1e8, angle_units='rad')")
uf.desc[-1].add_prompt("relax> diffusion_tensor.init(params=(1.698e-1, 1.417e-1, 1.1724, -1.4612), param_types=3, d_scale=1e8, angle_units='rad', fixed=True)")
uf.desc[-1].add_paragraph("To select ellipsoidal diffusion, type:")
uf.desc[-1].add_prompt("relax> diffusion_tensor.init((1.340e7, 1.516e7, 1.691e7, -82.027, -80.573, 65.568), param_types=2)")
uf.backend = diffusion_tensor.init
uf.menu_text = "&init"
uf.gui_icon = "relax.diff_tensor"
uf.wizard_size = (1000, 750)
uf.wizard_height_desc = 400
uf.wizard_image = WIZARD_IMAGE_PATH + 'diff_tensor.png'
