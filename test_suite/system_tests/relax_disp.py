###############################################################################
#                                                                             #
# Copyright (C) 2006-2013 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
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
from os import sep
from shutil import rmtree
from tempfile import mkdtemp

# relax module imports.
from auto_analyses import relax_disp
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Relax_disp(SystemTestCase):
    """Class for testing various aspects specific to relaxation dispersion curve-fitting."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('relax_disp', 'relax_disp')

        # Create a temporary directory for dumping files.
        ds.tmpdir = mkdtemp()
        self.tmpdir = ds.tmpdir


    def tearDown(self):
        """Reset the relax data storage object."""

        # Remove the temporary directory.
        rmtree(self.tmpdir)

        # Reset the relax data storage object.
        ds.__reset__()


    def test_hansen_cpmg_data_LM63(self):
        """Optimisation of Dr. Flemming Hansen's CPMG data to the LM63 dispersion model.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Set the model.
        ds.models = ['LM63']

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'hansen_data.py')

        # Printout.
        print("\n\nOptimised parameters:\n")
        spin70 = cdp.mol[0].res[0].spin[0]
        spin71 = cdp.mol[0].res[1].spin[0]
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.8g %20.8g" % ("R2 (500 MHz)", spin70.r2[0], spin71.r2[0]))
        print("%-20s %20.8g %20.8g" % ("R2 (800 MHz)", spin70.r2[1], spin71.r2[1]))
        print("%-20s %20.8g %20.8g" % ("phi_ex", spin70.phi_ex, spin71.phi_ex))
        print("%-20s %20.8g %20.8g" % ("phi_ex (500 MHz)", spin70.phi_ex * cdp.spectrometer_frq_list[0]**2, spin71.phi_ex * cdp.spectrometer_frq_list[0]**2))
        print("%-20s %20.8g %20.8g" % ("phi_ex (800 MHz)", spin70.phi_ex * cdp.spectrometer_frq_list[1]**2, spin71.phi_ex * cdp.spectrometer_frq_list[1]**2))
        print("%-20s %20.8g %20.8g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.8g %20.8g\n" % ("chi2", spin70.chi2, spin71.chi2))
        print("%-20s %20.8g %20.8g" % ("CPMGFit Rex (500)", spin70.phi_ex * cdp.spectrometer_frq_list[0]**2 / spin70.kex, spin71.phi_ex * cdp.spectrometer_frq_list[0]**2 / spin71.kex))
        print("%-20s %20.8g %20.8g" % ("CPMGFit Rex (800)", spin70.phi_ex * cdp.spectrometer_frq_list[1]**2 / spin70.kex, spin71.phi_ex * cdp.spectrometer_frq_list[1]**2 / spin71.kex))
        print("%-20s %20.8g %20.8g" % ("CPMGFit tau", 2/spin70.kex, 2/spin71.kex))


    def test_hansen_cpmg_data_CR72(self):
        """Optimisation of Dr. Flemming Hansen's CPMG data to the CR72 dispersion model.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Set the model.
        ds.models = ['CR72']

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'hansen_data.py')


    def test_hansen_cpmgfit_input(self):
        """Conversion of Dr. Flemming Hansen's CPMG R2eff values into input files for CPMGFit.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Load the state, preserving the temp directory.
        tmpdir = ds.tmpdir
        state = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Hansen'+sep+'r2eff_values'
        self.interpreter.state.load(state, force=True)
        ds.tmpdir = tmpdir

        # Set up the model.
        self.interpreter.relax_disp.select_model('LM63')

        # Generate the input files.
        self.interpreter.relax_disp.cpmgfit_input(force=True, dir=ds.tmpdir)

        # What the files should contain.
        batch_file = ['#! /bin/sh\n', '\n', 'cpmgfit -xmgr -f spin_:70@N.in\n', 'cpmgfit -xmgr -f spin_:71@N.in\n']
        spin1 = [
            'title :70@N\n',
            'fields 2 11.7432964915 18.7892743865\n',
            'function CPMG\n',
            'R2 1 10 20\n',
            'Rex 0 100.0 100\n',
            'tex 0 10.0 100\n',
            'xmgr\n',
            '@ xaxis label "1/tcp (1/ms)"\n',
            '@ yaxis label "R2(tcp) (rad/s)"\n',
            '@ xaxis ticklabel format decimal\n',
            '@ yaxis ticklabel format decimal\n',
            '@ xaxis ticklabel char size 0.8\n',
            '@ yaxis ticklabel char size 0.8\n',
            '@ world xmin 0.0\n',
            'data\n',
            '0.066667             16.045541            0.646426             11.743296           \n',
            '0.133333             14.877925            0.506308             11.743296           \n',
            '0.200000             14.357820            0.623633             11.743296           \n',
            '0.266667             12.664495            0.601993             11.743296           \n',
            '0.333333             12.363205            0.597972             11.743296           \n',
            '0.400000             11.092532            0.583223             11.743296           \n',
            '0.466667             10.566090            0.577133             11.743296           \n',
            '0.533333             9.805807             0.468139             11.743296           \n',
            '0.600000             9.564301             0.565981             11.743296           \n',
            '0.666667             9.015634             0.559685             11.743296           \n',
            '0.733333             8.607765             0.555779             11.743296           \n',
            '0.800000             8.279997             0.552292             11.743296           \n',
            '0.866667             8.474536             0.554452             11.743296           \n',
            '0.933333             8.158973             0.457694             11.743296           \n',
            '1.000000             7.988631             0.549378             11.743296           \n',
            '0.066667             22.224914            0.279012             18.789274           \n',
            '0.133333             21.230874            0.212524             18.789274           \n',
            '0.200000             20.603704            0.268504             18.789274           \n',
            '0.266667             20.327797            0.266352             18.789274           \n',
            '0.333333             18.855377            0.257852             18.789274           \n',
            '0.400000             18.537531            0.255847             18.789274           \n',
            '0.466667             17.508069            0.250116             18.789274           \n',
            '0.533333             16.035604            0.193445             18.789274           \n',
            '0.600000             15.168192            0.237554             18.789274           \n',
            '0.666667             14.431802            0.234056             18.789274           \n',
            '0.733333             14.034137            0.232203             18.789274           \n',
            '0.800000             12.920148            0.226811             18.789274           \n',
            '0.866667             12.653673            0.225537             18.789274           \n',
            '0.933333             12.610864            0.183112             18.789274           \n',
            '1.000000             11.969303            0.222437             18.789274           \n'
        ]
        spin2 = [
            'title :71@N\n',
            'fields 2 11.7432964915 18.7892743865\n',
            'function CPMG\n',
            'R2 1 10 20\n',
            'Rex 0 100.0 100\n',
            'tex 0 10.0 100\n',
            'xmgr\n',
            '@ xaxis label "1/tcp (1/ms)"\n',
            '@ yaxis label "R2(tcp) (rad/s)"\n',
            '@ xaxis ticklabel format decimal\n',
            '@ yaxis ticklabel format decimal\n',
            '@ xaxis ticklabel char size 0.8\n',
            '@ yaxis ticklabel char size 0.8\n',
            '@ world xmin 0.0\n',
            'data\n',
            '0.066667             7.044342             0.353119             11.743296           \n',
            '0.133333             6.781033             0.294209             11.743296           \n',
            '0.200000             6.467623             0.349666             11.743296           \n',
            '0.266667             6.333340             0.349164             11.743296           \n',
            '0.333333             6.323238             0.348851             11.743296           \n',
            '0.400000             6.005245             0.346720             11.743296           \n',
            '0.466667             5.767052             0.345395             11.743296           \n',
            '0.533333             5.476968             0.289667             11.743296           \n',
            '0.600000             5.469949             0.343719             11.743296           \n',
            '0.666667             5.295113             0.342447             11.743296           \n',
            '0.733333             5.435648             0.343768             11.743296           \n',
            '0.800000             5.410400             0.343286             11.743296           \n',
            '0.866667             5.437554             0.343403             11.743296           \n',
            '0.933333             5.176844             0.287960             11.743296           \n',
            '1.000000             5.227232             0.341943             11.743296           \n'
        ]

        # Check the batch file.
        print("\nChecking the batch file.")
        file = open("%s%sbatch_run.sh" % (ds.tmpdir, sep))
        lines = file.readlines()
        file.close()
        for i in range(len(lines)):
            self.assertEqual(batch_file[i], lines[i])

        # Check spin :70@N.
        print("\nChecking the spin :70@N input file.")
        file = open("%s%sspin_%s.in" % (ds.tmpdir, sep, ':70@N'))
        lines = file.readlines()
        file.close()
        for i in range(len(lines)):
            self.assertEqual(spin1[i], lines[i])

        # Check spin :71@N.
        print("\nChecking the spin :71@N input file.")
        file = open("%s%sspin_%s.in" % (ds.tmpdir, sep, ':71@N'))
        lines = file.readlines()
        file.close()
        for i in range(len(lines)):
            self.assertEqual(spin2[i], lines[i])


    def test_exp_fit(self):
        """Test the relaxation dispersion 'exp_fit' model curve fitting."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'exp_fit.py')

        # The original exponential curve parameters.
        res_data = [
            [15., 10., 20000., 25000.],
            [12., 11., 50000., 51000.],
            [17., 9., 100000., 96000.]
        ]

        # List of parameters which do not belong to the model.
        blacklist = ['cpmg_frqs', 'r2', 'rex', 'kex', 'r2a', 'ka', 'dw']

        # Checks for each residue.
        for i in range(len(res_data)):
            # Printout.
            print("\nResidue number %s." % (i+1))

            # Check the fitted parameters.
            print cdp.mol[0].res[i].spin[0].r2eff
            self.assertAlmostEqual(cdp.mol[0].res[i].spin[0].r2eff['1000.0'], res_data[i][0], places=2)
            self.assertAlmostEqual(cdp.mol[0].res[i].spin[0].r2eff['2000.0'], res_data[i][1], places=2)
            self.assertAlmostEqual(cdp.mol[0].res[i].spin[0].i0['1000.0']/10000, res_data[i][2]/10000, places=3)
            self.assertAlmostEqual(cdp.mol[0].res[i].spin[0].i0['2000.0']/10000, res_data[i][3]/10000, places=3)

            # Check the simulation errors.
            self.assert_(cdp.mol[0].res[i].spin[0].r2eff_err['1000.0'] < 5.0)
            self.assert_(cdp.mol[0].res[i].spin[0].r2eff_err['2000.0'] < 5.0)
            self.assert_(cdp.mol[0].res[i].spin[0].i0_err['1000.0']/10000 < 5.0)
            self.assert_(cdp.mol[0].res[i].spin[0].i0_err['2000.0']/10000 < 5.0)

            # Check that certain parameters are not present.
            for param in blacklist:
                print("\tChecking for the absence of the '%s' parameter." % param)
                self.assert_(not hasattr(cdp.mol[0].res[i].spin[0], param))

        # Check the clustering information.
        self.assert_(hasattr(cdp, 'clustering'))
        keys = ['free spins', 'cluster']
        for key in keys:
            self.assert_(key in cdp.clustering)
        self.assert_('test' not in cdp.clustering)
        self.assertEqual(cdp.clustering['free spins'], [':2@N'])
        self.assertEqual(cdp.clustering['cluster'], [':1@N', ':3@N'])


    def test_read_r2eff(self):
        """Test the reading of a file containing r2eff values."""

        # Create the sequence data, and name the spins.
        self.interpreter.residue.create(1, 'Gly')
        self.interpreter.residue.create(2, 'Gly')
        self.interpreter.residue.create(3, 'Gly')

        # Read the file.
        self.interpreter.relax_data.read(ri_id='R2eff.600', ri_type='R2eff', frq=600*1e6, file='r2eff.out', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'r2eff', res_num_col=1, res_name_col=2, data_col=3, error_col=4)

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].ri_data['R2eff.600'], 15.000)
        self.assertEqual(cdp.mol[0].res[1].spin[0].ri_data['R2eff.600'], 4.2003)
        self.assertEqual(cdp.mol[0].res[2].spin[0].ri_data['R2eff.600'], 7.2385)
