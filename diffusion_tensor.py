class Diffusion_tensor:
    def __init__(self, relax):
        """Class containing the macro for setting up the diffusion tensor."""

        self.relax = relax


    def set(self, diff=None, params=None):
        """Function for setting up the diffusion tensor."""

        # Setup the diffusion type.
        self.relax.data.diff_type = diff

        # Setup the parameter values.
        if diff == 'iso':
            self.relax.data.diff_params = [params]
        else:
            self.relax.data.diff_params = params
