#	Component formulae
#	~~~~~~~~~~~~~~~~~~
#
#		Dipolar constant
#		~~~~~~~~~~~~~~~~
#			                   1   / mu0  \ 2  (gH.gN.h_bar)**2
#			dip_const_func  =  - . | ---- |  . ----------------
#			                   4   \ 4.pi /         <r**6>
#
#
#			                     3   / mu0  \ 2  (gH.gN.h_bar)**2
#			dip_const_grad  =  - - . | ---- |  . ----------------
#			                     2   \ 4.pi /         <r**7>
#
#
#			                   21   / mu0  \ 2  (gH.gN.h_bar)**2
#			dip_const_hess  =  -- . | ---- |  . ----------------
#			                   2    \ 4.pi /         <r**8>
#
#
#		CSA constant
#		~~~~~~~~~~~~
#			                   (wN.csa)**2
#			csa_const_func  =  -----------
#			                        3
#
#			                   2.wN**2.csa
#			csa_const_grad  =  -----------
#			                        3
#
#			                   2.wN**2
#			csa_const_hess  =  -------
#			                      3
#
#
#		R1()
#		~~~~
#			dip_Jw_R1_func  =  J(wH-wN) + 3J(wN) + 6J(wH+wN)
#
#			                   dJ(wH-wN)         dJ(wN)         dJ(wH+wN)
#			dip_Jw_R1_grad  =  ---------  +  3 . ------  +  6 . ---------
#			                      dJw             dJw              dJw
#
#			                   d2J(wH-wN)          d2J(wN)          d2J(wH+wN)
#			dip_Jw_R1_hess  =  ----------  +  3 . ---------  +  6 . ----------
#			                   dJwi.dJwj          dJwi.dJwj         dJwi.dJwj
#
#
#			csa_Jw_R1_func  =  J(wN)
#
#			                   dJ(wN)
#			csa_Jw_R1_grad  =  ------
#			                    dJw
#
#			                   d2J(wN)
#			csa_Jw_R1_hess  =  -------
#			                   dJwi.dJwj
#
#
#		R2()
#		~~~~
#			dip_Jw_R2_func  =  4J(0) + J(wH-wN) + 3J(wN) + 6J(wH) + 6J(wH+wN)
#
#			                       dJ(0)     dJ(wH-wN)         dJ(wN)         dJ(wH)         dJ(wH+wN)
#			dip_Jw_R2_grad  =  4 . -----  +  ---------  +  3 . ------  +  6 . ------  +  6 . ---------
#			                        dJw         dJw             dJw            dJw              dJw
#
#			                         d2J(0)      d2J(wH-wN)          d2J(wN)           d2J(wH)          d2J(wH+wN)
#			dip_Jw_R2_hess  =  4 . ---------  +  ----------  +  3 . ---------  +  6 . ---------  +  6 . ----------
#			                       dJwi.dJwj     dJwi.dJwj          dJwi.dJwj         dJwi.dJwj         dJwi.dJwj
#
#
#			csa_Jw_R2_func  =  4J(0) + 3J(wN)
#
#			                       dJ(0)         dJ(wN)
#			csa_Jw_R2_grad  =  4 . -----  +  3 . ------
#			                        dJw           dJw
#
#			                         d2J(0)           d2J(wN)
#			csa_Jw_R2_hess  =  4 . ---------  +  3 . ---------
#			                       dJwi.dJwj         dJwi.dJwj
#
#
#		sigma_noe()
#		~~~~~~~~~~~
#			dip_Jw_sigma_noe_func  =  6J(wH+wN) - J(wH-wN)
#
#			                              dJ(wH+wN)     dJ(wH-wN)
#			dip_Jw_sigma_noe_grad  =  6 . ---------  -  ---------
#			                                 dJw           dJw
#
#			                              d2J(wH+wN)     d2J(wH-wN)
#			dip_Jw_sigma_noe_hess  =  6 . ----------  -  ----------
#			                              dJwi.dJwj      dJwi.dJwj
#
#
#	Spectral density parameter - Spectral density parameter
#	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#		  d2R1()
#		---------  =  dip_const_func . dip_Jw_R1_hess  +  csa_const_func . csa_Jw_R1_hess
#		dJwi.dJwj
#
#
#		  d2R2()      dip_const_func                      csa_const_func
#		---------  =  -------------- . dip_Jw_R2_hess  +  -------------- . csa_Jw_R2_hess
#		dJwi.dJwj           2                                   6
#
#
#		d2sigma_noe()      
#		-------------  =  dip_const_func . dip_Jw_sigma_noe_hess
#		  dJwi.dJwj     
#
#
#	Spectral density parameter - Chemical exchange
#	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#		 d2R1()               d2R2()              d2sigma_noe()
#		--------  =  0   ,   --------  =  0   ,   -------------  =  0
#		dJw.dRex             dJw.dRex               dJw.dRex
#
#
#	Spectral density parameter - CSA
#	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#		 d2R1()
#		--------  =  csa_const_grad . csa_Jw_R1_grad
#		dJw.dcsa
#
#
#		 d2R2()      csa_const_grad 
#		--------  =  -------------- . csa_Jw_R2_grad
#		dJw.dcsa           6
#
#
#		d2sigma_noe()
#		-------------  =  0
#		  dJw.dcsa
#
#
#	Spectral density parameter - Bond length
#	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#		d2R1()
#		------  =  dip_const_grad . dip_Jw_R1_grad
#		dJw.dr
#
#
#		d2R2()     dip_const_grad 
#		------  =  -------------- . dip_Jw_R2_grad
#		dJw.dr           2
#
#
#		d2sigma_noe()
#		-------------  =  dip_const_grad . dip_Jw_sigma_noe_grad
#		   dJw.dr
#
#
#	Chemical exchange - Chemical exchange
#	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#		 d2R1()              d2R2()             d2sigma_noe()
#		-------  =  0   ,   -------  =  0   ,   -------------  =  0
#		dRex**2             dRex**2                dRex**2
#
#
#	Chemical exchange - CSA
#	~~~~~~~~~~~~~~~~~~~~~~~
#
#		  d2R1()                d2R2()              d2sigma_noe()
#		---------  =  0   ,   ---------  =  0   ,   -------------  =  0
#		dRex.dcsa             dRex.dcsa               dRex.dcsa
#
#
#	Chemical exchange - Bond length
#	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#		 d2R1()              d2R2()             d2sigma_noe()
#		-------  =  0   ,   -------  =  0   ,   -------------  =  0
#		dRex.dr             dRex.dr                dRex.dr
#
#
#	CSA - CSA
#	~~~~~~~~~
#
#		 d2R1()
#		-------  =  csa_const_hess  . csa_Jw_R1_func
#		dcsa**2
#
#
#		 d2R2()     csa_const_hess 
#		-------  =  -------------- . csa_Jw_R2_func
#		dcsa**2           6
#
#
#		d2sigma_noe()
#		-------------  =  0
#		   dcsa**2
#
#
#	CSA - Bond length
#	~~~~~~~~~~~~~~~~~
#
#		 d2R1()              d2R2()             d2sigma_noe()
#		-------  =  0   ,   -------  =  0   ,   -------------  =  0
#		dcsa.dr             dcsa.dr                dcsa.dr
#
#
#	Bond length - Bond length
#	~~~~~~~~~~~~~~~~~~~~~~~~~
#
#		d2R1()
#		------  =  dip_const_hess . dip_Jw_R1_func
#		dr**2
#
#
#		d2R2()     dip_const_hess
#		------  =  -------------- . dip_Jw_R2_func
#		dr**2            2
#
#
#		d2sigma_noe()
#		-------------  =  dip_const_hess . dip_Jw_sigma_noe_func
#		    dr**2
#



