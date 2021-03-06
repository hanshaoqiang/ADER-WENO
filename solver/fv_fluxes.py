from numba import jit
from numpy import complex128, dot, zeros
from scipy.linalg import eig, solve

from options import n, N
from system import flux, jacobian, block, max_abs_eigs
from auxiliary.basis import quad


nodes, _, weights = quad()

@jit
def Bint(qL, qR, d):
    """ Returns the jump matrix for B, in the dth direction
    """
    temp = zeros([n, n])
    for i in range(N+1):
        q = qL + nodes[i] * (qR - qL)
        temp += weights[i] * block(q, d)
    return dot(temp, qR-qL)

def Aint(qL, qR, d):
    """ Returns the Osher-Solomon jump matrix for A, in the dth direction
        NB: eig function should be replaced with analytical function, if known
    """
    ret = zeros(n, dtype=complex128)
    for i in range(N+1):
        q = qL + nodes[i] * (qR - qL)
        J = jacobian(q, d)
        eigs, R = eig(J, overwrite_a=1, check_finite=0)
        b = solve(R, qR-qL, overwrite_b=1, check_finite=0)
        ret += weights[i] * dot(R, abs(eigs)*b)
    return ret.real

def s_max(qL, qR, d):
    maxL = max_abs_eigs(qL, d)
    maxR = max_abs_eigs(qR, d)
    return max(maxL, maxR) * (qR - qL)

def Drus(qL, qR, d, pos):
    """ Returns the Rusanov jump term at the dth boundary
    """
    if pos:
        ret = flux(qR, d)
        ret += flux(qL, d)
        ret += Bint(qL, qR, d)
    else:
        ret = -flux(qR, d)
        ret -= flux(qL, d)
        ret -= Bint(qL, qR, d)
    ret -= s_max(qL, qR, d)
    return ret

def Dos(qL, qR, d, pos):
    """ Returns the Osher-Solomon jump term at the dth boundary
    """
    if pos:
        ret = flux(qR, d)
        ret += flux(qL, d)
        ret += Bint(qL, qR, d)
    else:
        ret = -flux(qR, d)
        ret -= flux(qL, d)
        ret -= Bint(qL, qR, d)
    ret -= Aint(qL, qR, d)
    return ret
