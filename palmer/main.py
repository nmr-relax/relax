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

from os import F_OK, P_WAIT, access, chdir, chmod, getcwd, listdir, mkdir, remove, spawnlp, system
from re import match, search
import sys


class Palmer:
    def __init__(self, relax):
        """Class used to create and process input and output for the program Modelfree 4."""

        self.relax = relax


    def create(self, run, dir, force, sims, sim_type, trim, steps, constraints, nucleus, atom1, atom2):
        """Function for creating the Modelfree4 input files.

        The following files are created:
            dir/mfin
            dir/mfdata
            dir/mfpar
            dir/mfmodel
            dir/run.sh
        """

        # Test if the run exists.
        if not run in self.relax.data.runs:
            raise RelaxRunError, run

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

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

            # Test if the R1, R2, and NOE exists for this frequency, otherwise skip the data.
            if r1 and r2 and noe:
                file.write('%-7s%-10.3f%20f%20f %-3i\n' % ('R1', self.relax.data.res[i].frq[self.run][j]*1e-6, r1, r1_err, 1))
                file.write('%-7s%-10.3f%20f%20f %-3i\n' % ('R2', self.relax.data.res[i].frq[self.run][j]*1e-6, r2, r2_err, 1))
                file.write('%-7s%-10.3f%20f%20f %-3i\n' % ('NOE', self.relax.data.res[i].frq[self.run][j]*1e-6, noe, noe_err, 1))
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
            dratio = self.relax.data.diff[self.run].dratio
            theta = self.relax.data.diff[self.run].theta
            phi = self.relax.data.diff[self.run].phi
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
            diff_search = 'none'
            algorithm = 'fix'
        else:
            diff_search = 'grid'

        file.write("diffusion       " + diff + " " + diff_search + "\n\n")
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
        file.write('%5i' % 0)
        file.write('%6i' % 0)
        file.write('%4i\n' % self.steps)

        # dratio.
        file.write('%-7s' % 'Dratio')
        file.write('%14s' % dratio)
        file.write('%2i' % 1)
        file.write('%3i' % 0)
        file.write('%5i' % 0)
        file.write('%6i' % 0)
        file.write('%4i\n' % self.steps)

        # theta.
        file.write('%-7s' % 'Theta')
        file.write('%14s' % theta)
        file.write('%2i' % 1)
        file.write('%3i' % 0)
        file.write('%5i' % 0)
        file.write('%6i' % 0)
        file.write('%4i\n' % self.steps)

        # phi.
        file.write('%-7s' % 'Phi')
        file.write('%14s' % phi)
        file.write('%2i' % 1)
        file.write('%3i' % 0)
        file.write('%5i' % 0)
        file.write('%6i' % 0)
        file.write('%4i\n' % self.steps)


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
        """Function for executing Modelfree4."""

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
            spawnlp(P_WAIT, 'modelfree4', 'modelfree4', '-i', 'mfin', '-d', 'mfdata', '-p', 'mfpar', '-m', 'mfmodel', '-o', 'mfout', '-e', 'out')

        # Change back to the original directory.
        chdir('..')


    def open_file(self, file_name):
        file_name = self.dir + "/" + file_name
        if access(file_name, F_OK) and not self.force:
            raise RelaxFileOverwriteError, (file_name, 'force flag')
        return open(file_name, 'w')


