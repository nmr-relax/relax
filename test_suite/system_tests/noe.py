###############################################################################
#                                                                             #
# Copyright (C) 2006-2014 Edward d'Auvergne                                   #
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
from os import F_OK, access, sep
from tempfile import mkdtemp, mktemp

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from pipe_control.mol_res_spin import spin_loop
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Noe(SystemTestCase):
    """Class for testing various aspects specific to the NOE analysis."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('noe', 'noe')

        # Create a temporary file.
        ds.tmpfile = mktemp()

        # Create a temporary directory for dumping files.
        ds.tmpdir = mkdtemp()
        self.tmpdir = ds.tmpdir


    def test_bug_21562_noe_replicate_fail(self):
        """Catch U{bug #21562<https://gna.org/bugs/?21562>}, the failure of the NOE analysis when replicated spectra are used."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'noe'+sep+'bug_21562_noe_replicate_fail.py')

        # Open the NOE output file.
        file = open(ds.tmpfile)
        lines = file.readlines()
        file.close()

        # How the file should look like.
        data = [
            "# Parameter description:  The steady-state NOE value.\n",
            "#\n",
            "# mol_name       res_num    res_name    spin_num    spin_name    value                   error                   \n",
            "2AT7_fmf_mol1    12         PHE         150         N               0.803029108487728      0.0199040298831904    \n",
            "2AT7_fmf_mol1    13         ASN         170         N               0.829415981681132      0.0339996453012768    \n",
            "2AT7_fmf_mol1    14         LYS         184         N               0.755789564728523      0.0250941717735858    \n"
        ]

        # Printout of the real and generated data.
        print("\n\nThe real data:")
        for i in range(len(lines)):
            print(repr(data[i]))
        print("\nThe generated data:")
        for i in range(len(lines)):
            print(repr(lines[i]))
        print("\n")

        # Check each line.
        for i in range(len(lines)):
            self.assertEqual(data[i], lines[i])


    def test_bug_21591_noe_calculation_fail(self):
        """Catch U{bug #21591<https://gna.org/bugs/?21591>}, the failure of the NOE analysis."""

        # Generate the sequence.
        self.interpreter.spin.create(mol_name='XYZ_mol1', res_num=120, res_name='GLY', spin_num=1865, spin_name='N')

        # Load the reference spectrum and saturated spectrum peak intensities.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists'
        self.interpreter.spectrum.read_intensities(file='noe.140109.8.001.list', dir=path, spectrum_id='ref_ave')
        self.interpreter.spectrum.read_intensities(file='noe.140109.8.002.list', dir=path, spectrum_id='sat_ave')

        # Set the spectrum types.
        self.interpreter.noe.spectrum_type('ref', 'ref_ave')
        self.interpreter.noe.spectrum_type('sat', 'sat_ave')

        # Set the errors.
        self.interpreter.spectrum.baseplane_rmsd(error=1.3e06, spectrum_id='ref_ave')
        self.interpreter.spectrum.baseplane_rmsd(error=1.4e06, spectrum_id='sat_ave')

        # Peak intensity error analysis.
        self.interpreter.spectrum.error_analysis()

        # Calculate the NOEs.
        self.interpreter.calc()

        # Save the NOEs.
        self.interpreter.value.write(param='noe', file=ds.tmpfile)

        # Open the NOE output file.
        file = open(ds.tmpfile)
        lines = file.readlines()
        file.close()

        # How the file should look like.
        data = [
            "# Parameter description:  The steady-state NOE value.\n",
            "#\n",
            "# mol_name    res_num    res_name    spin_num    spin_name    value                   error                   \n",
            "XYZ_mol1      120        GLY         1865        N               0.520373965716017       0.208104738641507    \n",
        ]

        # Printout of the real and generated data.
        print("\n\nThe real data:")
        for i in range(len(lines)):
            print(repr(data[i]))
        print("\nThe generated data:")
        for i in range(len(lines)):
            print(repr(lines[i]))
        print("\n")

        # Check each line.
        for i in range(len(lines)):
            self.assertEqual(data[i], lines[i])


    def test_noe_analysis(self):
        """Test the NOE analysis.

        The test has been modified to also catch U{bug #21863<https://gna.org/bugs/?21863>}.
        """

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'noe'+sep+'noe.py')

        # The real data.
        sat = [5050.0, 51643.0, 53663.0, -65111.0, -181131.0, -105322.0]
        ref = [148614.0, 166842.0, 128690.0, 99566.0, 270047.0, 130959.0]
        noe = [0.033980647852826784, 0.30953237194471417, 0.4169943274535706, -0.6539481349054899, -0.6707387973204665, -0.8042364404126482]
        noe_err = [0.02020329903276632, 0.2320024671657343, 0.026067523940084526, 0.038300618865378507, 0.014260663438353431, 0.03183614777183591]

        # Check the data.
        i = 0
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Check the intensity data.
            self.assertEqual(sat[i], spin.peak_intensity['sat_ave'])
            self.assertEqual(ref[i], spin.peak_intensity['ref_ave'])

            # Check the NOE data.
            self.assertEqual(noe[i], spin.noe)
            self.assertAlmostEqual(noe_err[i], spin.noe_err)

            # Increment the spin index.
            i += 1

        # The real Grace file data.
        data = [[
            '@version 50121\n',
            '@page size 842, 595\n',
            '@with g0\n',
            '@    view 0.15, 0.15, 1.28, 0.85\n',
            '@    xaxis  label "Residue number"\n',
            '@    xaxis  label char size 1.00\n',
            '@    xaxis  tick major size 0.50\n',
            '@    xaxis  tick major linewidth 0.5\n',
            '@    xaxis  tick minor linewidth 0.5\n',
            '@    xaxis  tick minor size 0.25\n',
            '@    xaxis  ticklabel char size 0.70\n',
            '@    yaxis  label "\\qPeak intensities\\Q"\n',
            '@    yaxis  label char size 1.00\n',
            '@    yaxis  tick major size 0.50\n',
            '@    yaxis  tick major linewidth 0.5\n',
            '@    yaxis  tick minor linewidth 0.5\n',
            '@    yaxis  tick minor size 0.25\n',
            '@    yaxis  ticklabel char size 0.70\n',
            '@    legend on\n',
            '@    legend box fill pattern 1\n',
            '@    legend char size 1.0\n',
            '@    frame linewidth 0.5\n',
            '@    s0 symbol 1\n',
            '@    s0 symbol size 0.45\n',
            '@    s0 symbol linewidth 0.5\n',
            '@    s0 errorbar size 0.5\n',
            '@    s0 errorbar linewidth 0.5\n',
            '@    s0 errorbar riser linewidth 0.5\n',
            '@    s0 legend "ref_ave"\n',
            '@    s1 symbol 2\n',
            '@    s1 symbol size 0.45\n',
            '@    s1 symbol linewidth 0.5\n',
            '@    s1 errorbar size 0.5\n',
            '@    s1 errorbar linewidth 0.5\n',
            '@    s1 errorbar riser linewidth 0.5\n',
            '@    s1 legend "sat_ave"\n',
            '@target G0.S0\n',
            '@type xydy\n',
            '4                              148614.000000000000000         3600.000000000000000          \n',
            '5                              166842.000000000000000         122000.000000000000000        \n',
            '6                              128690.000000000000000         3600.000000000000000          \n',
            '40                             99566.000000000000000          3600.000000000000000          \n',
            '40                             270047.000000000000000         3600.000000000000000          \n',
            '55                             130959.000000000000000         3600.000000000000000          \n',
            '&\n',
            '@target G0.S1\n',
            '@type xydy\n',
            '4                              5050.000000000000000           3000.000000000000000          \n',
            '5                              51643.000000000000000          8500.000000000000000          \n',
            '6                              53663.000000000000000          3000.000000000000000          \n',
            '40                             -65111.000000000000000         3000.000000000000000          \n',
            '40                             -181131.000000000000000        3000.000000000000000          \n',
            '55                             -105322.000000000000000        3000.000000000000000          \n',
            '&\n',
            '@with g0\n',
            '@autoscale\n'
        ], [
            '@version 50121\n',
            '@page size 842, 595\n',
            '@with g0\n',
            '@    view 0.15, 0.15, 1.28, 0.85\n',
            '@    xaxis  label "Residue number"\n',
            '@    xaxis  label char size 1.00\n',
            '@    xaxis  tick major size 0.50\n',
            '@    xaxis  tick major linewidth 0.5\n',
            '@    xaxis  tick minor linewidth 0.5\n',
            '@    xaxis  tick minor size 0.25\n',
            '@    xaxis  ticklabel char size 0.70\n',
            '@    yaxis  label "\\qNOE\\Q"\n',
            '@    yaxis  label char size 1.00\n',
            '@    yaxis  tick major size 0.50\n',
            '@    yaxis  tick major linewidth 0.5\n',
            '@    yaxis  tick minor linewidth 0.5\n',
            '@    yaxis  tick minor size 0.25\n',
            '@    yaxis  ticklabel char size 0.70\n',
            '@    legend on\n',
            '@    legend box fill pattern 1\n',
            '@    legend char size 1.0\n',
            '@    frame linewidth 0.5\n',
            '@    s0 symbol 1\n',
            '@    s0 symbol size 0.45\n',
            '@    s0 symbol linewidth 0.5\n',
            '@    s0 errorbar size 0.5\n',
            '@    s0 errorbar linewidth 0.5\n',
            '@    s0 errorbar riser linewidth 0.5\n',
            '@    s0 legend "N spins"\n',
            '@    s1 symbol 2\n',
            '@    s1 symbol size 0.45\n',
            '@    s1 symbol linewidth 0.5\n',
            '@    s1 errorbar size 0.5\n',
            '@    s1 errorbar linewidth 0.5\n',
            '@    s1 errorbar riser linewidth 0.5\n',
            '@    s1 legend "NE1 spins"\n',
            '@target G0.S0\n',
            '@type xydy\n',
            '4                              0.033980647852827              0.020203299032766             \n',
            '5                              0.309532371944714              0.232002467165734             \n',
            '6                              0.416994327453571              0.026067523940085             \n',
            '40                             -0.653948134905490             0.038300618865379             \n',
            '55                             -0.804236440412648             0.031836147771836             \n',
            '&\n',
            '@target G0.S1\n',
            '@type xydy\n',
            '40                             -0.670738797320466             0.014260663438353             \n',
            '&\n',
            '@with g0\n',
            '@autoscale\n'
        ]]

        # Check the Grace files.
        ids = ['intensities', 'noe']
        for i in range(len(ids)):
            # The file name.
            file_name = "%s.agr" % ids[i]

            # Does the file exist?
            self.assert_(access(ds.tmpdir+sep+file_name, F_OK))

            # Open the file and extract the contents.
            file = open(ds.tmpdir + sep + file_name)
            lines = file.readlines()
            file.close()

            # Nothing.
            self.assertNotEqual(lines, [])

            # Check the file contents.
            for j in range(len(lines)):
                print("            '%s\\n'," % lines[j][:-1].replace('"', "\\\""))
            for j in range(len(lines)):
                self.assertEqual(data[i][j], lines[j])
