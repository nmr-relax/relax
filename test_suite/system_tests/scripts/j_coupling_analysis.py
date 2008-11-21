# Test of J-coupling analysis -- Han Sun.

# Create the J-coupling data pipe.
pipe.create('J-coupling', 'N-state')

# Load the structure.
structure.read_pdb('RR-4402_corr.pdb')

# Load the protons.
structure.load_spins('@*H*')

# Set up the Karplus equation.
j_couplings.karplus_params(A=7.76, B=-1.10, C=1.40)

# Load the J-Couplings.
j_couplings.read('J-test.tbl')

# Calculation the violation of J-couplings.
calc()

# Write the results.
results.write()
