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


def ri_comps(data, create_dip_jw_hess, create_csa_jw_hess, dip_func_flag, csa_func_flag):
	"Function for the calculation of the dipolar and CSA constant hessians and the dipolar and CSA Jw component hessians."

	# Dipolar constant function value.
	if dip_func_flag:
		data.dip_const_func = comp_dip_const_func(data)

	# CSA constant function value.
	if csa_func_flag:
		data.dip_const_func = comp_dip_const_func(data)

	# Loop over the relaxation values.
	for i in range(data.num_ri):
		data.dip_jw_comps_func[i] = create_dip_jw_func[i](data, data.remap_table[i])
		data.csa_jw_comps_func[i] = create_csa_jw_func[i](data, data.remap_table[i])


def d2ri_comps(data, create_dip_jw_hess, create_csa_jw_hess, dip_hess_flag, csa_hess_flag):
	"Function for the calculation of the dipolar and CSA constant hessians and the dipolar and CSA Jw component hessians."

	# Dipolar constant hessian.
	if dip_hess_flag:
		data.dip_const_hess = comp_dip_const_hess(data)

	# CSA constant hessian.
	if csa_hess_flag:
		data.dip_const_hess = comp_dip_const_hess(data)

	# Loop over the relaxation values.
	for i in range(data.num_ri):
		data.dip_jw_comps_hess[i] = create_dip_jw_hess[i](data, data.remap_table[i])
		data.csa_jw_comps_hess[i] = create_csa_jw_hess[i](data, data.remap_table[i])


def d2ri_comps(data, create_dip_jw_hess, create_csa_jw_hess, dip_hess_flag, csa_hess_flag):
	"Function for the calculation of the dipolar and CSA constant hessians and the dipolar and CSA Jw component hessians."

	# Dipolar constant hessian.
	if dip_hess_flag:
		data.dip_const_hess = comp_dip_const_hess(data)

	# CSA constant hessian.
	if csa_hess_flag:
		data.dip_const_hess = comp_dip_const_hess(data)

	# Loop over the relaxation values.
	for i in range(data.num_ri):
		data.dip_jw_comps_hess[i] = create_dip_jw_hess[i](data, data.remap_table[i])
		data.csa_jw_comps_hess[i] = create_csa_jw_hess[i](data, data.remap_table[i])


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
