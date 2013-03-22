# relax script for regenerating the 'basic_single_pipe.bz2' saved state.  This is for when the saved
# state becomes incompatible with relax.

# The relax data store.
from data_store import Relax_data_store; ds = Relax_data_store()


# Add a data pipe to the data store.
ds.add(pipe_name='orig', pipe_type='mf')

# Add a single object to the 'orig' data pipe.
ds['orig'].x = 1

# Add a single object to the storage object.
ds.y = 'Hello'

# Save the state.
state.save('basic_single_pipe', force=True)
