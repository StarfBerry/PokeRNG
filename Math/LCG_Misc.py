import numpy as np
from typing import Sequence

def inv_mod_pow_2(n: int, p: int) -> int:
    """Returns the multiplicative inverse of n modulo 2^p, using the Extended Euclidean algorithm."""  
    assert (n & 1) == 1, "n must be odd to be relatively prime with a power of 2."
    
    p2 = 1 << p
    prev_r, r = n, p2
    prev_x, x = 1, 0
    
    while r != 1:
        q = prev_r // r
        prev_r, r = r, prev_r - q * r
        prev_x, x = x, prev_x - q * x

    return x % p2

def reverse_lcg_32(mult: int, inc: int) -> tuple[int, int]:
    """Returns the multiplier and increment for a 32-bit LCG to move backward in the state sequence."""
    rmult = inv_mod_pow_2(mult, 32)
    rinc = (-inc * rmult) & 0xffffffff
    return (rmult, rinc)

def reverse_lcg_64(mult: int, inc: int) -> tuple[int, int]:
    """Returns the multiplier and increment for a 64-bit LCG to move backward in the state sequence."""
    rmult = inv_mod_pow_2(mult, 64)
    rinc = (-inc * rmult) & 0xffffffffffffffff
    return (rmult, rinc)

def lagrange_algorithm(u: Sequence[int], v: Sequence[int]) -> tuple[tuple[int, int], tuple[int, int]]:
    """Returns the shortest basis nearly orthogonal of a 2-dimensional integer lattice from a given basis."""
    assert len(u) == 2 and len(v) == 2, "Vectors are not 2-dimensional."
    assert u[0] * v[1] != u[1] * v[0], "Vectors are not linearly independent."

    u = np.array(u, object) 
    v = np.array(v, object)

    m = 1
    while m:
        m = round(np.dot(u, v) / np.dot(u, u)) # Gram-Schmidt coefficient rounded to nearest integer
        v -= m * u
        if np.dot(u, u) > np.dot(v, v):
            u, v = v, u

    return (tuple(u), tuple(v))

if __name__ == "__main__":
    #rmult, rinc = reverse_lcg_32(0x41c64e6d, 0x6073)
    #print(hex(rmult), hex(rinc)) # 0xeeb9eb65 0xa3561a1

    #rmult, rinc = reverse_lcg_32(0x41c64e6d, 0x3039)
    #print(hex(rmult), hex(rinc)) # 0xeeb9eb65 0xfc77a683

    #rmult, rinc = reverse_lcg_32(0x343fd, 0x269ec3)
    #print(hex(rmult), hex(rinc)) # 0xb9b33155 0xa170f641

    #rmult, rinc = reverse_lcg_32(0x6c078965, 0x1)
    #print(hex(rmult), hex(rinc)) # 0x9638806d 0x69c77f93

    #rmult, rinc = reverse_lcg_64(0x5d588b656c078965, 0x269ec3)
    #print(hex(rmult), hex(rinc)) # 0xdedcedae9638806d 0x9b1ae6e9a384e6f9

    #print(lagrange_algorithm([1, 0xeeb9eb65], [0, 1 << 32])) # ((32471, 26579), (-68321, 76347))

    #print(lagrange_algorithm([1, 0x41c64e6d], [0, 1 << 31])) # ((26579, 32471), (-51463, 17925))

    #print(lagrange_algorithm([1, 0xdc6c95d9], [0, 1 << 32])) # ((27697, 14985), (59251, -123013))

    #print(lagrange_algorithm([1, 0xdc6c95d9 % 2**31], [0, 1 << 31])) # ((-27697, -14985), (43474, -54014))

    #print(lagrange_algorithm([1, 0xb9b33155], [0, 1 << 32])) # ((-59601, -20069), (-35210, 60206))

    #print(lagrange_algorithm([1, 0x343fd], [0, 1 << 31])) # ((30103, -17605), (20069, 59601))

    print(lagrange_algorithm([1, 0xb9b33155 % 2**31], [0, 1 << 31])) # ((-17605, 30103), (-59601, -20069))