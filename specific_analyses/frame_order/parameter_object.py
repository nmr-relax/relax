###############################################################################
#                                                                             #
# Copyright (C) 2009-2014 Edward d'Auvergne                                   #
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
"""The module for the frame order parameter list object."""

# relax module imports.
from specific_analyses.parameter_object import Param_list


class Frame_order_params(Param_list):
    """The frame order parameter list singleton."""

    # Class variable for storing the class instance (for the singleton design pattern).
    _instance = None

    def __init__(self):
        """Define all the parameters of the analysis."""

        # The object is already initialised.
        if self._initialised: return

        # Execute the base class __init__ method.
        Param_list.__init__(self)

        # Add the model variables.
        self._add_model_info()

        # Add the base data.
        self._add_align_data()

        # Add the parameters of all models.
        self._add('pivot_x', scope='global', units='Angstrom', desc='The pivot point position x coordinate', py_type=float, set='params', err=True, sim=True)
        self._add('pivot_y', scope='global', units='Angstrom', desc='The pivot point position y coordinate', py_type=float, set='params', err=True, sim=True)
        self._add('pivot_z', scope='global', units='Angstrom', desc='The pivot point position z coordinate', py_type=float, set='params', err=True, sim=True)
        self._add('ave_pos_x', scope='global', units='Angstrom', desc='The average position x translation', py_type=float, set='params', err=True, sim=True)
        self._add('ave_pos_y', scope='global', units='Angstrom', desc='The average position y translation', py_type=float, set='params', err=True, sim=True)
        self._add('ave_pos_z', scope='global', units='Angstrom', desc='The average position z translation', py_type=float, set='params', err=True, sim=True)
        self._add('ave_pos_alpha', scope='global', units='rad', desc='The average position alpha Euler angle', py_type=float, set='params', err=True, sim=True)
        self._add('ave_pos_beta', scope='global', units='rad', desc='The average position beta Euler angle', py_type=float, set='params', err=True, sim=True)
        self._add('ave_pos_gamma', scope='global', units='rad', desc='The average position gamma Euler angle', py_type=float, set='params', err=True, sim=True)
        self._add('eigen_alpha', scope='global', units='rad', desc='The Eigenframe alpha Euler angle', py_type=float, set='params', err=True, sim=True)
        self._add('eigen_beta', scope='global', units='rad', desc='The Eigenframe beta Euler angle', py_type=float, set='params', err=True, sim=True)
        self._add('eigen_gamma', scope='global', units='rad', desc='The Eigenframe gamma Euler angle', py_type=float, set='params', err=True, sim=True)
        self._add('axis_theta', scope='global', units='rad', desc='The cone axis polar angle (for the isotropic cone model)', py_type=float, set='params', err=True, sim=True)
        self._add('axis_phi', scope='global', units='rad', desc='The cone axis azimuthal angle (for the isotropic cone model)', py_type=float, set='params', err=True, sim=True)
        self._add('axis_alpha', scope='global', units='rad', desc='The rotor axis alpha angle (the rotation angle out of the xy plane)', py_type=float, set='params', err=True, sim=True)
        self._add('cone_theta_x', scope='global', units='rad', desc='The pseudo-ellipse cone opening half-angle for the x-axis', py_type=float, set='params', err=True, sim=True)
        self._add('cone_theta_y', scope='global', units='rad', desc='The pseudo-ellipse cone opening half-angle for the y-axis', py_type=float, set='params', err=True, sim=True)
        self._add('cone_theta', scope='global', units='rad', desc='The isotropic cone opening half-angle', py_type=float, set='params', err=True, sim=True)
        self._add('cone_s1', scope='global', units='', desc='The isotropic cone order parameter', py_type=float, set='params', err=True, sim=True)
        self._add('cone_sigma_max', scope='global', units='rad', desc='The torsion angle', py_type=float, set='params', err=True, sim=True)

        # Add minimisation structures.
        self._add_min_data(min_stats_global=True)

        # Set up the user function documentation.
        self._set_uf_title("Frame order parameters")
        self._uf_param_table(label="table: frame order parameters", caption="Frame order parameters.", scope='global')
        self._uf_param_table(label="table: frame order parameter value setting with defaults", caption="Frame order parameter value setting.", scope='global', default=True)
