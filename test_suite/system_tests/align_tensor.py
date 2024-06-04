###############################################################################
#                                                                             #
# Copyright (C) 2006-2010,2012,2014-2015 Edward d'Auvergne                    #
# Copyright (C) 2008 Sebastien Morin                                          #
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

# Python module imports.
from copy import deepcopy
from tempfile import mkstemp

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from test_suite.system_tests.base_classes import SystemTestCase


class Align_tensor(SystemTestCase):
    """Class for testing various aspects specific to the alignment tensors."""

    def setUp(self):
        """Function for initialising a few alignment tensors."""

        # Create a data pipe.
        self.interpreter.pipe.create('test', 'N-state')

        # Temp file name.
        ds.tmpfile_handle, ds.tmpfile = mkstemp()

        # The alignment.
        align_id = 'test'

        # Tensor name lists.
        self.full_list = ['0 full', '1 full', '2 full', '3 full', '4 full']
        self.red_list = ['0 red', '1 red', '2 red', '3 red', '4 red']

        # Error.
        error = 1.47411211147e-05

        # Tensor lists.
        self.tensors_full = [
                (0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083),
                (-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637),
                (-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515),
                (0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05),
                (-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023)
        ]
        self.tensors_red = [
                (-0.0004037026160192775, 0.00023172423501111316, -0.00020915186581478394, -0.00028817367472760139, -8.7172337025481604e-05),
                (0.0003767999506688964, -0.00021492227011444111, 0.00019620694392616774, 0.00027163215478635274, 8.147201253457049e-05),
                (0.00025970120925482461, -0.00014782823602910519, 0.00013565269563569894, 0.00018741173517420359, 5.6252903270026344e-05),
                (0.00014574884684542708, -8.3162940224598374e-05, 7.4927100277784987e-05, 0.00010508245294401461, 3.1156238348722986e-05),
                (-0.00011267453337899962, 6.412308037476237e-05, -5.7897942333203444e-05, -8.1865863377039068e-05, -2.5273427585025123e-05)
        ]

        # Define the domains.
        self.interpreter.domain(id='full')
        self.interpreter.domain(id='red')

        # Set up the tensors.
        for i in range(5):
            # Load the tensor.
            self.interpreter.align_tensor.init(tensor=self.full_list[i], align_id=align_id, params=self.tensors_full[i], param_types=0)
            self.interpreter.align_tensor.init(tensor=self.red_list[i], align_id=align_id, params=self.tensors_red[i], param_types=0)

            # Errors.
            self.interpreter.align_tensor.init(tensor=self.full_list[i], align_id=align_id, params=(error, error, error, error, error), param_types=0, errors=True)
            self.interpreter.align_tensor.init(tensor=self.red_list[i], align_id=align_id, params=(error, error, error, error, error), param_types=0, errors=True)

            # Domain.
            self.interpreter.align_tensor.set_domain(tensor=self.full_list[i], domain='full')
            self.interpreter.align_tensor.set_domain(tensor=self.red_list[i], domain='red')

            # Tensor reductions.
            self.interpreter.align_tensor.reduction(full_tensor=self.full_list[i], red_tensor=self.red_list[i])

        # Reset some values.
        cdp.align_tensors[2].set(param='Axx', value=1)


    def test_align_tensor_matrix_angles(self):
        """Test the operation of the align_tensor.matrix_angles user function for different basis sets.

        This originates from the script in test_suite/shared_data/align_data/basis_sets/.
        """

        # Random tensors of {Axx, Ayy, Axy, Axz, Ayz} generated using random.uniform(0, 1e-4).
        tensor1 = [5.4839183673166663e-05, 3.692459844061351e-05, 1.994164790083226e-05, 4.5945264935308495e-05, 1.0090119622465559e-05]
        tensor2 = [1.5832157768761617e-05, -4.9797877146095514e-05, -3.6007226809999e-05, -3.8175058915299295e-05, 5.3131759988544946e-05]
        tensor3 = [3.892445496049645e-05, -1.7165585393754253e-05, 7.803231512226243e-05, -3.057296854986567e-05, 9.31348723610886e-05]
        tensor4 = [4.6720247808382186e-05, -9.140580842599e-05, -3.415945182796103e-05, -1.7753928806205142e-05, 5.20457038882803e-05]

        # Create a N-state analysis data pipe.
        self.interpreter.pipe.create('basis set comparison', 'N-state')

        # Load the tensors.
        self.interpreter.align_tensor.init(tensor='t1', align_id='t1', params=tuple(tensor1))
        self.interpreter.align_tensor.init(tensor='t2', align_id='t2', params=tuple(tensor2))
        self.interpreter.align_tensor.init(tensor='t3', align_id='t3', params=tuple(tensor3))
        self.interpreter.align_tensor.init(tensor='t4', align_id='t4', params=tuple(tensor4))

        # Display.
        self.interpreter.align_tensor.display()

        # The standard inter-matrix angles.
        self.interpreter.align_tensor.matrix_angles(basis_set='matrix')
        self.assertAlmostEqual(cdp.align_tensors.angles[0, 0], 0.000000000000000)
        self.assertAlmostEqual(cdp.align_tensors.angles[0, 1], 2.075565413247085)
        self.assertAlmostEqual(cdp.align_tensors.angles[0, 2], 1.338099052806276)
        self.assertAlmostEqual(cdp.align_tensors.angles[0, 3], 1.931864731843497)
        self.assertAlmostEqual(cdp.align_tensors.angles[1, 0], 2.075565413247085)
        self.assertAlmostEqual(cdp.align_tensors.angles[1, 1], 0.000000000000000)
        self.assertAlmostEqual(cdp.align_tensors.angles[1, 2], 1.238391416802885)
        self.assertAlmostEqual(cdp.align_tensors.angles[1, 3], 0.425283739619488)
        self.assertAlmostEqual(cdp.align_tensors.angles[2, 0], 1.338099052806276)
        self.assertAlmostEqual(cdp.align_tensors.angles[2, 1], 1.238391416802885)
        self.assertAlmostEqual(cdp.align_tensors.angles[2, 2], 0.000000000000000)
        self.assertAlmostEqual(cdp.align_tensors.angles[2, 3], 1.269973710252322)
        self.assertAlmostEqual(cdp.align_tensors.angles[3, 0], 1.931864731843497)
        self.assertAlmostEqual(cdp.align_tensors.angles[3, 1], 0.425283739619488)
        self.assertAlmostEqual(cdp.align_tensors.angles[3, 2], 1.269973710252322)
        self.assertAlmostEqual(cdp.align_tensors.angles[3, 3], 0.000000014901161)

        # The inter-tensor vector angles for the irreducible 5D basis set {A-2, A-1, A0, A1, A2}.
        self.interpreter.align_tensor.matrix_angles(basis_set='irreducible 5D')
        self.assertAlmostEqual(cdp.align_tensors.angles[0, 0], 0.000000000000000)
        self.assertAlmostEqual(cdp.align_tensors.angles[0, 1], 2.075565413247085)
        self.assertAlmostEqual(cdp.align_tensors.angles[0, 2], 1.338099052806276)
        self.assertAlmostEqual(cdp.align_tensors.angles[0, 3], 1.931864731843497)
        self.assertAlmostEqual(cdp.align_tensors.angles[1, 0], 2.075565413247085)
        self.assertAlmostEqual(cdp.align_tensors.angles[1, 1], 0.000000000000000)
        self.assertAlmostEqual(cdp.align_tensors.angles[1, 2], 1.238391416802885)
        self.assertAlmostEqual(cdp.align_tensors.angles[1, 3], 0.425283739619488)
        self.assertAlmostEqual(cdp.align_tensors.angles[2, 0], 1.338099052806276)
        self.assertAlmostEqual(cdp.align_tensors.angles[2, 1], 1.238391416802885)
        self.assertAlmostEqual(cdp.align_tensors.angles[2, 2], 0.000000021073424)
        self.assertAlmostEqual(cdp.align_tensors.angles[2, 3], 1.269973710252322)
        self.assertAlmostEqual(cdp.align_tensors.angles[3, 0], 1.931864731843497)
        self.assertAlmostEqual(cdp.align_tensors.angles[3, 1], 0.425283739619488)
        self.assertAlmostEqual(cdp.align_tensors.angles[3, 2], 1.269973710252322)
        self.assertAlmostEqual(cdp.align_tensors.angles[3, 3], 0.000000021073424)

        # The inter-tensor vector angles for the unitary 9D basis set {Sxx, Sxy, Sxz, Syx, Syy, Syz, Szx, Szy, Szz}.
        self.interpreter.align_tensor.matrix_angles(basis_set='unitary 9D')
        self.assertAlmostEqual(cdp.align_tensors.angles[0, 0], 0.000000000000000)
        self.assertAlmostEqual(cdp.align_tensors.angles[0, 1], 2.075565413247085)
        self.assertAlmostEqual(cdp.align_tensors.angles[0, 2], 1.338099052806276)
        self.assertAlmostEqual(cdp.align_tensors.angles[0, 3], 1.931864731843497)
        self.assertAlmostEqual(cdp.align_tensors.angles[1, 0], 2.075565413247085)
        self.assertAlmostEqual(cdp.align_tensors.angles[1, 1], 0.000000014901161)
        self.assertAlmostEqual(cdp.align_tensors.angles[1, 2], 1.238391416802885)
        self.assertAlmostEqual(cdp.align_tensors.angles[1, 3], 0.425283739619488)
        self.assertAlmostEqual(cdp.align_tensors.angles[2, 0], 1.338099052806276)
        self.assertAlmostEqual(cdp.align_tensors.angles[2, 1], 1.238391416802885)
        self.assertAlmostEqual(cdp.align_tensors.angles[2, 2], 0.000000000000000)
        self.assertAlmostEqual(cdp.align_tensors.angles[2, 3], 1.269973710252322)
        self.assertAlmostEqual(cdp.align_tensors.angles[3, 0], 1.931864731843497)
        self.assertAlmostEqual(cdp.align_tensors.angles[3, 1], 0.425283739619488)
        self.assertAlmostEqual(cdp.align_tensors.angles[3, 2], 1.269973710252322)
        self.assertAlmostEqual(cdp.align_tensors.angles[3, 3], 0.000000014901161)

        # The inter-tensor vector angles for the unitary 5D basis set {Sxx, Syy, Sxy, Sxz, Syz}.
        self.interpreter.align_tensor.matrix_angles(basis_set='unitary 5D')
        self.assertAlmostEqual(cdp.align_tensors.angles[0, 0], 0.000000000000000)
        self.assertAlmostEqual(cdp.align_tensors.angles[0, 1], 1.962377927826435)
        self.assertAlmostEqual(cdp.align_tensors.angles[0, 2], 1.334149185082829)
        self.assertAlmostEqual(cdp.align_tensors.angles[0, 3], 1.747728360218234)
        self.assertAlmostEqual(cdp.align_tensors.angles[1, 0], 1.962377927826435)
        self.assertAlmostEqual(cdp.align_tensors.angles[1, 1], 0.000000000000000)
        self.assertAlmostEqual(cdp.align_tensors.angles[1, 2], 1.163535022090889)
        self.assertAlmostEqual(cdp.align_tensors.angles[1, 3], 0.449110033170688)
        self.assertAlmostEqual(cdp.align_tensors.angles[2, 0], 1.334149185082829)
        self.assertAlmostEqual(cdp.align_tensors.angles[2, 1], 1.163535022090889)
        self.assertAlmostEqual(cdp.align_tensors.angles[2, 2], 0.000000000000000)
        self.assertAlmostEqual(cdp.align_tensors.angles[2, 3], 1.180324869602255)
        self.assertAlmostEqual(cdp.align_tensors.angles[3, 0], 1.747728360218234)
        self.assertAlmostEqual(cdp.align_tensors.angles[3, 1], 0.449110033170688)
        self.assertAlmostEqual(cdp.align_tensors.angles[3, 2], 1.180324869602255)
        self.assertAlmostEqual(cdp.align_tensors.angles[3, 3], 0.000000000000000)

        # The inter-tensor vector angles for the geometric 5D basis set {Szz, Sxxyy, Sxy, Sxz, Syz}.
        self.interpreter.align_tensor.matrix_angles(basis_set='geometric 5D')
        self.assertAlmostEqual(cdp.align_tensors.angles[0, 0], 0.000000000000000)
        self.assertAlmostEqual(cdp.align_tensors.angles[0, 1], 1.924475705542377)
        self.assertAlmostEqual(cdp.align_tensors.angles[0, 2], 1.290778333130633)
        self.assertAlmostEqual(cdp.align_tensors.angles[0, 3], 1.724794814547786)
        self.assertAlmostEqual(cdp.align_tensors.angles[1, 0], 1.924475705542377)
        self.assertAlmostEqual(cdp.align_tensors.angles[1, 1], 0.000000021073424)
        self.assertAlmostEqual(cdp.align_tensors.angles[1, 2], 1.128650397698967)
        self.assertAlmostEqual(cdp.align_tensors.angles[1, 3], 0.418891267835127)
        self.assertAlmostEqual(cdp.align_tensors.angles[2, 0], 1.290778333130633)
        self.assertAlmostEqual(cdp.align_tensors.angles[2, 1], 1.128650397698967)
        self.assertAlmostEqual(cdp.align_tensors.angles[2, 2], 0.000000000000000)
        self.assertAlmostEqual(cdp.align_tensors.angles[2, 3], 1.126308408980378)
        self.assertAlmostEqual(cdp.align_tensors.angles[3, 0], 1.724794814547786)
        self.assertAlmostEqual(cdp.align_tensors.angles[3, 1], 0.418891267835127)
        self.assertAlmostEqual(cdp.align_tensors.angles[3, 2], 1.126308408980378)
        self.assertAlmostEqual(cdp.align_tensors.angles[3, 3], 0.000000014901161)


    def test_align_tensor_svd(self):
        """Test the operation of the align_tensor.svd user function for different basis sets.

        This originates from the script in test_suite/shared_data/align_data/basis_sets/.
        """

        # Random tensors of {Axx, Ayy, Axy, Axz, Ayz} generated using random.uniform(0, 1e-4).
        tensor1 = [5.4839183673166663e-05, 3.692459844061351e-05, 1.994164790083226e-05, 4.5945264935308495e-05, 1.0090119622465559e-05]
        tensor2 = [1.5832157768761617e-05, -4.9797877146095514e-05, -3.6007226809999e-05, -3.8175058915299295e-05, 5.3131759988544946e-05]
        tensor3 = [3.892445496049645e-05, -1.7165585393754253e-05, 7.803231512226243e-05, -3.057296854986567e-05, 9.31348723610886e-05]
        tensor4 = [4.6720247808382186e-05, -9.140580842599e-05, -3.415945182796103e-05, -1.7753928806205142e-05, 5.20457038882803e-05]

        # Create a N-state analysis data pipe.
        self.interpreter.pipe.create('basis set comparison', 'N-state')

        # Load the tensors.
        self.interpreter.align_tensor.init(tensor='t1', align_id='t1', params=tuple(tensor1))
        self.interpreter.align_tensor.init(tensor='t2', align_id='t2', params=tuple(tensor2))
        self.interpreter.align_tensor.init(tensor='t3', align_id='t3', params=tuple(tensor3))
        self.interpreter.align_tensor.init(tensor='t4', align_id='t4', params=tuple(tensor4))

        # Display.
        self.interpreter.align_tensor.display()

        # SVD for the irreducible 5D basis set {A-2, A-1, A0, A1, A2}.
        self.interpreter.align_tensor.svd(basis_set='irreducible 5D')
        self.assertAlmostEqual(cdp.align_tensors.cond_num, 6.131054731740254)
        self.assertAlmostEqual(cdp.align_tensors.singular_vals[0], 0.000413550754079)
        self.assertAlmostEqual(cdp.align_tensors.singular_vals[1], 0.000346772331066)
        self.assertAlmostEqual(cdp.align_tensors.singular_vals[2], 0.000185983409775)
        self.assertAlmostEqual(cdp.align_tensors.singular_vals[3], 0.000067451812481)

        # SVD for the unitary 9D basis set {Sxx, Sxy, Sxz, Syx, Syy, Syz, Szx, Szy, Szz}.
        self.interpreter.align_tensor.svd(basis_set='unitary 9D')
        self.assertAlmostEqual(cdp.align_tensors.cond_num, 6.131054731740256)
        self.assertAlmostEqual(cdp.align_tensors.singular_vals[0], 0.000319487975056)
        self.assertAlmostEqual(cdp.align_tensors.singular_vals[1], 0.000267898410932)
        self.assertAlmostEqual(cdp.align_tensors.singular_vals[2], 0.000143681186401)
        self.assertAlmostEqual(cdp.align_tensors.singular_vals[3], 0.000052109790083)

        # SVD for the unitary 5D basis set {Sxx, Syy, Sxy, Sxz, Syz}.
        self.interpreter.align_tensor.svd(basis_set='unitary 5D')
        self.assertAlmostEqual(cdp.align_tensors.cond_num, 6.503663323975970)
        self.assertAlmostEqual(cdp.align_tensors.singular_vals[0], 0.000250394766677)
        self.assertAlmostEqual(cdp.align_tensors.singular_vals[1], 0.000177094839440)
        self.assertAlmostEqual(cdp.align_tensors.singular_vals[2], 0.000106716235329)
        self.assertAlmostEqual(cdp.align_tensors.singular_vals[3], 0.000038500573324)

        # SVD for the geometric 5D basis set {Szz, Sxxyy, Sxy, Sxz, Syz}.
        self.interpreter.align_tensor.svd(basis_set='geometric 5D')
        self.assertAlmostEqual(cdp.align_tensors.cond_num, 6.982475764795178)
        self.assertAlmostEqual(cdp.align_tensors.singular_vals[0], 0.000304033216708)
        self.assertAlmostEqual(cdp.align_tensors.singular_vals[1], 0.000201547771250)
        self.assertAlmostEqual(cdp.align_tensors.singular_vals[2], 0.000125447137629)
        self.assertAlmostEqual(cdp.align_tensors.singular_vals[3], 0.000043542323232)


    def test_copy(self):
        """Test the copying of alignment tensors (to catch U{bug #20338<https://web.archive.org/web/https://gna.org/bugs/?20338>}."""

        # First reset.
        self.interpreter.reset()

        # Create a data pipe.
        self.interpreter.pipe.create('copy test', 'N-state')

        # Initialise one tensor.
        self.interpreter.align_tensor.init(tensor='orig', align_id='test', params=self.tensors_full[0], param_types=0)

        # Copy the tensor.
        self.interpreter.align_tensor.copy(tensor_from='orig', tensor_to='new')

        # Checks.
        self.assertEqual(len(cdp.align_tensors), 2)
        self.assertEqual(cdp.align_tensors[0].name, 'orig')
        self.assertEqual(cdp.align_tensors[1].name, 'new')


    def test_copy_pipes(self):
        """Test the copying of alignment tensors between data pipes."""

        # First reset.
        self.interpreter.reset()

        # Create two data pipes.
        self.interpreter.pipe.create('target', 'N-state')
        self.interpreter.pipe.create('source', 'N-state')

        # Initialise one tensor.
        self.interpreter.align_tensor.init(tensor='orig', align_id='test', params=self.tensors_full[0], param_types=0)

        # Copy the tensor.
        self.interpreter.align_tensor.copy(pipe_from='source', pipe_to='target')

        # Checks.
        self.interpreter.pipe.switch('target')
        self.assertEqual(len(cdp.align_tensors), 1)
        self.assertEqual(cdp.align_tensors[0].name, 'orig')


    def test_copy_pipes_sims(self):
        """Test the copying of alignment tensor Monte Carlo simulations between data pipes."""

        # First reset.
        self.interpreter.reset()

        # Create two data pipes.
        self.interpreter.pipe.create('target', 'N-state')
        self.interpreter.pipe.create('source', 'N-state')

        # Initialise one tensor.
        self.interpreter.align_tensor.init(tensor='orig', align_id='test', params=self.tensors_full[0], param_types=0)

        # Set up the number of simulations.
        sim_number = 10
        cdp.align_tensors[0].set_sim_num(sim_number)

        # Initialise simulation tensors.
        for object_name in ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz']:
            for i in range(sim_number):
                cdp.align_tensors[0].set(param=object_name, value=deepcopy(getattr(cdp.align_tensors[0], object_name)), category='sim', sim_index=i)

        # Copy the tensor.
        self.interpreter.align_tensor.copy(pipe_from='source', pipe_to='target')

        # Checks.
        self.interpreter.pipe.switch('target')
        self.assertEqual(len(cdp.align_tensors), 1)
        self.assertEqual(cdp.align_tensors[0].name, 'orig')


    def test_fix(self):
        """Test the align_tensor.fix user function."""

        # Fix all tensors.
        self.interpreter.align_tensor.fix()

        # Unfix one tensor.
        self.interpreter.align_tensor.fix('2 full', fixed=False)

        # Check the fixed flags.
        flags = [True]*10
        flags[4] = False
        for i in range(10):
            print("Checking the tensor %s: '%s'." % (i, cdp.align_tensors[i].name))
            self.assertEqual(cdp.align_tensors[i].fixed, flags[i])


    def test_to_and_from_xml(self):
        """Test the conversion to and from XML."""

        # Save the data pipe.
        self.interpreter.results.write(ds.tmpfile, dir=None, compress_type=0, force=True)

        # Create a new data pipe.
        self.interpreter.pipe.create('new', 'N-state')

        # Load the data.
        self.interpreter.results.read(ds.tmpfile, dir=None)

        # Checks.
        self.assertEqual(len(cdp.align_tensors), 10)
        self.assertTrue(hasattr(cdp.align_tensors, 'reduction'))
        for i in range(5):
            # Full tensors.
            if i == 1:
                self.assertAlmostEqual(cdp.align_tensors[i*2].Axx, 1.0)
            else:
                self.assertAlmostEqual(cdp.align_tensors[i*2].Sxx, self.tensors_full[i][0])
            self.assertAlmostEqual(cdp.align_tensors[i*2].Syy, self.tensors_full[i][1])
            self.assertAlmostEqual(cdp.align_tensors[i*2].Sxy, self.tensors_full[i][2])
            self.assertAlmostEqual(cdp.align_tensors[i*2].Sxz, self.tensors_full[i][3])
            self.assertAlmostEqual(cdp.align_tensors[i*2].Syz, self.tensors_full[i][4])
            self.assertEqual(cdp.align_tensors[i*2].name, self.full_list[i])

            # Reduced tensors.
            self.assertAlmostEqual(cdp.align_tensors[i*2+1].Sxx, self.tensors_red[i][0])
            self.assertAlmostEqual(cdp.align_tensors[i*2+1].Syy, self.tensors_red[i][1])
            self.assertAlmostEqual(cdp.align_tensors[i*2+1].Sxy, self.tensors_red[i][2])
            self.assertAlmostEqual(cdp.align_tensors[i*2+1].Sxz, self.tensors_red[i][3])
            self.assertAlmostEqual(cdp.align_tensors[i*2+1].Syz, self.tensors_red[i][4])
            self.assertEqual(cdp.align_tensors[i*2+1].name, self.red_list[i])

            # Reduction.
            self.assertEqual(cdp.align_tensors.reduction[i], [i*2, i*2+1])
