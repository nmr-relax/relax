# Python module imports.
from random import uniform

# Create a data pipe.
pipe.create('random tensors', 'N-state')

# Generate a number of tensors
for i in range(4):
    align_tensor.init(tensor='tensor %i'%i, params=(uniform(-1e-3, 1e-3), uniform(-1e-3, 1e-3), uniform(-1e-3, 1e-3), uniform(-1e-3, 1e-3), uniform(-1e-3, 1e-3)))

# Display the tensor info.
align_tensor.display()

# Save the results.
results.write('random_tensors', dir=None, force=True)
