from Numeric import dot

def backtrack(func, args, x, f, g, p, a_init=1.0, rho=0.5, c=1e-4):
    """Backtracking line search.

    Procedure 3.1, page 41, from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright,
    1999, 2nd ed.

    Requires the gradient vector at point xk.


    Function options
    ~~~~~~~~~~~~~~~~

    func   - The function to minimise.
    args   - The tuple of arguments to supply to the functions func.
    x      - The parameter vector.
    f      - The function value at the point x.
    g      - The gradient vector at the point x.
    p      - The descent direction.
    a_init - Initial step length.
    rho    - The step length scaling factor (should be between 0 and 1).
    c      - Constant between 0 and 1 determining the slope for the sufficient decrease condition.


    Returned objects
    ~~~~~~~~~~~~~~~~

    The parameter vector, minimised along the direction xk + ak.pk, to be used at k+1.


    Internal variables
    ~~~~~~~~~~~~~~~~~~

    ai  - The step length at line search iteration i.
    xai - The parameter vector at step length ai.
    fai - The function value at step length ai.
    """

    # Initialise values.
    a = a_init
    f_count = 0

    while 1:
        fk = apply(func, (x + a*p,)+args)
        f_count = f_count + 1

        # Check if the sufficient decrease condition is met.  If not, scale the step length by rho.
        if fk <= f + c*a*dot(g, p):
            return a, f_count
        else:
            a = rho*a
