"""Script for creating model m4 with parameters {S2, te, Rex}."""

# Python module imports.
import sys


# Path of the files.
path = sys.path[-1] + '/test_suite/shared_data/model_free/S2_0.970_te_2048_Rex_0.149'

# Read the sequence.
sequence.read(file='noe.500.out', dir=path)

# Select the model.
model_free.create_model(model='m4', equation='mf_orig', params=['S2', 'te', 'Rex'], spin_id=None)
