# Script for isotropic model-free analysis.
#
# This script is designed for those who appreciate black-boxes, although it will need to be
# heavily tailored to the protein in question, or those who appreciate complex code.  For a
# description of object-oriented coding in python using classes, functions/methods, self, etc,
# look at the python tutorial.


# Import functions from the python modules 'os' and 're'.
from os import getcwd, listdir
from re import search


class Main:
    def __init__(self):
        """Script for black-box model-free analysis.

        The value of the variable self.diff_model will determine the behaviour of this script.  The
        five diffusion models used in this script are:

            Model I   (MI)   - Local tm.
            Model II  (MII)  - Isotropic diffusion tensor.
            Model III (MIII) - Prolate axially symmetrical anisotropic diffusion tensor.
            Model IV  (MIV)  - Oblate axiallty symmetrical anisotropic diffusion tensor.
            Model V   (MV)   - Fully anisotropic diffusion tensor.

        Model I must be optimised prior to any of the other diffusion models, while the Models II to
        V can be optimised in any order.  To select the various models, set the variable
        self.diff_model to the following strings:

            MI   - 'local_tm'
            MII  - 'iso'
            MIII - 'prolate'
            MIV  - 'oblate'
            MV   - 'aniso'

        This approach has the advantage of eliminating the need for an initial estimate of a global
        diffusion tensor and removing all the problems associated with the initial estimate.


        Model I - Local tm
        ~~~~~~~~~~~~~~~~~~

        This will optimise the diffusion model where all residues of the protein have a local tm
        value, i.e. there is no global diffusion tensor.  This model needs to be optimised prior to
        optimising any of the other diffusion models.  The following steps are used:

        Each residue is fitted to the multiple model-free models separately, where the parameter tm
        is included in each model.  No R2 data is used in this case and all model-free models with
        the parameter Rex are removed.  This is to avoid the minimisation problem of having the
        parameters tm and Rex together.

        AIC model selection is used to select the models for each residue.


        Model II - Isotropic diffusion
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        This will optimise the isotropic diffusion model.  Multiple steps are required, an initial
        optimisation of the diffusion tensor, followed by a repetitive optimisation until
        convergence of the diffusion tensor.  Each of these steps requires this script to be rerun.
        For the initial optimisation, which will be placed in the directory './iso/init/', the
        following steps are used:

        The model-free models and parameter values for each residue are set to those of diffusion
        model MI.

        The local tm parameter is removed from the models.

        The model-free parameters are fixed and a global isotropic diffusion tensor is minimised.


        For the repetitive optimisation, each minimisation is named from 'round_1' onwards.  The
        initial 'round_1' optimisation will extract the diffusion tensor from the results file in
        './iso/init/', and the results will be placed in the directory './iso/round_1/'.  Each
        successive round will take the diffusion tensor from the previous round.  The following
        steps are used:

        The global diffusion tensor is fixed and the multiple model-free models are fitted to each
        residue.

        AIC model selection is used to select the models for each residue.

        All model-free and diffusion parameters are allowed to vary and a global optimisation of all
        parameters is carried out.


        Model III - Prolate axially symmetrical anisotropic diffusion
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        The methods used are identical to those of diffusion model MII, except that an axially
        symmetric diffusion tensor with Dpar >= Dper is used.  The base directory containing all the
        results is './prolate/'.


        Model IV - Oblate axially symmetrical anisotropic diffusion
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        The methods used are identical to those of diffusion model MII, except that an axially
        symmetric diffusion tensor with Dpar <= Dper is used.  The base directory containing all the
        results is './oblate/'.


        Model V - Fully anisotropic diffusion
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        The methods used are identical to those of diffusion model MII, except that a fully
        anisotropic diffusion tenosr is used.  The base directory is './aniso/'.
        """

        # The diffusion model.
        self.diff_model = 'oblate'


        # MI - Local tm.
        ################

        if self.diff_model == 'local_tm':
            # Base directory to place files into.
            self.base_dir = 'local_tm/'

            # Sequential optimisation of all model-free models (function must be modified to suit).
            self.multi_model_local_tm()

            # Model selection run.
            create_run('aic', 'mf')

            # Model selection.
            self.model_selection(run='aic')


        # Diffusion models MII to MV.
        #############################

        elif self.diff_model == 'iso' or self.diff_model == 'prolate' or self.diff_model == 'oblate' or self.diff_model == 'aniso':
            # Determine which round of optimisation to do (init, round_1, round_2, etc).
            self.round = self.determine_rnd()


            # Inital round of optimisation for diffusion models MII to MV.
            if self.round == 0:
                # Base directory to place files into.
                self.base_dir = self.diff_model + '/init/'

                # Run name.
                run = self.diff_model

                # Create the run.
                create_run(run, 'mf')

                # Load the local tm diffusion model MI results.
                read(run=run, file='results', dir='local_tm/aic')

                # Remove the tm parameter.
                model_free.remove_tm(run=run)

                # Load the PDB file.
                pdb(run, 'schurr.pdb')
                vectors(run)

                # Add an arbitrary diffusion tensor which will be optimised.
                if self.diff_model == 'iso':
                    diffusion_tensor.set(run, 10e-9, fixed=0)
                elif self.diff_model == 'prolate':
                    diffusion_tensor.set(run, (10e-9, 0, 0, 0), axial_type='prolate', fixed=0)
                elif self.diff_model == 'oblate':
                    diffusion_tensor.set(run, (10e-9, 0, 0, 0), axial_type='oblate', fixed=0)
                elif self.diff_model == 'aniso':
                    diffusion_tensor.set(run, (10e-9, 0, 0, 0, 0, 0), fixed=0)

                # Minimise just the diffusion tensor.
                fix(run, 'all_res')
                grid_search(run, inc=11)
                minimise('newton', run=run)

                # Write the results.
                write(run=run, file='results', dir=self.base_dir, force=1)


            # Normal round of optimisation for diffusion models MII to MV.
            else:
                # Base directory to place files into.
                self.base_dir = self.diff_model + '/round_' + `self.round` + '/'

                # Load the optimised diffusion tensor from either the previous round.
                self.load_tensor()

                # Sequential optimisation of all model-free models (function must be modified to suit).
                self.multi_model()

                # Create the final run (for model selection and final optimisation).
                run = 'final'
                create_run(run, 'mf')

                # Model selection.
                self.model_selection(run)

                # Final optimisation of all diffusion and model-free parameters.
                fix(run, 'all', fixed=0)

                # Minimise all parameters.
                minimise('newton', run=run)

                # Write the results.
                dir = self.base_dir + 'opt'
                write(run=run, file='results', dir=dir, force=1)


        # Unknown script behaviour.
        ###########################

        else:
            raise RelaxError, "Unknown diffusion model, change the value of 'self.diff_model'"


    def determine_rnd(self):
        """Function for returning the name of next round of optimisation."""

        # Get a list of all files in the directory self.diff_model.  If no directory exists, set the round to 'init' or 0.
        try:
            dir_list = listdir(getcwd() + '/' + self.diff_model)
        except:
            print "Hello"
            return 0

        # Set the round to 'init' or 0 if there is no directory called 'init'.
        if 'init' not in dir_list:
            return 0

        # Create a list of all files which begin with 'round_'.
        rnd_dirs = []
        for file in dir_list:
            if search('^round_', file):
                rnd_dirs.append(file)

        # Create a sorted list of integer round numbers.
        numbers = []
        for dir in rnd_dirs:
            try:
                numbers.append(int(dir[6:]))
            except:
                pass
        numbers.sort()

        # No directories begining with 'round_' exist, set the round to 1.
        if not len(numbers):
            return 1

        # Determine the number for the next round (add 1 to the highest number).
        return numbers[-1] + 1


    def load_tensor(self):
        """Function for loading the optimised diffusion tensor."""

        # Create the run for the previous data.
        create_run('opt', 'mf')

        # Load the optimised diffusion tensor from the initial round.
        if self.round == 1:
            read('opt', 'results', self.diff_model + '/init')

        # Load the optimised diffusion tensor from the previous round.
        else:
            read('opt', 'results', self.diff_model + '/round_' + `self.round - 1` + '/opt')


    def model_selection(self, run=None):
        """Model selection function."""

        # Model elimination.
        eliminate()

        # Model selection.
        model_selection('AIC', run)

        # Write the results.
        dir = self.base_dir + 'aic'
        write(run=run, file='results', dir=dir, force=1)


    def multi_model(self):
        """Function for optimisation of all model-free models."""

        # Set the run names (also the names of preset model-free models).
        runs = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']

        # Nuclei type
        nuclei('N')

        for run in runs:
            # Create the run.
            create_run(run, 'mf')

            # Load the sequence.
            sequence.read(run, 'noe.600.out')

            # Load the PDB file.
            pdb(run, 'schurr.pdb')
            vectors(run)

            # Load the relaxation data.
            relax_data.read(run, 'R1', '600', 600.0 * 1e6, 'r1.600.out')
            relax_data.read(run, 'R2', '600', 600.0 * 1e6, 'r2.600.out')
            relax_data.read(run, 'NOE', '600', 600.0 * 1e6, 'noe.600.out')
            relax_data.read(run, 'R1', '500', 500.0 * 1e6, 'r1.500.out')
            relax_data.read(run, 'R2', '500', 500.0 * 1e6, 'r2.500.out')
            relax_data.read(run, 'NOE', '500', 500.0 * 1e6, 'noe.500.out')

            # Copy the diffusion tensor from the run 'opt'.
            diffusion_tensor.copy('opt', run)

            # Set the bond length and CSA values.
            value.set(run, 1.02 * 1e-10, 'bond_length')
            value.set(run, -170 * 1e-6, 'csa')

            # Select the model-free model.
            model_free.select_model(run=run, model=run)

            # Minimise.
            grid_search(run, inc=11)
            minimise('newton', run=run)

            # Write the results.
            dir = self.base_dir + run
            write(run=run, file='results', dir=dir, force=1)


    def multi_model_local_tm(self):
        """Function for optimisation of all model-free models (where a local tm parameter is included)."""

        # Set the run names (also the names of preset model-free models).
        runs = ['tm1', 'tm2', 'tm5', 'tm6']

        # Nuclei type
        nuclei('N')

        for run in runs:
            # Create the run.
            create_run(run, 'mf')

            # Load the sequence.
            sequence.read(run, 'noe.600.out')

            # Load the relaxation data.
            relax_data.read(run, 'R1', '600', 600.0 * 1e6, 'r1.600.out')
            relax_data.read(run, 'NOE', '600', 600.0 * 1e6, 'noe.600.out')
            relax_data.read(run, 'R1', '500', 500.0 * 1e6, 'r1.500.out')
            relax_data.read(run, 'NOE', '500', 500.0 * 1e6, 'noe.500.out')

            # Set the bond length and CSA values.
            value.set(run, 1.02 * 1e-10, 'bond_length')
            value.set(run, -170 * 1e-6, 'csa')

            # Select the model-free model.
            model_free.select_model(run=run, model=run)

            # Minimise.
            grid_search(run, inc=11)
            minimise('newton', run=run)

            # Write the results.
            dir = self.base_dir + run
            write(run=run, file='results', dir=dir, force=1)


# The main class.
Main()
