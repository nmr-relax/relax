# The transformed relaxation equations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#	Relaxation equations
#	~~~~~~~~~~~~~~~~~~~~
#
#		R1()  =  dip_const_func . dip_Jw_R1_func  +  csa_const_func . csa_Jw_R1_func
#
#
#		         dip_const_func                      csa_const_func
#		R2()  =  -------------- . dip_Jw_R2_func  +  -------------- . csa_Jw_R2_func  +  Rex
#		               2                                   6
#
#
#		sigma_noe()  =  dip_const_func . dip_Jw_sigma_noe_func
#


def func_ri_prime(data):
	"Calculate the transformed relaxation values."

	data.ri_prime = data.dip_comps_func * data.dip_jw_comps_func + data.csa_comps_func * data.csa_jw_comps_func


def func_ri_prime_rex(data):
	"Calculate the transformed relaxation values."

	data.ri_prime = data.dip_comps_func * data.dip_jw_comps_func + data.csa_comps_func * data.csa_jw_comps_func + data.rex_comps_func
