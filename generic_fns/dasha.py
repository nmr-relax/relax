###############################################################################
#                                                                             #
# Copyright (C) 2005 Edward d'Auvergne                                        #
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

from math import pi
from os import F_OK, P_WAIT, access, chdir, chmod, getcwd, listdir, remove, spawnlp, system
from re import match, search
from string import split


class Dasha:
    def __init__(self, relax):
        """Class used to create and process input and output for the program Modelfree 4."""

        self.relax = relax


    def create(self, run, dir, force, diff_search, sims, sim_type, trim, steps, constraints, nucleus, atom1, atom2):
        """Function for creating the Dasha script file 'dir/dasha_script'."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError, run

        # Test if the PDB file is loaded (for the spheroid and ellipsoid).
        if not self.relax.data.diff[run].type == 'sphere' and not self.relax.data.pdb.has_key(run):
            raise RelaxNoPdbError, run

        # Test if the nucleus type has been set.
        if not hasattr(self.relax.data, 'gx'):
            raise RelaxNucleusError

        # Directory creation.
        if dir == None:
            dir = run
        self.relax.IO.mkdir(dir, print_flag=0)

        # Place the arguments into 'self'.
        self.run = run
        self.dir = dir
        self.force = force
        self.diff_search = diff_search
        self.sims = sims
        self.sim_type = sim_type
        self.trim = trim
        self.steps = steps
        self.constraints = constraints
        self.nucleus = nucleus
        self.atom1 = atom1
        self.atom2 = atom2

        # Number of field strengths and values.
        self.num_frq = 0
        self.frq = []
        for i in xrange(len(self.relax.data.res[self.run])):
            if hasattr(self.relax.data.res[self.run][i], 'num_frq'):
                if self.relax.data.res[self.run][i].num_frq > self.num_frq:
                    # Number of field strengths.
                    self.num_frq = self.relax.data.res[self.run][i].num_frq

                    # Field strength values.
                    for frq in self.relax.data.res[self.run][i].frq:
                        if frq not in self.frq:
                            self.frq.append(frq)

        # The 'dasha_script' file.
        mfin = self.open_file('dasha_script')
        self.create_script(mfin)
        mfin.close()

        # Open the 'mfdata', 'mfmodel', and 'mfpar' files.
        mfdata = self.open_file('mfdata')
        mfmodel = self.open_file('mfmodel')
        mfpar = self.open_file('mfpar')

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            if hasattr(self.relax.data.res[self.run][i], 'num_frq'):
                # The 'mfdata' file.
                if not self.create_mfdata(i, mfdata):
                    continue

                # The 'mfmodel' file.
                self.create_mfmodel(i, mfmodel)

                # The 'mfpar' file.
                self.create_mfpar(i, mfpar)

        # Close the 'mfdata', 'mfmodel', and 'mfpar' files.
        mfdata.close()
        mfmodel.close()
        mfpar.close()

        # The 'run.sh' script.
        run = self.open_file('run.sh')
        self.create_run(run)
        run.close()
        chmod(self.dir + '/run.sh', 0755)


    def create_script(self, file):
        """Create the Modelfree4 input file 'mfin'."""

        # Set the diffusion tensor specific values.
        if self.relax.data.diff[self.run].type == 'sphere':
            diff = 'isotropic'
            algorithm = 'brent'
            tm = self.relax.data.diff[self.run].tm / 1e-9
            dratio = 1
            theta = 0
            phi = 0
        elif self.relax.data.diff[self.run].type == 'spheroid':
            diff = 'axial'
            algorithm = 'powell'
            tm = self.relax.data.diff[self.run].tm / 1e-9
            dratio = self.relax.data.diff[self.run].Dratio
            theta = self.relax.data.diff[self.run].theta * 360.0 / (2.0 * pi)
            phi = self.relax.data.diff[self.run].phi * 360.0 / (2.0 * pi)
        elif self.relax.data.diff[self.run].type == 'ellipsoid':
            diff = 'anisotropic'
            algorithm = 'powell'
            tm = self.relax.data.diff[self.run].tm / 1e-9
            dratio = 0
            theta = 0
            phi = 0

        # Add the main options.
        file.write("optimization    tval\n\n")
        file.write("seed            0\n\n")
        file.write("search          grid\n\n")

        # Diffusion type.
        if self.relax.data.diff[self.run].fixed:
            algorithm = 'fix'

        file.write("diffusion       " + diff + " " + self.diff_search + "\n\n")
        file.write("algorithm       " + algorithm + "\n\n")

        # Monte Carlo simulations.
        if self.sims:
            file.write("simulations     " + self.sim_type + "    " + `self.sims` + "       " + `self.trim` + "\n\n")
        else:
            file.write("simulations     none\n\n")

        selection = 'none'    # To be changed.
        file.write("selection       " + selection + "\n\n")
        file.write("sim_algorithm   " + algorithm + "\n\n")

        file.write("fields          " + `self.num_frq`)
        for frq in self.frq:
            file.write("  " + `frq*1e-6`)
        file.write("\n")

        # tm.
        file.write('%-7s' % 'tm')
        file.write('%14.3f' % tm)
        file.write('%2i' % 1)
        file.write('%3i' % 0)
        file.write('%5i' % 5)
        file.write('%6i' % 15)
        file.write('%4i\n' % 20)

        # dratio.
        file.write('%-7s' % 'Dratio')
        file.write('%14s' % dratio)
        file.write('%2i' % 1)
        file.write('%3i' % 0)
        file.write('%5i' % 0)
        file.write('%6i' % 2)
        file.write('%4i\n' % 5)

        # theta.
        file.write('%-7s' % 'Theta')
        file.write('%14s' % theta)
        file.write('%2i' % 1)
        file.write('%3i' % 0)
        file.write('%5i' % 0)
        file.write('%6i' % 180)
        file.write('%4i\n' % 10)

        # phi.
        file.write('%-7s' % 'Phi')
        file.write('%14s' % phi)
        file.write('%2i' % 1)
        file.write('%3i' % 0)
        file.write('%5i' % 0)
        file.write('%6i' % 360)
        file.write('%4i\n' % 10)


    def execute(self, run, dir, force):
        """Function for executing Dasha."""

        # The current directory.
        orig_dir = getcwd()

        # The directory.
        if dir == None:
            dir = run
        if not access(dir, F_OK):
            raise RelaxDirError, ('Dasha', dir)

        # Change to this directory.
        chdir(dir)

        # Catch failures and return to the correct directory.
        try:
            # Test if the 'dasha_script' script file exists.
            if not access('dasha_script', F_OK):
                raise RelaxFileError, ('dasha script', 'dasha_script')

            # Test if the 'PDB' input file exists.
            if self.relax.data.diff[run].type != 'sphere':
                pdb = self.relax.data.pdb[self.run].file_name.split('/')[-1]
                if not access(pdb, F_OK):
                    raise RelaxFileError, ('PDB', pdb)
            else:
                pdb = None

            # Execute Dasha.
            if pdb:
                spawnlp(P_WAIT, 'dasha', 'dasha', '<', 'dasha_script', '>', 'dasha_results')
            else:
                test = spawnlp(P_WAIT, 'dasha', 'dasha', '<', 'dasha_script', '>', 'dasha_results')
                if test:
                    raise RelaxProgFailError, 'Dasha'

        # Failure.
        except:
            # Change back to the original directory.
            chdir(orig_dir)

            # Reraise the error.
            raise

        # Change back to the original directory.
        chdir(orig_dir)


    def extract(self, run, dir):
        """Function for extracting the Dasha results out of the 'dasha_results' file."""

        # Arguments.
        self.run = run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # The directory.
        if dir == None:
            dir = run
        if not access(dir, F_OK):
            raise RelaxDirError, ('Dasha', dir)

        # Test if the file exists.
        if not access(dir + "/dasha_results", F_OK):
            raise RelaxFileError, ('Dasha', dir + "/dasha_results")

        # Open the file.
        results_file = open(dir + "/dasha_results", 'r')
        results = results_file.readlines()
        results_file.close()

        # Find out if simulations were carried out.
        sims = 0
        for i in xrange(len(mfout)):
            if search('_iterations', mfout[i]):
                row = split(mfout[i])
                sims = int(row[1])

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Missing data sets.
            if not hasattr(self.relax.data.res[self.run][i], 'model'):
                continue

            # Get the S2 data.
            data = self.get_mf_data('S2', mfout, self.relax.data.res[self.run][i].num)
            if data != None:
                s2, s2_err = data
                self.relax.data.res[self.run][i].s2 = s2
                #self.relax.data.res[self.run][i].s2_err = s2_err

            # Get the S2f data.
            if 'S2f' in self.relax.data.res[self.run][i].params or 'S2s' in self.relax.data.res[self.run][i].params:
                data = self.get_mf_data('S2f', mfout, self.relax.data.res[self.run][i].num)
                if data != None:
                    s2f, s2f_err = data
                    self.relax.data.res[self.run][i].s2f = s2f
                    #self.relax.data.res[self.run][i].s2f_err = s2f_err

            # Get the S2s data.
            if 'S2f' in self.relax.data.res[self.run][i].params or 'S2s' in self.relax.data.res[self.run][i].params:
                data = self.get_mf_data('S2s', mfout, self.relax.data.res[self.run][i].num)
                if data != None:
                    s2s, s2s_err = data
                    self.relax.data.res[self.run][i].s2s = s2s
                    #self.relax.data.res[self.run][i].s2s_err = s2s_err

            # Get the te and ts data.
            if 'te' in self.relax.data.res[self.run][i].params or 'ts' in self.relax.data.res[self.run][i].params:
                data = self.get_mf_data('te', mfout, self.relax.data.res[self.run][i].num)
                if data != None:
                    te, te_err = data
                    self.relax.data.res[self.run][i].te = te / 1e12
                    #self.relax.data.res[self.run][i].te_err = te_err / 1e12
                    if 'ts' in self.relax.data.res[self.run][i].params:
                        self.relax.data.res[self.run][i].ts = te / 1e12
                        #self.relax.data.res[self.run][i].ts_err = te_err / 1e12

            # Get the Rex data.
            if 'Rex' in self.relax.data.res[self.run][i].params:
                data = self.get_mf_data('Rex', mfout, self.relax.data.res[self.run][i].num)
                if data != None:
                    rex, rex_err = data
                    self.relax.data.res[self.run][i].rex = rex / (2.0 * pi * self.relax.data.res[self.run][i].frq[0])**2
                    #self.relax.data.res[self.run][i].rex_err = rex_err / (2.0 * pi * self.relax.data.res[self.run][i].frq[0])**2

            # Get the chi-squared data.
            self.relax.data.res[self.run][i].chi2 = self.get_chi2(sims, mfout, self.relax.data.res[self.run][i].num)


    def get_chi2(self, sims, mfout, res):
        """Extract the chi-squared data from the mfout file."""

        # Move to the section starting with 'data_sse'.
        for i in xrange(len(mfout)):
            if match('data_sse', mfout[i]):
                break

        # Get the chi-squared value.
        for j in xrange(i+3, len(mfout)):
            row = split(mfout[j])
            if `res` == row[0]:
                return float(row[1])

            # Catch the end.
            if row[0] == 'data_correlation_matrix':
                return


    def get_mf_data(self, data_type, mfout, res):
        """Extract the model-free data from the mfout file."""

        # Move to the section starting with 'data_model_1'.
        for i in xrange(len(mfout)):
            if match('data_model_1', mfout[i]):
                break

        # Move to the subsection starting with data_type.
        for j in xrange(i, len(mfout)):
            row = split(mfout[j])
            if len(row) == 0:
                continue
            elif match(data_type, row[0]):
                break

        # Find the residue specific information.
        for k in xrange(j+1, len(mfout)):
            row = split(mfout[k])
            if `res` == row[0]:
                try:
                    # Catch a series of '*' joining two columns.
                    val = split(row[1], '*')
                    err = split(row[4], '*')

                    # Return the values.
                    return float(val[0]), float(err[0])
                except:
                    return None, None

            # Catch the end.
            if row[0] == 'stop_':
                return


    def open_file(self, file_name):
        """Function for opening a file to write to."""

        file_name = self.dir + "/" + file_name
        if access(file_name, F_OK) and not self.force:
            raise RelaxFileOverwriteError, (file_name, 'force flag')
        return open(file_name, 'w')
