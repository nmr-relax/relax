def d2ri_prime(data, create_d2ri_prime_comps, create_d2ri_prime):
	"""Function for the calculation of the trasformed relaxation hessians.

	The trasformed relaxation hessians
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	Data structure:  data.d2ri_prime
	Dimension:  3D, (parameters, parameters, relaxation data)
	Type:  Numeric 3D matrix, Float64
	Dependencies:  data.jw, data.djw, data.d2jw
	Required by:  data.d2ri


	Formulae (a hessian matrix is symmetric)
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


			                   21   / mu0  \ 2  (gH.gN.h_bar)**2
			dip_const_hess  =  -- . | ---- |  . ----------------
			                   2    \ 4.pi /         <r**8>


		CSA
		~~~
			                   (wN.csa)**2
			csa_const_func  =  -----------
			                        3

			                   2.wN**2.csa
			csa_const_grad  =  -----------
			                        3

			                   2.wN**2
			csa_const_hess  =  -------
			                      3


		R1()
		~~~~
			dip_Jw_R1_func  =  J(wH-wN) + 3J(wN) + 6J(wH+wN)

			                   dJ(wH-wN)         dJ(wN)         dJ(wH+wN)
			dip_Jw_R1_grad  =  ---------  +  3 . ------  +  6 . ---------
			                      dJw             dJw              dJw

			                   d2J(wH-wN)          d2J(wN)          d2J(wH+wN)
			dip_Jw_R1_hess  =  ----------  +  3 . ---------  +  6 . ----------
			                   dJwi.dJwj          dJwi.dJwj         dJwi.dJwj


			csa_Jw_R1_func  =  J(wN)

			                   dJ(wN)
			csa_Jw_R1_grad  =  ------
			                    dJw

			                   d2J(wN)
			csa_Jw_R1_hess  =  -------
			                   dJwi.dJwj


		R2()
		~~~~
			dip_Jw_R2_func  =  4J(0) + J(wH-wN) + 3J(wN) + 6J(wH) + 6J(wH+wN)

			                       dJ(0)     dJ(wH-wN)         dJ(wN)         dJ(wH)         dJ(wH+wN)
			dip_Jw_R2_grad  =  4 . -----  +  ---------  +  3 . ------  +  6 . ------  +  6 . ---------
			                        dJw         dJw             dJw            dJw              dJw

			                         d2J(0)      d2J(wH-wN)          d2J(wN)           d2J(wH)          d2J(wH+wN)
			dip_Jw_R2_hess  =  4 . ---------  +  ----------  +  3 . ---------  +  6 . ---------  +  6 . ----------
			                       dJwi.dJwj     dJwi.dJwj          dJwi.dJwj         dJwi.dJwj         dJwi.dJwj


			csa_Jw_R2_func  =  4J(0) + 3J(wN)

			                       dJ(0)         dJ(wN)
			csa_Jw_R2_grad  =  4 . -----  +  3 . ------
			                        dJw           dJw

			                         d2J(0)           d2J(wN)
			csa_Jw_R2_hess  =  4 . ---------  +  3 . ---------
			                       dJwi.dJwj         dJwi.dJwj


		sigma_noe()
		~~~~~~~~~~~
			dip_Jw_sigma_noe_func  =  6J(wH+wN) - J(wH-wN)

			                              dJ(wH+wN)     dJ(wH-wN)
			dip_Jw_sigma_noe_grad  =  6 . ---------  -  ---------
			                                 dJw           dJw

			                              d2J(wH+wN)     d2J(wH-wN)
			dip_Jw_sigma_noe_hess  =  6 . ----------  -  ----------
			                              dJwi.dJwj      dJwi.dJwj


	Spectral density parameter - Spectral density parameter
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		  d2R1()
		---------  =  dip_const_func . dip_Jw_R1_hess  +  csa_const_func . csa_Jw_R1_hess
		dJwi.dJwj


		  d2R2()      dip_const_func                      csa_const_func
		---------  =  -------------- . dip_Jw_R2_hess  +  -------------- . csa_Jw_R2_hess
		dJwi.dJwj           2                                   6


		d2sigma_noe()      
		-------------  =  dip_const_func . dip_Jw_sigma_noe_hess
		  dJwi.dJwj     


	Spectral density parameter - Chemical exchange
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		 d2R1()               d2R2()              d2sigma_noe()
		--------  =  0   ,   --------  =  0   ,   -------------  =  0
		dJw.dRex             dJw.dRex               dJw.dRex


	Spectral density parameter - CSA
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		 d2R1()
		--------  =  csa_const_grad . csa_Jw_R1_grad
		dJw.dcsa


		 d2R2()      csa_const_grad 
		--------  =  -------------- . csa_Jw_R2_grad
		dJw.dcsa           6


		d2sigma_noe()
		-------------  =  0
		  dJw.dcsa


	Spectral density parameter - Bond length
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		d2R1()
		------  =  dip_const_grad . dip_Jw_R1_grad
		dJw.dr


		d2R2()     dip_const_grad 
		------  =  -------------- . dip_Jw_R2_grad
		dJw.dr           2


		d2sigma_noe()
		-------------  =  dip_const_grad . dip_Jw_sigma_noe_grad
		   dJw.dr


	Chemical exchange - Chemical exchange
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		 d2R1()              d2R2()             d2sigma_noe()
		-------  =  0   ,   -------  =  0   ,   -------------  =  0
		dRex**2             dRex**2                dRex**2


	Chemical exchange - CSA
	~~~~~~~~~~~~~~~~~~~~~~~

		  d2R1()                d2R2()              d2sigma_noe()
		---------  =  0   ,   ---------  =  0   ,   -------------  =  0
		dRex.dcsa             dRex.dcsa               dRex.dcsa


	Chemical exchange - Bond length
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		 d2R1()              d2R2()             d2sigma_noe()
		-------  =  0   ,   -------  =  0   ,   -------------  =  0
		dRex.dr             dRex.dr                dRex.dr


	CSA - CSA
	~~~~~~~~~

		 d2R1()
		-------  =  csa_const_hess  . csa_Jw_R1_func
		dcsa**2


		 d2R2()     csa_const_hess 
		-------  =  -------------- . csa_Jw_R2_func
		dcsa**2           6


		d2sigma_noe()
		-------------  =  0
		   dcsa**2


	CSA - Bond length
	~~~~~~~~~~~~~~~~~

		 d2R1()              d2R2()             d2sigma_noe()
		-------  =  0   ,   -------  =  0   ,   -------------  =  0
		dcsa.dr             dcsa.dr                dcsa.dr


	Bond length - Bond length
	~~~~~~~~~~~~~~~~~~~~~~~~~

		d2R1()
		------  =  dip_const_hess . dip_Jw_R1_func
		dr**2


		d2R2()     dip_const_hess
		------  =  -------------- . dip_Jw_R2_func
		dr**2            2


		d2sigma_noe()
		-------------  =  dip_const_hess . dip_Jw_sigma_noe_func
		    dr**2

	"""

	# Loop over the relaxation values.
	for i in range(data.num_ri):
		create_d2ri_prime_comps[i](data, i, data.remap_table[i])

	# Calculate the transformed relaxation gradients.
	for i in range(len(data.params)):
		for j in range(i + 1):
			if create_d2ri_prime[i][j]:
				create_d2ri_prime[i][j](data, i, j)

				# Make the hessian symmetric.
				if i != j:
					data.d2ri_prime[j, i] = data.d2ri_prime[i, j]


