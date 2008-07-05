"""Script for performing a very minimal model-free analysis using the OMP relaxation data."""

# Python module imports.
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()


# Path of the relaxation data.
DATA_PATH = sys.path[-1] + '/test_suite/shared_data/model_free/OMP'

# Mini subset of local tm and model-free data pipes.
LOCAL_TM_MODELS = ['tm0', 'tm1', 'tm2']
MF_MODELS = ['m0', 'm1', 'm2']

# The bond length, CSA values, heteronucleus type, and proton type.
BOND_LENGTH = 1.02 * 1e-10
CSA = -172 * 1e-6
HETNUC = '15N'
PROTON = '1H'

# The grid search size (the number of increments per dimension).
GRID_INC = 3

# The optimisation technique.
MIN_ALGOR = 'simplex'


class Main:
    def __init__(self, relax):
        """Execute the model-free analysis."""

        # Setup.
        self.relax = relax

        # Read the results file to get the relaxation data from.
        pipe.create('data', 'mf')
        results.read(file='final_results_trunc_1.3', dir=DATA_PATH)


        # MI - Local tm.
        ################

        # Sequential optimisation of all model-free models (function must be modified to suit).
        self.multi_model(local_tm=True)

        # Model selection.
        self.model_selection(pipe='aic')


        #######################
        # Spherical diffusion #
        #######################

        # Initial round of optimisation.
        ################################

        # Copy the model selection data pipe to a new pipe for the spherical diffusion tensor.
        pipe.copy('aic', 'sphere')
        pipe.switch('sphere')

        # Remove the tm parameter.
        model_free.remove_tm()

        # Set up the diffusion tensor.
        diffusion_tensor.init(10e-9, fixed=False)

        # Minimise just the diffusion tensor.
        fix('all_spins')
        grid_search(inc=GRID_INC)
        minimise(MIN_ALGOR)

        # Write the results.
        results.write(file='devnull', force=True)


        # Normal optimisation.
        ######################

        # Sequential optimisation of all model-free models.
        pipe.copy('sphere', 'previous')
        self.multi_model(local_tm=False)

        # Model selection.
        self.model_selection(pipe='aic')


    def model_selection(self, pipe=None):
        """Model selection function."""

        # Model elimination.
        eliminate()

        # Model selection.
        model_selection(method='AIC', modsel_pipe=pipe, pipes=self.pipes)


    def multi_model(self, local_tm=False):
        """Function for optimisation of all model-free models."""

        # Set the data pipe names (also the names of preset model-free models).
        if local_tm:
            self.pipes = LOCAL_TM_MODELS
        else:
            self.pipes = MF_MODELS

        # Loop over the data pipes.
        for name in self.pipes:
            # Create the data pipe.
            if ds.has_key(name):
                pipe.delete(name)
            pipe.create(name, 'mf')

            # Copy the sequence.
            sequence.copy('data')

            # Select only 3 spins (residues 9, 10, and 11).
            deselect.all()
            select.spin(':9')
            select.spin(':10')
            select.spin(':11')

            # Copy the relaxation data.
            relax_data.copy('data')

            # Copy the diffusion tensor from the 'opt' data pipe and prevent it from being minimised.
            if not local_tm:
                diffusion_tensor.copy('previous')
                fix('diff')

            # Set all the necessary values.
            value.set(BOND_LENGTH, 'bond_length')
            value.set(CSA, 'csa')
            value.set(HETNUC, 'heteronucleus')
            value.set(PROTON, 'proton')

            # Select the model-free model.
            model_free.select_model(model=name)

            # Minimise.
            grid_search(inc=GRID_INC)
            minimise(MIN_ALGOR)



# Execute the main class.
Main(self.relax)