# The main functions, ri_comps, dri_comps, and d2ri_comps.
##########################################################

# Ri.

def ri_comps(data, create_dip_func, create_dip_jw_func, create_csa_func, create_csa_jw_func):
	"Function for the calculation of the dipolar and CSA J(w) components."

	# Loop over the relaxation values.
	for i in range(data.num_ri):
		# Dipolar J(w) components
		data.dip_jw_comps_func[i] = create_dip_jw_func[i](data.jw, data.remap_table[i])

		# CSA J(w) components.
		if create_csa_jw_func[i]:
			data.csa_jw_comps_func[i] = create_csa_jw_func[i](data.jw, data.remap_table[i])


def ri_comps_r(data, create_dip_func, create_dip_jw_func, create_csa_func, create_csa_jw_func):
	"Function for the calculation of the dipolar constant components and the dipolar and CSA J(w) components."

	# Dipolar constant function value.
	data.dip_const_func = comp_dip_const_func(data)

	# Loop over the relaxation values.
	for i in range(data.num_ri):
		# Dipolar constant components.
		data.dip_comp_func[i] = data.dip_const_func
		if create_dip_func[i]:
			data.dip_comp_func[i] = create_dip_func[i](data.dip_const_func)

		# Dipolar J(w) components
		data.dip_jw_comps_func[i] = create_dip_jw_func[i](data.jw, data.remap_table[i])

		# CSA J(w) components.
		if create_csa_jw_func[i]:
			data.csa_jw_comps_func[i] = create_csa_jw_func[i](data.jw, data.remap_table[i])


