from Numeric import dot, sqrt

def temp(f, xk, pk, gfk, args=(), c1=1e-4, alpha0=1):
    """Minimize over alpha, the function f(xk+alpha pk)

    Uses the interpolation algorithm (Armiijo backtracking) as suggested by
    Wright and Nocedal in 'Numerical Optimization', 1999, pg. 56-57
    
    Outputs: (alpha, fc, gc)
    """

    fc = 0
    phi0 = apply(f,(xk,)+args)               # compute f(xk)
    phi_a0 = apply(f,(xk+alpha0*pk,)+args)     # compute f
    fc = fc + 2
    derphi0 = dot(gfk,pk)

    if (phi_a0 <= phi0 + c1*alpha0*derphi0):
        return xk + alpha0*pk
        #return alpha0, fc, 0

    # Otherwise compute the minimizer of a quadratic interpolant:

    alpha1 = -(derphi0) * alpha0**2 / 2.0 / (phi_a0 - phi0 - derphi0 * alpha0)
    phi_a1 = apply(f,(xk+alpha1*pk,)+args)
    fc = fc + 1

    if (phi_a1 <= phi0 + c1*alpha1*derphi0):
        return xk + alpha1*pk
        #return alpha1, fc, 0

    # Otherwise loop with cubic interpolation until we find an alpha which 
    # satifies the first Wolfe condition (since we are backtracking, we will
    # assume that the value of alpha is not too small and satisfies the second
    # condition.

    while 1:       # we are assuming pk is a descent direction
        factor = alpha0**2 * alpha1**2 * (alpha1-alpha0)
        a = alpha0**2 * (phi_a1 - phi0 - derphi0*alpha1) - \
            alpha1**2 * (phi_a0 - phi0 - derphi0*alpha0)
        a = a / factor
        b = -alpha0**3 * (phi_a1 - phi0 - derphi0*alpha1) + \
            alpha1**3 * (phi_a0 - phi0 - derphi0*alpha0)
        b = b / factor

        alpha2 = (-b + sqrt(abs(b**2 - 3 * a * derphi0))) / (3.0*a)
        phi_a2 = apply(f,(xk+alpha2*pk,)+args)
        fc = fc + 1

        if (phi_a2 <= phi0 + c1*alpha2*derphi0):
            return xk + alpha2*pk
            #return alpha2, fc, 0

        if (alpha1 - alpha2) > alpha1 / 2.0 or (1 - alpha2/alpha1) < 0.96:
            alpha2 = alpha1 / 2.0

        alpha0 = alpha1
        alpha1 = alpha2
        phi_a0 = phi_a1
        phi_a1 = phi_a2
