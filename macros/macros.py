import sys
from re import match

from command import *
from diffusion_tensor import diffusion_tensor
from echo_data import echo_data
from fixed import fixed
from format import format
from init_data import init_data
from load import load
from mf_model import mf_model
from min import min
from pdb import pdb
from print_all_data import print_all_data
from set_model_selection import set_model_selection
from state import state
from value_setup import value_setup


class macros:
	def __init__(self, relax):
		"Class for holding all macros."

		self.diffusion_tensor = diffusion_tensor(relax)
		self.echo_data = echo_data(relax)
		self.fixed = fixed(relax)
		self.format = format(relax)
		self.init_data = init_data(relax)
		self.load = load(relax)
		self.ls = ls
		self.mf_model = mf_model(relax)
		self.min = min(relax)
		self.pdb = pdb(relax)
		self.print_all_data = print_all_data(relax)
		self.set_model_selection = set_model_selection(relax)
		self.state = state(relax)
		self.system = system
		self.value_setup = value_setup(relax)