def ri_comps_csa(data, create_dip_func, create_dip_jw_func, create_csa_func, create_csa_jw_func):
	"Function for the calculation of the CSA constant components and the dipolar and CSA J(w) components."

	# CSA constant function value.
	data.dip_const_func = comp_dip_const_func(data)

	# Loop over the relaxation values.
	for i in range(data.num_ri):
		# Dipolar J(w) components
		data.dip_jw_comps_func[i] = create_dip_jw_func[i](data.jw, data.remap_table[i])

		# CSA constant components.
		if create_csa_func[i]:
			data.csa_comp_func[i] = create_csa_func[i](data.csa_const_func, data.remap_table[i])

		# CSA J(w) components.
		if create_csa_jw_func[i]:
			data.csa_jw_comps_func[i] = create_csa_jw_func[i](data.jw, data.remap_table[i])


def ri_comps_r_csa(data, create_dip_func, create_dip_jw_func, create_csa_func, create_csa_jw_func):
	"Function for the calculation of the dipolar and CSA constant components and the dipolar and CSA J(w) components."

	# Dipolar constant function value.
	data.dip_const_func = comp_dip_const_func(data)

	# CSA constant function value.
	data.dip_const_func = comp_dip_const_func(data)

	# Loop over the relaxation values.
	for i in range(data.num_ri):
		# Dipolar constant components.
		data.dip_comp_func[i] = data.dip_const_func
		if create_dip_func[i]:
			data.dip_comp_func[i] = create_dip_func[i](data.dip_const_func)

		# Dipolar J(w) components
		data.dip_jw_comps_func[i] = create_dip_jw_func[i](data.jw, data.remap_table[i])

		# CSA constant components.
		if create_csa_func[i]:
			data.csa_comp_func[i] = create_csa_func[i](data.csa_const_func, data.remap_table[i])

		# CSA J(w) components.
		if create_csa_jw_func[i]:
			data.csa_jw_comps_func[i] = create_csa_jw_func[i](data.jw, data.remap_table[i])


# dRi.

def dri_comps(data, create_dip_grad, create_dip_jw_grad, create_csa_grad, create_csa_jw_grad):
	"Function for the calculation of the dipolar and CSA constant gradients and the dipolar and CSA J(w) component gradients."

	# Dipolar constant gradients.
	if dip_grad_flag:
		data.dip_const_grad = comp_dip_const_grad(data)

	# CSA constant gradients.
	if csa_grad_flag:
		data.dip_const_grad = comp_dip_const_grad(data)

	# Loop over the relaxation values.
	for i in range(data.num_ri):
		data.dip_comp_grad[i] = create_dip_grad[i](data)
		data.dip_jw_comps_grad[i] = create_dip_jw_grad[i](data, data.remap_table[i])
		if create_csa_grad[i]:
			data.csa_comp_grad[i] = create_csa_grad[i](data, data.remap_table[i])
		if create_csa_jw_grad[i]:
			data.csa_jw_comps_grad[i] = create_csa_jw_grad[i](data, data.remap_table[i])


# d2Ri.

def d2ri_comps(data, create_dip_hess, create_dip_jw_hess, create_csa_hess, create_csa_jw_hess):
	"Function for the calculation of the dipolar and CSA constant hessians and the dipolar and CSA J(w) component hessians."

	# Dipolar constant hessian.
	if dip_hess_flag:
		data.dip_const_hess = comp_dip_const_hess(data)

	# CSA constant hessian.
	if csa_hess_flag:
		data.dip_const_hess = comp_dip_const_hess(data)

	# Loop over the relaxation values.
	for i in range(data.num_ri):
		data.dip_comp_hess[i] = create_dip_hess[i](data)
		data.dip_jw_comps_hess[i] = create_dip_jw_hess[i](data, data.remap_table[i])
		if create_csa_hess[i]:
			data.csa_comp_hess[i] = create_csa_hess[i](data, data.remap_table[i])
		if create_csa_jw_hess[i]:
			data.csa_jw_comps_hess[i] = create_csa_jw_hess[i](data, data.remap_table[i])



