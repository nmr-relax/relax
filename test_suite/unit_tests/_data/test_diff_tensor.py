###############################################################################
#                                                                             #
# Copyright (C) 2007, 2010 Edward d'Auvergne                                  #
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

# Python module imports.
from math import cos, pi, sin
from numpy import array, dot, transpose
from unittest import TestCase

# relax module imports.
from data.diff_tensor import DiffTensorData, DiffTensorSimList
from relax_errors import RelaxError


class Test_diff_tensor(TestCase):
    """Unit tests for the data.diff_tensor relax module."""

    def calc_spheroid_objects(self, tm, Da, theta, phi):
        """Function for calculating the spheroidal diffusion tensor objects."""

        # The parameter values.
        Diso = 1/(6*tm)
        Dpar = Diso + 2.0/3.0 * Da
        Dper = Diso - 1.0/3.0 * Da
        Dratio = Dpar / Dper

        # Vectors.
        Dpar_unit = array([sin(theta) * cos(phi), sin(theta) * sin(phi), cos(theta)])

        # Matrices.
        if Dpar > Dper:
            tensor_diag = array([[ Dper,  0.0,  0.0],
                                 [  0.0, Dper,  0.0],
                                 [  0.0,  0.0, Dpar]])
        else:
            tensor_diag = array([[ Dpar,  0.0,  0.0],
                                 [  0.0, Dper,  0.0],
                                 [  0.0,  0.0, Dper]])
        rotation = array([[ cos(theta) * cos(phi), -sin(phi), sin(theta) * cos(phi) ],
                          [ cos(theta) * sin(phi),  cos(phi), sin(theta) * sin(phi) ],
                          [           -sin(theta),       0.0,            cos(theta) ]])
        tensor = dot(rotation, dot(tensor_diag, transpose(rotation)))

        # Return the objects.
        return Diso, Dpar, Dper, Dratio, Dpar_unit, tensor_diag, rotation, tensor


    def setUp(self):
        """Set 'self.diff_data' to an empty instance of the DiffTensorData class."""

        self.diff_data = DiffTensorData()


    def test_append_spheroid_sim(self):
        """Test the appending of Monte Carlo simulation spheroidal diffusion tensor parameters.

        The following parameters will be appended to empty lists:
            - tm: 8 ns
            - Da: -1e7
            - theta: 150 degrees
            - phi: 30 degrees
        """

        # The MC sim parameter values.
        tm = 8e-9
        Da = -1e7
        theta = (150 / 360.0) * 2.0 * pi
        phi = (30 / 360.0) * 2.0 * pi

        # Set the diffusion type.
        self.diff_data.type = 'spheroid'

        # Set the MC sim diffusion parameter lists.
        self.diff_data.tm_sim = DiffTensorSimList('tm', self.diff_data)
        self.diff_data.Da_sim = DiffTensorSimList('Da', self.diff_data)
        self.diff_data.theta_sim = DiffTensorSimList('theta', self.diff_data)
        self.diff_data.phi_sim = DiffTensorSimList('phi', self.diff_data)

        # Append the values.
        self.diff_data.tm_sim.append(tm)
        self.diff_data.Da_sim.append(Da)
        self.diff_data.theta_sim.append(theta)
        self.diff_data.phi_sim.append(phi)

        # Test the set values.
        self.assertEqual(self.diff_data.type, 'spheroid')
        self.assertEqual(self.diff_data.tm_sim[0], tm)
        self.assertEqual(self.diff_data.Da_sim[0], Da)
        self.assertEqual(self.diff_data.theta_sim[0], theta)
        self.assertEqual(self.diff_data.phi_sim[0], phi)

        # Calculate the diffusion tensor objects.
        Diso, Dpar, Dper, Dratio, Dpar_unit, tensor_diag, rotation, tensor = self.calc_spheroid_objects(tm, Da, theta, phi)

        # Test the automatically created values.
        self.assertEqual(self.diff_data.Diso_sim[0], Diso)
        self.assertEqual(self.diff_data.Dpar_sim[0], Dpar)
        self.assertEqual(self.diff_data.Dper_sim[0], Dper)
        self.assertEqual(self.diff_data.Dratio_sim[0], Dratio)

        # Test the vectors.
        self.assertEqual(self.diff_data.Dpar_unit_sim[0].tostring(), Dpar_unit.tostring())

        # Test the matrices.
        self.assertEqual(self.diff_data.tensor_diag_sim[0].tostring(), tensor_diag.tostring())
        self.assertEqual(self.diff_data.rotation_sim[0].tostring(), rotation.tostring())
        self.assertEqual(self.diff_data.tensor_sim[0].tostring(), tensor.tostring())


    def test_display(self):
        """Test that the contents of the diffusion tensor object can be displayed."""

        print((self.diff_data))


    def test_set_Diso(self):
        """Test that the Diso parameter cannot be set."""

        # Assert that a RelaxError occurs when Diso is set (to the tm value of 10 ns).
        self.assertRaises(RelaxError, setattr, self.diff_data, 'Diso', 1/(6*1e-8))

        # Make sure that the Diso parameter has not been set.
        self.assert_(not hasattr(self.diff_data, 'Diso'))


    def test_set_spheroid_errors(self):
        """Test the setting of spheroidal diffusion tensor parameter errors.

        The following parameter errors will be set:
            - tm: 1 ns
            - Da: 1e3
            - theta: 3 degrees
            - phi: 5 degrees
        """

        # The parameter errors.
        tm = 1e-8
        Da = 1e3
        theta = (3 / 360.0) * 2.0 * pi
        phi = (5 / 360.0) * 2.0 * pi

        # Set the diffusion type.
        self.diff_data.type = 'spheroid'

        # Set the diffusion parameters.
        self.diff_data.tm_err = tm
        self.diff_data.Da_err = Da
        self.diff_data.theta_err = theta
        self.diff_data.phi_err = phi

        # Test the set values.
        self.assertEqual(self.diff_data.type, 'spheroid')
        self.assertEqual(self.diff_data.tm_err, tm)
        self.assertEqual(self.diff_data.Da_err, Da)
        self.assertEqual(self.diff_data.theta_err, theta)
        self.assertEqual(self.diff_data.phi_err, phi)

        # Calculate the diffusion tensor objects.
        Diso, Dpar, Dper, Dratio, Dpar_unit, tensor_diag, rotation, tensor = self.calc_spheroid_objects(tm, Da, theta, phi)

        # Test the automatically created values.
        self.assertEqual(self.diff_data.Diso_err, Diso)
        self.assertEqual(self.diff_data.Dpar_err, Dpar)
        self.assertEqual(self.diff_data.Dper_err, Dper)
        self.assertEqual(self.diff_data.Dratio_err, Dratio)

        # Test the vectors.
        self.assertEqual(self.diff_data.Dpar_unit_err.tostring(), Dpar_unit.tostring())


    def test_set_spheroid_params(self):
        """Test the setting of spheroidal diffusion tensor parameters.

        The following parameters will be set:
            - tm: 20 ns
            - Da: 2e6
            - theta: 60 degrees
            - phi: 290 degrees
        """

        # The parameter values.
        tm = 2e-8
        Da = 2e6
        theta = (60 / 360.0) * 2.0 * pi
        phi = (290 / 360.0) * 2.0 * pi

        # Set the diffusion type.
        self.diff_data.type = 'spheroid'

        # Set the diffusion parameters.
        self.diff_data.tm = tm
        self.diff_data.Da = Da
        self.diff_data.theta = theta
        self.diff_data.phi = phi

        # Test the set values.
        self.assertEqual(self.diff_data.type, 'spheroid')
        self.assertEqual(self.diff_data.tm, tm)
        self.assertEqual(self.diff_data.Da, Da)
        self.assertEqual(self.diff_data.theta, theta)
        self.assertEqual(self.diff_data.phi, phi)

        # Calculate the diffusion tensor objects.
        Diso, Dpar, Dper, Dratio, Dpar_unit, tensor_diag, rotation, tensor = self.calc_spheroid_objects(tm, Da, theta, phi)

        # Test the automatically created values.
        self.assertEqual(self.diff_data.Diso, Diso)
        self.assertEqual(self.diff_data.Dpar, Dpar)
        self.assertEqual(self.diff_data.Dper, Dper)
        self.assertEqual(self.diff_data.Dratio, Dratio)

        # Test the vectors.
        self.assertEqual(self.diff_data.Dpar_unit.tostring(), Dpar_unit.tostring())

        # Test the matrices.
        self.assertEqual(self.diff_data.tensor_diag.tostring(), tensor_diag.tostring())
        self.assertEqual(self.diff_data.rotation.tostring(), rotation.tostring())
        self.assertEqual(self.diff_data.tensor.tostring(), tensor.tostring())


    def test_set_spheroid_sim(self):
        """Test the setting of Monte Carlo simulation spheroidal diffusion tensor parameters.

        Firstly the following parameters will be appended to empty lists:
            - tm: 2 ns
            - Da: 1e5
            - theta: 0 degrees
            - phi: 360 degrees

        These MC sim values will then be explicity overwritten by setting the first elements of the
        lists to:
            - tm: 0.5 ns
            - Da: 3e5
            - theta: 2 degrees
            - phi: 0 degrees
        """

        # Set the diffusion type.
        self.diff_data.type = 'spheroid'

        # Set the MC sim diffusion parameter lists.
        self.diff_data.tm_sim = DiffTensorSimList('tm', self.diff_data)
        self.diff_data.Da_sim = DiffTensorSimList('Da', self.diff_data)
        self.diff_data.theta_sim = DiffTensorSimList('theta', self.diff_data)
        self.diff_data.phi_sim = DiffTensorSimList('phi', self.diff_data)

        # Append the initial values.
        self.diff_data.tm_sim.append(2e-9)
        self.diff_data.Da_sim.append(1e5)
        self.diff_data.theta_sim.append(0.0)
        self.diff_data.phi_sim.append(2.0 * pi)

        # The new MC sim parameter values.
        tm = 0.5e-9
        Da = 3e5
        theta = (2 / 360.0) * 2.0 * pi
        phi = 0.0

        # Set the MC sim parameter values (overwriting the initial values).
        self.diff_data.tm_sim[0] = tm
        self.diff_data.Da_sim[0] = Da
        self.diff_data.theta_sim[0] = theta
        self.diff_data.phi_sim[0] = phi

        # Test the set values.
        self.assertEqual(self.diff_data.type, 'spheroid')
        self.assertEqual(self.diff_data.tm_sim[0], tm)
        self.assertEqual(self.diff_data.Da_sim[0], Da)
        self.assertEqual(self.diff_data.theta_sim[0], theta)
        self.assertEqual(self.diff_data.phi_sim[0], phi)

        # Calculate the diffusion tensor objects.
        Diso, Dpar, Dper, Dratio, Dpar_unit, tensor_diag, rotation, tensor = self.calc_spheroid_objects(tm, Da, theta, phi)

        # Test the automatically created values.
        self.assertEqual(self.diff_data.Diso_sim[0], Diso)
        self.assertEqual(self.diff_data.Dpar_sim[0], Dpar)
        self.assertEqual(self.diff_data.Dper_sim[0], Dper)
        self.assertEqual(self.diff_data.Dratio_sim[0], Dratio)

        # Test the vectors.
        self.assertEqual(self.diff_data.Dpar_unit_sim[0].tostring(), Dpar_unit.tostring())

        # Test the matrices.
        self.assertEqual(self.diff_data.tensor_diag_sim[0].tostring(), tensor_diag.tostring())
        self.assertEqual(self.diff_data.rotation_sim[0].tostring(), rotation.tostring())
        self.assertEqual(self.diff_data.tensor_sim[0].tostring(), tensor.tostring())


    def test_set_tm(self):
        """Test the setting of the tm parameter.

        The tm parameter will be set to 10 ns.  The setting of tm should automatically create the
        Diso parameter.
        """

        # Set the diffusion type.
        self.diff_data.type = 'sphere'

        # Set the tm value to 10 ns.
        self.diff_data.tm = 1e-8

        # Test that the tm parameter has been set correctly.
        self.assert_(hasattr(self.diff_data, 'tm'))
        self.assertEqual(self.diff_data.tm, 1e-8)

        # Test that the Diso parameter has been set correctly.
        self.assert_(hasattr(self.diff_data, 'Diso'))
        self.assertEqual(self.diff_data.Diso, 1/(6*1e-8))
