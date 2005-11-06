# Script for complete model-free analysis.
#
# This script is designed for those who appreciate black-boxes, although it will need to be
# heavily tailored to the protein in question, or those who appreciate complex code.  For a
# description of object-oriented coding in python using classes, functions/methods, self, etc,
# see the python tutorial.


# Import functions from the python modules 'os' and 're'.
from os import getcwd, listdir
from re import search


class Main:
    def __init__(self):
        """Script for black-box model-free analysis.

        The value of the variable self.diff_model will determine the behaviour of this script.  The
        five diffusion models used in this script are:

            Model I   (MI)   - Local tm.
            Model II  (MII)  - Sphere.
            Model III (MIII) - Prolate spheroid.
            Model IV  (MIV)  - Oblate spheroid.
            Model V   (MV)   - Ellipsoid.

        Model I must be optimised prior to any of the other diffusion models, while the Models II to
        V can be optimised in any order.  To select the various models, set the variable
        self.diff_model to the following strings:

            MI   - 'local_tm'
            MII  - 'sphere'
            MIII - 'prolate'
            MIV  - 'oblate'
            MV   - 'ellipsoid'

        This approach has the advantage of eliminating the need for an initial estimate of a global
        diffusion tensor and removing all the problems associated with the initial estimate.

        It is important that the number of parameters in a model does not excede the number of
        relaxation data sets for that residue.  If this is the case, the list of models in the
        'multi_model' functions will need to be trimmed.


        Model I - Local tm
        ~~~~~~~~~~~~~~~~~~

        This will optimise the diffusion model whereby all residues of the protein have a local tm
        value, i.e. there is no global diffusion tensor.  This model needs to be optimised prior to
        optimising any of the other diffusion models.  Each residue is fitted to the multiple model-
        free models separately, where the parameter tm is included in each model.

        AIC model selection is used to select the models for each residue.


        Model II - Sphere
        ~~~~~~~~~~~~~~~~~

        This will optimise the isotropic diffusion model.  Multiple steps are required, an initial
        optimisation of the diffusion tensor, followed by a repetitive optimisation until
        convergence of the diffusion tensor.  Each of these steps requires this script to be rerun.
        For the initial optimisation, which will be placed in the directory './sphere/init/', the
        following steps are used:

        The model-free models and parameter values for each residue are set to those of diffusion
        model MI.

        The local tm parameter is removed from the models.

        The model-free parameters are fixed and a global spherical diffusion tensor is minimised.


        For the repetitive optimisation, each minimisation is named from 'round_1' onwards.  The
        initial 'round_1' optimisation will extract the diffusion tensor from the results file in
        './sphere/init/', and the results will be placed in the directory './sphere/round_1/'.  Each
        successive round will take the diffusion tensor from the previous round.  The following
        steps are used:

        The global diffusion tensor is fixed and the multiple model-free models are fitted to each
        residue.

        AIC model selection is used to select the models for each residue.

        All model-free and diffusion parameters are allowed to vary and a global optimisation of all
        parameters is carried out.


        Model III - Prolate spheroid
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        The methods used are identical to those of diffusion model MII, except that an axially
        symmetric diffusion tensor with Da >= 0 is used.  The base directory containing all the
        results is './prolate/'.


        Model IV - Oblate spheroid
        ~~~~~~~~~~~~~~~~~~~~~~~~~~

        The methods used are identical to those of diffusion model MII, except that an axially
        symmetric diffusion tensor with Da <= 0 is used.  The base directory containing all the
        results is './oblate/'.


        Model V - Ellipsoid
        ~~~~~~~~~~~~~~~~~~~

        The methods used are identical to those of diffusion model MII, except that a fully
        anisotropic diffusion tensor is used (also known as rhombic or asymmetric diffusion).  The
        base directory is './ellipsoid/'.



        Final run
        ~~~~~~~~~

        Once all the diffusion models have converged, the final run can be executed.  This is done
        by setting the variable self.diff_model to 'final'.  This consists of two steps, diffusion
        tensor model selection, and Monte Carlo simulations.  Firstly AIC model selection is used to
        select between the diffusion tensor models.  Monte Carlo simulations are then run soley on
        this selected diffusion model.  Minimisation of the model is bypassed as it is assumed that
        the model is already fully optimised (if this is not the case the final run is not yet
        appropriate).

        The final black-box model-free results will be placed in the file 'final/results'.
        """

        # The diffusion model (this is the variable which should be changed).
        self.diff_model = 'final'


        # MI - Local tm.
        ################

        if self.diff_model == 'local_tm':
            # Base directory to place files into.
            self.base_dir = 'local_tm/'

            # Sequential optimisation of all model-free models (function must be modified to suit).
            self.multi_model(local_tm=1)

            # Model selection run.
            run.create('aic', 'mf')

            # Model selection.
            self.model_selection(run='aic', dir=self.base_dir + 'aic')


        # Diffusion models MII to MV.
        #############################

        elif self.diff_model == 'sphere' or self.diff_model == 'prolate' or self.diff_model == 'oblate' or self.diff_model == 'ellipsoid':
            # Determine which round of optimisation to do (init, round_1, round_2, etc).
            self.round = self.determine_rnd(model=self.diff_model)


            # Inital round of optimisation for diffusion models MII to MV.
            if self.round == 0:
                # Base directory to place files into.
                self.base_dir = self.diff_model + '/init/'

                # Run name.
                name = self.diff_model

                # Create the run.
                run.create(name, 'mf')

                # Load the local tm diffusion model MI results.
                results.read(run=name, file='results', dir='local_tm/aic')

                # Remove the tm parameter.
                model_free.remove_tm(run=name)

                # Load the PDB file.
                pdb(name, '1F3Y.pdb')

                # Add an arbitrary diffusion tensor which will be optimised.
                if self.diff_model == 'sphere':
                    diffusion_tensor.set(name, 10e-9, fixed=0)
                elif self.diff_model == 'prolate':
                    diffusion_tensor.set(name, (10e-9, 0, 0, 0), spheroid_type='prolate', fixed=0)
                elif self.diff_model == 'oblate':
                    diffusion_tensor.set(name, (10e-9, 0, 0, 0), spheroid_type='oblate', fixed=0)
                elif self.diff_model == 'ellipsoid':
                    diffusion_tensor.set(name, (8.6e-09, -8e6, 0, 360, 90, 360), fixed=0)

                # Minimise just the diffusion tensor.
                fix(name, 'all_res')
                grid_search(name, inc=11)
                minimise('newton', run=name)

                # Write the results.
                results.write(run=name, file='results', dir=self.base_dir, force=1)


            # Normal round of optimisation for diffusion models MII to MV.
            else:
                # Base directory to place files into.
                self.base_dir = self.diff_model + '/round_' + `self.round` + '/'

                # Load the optimised diffusion tensor from either the previous round.
                self.load_tensor()

                # Sequential optimisation of all model-free models (function must be modified to suit).
                self.multi_model()

                # Delete the run containing the optimised diffusion tensor.
                run.delete('tensor')

                # Create the final run (for model selection and final optimisation).
                name = 'final'
                run.create(name, 'mf')

                # Model selection.
                self.model_selection(run=name, dir=self.base_dir + 'aic')

                # Final optimisation of all diffusion and model-free parameters.
                fix(name, 'all', fixed=0)

                # Minimise all parameters.
                minimise('newton', run=name)

                # Write the results.
                dir = self.base_dir + 'opt'
                results.write(run=name, file='results', dir=dir, force=1)


        # Final run.
        ############

        elif self.diff_model == 'final':
            # Diffusion model selection.
            ############################

            # Create the local_tm run.
            run.create('local_tm', 'mf')

            # Load the local tm diffusion model MI results.
            results.read(run='local_tm', file='results', dir='local_tm/aic')

            # Loop over models MII to MV.
            for model in ['sphere', 'prolate', 'oblate', 'ellipsoid']:
                # Determine which was the last round of optimisation for each of the models.
                self.round = self.determine_rnd(model=model) - 1

                # Skip the diffusion model if no directories begining with 'round_' exist.
                if self.round < 1:
                    continue

                # Create the run.
                run.create(model, 'mf')

                # Load the diffusion model results.
                results.read(run=model, file='results', dir=model + '/round_' + `self.round` + '/opt')

            # Create the run for model selection (which will be a copy of the selected diffusion model or run).
            run.create('final', 'mf')

            # Model selection between MI to MV.
            self.model_selection(run='final', write_flag=0)


            # Monte Carlo simulations.
            ##########################

            # Fix the diffusion tensor.
            fix('final', 'diff')

            # Simulations.
            monte_carlo.setup('final', number=200)
            monte_carlo.create_data('final')
            monte_carlo.initial_values('final')
            minimise('newton', run='final')
            monte_carlo.error_analysis('final')


            # Write the final results.
            ##########################

            results.write(run='final', file='results', dir='final', force=1)


        # Unknown script behaviour.
        ###########################

        else:
            raise RelaxError, "Unknown diffusion model, change the value of 'self.diff_model'"


    def determine_rnd(self, model=None):
        """Function for returning the name of next round of optimisation."""

        # Get a list of all files in the directory model.  If no directory exists, set the round to 'init' or 0.
        try:
            dir_list = listdir(getcwd() + '/' + model)
        except:
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
        run.create('tensor', 'mf')

        # Load the optimised diffusion tensor from the initial round.
        if self.round == 1:
            results.read('tensor', 'results', self.diff_model + '/init')

        # Load the optimised diffusion tensor from the previous round.
        else:
            results.read('tensor', 'results', self.diff_model + '/round_' + `self.round - 1` + '/opt')


    def model_selection(self, run=None, dir=None, write_flag=1):
        """Model selection function."""

        # Model elimination.
        eliminate()

        # Model selection.
        model_selection('AIC', run)

        # Write the results.
        if write_flag:
            results.write(run=run, file='results', dir=dir, force=1)


    def multi_model(self, local_tm=0):
        """Function for optimisation of all model-free models."""

        # Set the run names (also the names of preset model-free models).
        if local_tm:
            runs = ['tm1', 'tm2', 'tm3', 'tm4', 'tm5', 'tm6', 'tm7', 'tm8', 'tm9']
        else:
            runs = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']

        # Nuclei type
        nuclei('N')

        for name in runs:
            # Create the run.
            run.create(name, 'mf')

            # Load the sequence.
            sequence.read(name, 'noe.600.out')

            # Load the PDB file.
            if not local_tm:
                pdb(name, '1F3Y.pdb')

            # Load the relaxation data.
            relax_data.read(name, 'R1', '600', 599.719 * 1e6, 'r1.600.out')
            relax_data.read(name, 'R2', '600', 599.719 * 1e6, 'r2.600.out')
            relax_data.read(name, 'NOE', '600', 599.719 * 1e6, 'noe.600.out')
            relax_data.read(name, 'R1', '500', 500.208 * 1e6, 'r1.500.out')
            relax_data.read(name, 'R2', '500', 500.208 * 1e6, 'r2.500.out')
            relax_data.read(name, 'NOE', '500', 500.208 * 1e6, 'noe.500.out')

            # Unselect unresolved residues.
            unselect.read(name, file='unresolved')

            # Copy the diffusion tensor from the run 'opt' and prevent it from being minimised.
            if not local_tm:
                diffusion_tensor.copy('tensor', name)
                fix(name, 'diff')

            # Set the bond length and CSA values.
            value.set(name, 1.02 * 1e-10, 'bond_length')
            value.set(name, -170 * 1e-6, 'csa')

            # Select the model-free model.
            model_free.select_model(run=name, model=name)

            # Minimise.
            grid_search(name, inc=11)
            minimise('newton', run=name)

            # Write the results.
            dir = self.base_dir + name
            results.write(run=name, file='results', dir=dir, force=1)


# The main class.
Main()