#  CSA constant components.
###########################

# Sigma NOE has no CSA components!

def comp_r1_csa_const(csa_const_data, frq_num):
	"""Calculate the R1 CSA constant components.

	csa_const_func

	csa_const_grad

	csa_const_hess

	"""

	return csa_const_data[frq_num]


def comp_r2_csa_const(csa_const_data, frq_num):
	"""Calculate the R2 CSA constant. components

	csa_const_func / 6

	csa_const_grad / 6

	csa_const_hess / 6

	"""

	return csa_const_data[frq_num] / 6.0



# Dipolar constant components.
##############################


def comp_r2_dip_const(dip_const_data):
	"""Calculate the R1 dipolar constant components.

	dip_const_func / 2

	dip_const_grad / 2

	dip_const_hess / 2

	"""

	return dip_const_data / 2.0



# CSA J(w) components.
######################

def comp_r1_csa_jw(jw_data, frq_num):
	"""Calculate the R1 CSA J(w) components.

	csa_Jw_R1_func  =  J(wN)

	                   dJ(wN)
	csa_Jw_R1_grad  =  ------
	                    dJw

	                    d2J(wN)
	csa_Jw_R1_hess  =  ---------
	                   dJwi.dJwj

	"""

	return jw_data[frq_num, 1]



# Dipolar J(w) components.
##########################

def comp_r1_dip_jw(jw_data, frq_num):
	"""Calculate the R1 dipolar J(w) components.

	dip_Jw_R1_func  =  J(wH-wN) + 3J(wN) + 6J(wH+wN)

	                   dJ(wH-wN)         dJ(wN)         dJ(wH+wN)
	dip_Jw_R1_grad  =  ---------  +  3 . ------  +  6 . ---------
	                      dJw             dJw              dJw

	                   d2J(wH-wN)          d2J(wN)          d2J(wH+wN)
	dip_Jw_R1_hess  =  ----------  +  3 . ---------  +  6 . ----------
	                   dJwi.dJwj          dJwi.dJwj         dJwi.dJwj

	"""

	return jw_data[frq_num, 2] + 3.0*jw_data[frq_num, 1] + 6.0*jw_data[frq_num, 4]



# Crap.
#######

def comp_d2r2_csa_jw(data, frq_num):
	"""Calculate the d2r2/dJwi.dJwj CSA J(w) components.

	                         d2J(0)           d2J(wN)
	csa_Jw_R2_hess  =  4 . ---------  +  3 . ---------
	                       dJwi.dJwj         dJwi.dJwj

	"""

	return 4.0*data.d2jw[frq_num, 0] + 3.0*data.d2jw[frq_num, 1]


def comp_d2r2_dip_const(data):
	"""Calculate the R2 dipolar constant hessian.

	  d2R2()      dip_const_func                      csa_const_func
	---------  =  -------------- . dip_Jw_R2_hess  +  -------------- . csa_Jw_R2_hess
	dJwi.dJwj           2                                   6

	"""

	return data.dip_const_hess / 6.0


def comp_d2r2_dip_jw(data, frq_num):
	"""Calculate the d2r1/dJwi.dJwj components.

	                         d2J(0)      d2J(wH-wN)          d2J(wN)           d2J(wH)          d2J(wH+wN)
	dip_Jw_R2_hess  =  4 . ---------  +  ----------  +  3 . ---------  +  6 . ---------  +  6 . ----------
	                       dJwi.dJwj     dJwi.dJwj          dJwi.dJwj         dJwi.dJwj         dJwi.dJwj

	"""

	return 4.0*data.d2jw[frq_num, 0] + data.d2jw[frq_num, 2] + 3.0*data.d2jw[frq_num, 1] + 6.0*data.d2jw[frq_num, 3] + 6.0*data.d2jw[frq_num, 4]


def comp_d2sigma_noe_dip_comp(data):
	"""Calculate the d2r1/dJwi.dJwj components.

	d2sigma_noe()      
	-------------  =  dip_const_func . dip_Jw_sigma_noe_hess
	  dJwi.dJwj     

	"""

	return data.dip_const_hess


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
