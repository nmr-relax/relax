
class diffusion_tensor:
	def __init__(self, relax):
		"Class containing the macro for selecting which model selection method should be used."

		self.relax = relax


	def set(self, diff=None, *params):
		"Macro for selecting which model selection method should be used."

		# Macro intro print out.
		print "Executing macro set_diffusion_tensor"

		# Test if the diffusion tensor is given.
		if not diff:
			print "No diffusion tensor given."
			print "[ failed ]"
			return

		# Test diffusion tensor parameters.
		if diff == 'iso' and ( len(params) != 1 or type(params[0]) != float ):
			print "Isotropic diffusion parameters are invalid."
			print "[ failed ]"
			return
		elif diff == 'axial' and ( len(params) != 3 or type(params[0]) != float or type(params[1]) != float or type(params[2]) != float ):
			print "Axially symmetric diffusion parameters are invalid."
			print "[ failed ]"
			return
		elif diff == 'aniso' and ( len(params) != 6 or type(params[0]) != float or type(params[1]) != float or type(params[2]) != float or type(params[3]) != float or type(params[4]) != float or type(params[5]) != float ):
			print "Anisotropic diffusion parameters are invalid."
			print "[ failed ]"
			return

		self.relax.data.diff_type = diff

		self.relax.data.diff_params = []
		for i in range(len(params)):
			self.relax.data.diff_params.append(params[i])

		print "   Tensor:     " + `diff`
		print "   Parameters: " + `params`
		print "[ OK ]"
