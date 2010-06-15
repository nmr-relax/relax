"""Script for creating model m4 with parameters {S2, te, Rex}."""

# Python module imports.
import __main__
from os import sep
import sys


# Path of the files.
path = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'S2_0.970_te_2048_Rex_0.149'

# Read the sequence.
sequence.read(file='noe.500.out', dir=path, res_num_col=1, res_name_col=2)

# Select the model.
model_free.create_model(model='m4', equation='mf_orig', params=['S2', 'te', 'Rex'], spin_id=None)
