###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
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
from os import F_OK, P_WAIT, access, chdir, chmod, getcwd, listdir, mkdir, remove, spawnlp, system
from re import match, search
from string import split
import sys


class Palmer:
    def __init__(self, relax):
        """Class used to create and process input and output for the program Modelfree 4."""

        self.relax = relax


    def create(self, run, dir, force, diff_search, sims, sim_type, trim, steps, constraints, nucleus, atom1, atom2):
        """Function for creating the Modelfree4 input files.

        The following files are created:
            dir/mfin
            dir/mfdata
            dir/mfpar
            dir/mfmodel
            dir/run.sh
        """

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # Test if the PDB file is loaded (axially symmetric and anisotropic diffusion).
        if not match('iso', self.relax.data.diff[run].type):
            if not hasattr(self.relax.data, 'pdb'):
                raise RelaxPdbError

        # Directory creation.
        if dir == None:
            dir = run
        try:
            mkdir(dir)
        except OSError:
            pass

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

        # The 'mfin' file.
        mfin = self.open_file('mfin')
        self.create_mfin(mfin)
        mfin.close()

        # Open the 'mfdata', 'mfmodel', and 'mfpar' files.
        mfdata = self.open_file('mfdata')
        mfmodel = self.open_file('mfmodel')
        mfpar = self.open_file('mfpar')

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res)):
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


    def create_mfdata(self, i, file):
        """Create the Modelfree4 input file 'mfmodel'."""

        # Spin title.
        file.write("\nspin     " + self.relax.data.res[i].name + "_" + `self.relax.data.res[i].num` + "\n")

        # Data written flag.
        written = 0

        # Loop over the frequencies.
        for j in xrange(self.relax.data.res[i].num_frq[self.run]):
            # Set the data to None.
            r1, r2, noe = None, None, None

            # Loop over the relevant relaxation data.
            for k in xrange(self.relax.data.res[i].num_ri[self.run]):
                if self.relax.data.res[i].remap_table[self.run][k] != j:
                    continue

                # Find the corresponding R1.
                if match('R1', self.relax.data.res[i].ri_labels[self.run][k]):
                    r1 = self.relax.data.res[i].relax_data[self.run][k]
                    r1_err = self.relax.data.res[i].relax_error[self.run][k]

                # Find the corresponding R2.
                elif match('R2', self.relax.data.res[i].ri_labels[self.run][k]):
                    r2 = self.relax.data.res[i].relax_data[self.run][k]
                    r2_err = self.relax.data.res[i].relax_error[self.run][k]

                # Find the corresponding NOE.
                elif match('NOE', self.relax.data.res[i].ri_labels[self.run][k]):
                    noe = self.relax.data.res[i].relax_data[self.run][k]
                    noe_err = self.relax.data.res[i].relax_error[self.run][k]

            # Test if the R1 exists for this frequency, otherwise skip the data.
            if r1:
                file.write('%-7s%-10.3f%20f%20f %-3i\n' % ('R1', self.relax.data.res[i].frq[self.run][j]*1e-6, r1, r1_err, 1))
            else:
                file.write('%-7s%-10.3f%20f%20f %-3i\n' % ('R1', self.relax.data.res[i].frq[self.run][j]*1e-6, 0, 0, 0))

            # Test if the R2 exists for this frequency, otherwise skip the data.
            if r2:
                file.write('%-7s%-10.3f%20f%20f %-3i\n' % ('R2', self.relax.data.res[i].frq[self.run][j]*1e-6, r2, r2_err, 1))
            else:
                file.write('%-7s%-10.3f%20f%20f %-3i\n' % ('R2', self.relax.data.res[i].frq[self.run][j]*1e-6, 0, 0, 0))

            # Test if the NOE exists for this frequency, otherwise skip the data.
            if noe:
                file.write('%-7s%-10.3f%20f%20f %-3i\n' % ('NOE', self.relax.data.res[i].frq[self.run][j]*1e-6, noe, noe_err, 1))
            else:
                file.write('%-7s%-10.3f%20f%20f %-3i\n' % ('NOE', self.relax.data.res[i].frq[self.run][j]*1e-6, 0, 0, 0))

            written = 1

        return written


    def create_mfin(self, file):
        """Create the Modelfree4 input file 'mfin'."""

        # Set the diffusion tensor specific values.
        if match('iso', self.relax.data.diff[self.run].type):
            diff = 'isotropic'
            algorithm = 'brent'
            tm = self.relax.data.diff[self.run].tm / 1e-9
            dratio = 1
            theta = 0
            phi = 0
        elif match('axial', self.relax.data.diff[self.run].type):
            diff = 'axial'
            algorithm = 'powell'
            tm = self.relax.data.diff[self.run].tm / 1e-9
            dratio = self.relax.data.diff[self.run].Dratio
            theta = self.relax.data.diff[self.run].theta * 360.0 / (2.0 * pi)
            phi = self.relax.data.diff[self.run].phi * 360.0 / (2.0 * pi)
        elif match('aniso', self.relax.data.diff[self.run].type):
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

        file.write("fields          " + `self.relax.data.res[0].num_frq[self.run]`)
        for frq in xrange(self.relax.data.res[0].num_frq[self.run]):
            file.write("  " + `self.relax.data.res[0].frq[self.run][frq]*1e-6`)
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


    def create_mfmodel(self, i, file):
        """Create the Modelfree4 input file 'mfmodel'."""

        # Spin title.
        file.write("\nspin     " + self.relax.data.res[i].name + "_" + `self.relax.data.res[i].num` + "\n")

        # tloc.
        file.write('%-3s%-6s%-6.1f' % ('M1', 'tloc', 0))
        if 'tm' in self.relax.data.res[i].params[self.run]:
            file.write('%-4i' % 1)
        else:
            file.write('%-4i' % 0)

        if self.constraints:
            file.write('%-2i' % 2)
        else:
            file.write('%-2i' % 0)

        file.write('%11.3f%12.3f %-4s\n' % (0, 20, self.steps))

        # Theta.
        file.write('%-3s%-6s%-6.1f' % ('M1', 'Theta', 0))
        file.write('%-4i' % 0)

        if self.constraints:
            file.write('%-2i' % 2)
        else:
            file.write('%-2i' % 0)

        file.write('%11.3f%12.3f %-4s\n' % (0, 90, self.steps))

        # S2f.
        file.write('%-3s%-6s%-6.1f' % ('M1', 'Sf2', 1))
        if 'S2f' in self.relax.data.res[i].params[self.run]:
            file.write('%-4i' % 1)
        else:
            file.write('%-4i' % 0)

        if self.constraints:
            file.write('%-2i' % 2)
        else:
            file.write('%-2i' % 0)

        file.write('%11.3f%12.3f %-4s\n' % (0, 1, self.steps))

        # S2s.
        file.write('%-3s%-6s%-6.1f' % ('M1', 'Ss2', 1))
        if 'S2s' in self.relax.data.res[i].params[self.run] or 'S2' in self.relax.data.res[i].params[self.run]:
            file.write('%-4i' % 1)
        else:
            file.write('%-4i' % 0)

        if self.constraints:
            file.write('%-2i' % 2)
        else:
            file.write('%-2i' % 0)

        file.write('%11.3f%12.3f %-4s\n' % (0, 1, self.steps))

        # te.
        file.write('%-3s%-6s%-6.1f' % ('M1', 'te', 0))
        if 'te' in self.relax.data.res[i].params[self.run] or 'ts' in self.relax.data.res[i].params[self.run]:
            file.write('%-4i' % 1)
        else:
            file.write('%-4i' % 0)

        if self.constraints:
            file.write('%-2i' % 2)
        else:
            file.write('%-2i' % 0)

        file.write('%11.3f%12.3f %-4s\n' % (0, 10000, self.steps))

        # Rex.
        file.write('%-3s%-6s%-6.1f' % ('M1', 'Rex', 0))
        if 'Rex' in self.relax.data.res[i].params[self.run]:
            file.write('%-4i' % 1)
        else:
            file.write('%-4i' % 0)

        if self.constraints:
            file.write('%-2i' % -1)
        else:
            file.write('%-2i' % 0)

        file.write('%11.3f%12.3f %-4s\n' % (0, 20, self.steps))


    def create_mfpar(self, i, file):
        """Create the Modelfree4 input file 'mfpar'."""

        # Spin title.
        file.write("\nspin     " + self.relax.data.res[i].name + "_" + `self.relax.data.res[i].num` + "\n")

        file.write('%-14s' % "constants")
        file.write('%-6i' % self.relax.data.res[i].num)
        file.write('%-7s' % self.nucleus)
        file.write('%-8.3f' % (self.relax.data.gx / 1e7))
        file.write('%-8.3f' % (self.relax.data.res[i].r[self.run] * 1e10))
        file.write('%-8.3f\n' % (self.relax.data.res[i].csa[self.run] * 1e6))

        file.write('%-10s' % "vector")
        file.write('%-4s' % self.atom1)
        file.write('%-4s\n' % self.atom2)


    def create_run(self, file):
        """Create the script 'run.sh' for the execution of Modelfree4."""

        file.write("modelfree4 -i mfin -d mfdata -p mfpar -m mfmodel -o mfout -e out")
        if not match('iso', self.relax.data.diff[self.run].type):
            # Copy the pdb file to the model directory so there are no problems with the existance of *.rotate files.
            system('cp ' + self.relax.data.pdb.filename + ' ' + self.dir)
            file.write(" -s " + self.relax.data.pdb.filename.split('/')[-1])
        file.write("\n")


    def execute(self, run, dir, force):
        """Function for executing Modelfree4.
        
        BUG:  Control-C during execution causes the cwd to stay as dir.
        """

        # The directory.
        if dir == None:
            dir = run
        if not access(dir, F_OK):
            raise RelaxDirError, ('Modelfree4', dir)

        # Change to this directory.
        chdir(dir)

        # Test if the 'mfin' input file exists.
        if not access('mfin', F_OK):
            raise RelaxFileError, ('mfin input', 'mfin')

        # Test if the 'mfdata' input file exists.
        if not access('mfdata', F_OK):
            raise RelaxFileError, ('mfdata input', 'mfdata')

        # Test if the 'mfmodel' input file exists.
        if not access('mfmodel', F_OK):
            raise RelaxFileError, ('mfmodel input', 'mfmodel')

        # Test if the 'mfpar' input file exists.
        if not access('mfpar', F_OK):
            raise RelaxFileError, ('mfpar input', 'mfpar')

        # Test if the 'PDB' input file exists.
        if not match('iso', self.relax.data.diff[run].type):
            pdb = self.relax.data.pdb.filename.split('/')[-1]
            if not access(pdb, F_OK):
                raise RelaxFileError, ('PDB', pdb)
        else:
            pdb = None

        # Remove the file 'mfout' and '*.out' if the force flag is set.
        if force:
            for file in listdir(getcwd()):
                if search('out$', file):
                    remove(file)

        # Execute Modelfree4.
        if pdb:
            spawnlp(P_WAIT, 'modelfree4', 'modelfree4', '-i', 'mfin', '-d', 'mfdata', '-p', 'mfpar', '-m', 'mfmodel', '-o', 'mfout', '-e', 'out', '-s', pdb)
        else:
            test = spawnlp(P_WAIT, 'modelfree4', 'modelfree4', '-i', 'mfin', '-d', 'mfdata', '-p', 'mfpar', '-m', 'mfmodel', '-o', 'mfout', '-e', 'out')
            if test:
                raise RelaxProgError, 'Modelfree4'

        # Change back to the original directory.
        chdir('..')


    def extract(self, run, dir):
        """Function for extracting the Modelfree4 results out of the 'mfout' file."""

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # The directory.
        if dir == None:
            dir = run
        if not access(dir, F_OK):
            raise RelaxDirError, ('Modelfree4', dir)

        # Test if the file exists.
        if not access(dir + "/mfout", F_OK):
            raise RelaxFileError, ('Modelfree4', dir + "/mfout")

        # Open the file.
        mfout_file = open(dir + "/mfout", 'r')
        mfout = mfout_file.readlines()
        mfout_file.close()

        # Find out if simulations were carried out.
        for i in xrange(len(mfout)):
            if search('_iterations', mfout[i]):
                row = split(mfout[i])
                sims = int(row[1])

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res)):
            # Get the S2 data.
            data = self.get_mf_data('S2', mfout, self.relax.data.res[i].num)
            if data != None:
                s2, s2_err = data
                self.relax.data.res[i].s2[run] = s2
                #self.relax.data.res[i].s2_err[run] = s2_err

            # Get the S2f data.
            if 'S2f' in self.relax.data.res[i].params[self.run] or 'S2s' in self.relax.data.res[i].params[self.run]:
                data = self.get_mf_data('S2f', mfout, self.relax.data.res[i].num)
                if data != None:
                    s2f, s2f_err = data
                    self.relax.data.res[i].s2f[run] = s2f
                    #self.relax.data.res[i].s2f_err[run] = s2f_err

            # Get the S2s data.
            if 'S2f' in self.relax.data.res[i].params[self.run] or 'S2s' in self.relax.data.res[i].params[self.run]:
                data = self.get_mf_data('S2s', mfout, self.relax.data.res[i].num)
                if data != None:
                    s2s, s2s_err = data
                    self.relax.data.res[i].s2s[run] = s2s
                    #self.relax.data.res[i].s2s_err[run] = s2s_err

            # Get the te and ts data.
            if 'te' in self.relax.data.res[i].params[self.run] or 'ts' in self.relax.data.res[i].params[self.run]:
                data = self.get_mf_data('te', mfout, self.relax.data.res[i].num)
                if data != None:
                    te, te_err = data
                    self.relax.data.res[i].te[run] = te / 1e12
                    #self.relax.data.res[i].te_err[run] = te_err / 1e12
                    if 'ts' in self.relax.data.res[i].params[self.run]:
                        self.relax.data.res[i].ts[run] = te / 1e12
                        #self.relax.data.res[i].ts_err[run] = te_err / 1e12

            # Get the Rex data.
            if 'Rex' in self.relax.data.res[i].params[self.run]:
                data = self.get_mf_data('Rex', mfout, self.relax.data.res[i].num)
                if data != None:
                    rex, rex_err = data
                    self.relax.data.res[i].rex[run] = rex / (2.0 * pi * self.relax.data.res[i].frq[run][0])**2
                    #self.relax.data.res[i].rex_err[run] = rex_err / (2.0 * pi * self.relax.data.res[i].frq[run][0])**2

            # Get the chi-squared data.
            self.relax.data.res[i].chi2[run] = self.get_chi2(sims, mfout, self.relax.data.res[i].num)


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
                return float(row[1]), float(row[4])

            # Catch the end.
            if row[0] == 'stop_':
                return


    def open_file(self, file_name):
        """Function for opening a file to write to."""

        file_name = self.dir + "/" + file_name
        if access(file_name, F_OK) and not self.force:
            raise RelaxFileOverwriteError, (file_name, 'force flag')
        return open(file_name, 'w')
