/* swig interface for c_chi2.c */
%module c_chi2

/*
%inline %{
	double *array(int size) {
		return (double *) malloc(size*sizeof(int));
	}
%}
*/

extern double chi2(double data[], double back_calc[], double errors[]);


