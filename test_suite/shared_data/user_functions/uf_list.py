
# relax module imports.
import user_functions
from user_functions.data import Uf_info; uf_info = Uf_info()

# Set up the user functions.
user_functions.initialise()

# Loop over all user functions and print out their name.
for uf_name, uf in uf_info.uf_loop():
    print(uf_name)