def comp_d2r1_djwidjwj_prime(data, i, frq_num):
	"""Calculate the d2r1/dJwi.dJwj components.

	  d2R1()
	---------  =  dip_const_func . dip_Jw_R1_hess  +  csa_const_func . csa_Jw_R1_hess
	dJwi.dJwj

	                   d2J(wH-wN)          d2J(wN)          d2J(wH+wN)
	dip_Jw_R1_hess  =  ----------  +  3 . ---------  +  6 . ----------
	                   dJwi.dJwj          dJwi.dJwj         dJwi.dJwj

	                   d2J(wN)
	csa_Jw_R1_hess  =  -------
	                   dJwi.dJwj

	"""
	data.dip_jw_comps_hess[:, :, i] = data.d2jw[frq_num, 2] + 3.0*data.d2jw[frq_num, 1] + 6.0*data.d2jw[frq_num, 4]
	data.csa_jw_comps_hess[:, :, i] = data.d2jw[frq_num, 1]


def comp_d2r2_djwidjwj_prime(data, i, frq_num):
	"""Calculate the d2r1/dJwi.dJwj components.

	  d2R2()      dip_const_func                      csa_const_func
	---------  =  -------------- . dip_Jw_R2_hess  +  -------------- . csa_Jw_R2_hess
	dJwi.dJwj           2                                   6

	                         d2J(0)      d2J(wH-wN)          d2J(wN)           d2J(wH)          d2J(wH+wN)
	dip_Jw_R2_hess  =  4 . ---------  +  ----------  +  3 . ---------  +  6 . ---------  +  6 . ----------
	                       dJwi.dJwj     dJwi.dJwj          dJwi.dJwj         dJwi.dJwj         dJwi.dJwj

	                         d2J(0)           d2J(wN)
	csa_Jw_R2_hess  =  4 . ---------  +  3 . ---------
	                       dJwi.dJwj         dJwi.dJwj

	"""
	data.dip_jw_comps_hess[:, :, i] = 4.0*data.d2jw[frq_num, 0] + data.d2jw[frq_num, 2] + 3.0*data.d2jw[frq_num, 1] + 6.0*data.d2jw[frq_num, 3] + 6.0*data.d2jw[frq_num, 4]
	data.csa_jw_comps_hess[:, :, i] = 4.0*data.d2jw[frq_num, 0] + 3.0*data.d2jw[frq_num, 1]


