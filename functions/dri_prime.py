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
			dip_const_func  =  - . | ---- |  . ----------------
			                   4   \ 4.pi /         <r**6>


			                     3   / mu0  \ 2  (gH.gN.h_bar)**2
			dip_const_grad  =  - - . | ---- |  . ----------------
			                     2   \ 4.pi /         <r**7>


		CSA
		~~~
			                   (wN.csa)**2
			csa_const_func  =  -----------
			                        3

			                   2.wN**2.csa
			csa_const_grad  =  -----------
			                        3


		R1()
		~~~~
			dip_Jw_R1_func  =  J(wH-wN) + 3J(wN) + 6J(wH+wN)

			                   dJ(wH-wN)         dJ(wN)         dJ(wH+wN)
			dip_Jw_R1_grad  =  ---------  +  3 . ------  +  6 . ---------
			                      dJw             dJw              dJw


			csa_Jw_R1_func  =  J(wN)

			                   dJ(wN)
			csa_Jw_R1_grad  =  ------
			                    dJw


		R2()
		~~~~
			dip_Jw_R2_func  =  4J(0) + J(wH-wN) + 3J(wN) + 6J(wH) + 6J(wH+wN)

			                       dJ(0)     dJ(wH-wN)         dJ(wN)         dJ(wH)         dJ(wH+wN)
			dip_Jw_R2_grad  =  4 . -----  +  ---------  +  3 . ------  +  6 . ------  +  6 . ---------
			                        dJw         dJw             dJw            dJw              dJw


			csa_Jw_R2_func  =  4J(0) + 3J(wN)

			                       dJ(0)         dJ(wN)
			csa_Jw_R2_grad  =  4 . -----  +  3 . ------
			                        dJw           dJw


		sigma_noe()
		~~~~~~~~~~~
			dip_Jw_sigma_noe_func  =  6J(wH+wN) - J(wH-wN)

			                              dJ(wH+wN)     dJ(wH-wN)
			dip_Jw_sigma_noe_grad  =  6 . ---------  -  ---------
			                                 dJw           dJw


	Spectral density parameter
	~~~~~~~~~~~~~~~~~~~~~~~~~~

		dR1()
		-----  =  dip_const_func . dip_Jw_R1_grad  +  csa_const_func . csa_Jw_R1_grad
		 dJw


		dR2()     dip_const_func                      csa_const_func
		-----  =  -------------- . dip_Jw_R2_grad  +  -------------- . csa_Jw_R2_grad
		 dJw            2                                   6


		dsigma_noe()
		------------  = dip_const_func . dip_Jw_sigma_noe_grad
		    dJw


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
		-----  =  csa_const_grad . csa_Jw_R1_func
		dcsa


		dR2()     csa_const_grad
		-----  =  -------------- . csa_Jw_R2_func
		dcsa            6


		dsigma_noe()
		------------  =  0
		    dcsa


	Bond length
	~~~~~~~~~~~

		dR1()
		-----  =  dip_const_grad . dip_Jw_R1_func
		 dr


		dR2()     dip_const_grad
		-----  =  -------------- . dip_Jw_R2_func
		 dr             2


		dsigma_noe()
		------------  =  dip_const_grad . dip_Jw_sigma_noe_func
		     dr

	"""

	# Loop over the relaxation values.
	for i in range(data.num_ri):
		create_dri_prime_comps[i](data, i, data.remap_table[i])

	# Calculate the transformed relaxation gradients.
	for i in range(len(data.params)):
		create_dri_prime[i](data, i)


def comp_dr1_djw_prime(data, i, frq_num):
	"""Calculate the dr1/dJw components.

	dR1()
	-----  =  dip_const_func . dip_Jw_R1_grad  +  csa_const_func . csa_Jw_R1_grad
	 dJw

	                   dJ(wH-wN)         dJ(wN)         dJ(wH+wN)
	dip_Jw_R1_grad  =  ---------  +  3 . ------  +  6 . ---------
	                      dJw             dJw              dJw

	                   dJ(wN)
	csa_Jw_R1_grad  =  ------
	                    dJw

	"""

	data.dip_jw_comps_grad[:, i] = data.djw[frq_num, 2] + 3.0*data.djw[frq_num, 1] + 6.0*data.djw[frq_num, 4]
	data.csa_jw_comps_grad[:, i] = data.djw[frq_num, 1]


def comp_dr1_drex_prime(data, i, frq_num):
	"""Calculate the dr1/drex components.

	dR1()
	-----  =  0
	dRex

	"""

	return


def comp_dr2_djw_prime(data, i, frq_num):
	"""Calculate the dr2/dJw components.

	dR2()     dip_const_func                      csa_const_func
	-----  =  -------------- . dip_Jw_R2_grad  +  -------------- . csa_Jw_R2_grad
	 dJw            2                                   6

	                       dJ(0)     dJ(wH-wN)         dJ(wN)         dJ(wH)         dJ(wH+wN)
	dip_Jw_R2_grad  =  4 . -----  +  ---------  +  3 . ------  +  6 . ------  +  6 . ---------
	                        dJw         dJw             dJw            dJw              dJw

	                       dJ(0)         dJ(wN)
	csa_Jw_R2_grad  =  4 . -----  +  3 . ------
	                        dJw           dJw

	"""

	data.dip_jw_comps_grad[:, i] = 4.0*data.djw[frq_num, 0] + data.djw[frq_num, 2] + 3.0*data.djw[frq_num, 1] + 6.0*data.djw[frq_num, 3] + 6.0*data.djw[frq_num, 4]
	data.csa_jw_comps_grad[:, i] = 4.0*data.djw[frq_num, 0] + 3.0*data.djw[frq_num, 1]
	data.rex_comps_grad[:, i] = (1e-8 * data.frq[frq_num])**2


def comp_dr2_drex_prime(data, i, frq_num):
	"""Calculate the dr2/drex components.

	 dR2()
	------  =  (2.pi.wH)**2
	drhoex

	"""

	data.rex_comps_grad[:, i] = (1e-8 * data.frq[frq_num])**2


def comp_dsigma_noe_djw_prime(data, i, frq_num):
	"""Calculate the dsigma_noe/dJw components.

	dsigma_noe()
	------------  = dip_const_func . dip_Jw_sigma_noe_grad
	    dJw

	                              dJ(wH+wN)     dJ(wH-wN)
	dip_Jw_sigma_noe_grad  =  6 . ---------  -  ---------
	                                 dJw           dJw

	"""

	data.dip_jw_comps_grad[:, i] = 6.0*data.djw[frq_num, 4] - data.djw[frq_num, 2]


def comp_dsigma_noe_drex_prime(data, i, frq_num):
	"""Calculate the dsigma_noe/drex components.

	dsigma_noe()
	------------  =  0
	    dcsa

	"""

	return


def func_dcsa_prime(data, i):
	"CSA derivatives."

	data.dri_grad[i] = data.csa_comps_grad[i] * data.csa_jw_comps


def func_dri_djw_prime(data, i):
	"Spectral density parameter derivatives."

	data.dri_prime[i] = data.dip_comps * data.dip_jw_comps_grad[i] + data.csa_comps * data.csa_jw_comps_grad[i]


def func_dri_dr_prime(data, i):
	"Bond length derivatives."

	data.dri_prime[i] = data.dip_comps_grad[i] * data.dip_jw_comps


def func_dri_drex_prime(data, i):
	"Chemical exchange derivatives."

	data.dri_prime[i] = data.rex_comps_grad[i]