####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
########################### Delete everything below ################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
class Palmer_old:
    def __init__(self, relax):
        """Class used to create and process input and output for the program Modelfree 4."""

        self.relax = relax

        print "Model-free analysis based on " + self.relax.usr_param.method + " model selection."
        self.ask_stage()
        title = "<<< Stage " + self.relax.data.stage + " - "
        title = title + self.relax.usr_param.method + " model selection >>>\n\n\n"

        if self.relax.debug:
            self.relax.file_ops.init_log_file(title)

        self.update_data()
        self.extract_relax_data()

        if self.relax.debug:
            self.log_input_info()

        if match('^AIC$', self.relax.usr_param.method) or match('^AICc$', self.relax.usr_param.method):
            self.relax.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
            self.model_selection = self.relax.modsel.asymptotic
        elif match('^BIC$', self.relax.usr_param.method):
            self.relax.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
            self.model_selection = self.relax.modsel.asymptotic
        elif match('^Bootstrap$', self.relax.usr_param.method):
            self.relax.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
            self.model_selection = self.relax.modsel.bootstrap
        elif match('^CV$', self.relax.usr_param.method):
            self.relax.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
            self.model_selection = self.relax.modsel.cv
        elif match('^Expect$', self.relax.usr_param.method):
            self.relax.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
            self.model_selection = self.relax.modsel.exp_overall_disc
        elif match('^Farrow$', self.relax.usr_param.method):
            self.relax.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
            self.model_selection = self.relax.modsel.farrow
        elif match('^Palmer$', self.relax.usr_param.method):
            self.relax.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5', 'f-m1m2', 'f-m1m3']
            if self.relax.data.num_data_sets > 3:
                self.relax.data.runs.append('f-m2m4')
                self.relax.data.runs.append('f-m2m5')
                self.relax.data.runs.append('f-m3m4')
            self.model_selection = self.relax.modsel.palmer
        elif match('^Overall$', self.relax.usr_param.method):
            message = "See the file 'modsel/overall_disc.py' for details.\n"
            self.relax.file_ops.read_file('op_data', message)
            self.relax.data.overall_disc.op_data = self.relax.file_ops.open_file(file_name='op_data')
            self.relax.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
            #self.relax.modsel.overall_disc(self.mf)
        else:
            raise NameError, "The model-free analysis method is not set correctly.  Check self.method in the file 'usr_param.py', quitting program."

        self.relax.data.mfin.default_data()
        self.goto_stage()


    def ask_stage(self):
        """User input of stage number."""

        print "\n[ Select the stage for model-free analysis ]\n"
        print "The stages are:"
        print "   Stage 1 (1):  Creation of the files for the model-free calculations for models 1 to 5."
        print "   Stage 2 (2):  Model selection and creation of a final run."
        print "   Stage 3 (3):  Extraction of the data."

        while 1:
            input = raw_input('> ')
            valid_stages = ['1', '2', '3']
            if input in valid_stages:
                self.relax.data.stage = input
                break
            else:
                print "Invalid stage number.  Choose either 1, 2, or 3."
        if match('2', self.relax.data.stage):
            while 1:
                print "Stage 2 has the following two options for the final run:"
                print "   (a):   No optimization of the diffusion tensor."
                print "   (b):   Optimization of the diffusion tensor."
                input = raw_input('> ')
                valid_stages = ['a', 'b']
                if input in valid_stages:
                    self.relax.data.stage = self.relax.data.stage + input
                    break
                else:
                    print "Invalid option, choose either a or b."

        print "The stage chosen is " + self.relax.data.stage + "\n"


    def close_mf_files(self, dir):
        """Close the mfin, mfdata, mfmodel, mfpar, and run files, and make the run file executable."""

        self.relax.mfin.close()
        self.relax.mfdata.close()
        self.relax.mfmodel.close()
        self.relax.mfpar.close()
        self.relax.run.close()
        chmod(dir + '/run', 0777)


    def extract_mf_data(self):
        """Extract the model-free results."""

        for model in self.relax.data.runs:
            mfout = self.relax.file_ops.read_file(model + '/mfout')
            mfout_lines = mfout.readlines()
            mfout.close()
            print "Extracting model-free data from " + model + "/mfout."
            num_res = len(self.relax.data.relax_data[0])
            if match('^m', model):
                self.relax.data.model = self.relax.star.extract(mfout_lines, num_res, self.relax.usr_param.chi2_lim, self.relax.usr_param.ftest_lim, ftest='n')
            if match('^f', model):
                self.relax.data.model = self.relax.star.extract(mfout_lines, num_res, self.relax.usr_param.chi2_lim, self.relax.usr_param.ftest_lim, ftest='y')


    def final_run(self):
        """Creation of the final run.  Files are placed in the directory 'final'."""

        self.relax.file_ops.mkdir('final')
        open_mf_files(dir='final')
        self.create_mfin()

        self.create_run(dir='final')
        for res in xrange(len(self.relax.data.relax_data[0])):
            if match('0', self.relax.data.results[res]['model']):
                model = 'none'
            elif match('2+3', self.relax.data.results[res]['model']):
                model = 'none'
            elif match('4+5', self.relax.data.results[res]['model']):
                model = 'none'
            elif match('^1', self.relax.data.results[res]['model']):
                model = "m1"
            else:
                model = 'm' + self.relax.data.results[res]['model']
            self.set_run_flags(model)
            # Mfdata.
            if match('none', model):
                self.create_mfdata(res, flag='0')
            else:
                self.create_mfdata(res, flag='1')
            # Mfmodel.
            self.create_mfmodel(res, self.relax.usr_param.md1, type='M1')
            # Mfpar.
            self.create_mfpar(res)
        self.close_mf_files(dir='final')


    def goto_stage(self):
        if match('1', self.relax.data.stage):
            print "\n[ Stage 1 ]\n"
            self.set_vars_stage_initial()
            if match('^CV$', self.relax.usr_param.method):
                self.stage_initial_cv()
            else:
                self.stage_initial()
            print "\n[ End of stage 1 ]\n\n"

        if match('^2', self.relax.data.stage):
            print "\n[ Stage 2 ]\n"
            self.set_vars_stage_selection()
            self.stage_selection()
            if match('2a', self.relax.data.stage):
                self.final_run()
            if match('2b', self.relax.data.stage):
                if match('isotropic', self.relax.data.mfin.diff):
                    self.relax.data.mfin.algorithm = 'brent'
                    self.relax.data.mfin.diff_search = 'grid'
                elif match('axial', self.relax.data.mfin.diff):
                    self.relax.data.mfin.algorithm = 'powell'
                self.final_run()
            print "\n[ End of stage 2 ]\n\n"

        if match('3', self.relax.data.stage):
            print "\n[ Stage 3 ]\n"
            self.stage_final()
            print "\n[ End of stage 3 ]\n\n"


    def open_mf_files(self, dir):
        """Open the mfin, mfdata, mfmodel, mfpar, and run files for writing."""

        self.relax.mfin = open(dir + '/mfin', 'w')
        self.relax.mfdata = open(dir + '/mfdata', 'w')
        self.relax.mfmodel = open(dir + '/mfmodel', 'w')
        self.relax.mfpar = open(dir + '/mfpar', 'w')
        self.relax.run = open(dir + '/run', 'w')


    def set_run_flags(self, model):
        """Reset, and then set the flags in self.relax.usr_param.md1 and md2."""

        self.relax.usr_param.md1['sf2']['flag'] = '0'
        self.relax.usr_param.md1['ss2']['flag'] = '0'
        self.relax.usr_param.md1['te']['flag']  = '0'
        self.relax.usr_param.md1['rex']['flag'] = '0'

        self.relax.usr_param.md2['sf2']['flag'] = '0'
        self.relax.usr_param.md2['ss2']['flag'] = '0'
        self.relax.usr_param.md2['te']['flag']  = '0'
        self.relax.usr_param.md2['rex']['flag'] = '0'

        # Normal runs.
        if model == "m1":
            self.relax.usr_param.md1['ss2']['flag'] = '1'
        if model == "m2":
            self.relax.usr_param.md1['ss2']['flag'] = '1'
            self.relax.usr_param.md1['te']['flag']  = '1'
        if model == "m3":
            self.relax.usr_param.md1['ss2']['flag'] = '1'
            self.relax.usr_param.md1['rex']['flag'] = '1'
        if model == "m4":
            self.relax.usr_param.md1['ss2']['flag'] = '1'
            self.relax.usr_param.md1['te']['flag']  = '1'
            self.relax.usr_param.md1['rex']['flag'] = '1'
        if model == "m5":
            self.relax.usr_param.md1['sf2']['flag'] = '1'
            self.relax.usr_param.md1['ss2']['flag'] = '1'
            self.relax.usr_param.md1['te']['flag']  = '1'

        # F-tests.
        if model == "f-m1m2":
            self.relax.usr_param.md1['ss2']['flag'] = '1'
            self.relax.usr_param.md2['ss2']['flag'] = '1'
            self.relax.usr_param.md2['te']['flag']  = '1'
        if model == "f-m1m3":
            self.relax.usr_param.md1['ss2']['flag'] = '1'
            self.relax.usr_param.md2['ss2']['flag'] = '1'
            self.relax.usr_param.md2['rex']['flag'] = '1'
        if model == "f-m1m4":
            self.relax.usr_param.md1['ss2']['flag'] = '1'
            self.relax.usr_param.md2['ss2']['flag'] = '1'
            self.relax.usr_param.md2['te']['flag']  = '1'
            self.relax.usr_param.md2['rex']['flag'] = '1'
        if model == "f-m1m5":
            self.relax.usr_param.md1['ss2']['flag'] = '1'
            self.relax.usr_param.md2['ss2']['flag'] = '1'
            self.relax.usr_param.md2['sf2']['flag'] = '1'
            self.relax.usr_param.md2['te']['flag']  = '1'
        if model == "f-m2m4":
            self.relax.usr_param.md1['ss2']['flag'] = '1'
            self.relax.usr_param.md1['te']['flag']  = '1'
            self.relax.usr_param.md2['ss2']['flag'] = '1'
            self.relax.usr_param.md2['te']['flag']  = '1'
            self.relax.usr_param.md2['rex']['flag'] = '1'
        if model == "f-m2m5":
            self.relax.usr_param.md1['ss2']['flag'] = '1'
            self.relax.usr_param.md1['te']['flag']  = '1'
            self.relax.usr_param.md2['ss2']['flag'] = '1'
            self.relax.usr_param.md2['sf2']['flag'] = '1'
            self.relax.usr_param.md2['te']['flag']  = '1'
        if model == "f-m3m4":
            self.relax.usr_param.md1['ss2']['flag'] = '1'
            self.relax.usr_param.md1['rex']['flag'] = '1'
            self.relax.usr_param.md2['ss2']['flag'] = '1'
            self.relax.usr_param.md2['te']['flag']  = '1'
            self.relax.usr_param.md2['rex']['flag'] = '1'


    def stage_final(self):
        raise NameError, "Stage 3 not implemented yet.\n"


    def stage_initial(self):
        """Initial stage function.

        Creation of the files for the Modelfree calculations for the models in self.relax.data.runs
        """

        for model in self.relax.data.runs:
            if match('^m', model):
                print "Creating input files for model " + model
                if self.relax.debug:
                    self.relax.log.write("\n\n<<< Model " + model + " >>>\n\n")
            elif match('^f', model):
                print "Creating input files for the F-test " + model
                if self.relax.debug:
                    self.relax.log.write("\n\n<<< F-test " + model + " >>>\n\n")
            else:
                raise NameError, "The run '" + model + "'does not start with an m or f, quitting program!\n\n"
            self.relax.file_ops.mkdir(dir=model)
            self.open_mf_files(dir=model)
            self.set_run_flags(model)

            if self.relax.debug:
                self.log_params('M1', self.relax.usr_param.md1)
                self.log_params('M2', self.relax.usr_param.md2)

            if match('^m', model):
                self.relax.data.mfin.selection = 'none'
                self.create_mfin()
            elif match('^f', model):
                self.relax.data.mfin.selection = 'ftest'
                self.create_mfin()
            self.create_run(dir=model)
            for res in xrange(len(self.relax.data.relax_data[0])):
                # Mfdata.
                self.create_mfdata(res)
                # Mfmodel.
                self.create_mfmodel(res, self.relax.usr_param.md1, type='M1')
                if match('^f', model):
                    self.create_mfmodel(res, self.relax.usr_param.md2, type='M2')
                # Mfpar.
                self.create_mfpar(res)
            self.close_mf_files(dir=model)


    def stage_initial_cv(self):
        """Initial stage function for cross validation.

        Creation of the files for the Modelfree calculations for the models in self.relax.data.runs
        """

        for model in self.relax.data.runs:
            print "Creating input files for model " + model

            if self.relax.debug:
                self.relax.log.write("\n\n<<< Model " + model + " >>>\n\n")

            self.relax.file_ops.mkdir(dir=model)
            self.set_run_flags(model)

            if self.relax.debug:
                self.log_params('M1', self.relax.usr_param.md1)
                self.log_params('M2', self.relax.usr_param.md2)

            for i in xrange(self.relax.data.num_ri):
                cv_dir = model + "/" + model + "-" + self.relax.data.frq_label[self.relax.data.remap_table[i]] + "_" + self.relax.data.data_types[i]
                self.relax.file_ops.mkdir(dir=cv_dir)
                open_mf_files(dir=cv_dir)
                self.relax.data.mfin.selection = 'none'
                self.create_mfin()
                self.create_run(dir=model)
                for res in xrange(len(self.relax.data.relax_data[0])):
                    # Mfdata.
                    self.create_mfdata(res, i)
                    # Mfmodel.
                    self.create_mfmodel(res, self.relax.usr_param.md1, type='M1')
                    # Mfpar.
                    self.create_mfpar(res)
                self.close_mf_files(dir=cv_dir)


    def set_vars_stage_initial(self):
        """Set the options for the initial runs."""

        self.relax.data.mfin.sims = 'n'


    def set_vars_stage_selection(self):
        """Set the options for the final run."""

        self.relax.data.mfin.sims = 'y'