def comp_d2sigma_noe_djwidjwj_prime(data, i, frq_num):
	"""Calculate the d2r1/dJwi.dJwj components.

	d2sigma_noe()      
	-------------  =  dip_const_func . dip_Jw_sigma_noe_hess
	  dJwi.dJwj     

	                              d2J(wH+wN)     d2J(wH-wN)
	dip_Jw_sigma_noe_hess  =  6 . ----------  -  ----------
	                              dJwi.dJwj      dJwi.dJwj

	"""
	data.dip_jw_comps_hess[:, :, i] = 6.0*data.d2jw[frq_num, 4] - data.d2jw[frq_num, 2]


def func_d2ri_djwidjwj_prime(data, i, j):
	"Spectral density parameter / spectral density parameter hessian."

	data.d2ri_prime[i, j] = data.dip_comps * data.dip_jw_comps_hess[i, j] + data.csa_comps * data.csa_jw_comps_hess[i, j]


def func_d2ri_djwdcsa_prime(data, i, j):
	"Spectral density parameter / CSA hessian."

	data.d2ri_prime[i, j] = data.csa_comps_prime[i] * data.csa_comps_prime[j]


def func_d2ri_djwdr_prime(data, i, j):
	"Spectral density parameter / bond length hessian."

	data.d2ri_prime[i, j] = data.dip_comps_prime[i] * data.dip_comps_prime[j]


def func_d2ri_dcsa2_prime(data, i, j):
	"CSA / CSA hessian."

	data.d2ri_prime[i, j] = data.csa_jw_comps_hess[i, j] * data.csa_comps


def func_d2ri_dr2_prime(data, i, j):
	"Bond length / bond length hessian."

	data.d2ri_prime[i, j] = data.csa_jw_comps_hess[i, j] * data.csa_comps
