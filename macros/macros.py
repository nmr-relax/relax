import sys
from re import match

from bond_length import bond_length
from csa import csa
from echo_data import echo_data
from load_relax_data import load_relax_data
from load_seq import load_seq
from ls import ls
from pdb import pdb
from mf_model import mf_model
from set_diffusion_tensor import set_diffusion_tensor
from set_model_selection import set_model_selection


class macros:
	def __init__(self, relax):
		"Class for holding all macros."

		self.bond_length = bond_length(relax)
		self.csa = csa(relax)
		self.echo_data = echo_data(relax)
		self.load_relax_data = load_relax_data(relax)
		self.load_seq = load_seq(relax)
		self.ls = ls
		self.pdb = pdb(relax)
		self.mf_model = mf_model(relax)
		self.set_diffusion_tensor = set_diffusion_tensor(relax)
		self.set_model_selection = set_model_selection(relax)
