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


    def create(self, run, dir, force):
        """Function for creating the Dasha script file 'dir/dasha_script'."""

        # Arguments.
        self.run = run
        self.dir = dir
        self.force = force

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Determine the parameter set.
        self.param_set = self.relax.specific.model_free.determine_param_set_type(self.run)

        # Test if diffusion tensor data for the run exists.
        if self.param_set != 'local_tm' and not self.relax.data.diff.has_key(self.run):
            raise RelaxNoTensorError, self.run

        # Test if the PDB file has been loaded (for the spheroid and ellipsoid).
        if self.param_set != 'local_tm' and self.relax.data.diff[self.run].type != 'sphere' and not self.relax.data.pdb.has_key(self.run):
            raise RelaxNoPdbError, self.run

        # Test if the nucleus type has been set.
        if not hasattr(self.relax.data, 'gx'):
            raise RelaxNucleusError

        # Directory creation.
        if self.dir == None:
            self.dir = self.run
        self.relax.IO.mkdir(self.dir, print_flag=0)

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
        script = self.open_file('dasha_script')
        self.create_script(script)
        script.close()


    def create_script(self, file):
        """Create the Dasha script file."""

        # Delete all data.
        file.write('# Delete all data.\n')
        file.write('del 1 10000\n')

        # Nucleus type.
        file.write('\n# Nucleus type.\n')
        nucleus = self.relax.generic.nuclei.find_nucleus()
        if nucleus == 'N':
            nucleus = 'N15'
        elif nucleus == 'C':
            nucleus = 'C13'
        else:
            raise RelaxError, 'Cannot handle the nucleus type ' + `nucleus` + ' within Dasha.'
        file.write('set nucl ' + nucleus + '\n')

        # Number of frequencies.
        file.write('\n# Number of frequencies.\n')
        file.write('set n_freq ' + `self.relax.data.num_frq[self.run]` + '\n')

        # Frequency values.
        file.write('\n# Frequency values.\n')
        for i in xrange(self.relax.data.num_frq[self.run]):
            file.write('set H1_freq ' + `self.relax.data.frq[self.run][i] / 1e6` + ' ' + `i+1` + '\n')

        # Set the diffusion tensor.
        file.write('\n# Set the diffusion tensor.\n')
        if self.param_set != 'local_tm':
            # Sphere.
            if self.relax.data.diff[self.run].type == 'sphere':
                file.write('set tr ' + `self.relax.data.diff[self.run].tm / 1e-9` + '\n')

            # Spheroid.
            elif self.relax.data.diff[self.run].type == 'spheroid':
                file.write('set tr ' + `self.relax.data.diff[self.run].tm / 1e-9` + '\n')

            # Ellipsoid.
            elif self.relax.data.diff[self.run].type == 'ellipsoid':
                # Get the eigenvales.
                Dx, Dy, Dz = self.relax.generic.diffusion_tensor.return_eigenvalues(self.run)

                # Geometric parameters.
                file.write('set tr ' + `self.relax.data.diff[self.run].tm / 1e-9` + '\n')
                file.write('set D1/D3 ' + `Dx / Dz` + '\n')
                file.write('set D2/D3 ' + `Dy / Dz` + '\n')

                # Orientational parameters.
                file.write('set alfa ' + `self.relax.data.diff[self.run].alpha / (2.0 * pi) * 360.0` + '\n')
                file.write('set betta ' + `self.relax.data.diff[self.run].beta / (2.0 * pi) * 360.0` + '\n')
                file.write('set gamma ' + `self.relax.data.diff[self.run].gamma / (2.0 * pi) * 360.0` + '\n')

        # Reading the relaxation data.
        file.write('\n# Reading the relaxation data.\n')
        file.write('echo Reading the relaxation data.\n')
        noe_index = 1
        r1_index = 1
        r2_index = 1
        for i in xrange(self.relax.data.num_ri[self.run]):
            # NOE.
            if self.relax.data.ri_labels[self.run][i] == 'NOE':
                # Data set number.
                number = noe_index

                # Data type.
                data_type = 'noe'

                # Increment the data set index.
                noe_index = noe_index + 1

            # R1.
            elif self.relax.data.ri_labels[self.run][i] == 'R1':
                # Data set number.
                number = r1_index

                # Data type.
                data_type = '1/t1'

                # Increment the data set index.
                r1_index = r1_index + 1

            # R2.
            elif self.relax.data.ri_labels[self.run][i] == 'R2':
                # Data set number.
                number = r2_index

                # Data type.
                data_type = '1/t2'

                # Increment the data set index.
                r2_index = r2_index + 1

            # Set the data type.
            if number == 1:
                file.write('\nread < ' + data_type + '\n')
            else:
                file.write('\nread < ' + data_type + ' ' + `number` + '\n')

            # The relaxation data.
            for j in xrange(len(self.relax.data.res[self.run])):
                # Reassign the data.
                data = self.relax.data.res[self.run][j]

                # Data and errors.
                file.write(`data.num` + ' ' + `data.relax_data[i]` + ' ' + `data.relax_error[i]` + '\n')

            # Terminate the reading.
            file.write('exit\n')

        # Individual residue optimisation.
        if self.param_set == 'mf':
            # Loop over the residues.
            for i in xrange(len(self.relax.data.res[self.run])):
                # Reassign the data.
                data = self.relax.data.res[self.run][i]

                # Comment.
                file.write('\n\n\n# Residue ' + `data.num` + '\n\n')

                # Echo.
                file.write('echo Optimisation of residue ' + `data.num` + '\n')

                # Select the residue.
                file.write('\n# Select the residue.\n')
                file.write('set cres ' + `data.num` + '\n')

                # The 'jmode'.
                if 'te' in data.params:
                    jmode = 2
                elif 'S2' in data.params:
                    jmode = 1
                elif 'ts' in data.params:
                    jmode = 3

                # Chemical exchange.
                if 'Rex' in data.params:
                    exch = 1
                else:
                    exch = 0

                # Set the jmode.
                file.write('\n# Set the jmode.\n')
                file.write('set def jmode ' + `jmode`)
                if exch:
                    file.write(' exch\n')
                else:
                    file.write('\n')

                # Bond length.
                file.write('\n# Bond length.\n')
                file.write('set r_hx ' + `data.r / 1e-10` + '\n')

                # CSA value.
                file.write('\n# CSA value.\n')
                file.write('set csa ' + `data.csa / 1e-6` + '\n')

                # Parameter default values.
                file.write('\n# Parameter default values.\n')
                file.write('reset jmode ' + `data.num` + '\n')

            # Optimisation of all residues.
            file.write('\n\n\n# Optimisation of all residues.\n')
            file.write('min all')

            # Show the results.
            file.write('\n# Show the results.\n')
            file.write('echo\n')
            file.write('show all\n')


        else:
            raise RelaxError, 'Optimisation of the parameter set ' + `self.param_set` + ' currently not supported.'


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
