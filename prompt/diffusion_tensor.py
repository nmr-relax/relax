class Diffusion_tensor:
    def __init__(self, relax):
        """Class containing the macro for setting up the diffusion tensor."""

        self.relax = relax


    def set(self, diff=None, params=None):
        """Macro for setting up the diffusion tensor."""

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = self.relax.interpreter.macro_prompt + "diffusion_tensor.set("
            text = text + "diff=" + `diff`
            text = text + ", params=" + `params` + ")\n"
            print text

        # Diffusion tensor argument.
        if diff == None:
            print "No diffusion tensor given."
            return
        elif type(diff) != str:
            print "The argument 'diff' must be a string."
            return

        # Isotropic diffusion tensor parameters.
        elif diff == 'iso' and type(params) != float:
            print "For isotropic diffusion the 'params' argument must be a floating point number."
            return

        # Axially symmetric diffusion tensor parameters.
        elif diff == 'axial':
            if type(params) != list:
                print "For axially symmetric diffusion the 'params' argument must be an array."
                return
            elif len(params) != 3:
                print "For axially symmetric diffusion the 'params' argument must be an array of three elements."
                return
            for i in range(len(params)):
                if type(params[i]) != float:
                    print "The elements of the 'params' array must be floating point numbers."
                    return

        # Anisotropic diffusion tensor parameters.
        elif diff == 'aniso':
            if type(params) != list:
                print "For anisotropic diffusion the 'params' argument must be an array."
                return
            elif len(params) != 6:
                print "For anisotropic diffusion the 'params' argument must be an array of six elements."
                return
            for i in range(len(params)):
                if type(params[i]) != float:
                    print "The elements of the 'params' array must be floating point numbers."
                    return

        # Execute the functional code.
        self.relax.diffusion_tensor.set(diff=diff, params=params)
