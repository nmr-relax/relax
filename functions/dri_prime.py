def dri_prime(data, create_dri_prime_comps, create_dri_prime):
	"""Function for the calculation of the transformed relaxation gradients.

	The transformed relaxation gradients
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	Data structure:  data.dri_prime
	Dimension:  2D, (parameters, transformed relaxation data)
	Type:  Numeric matrix, Float64
	Dependencies:  data.jw, data.djw
	Required by:  data.dri, data.d2ri


	Formulae
	~~~~~~~~

	Components
	~~~~~~~~~~

		Dipolar
		~~~~~~~
			      1   / mu0  \ 2  (gH.gN.h_bar)**2
			d  =  - . | ---- |  . ----------------
			      4   \ 4.pi /         <r**6>


			         3   / mu0  \ 2  (gH.gN.h_bar)**2
			d'  =  - - . | ---- |  . ----------------
			         2   \ 4.pi /         <r**7>


		CSA
		~~~
			      (wN.csa)**2
			c  =  -----------
			           3

			       2.wN**2.csa
			c'  =  -----------
			            3


		R1()
		~~~~
			J_R1_d  =  J(wH-wN) + 3J(wN) + 6J(wH+wN)

			                 dJ(wH-wN)         dJ(wN)         dJ(wH+wN)
			J_R1_d_prime  =  ---------  +  3 . ------  +  6 . ---------
			                    dmf             dmf              dmf


			J_R1_c  =  J(wN)

			                 dJ(wN)
			J_R1_c_prime  =  ------
			                  dmf



		R2()
		~~~~
			J_R2_d  =  4J(0) + J(wH-wN) + 3J(wN) + 6J(wH) + 6J(wH+wN)

			                     dJ(0)     dJ(wH-wN)         dJ(wN)         dJ(wH)         dJ(wH+wN)
			J_R2_d_prime  =  4 . -----  +  ---------  +  3 . ------  +  6 . ------  +  6 . ---------
			                      dmf         dmf             dmf            dmf             dmf


			J_R2_c  =  4J(0) + 3J(wN)

			                     dJ(0)         dJ(wN)
			J_R2_c_prime  =  4 . -----  +  3 . ------
			                      dmf           dmf


		sigma_noe()
		~~~~~~~~~~~
			J_sigma_noe  =  6J(wH+wN) - J(wH-wN)

			                          dJ(wH+wN)     dJ(wH-wN)
			J_sigma_noe_prime  =  6 . ---------  -  ---------
			                             dmf           dmf


	Spectral density parameter
	~~~~~~~~~~~~~~~~~~~~~~~~~~

		dR1()
		-----  =  d . J_R1_d_prime  +  c . J_R1_c_prime
		 dJj


		dR2()     d                    c
		-----  =  - . J_R2_d_prime  +  - . J_R2_c_prime
		 dJj      2                    6


		dsigma_noe()
		------------  = d . J_sigma_noe_prime
		    dJj


	Chemical exchange
	~~~~~~~~~~~~~~~~~

		dR1()
		-----  =  0
		dRex


		dR2()
		-----  =  1
		dRex


		 dR2()
		------  =  (2.pi.wH)**2
		drhoex


		dsigma_noe()
		------------  =  0
		   dRex


	CSA
	~~~

		dR1()
		-----  =  c' . J_R1_c
		dcsa


		dR2()     c'
		-----  =  - . J_R2_c
		dcsa      6


		dsigma_noe()
		------------  =  0
		    dcsa


	Bond length
	~~~~~~~~~~~

		dR1()
		-----  =  d' . J_R1_d
		 dr


		dR2()     d'
		-----  =  - . J_R2_d
		 dr       2


		dsigma_noe()
		------------  =  d' . J_sigma_noe
		     dr

	"""

	# Loop over the relaxation values.
	for i in range(data.num_ri):
		create_dri_prime_comps[i](data, i, data.remap_table[i])

	# Calculate the transformed relaxation gradients.
	for i in range(len(data.params)):
		create_dri_prime[i](data, i)


def comp_dr1_dmf_prime(data, i, frq_num):
	"""Calculate the dr1 components.

	dR1()
	-----  =  d . J_R1_d_prime  +  c . J_R1_c_prime
	 dJj

	                 dJ(wH-wN)         dJ(wN)         dJ(wH+wN)
	J_R1_d_prime  =  ---------  +  3 . ------  +  6 . ---------
	                    dmf             dmf              dmf

	                 dJ(wN)
	J_R1_c_prime  =  ------
	                  dmf

	"""

	data.dip_jw_comps_prime[:, i] = data.djw[frq_num, 2] + 3.0*data.djw[frq_num, 1] + 6.0*data.djw[frq_num, 4]
	data.csa_jw_comps_prime[:, i] = data.djw[frq_num, 1]


def comp_dr2_dmf_prime(data, i, frq_num):
	"""Calculate the dr2 components.

	dR2()     d                    c
	-----  =  - . J_R2_d_prime  +  - . J_R2_c_prime
	 dJj      2                    6

	                     dJ(0)     dJ(wH-wN)         dJ(wN)         dJ(wH)         dJ(wH+wN)
	J_R2_d_prime  =  4 . -----  +  ---------  +  3 . ------  +  6 . ------  +  6 . ---------
	                      dmf         dmf             dmf            dmf             dmf

	                     dJ(0)         dJ(wN)
	J_R2_c_prime  =  4 . -----  +  3 . ------
	                      dmf           dmf

	"""

	data.dip_jw_comps_prime[:, i] = 4.0*data.djw[frq_num, 0] + data.djw[frq_num, 2] + 3.0*data.djw[frq_num, 1] + 6.0*data.djw[frq_num, 3] + 6.0*data.djw[frq_num, 4]
	data.csa_jw_comps_prime[:, i] = 4.0*data.djw[frq_num, 0] + 3.0*data.djw[frq_num, 1]
	data.rex_comps_prime[:, i] = (1e-8 * relax.data.frq[frq_num])**2


def comp_dr2_drex_prime(data, i, frq_num):
	"""Calculate the dr2 components.

	 dR2()
	------  =  (2.pi.wH)**2
	drhoex

	"""

	data.rex_comps_prime[:, i] = (1e-8 * relax.data.frq[frq_num])**2


def comp_dsigma_noe_dmf_prime(data, i, frq_num):
	"""Calculate the dsigma_noe components.

	dsigma_noe()
	------------  = d . J_sigma_noe_prime
	    dJj

	                          dJ(wH+wN)     dJ(wH-wN)
	J_sigma_noe_prime  =  6 . ---------  -  ---------
	                             dmf           dmf

	"""

	data.dip_jw_comps_prime[:, i] = 6.0*data.djw[frq_num, 4] - data.djw[frq_num, 2]


def func_dcsa_prime(data, i):
	"CSA derivatives."

	data.dri_prime[i] = data.csa_comps_prime[i] * data.csa_jw_comps


def func_dri_dmf_prime(data, i):
	"Spectral density parameter derivatives."

	data.dri_prime[i] = data.dip_comps * data.dip_jw_comps_prime[i] + data.csa_comps * data.csa_jw_comps_prime[i]


def func_dri_dr_prime(data, i):
	"Bond length derivatives."

	data.dri_prime[i] = data.dip_comps_prime[i] * data.dip_jw_comps


def func_dri_drex_prime(data, i):
	"Chemical exchange derivatives."

	data.dri_prime[i] = data.rex_comps_prime[i]
