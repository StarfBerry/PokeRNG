# Polynomials over GF(2) can be encoded as positive integers where each bit is a coefficient.
# For example: x^3 + x^2 + 1 can be represented as 0b1101 = 13.
# Then we can implement arithmetic operations on them using bitwise operators.

from typing import Iterator
from math import isqrt

def poly_deg_gf2(f: int) -> int:
    """Returns the degree of f(x)."""
    return f.bit_length() - 1

def poly_mul_gf2(f: int, g: int) -> int:    
    """Calculates f(x) * g(x)."""
    if f > g:
        f, g = g, f
    
    res = 0
    
    while f:
        if f & 1:
            res ^= g 
        f >>= 1
        g <<= 1
    
    return res

def poly_mul_skip_gf2(f: int, g: int) -> int:
    """Calculates f(x) * g(x) by skipping zeros."""
    if f.bit_count() > g.bit_count():
        f, g = g, f
    
    res = 0

    while f:
        d = f.bit_length() - 1
        res ^= g << d
        f ^= 1 << d
        
    return res

def poly_prod_gf2(*args: int) -> int:
    """Calculates the product of the polynomials passed as arguments."""
    p = 1
    
    for f in args:
        p = poly_mul_skip_gf2(p, f)
    
    return p

def poly_square_gf2(f: int):
    """Calculates the square of f(x)."""
    res = 0
    g = f

    while f:
        d = f.bit_length() - 1
        #res ^= 1 << (d << 1) # f^2(x) = f(x^2) in GF(2)
        res ^= g << d
        f ^= 1 << d

    return res

def poly_pow_gf2(f: int, n: int) -> int:
    """Calculates f(x) raised to the power of n using binary exponentiation."""
    res = 1
    
    while n:
        if n & 1:
            res = poly_mul_skip_gf2(res, f)
        f = poly_square_gf2(f)
        n >>= 1
    
    return res

def poly_divmod_gf2(f: int, g: int) -> tuple[int, int]:
    """Calculates the quotient and the remainder in the Euclidean divison of f(x) by g(x)."""
    assert g != 0, "division by zero"
    
    fl = f.bit_length()
    gl = g.bit_length()
    q = 0 
    
    while fl >= gl:
        diff = fl - gl
        q ^= 1 << diff
        f ^= g << diff
        fl = f.bit_length()
    
    return (q, f)

def poly_div_gf2(f: int, g: int) -> int:
    """Calculates the quotient in the Euclidean divison of f(x) by g(x)."""
    return poly_divmod_gf2(f, g)[0]

def poly_mod_gf2(f: int, m: int) -> int:
    """Calculates the remainder in the Euclidean divison of f(x) by m(x)."""
    assert m != 0, "modulo by zero"
    
    fl = f.bit_length()
    ml = m.bit_length()
    
    while fl >= ml: 
        f ^= m << (fl - ml)
        fl = f.bit_length()
    
    return f

def poly_mul_mod_gf2(f: int, g: int, m: int) -> int:
    """Calculates f(x) * g(x) modulo m(x)."""        
    f = poly_mod_gf2(f, m)
    g = poly_mod_gf2(g, m)
    
    if f > g:
        f, g = g, f
    
    gl = g.bit_length()
    ml = m.bit_length()
    res = 0
    
    while f:
        if f & 1:
            res ^= g
        f >>= 1
        g <<= 1
        gl += 1
        if gl == ml:
            g ^= m
            gl = g.bit_length()
    
    return res

def poly_square_mod_gf2(f: int, m: int):
    """Calculates f^2(x) modulo m(x)."""
    f = poly_mod_gf2(f, m)
    f2 = poly_square_gf2(f)
    return poly_mod_gf2(f2, m)

def poly_pow_mod_gf2(f: int, n: int, m: int) -> int:
    """Calculates f^n(x) modulo m(x) using binary exponentiation."""
    res = 1
    
    while n:
        if n & 1:
            res = poly_mul_mod_gf2(res, f, m)
        f = poly_square_mod_gf2(f, m)
        n >>= 1
    
    return res

def poly_gcd_gf2(f: int, g: int) -> int:
    """Calculates the Greatest Common Divisor of f(x) and g(x) using Euclid's algorithm."""
    while g:
        f, g = g, poly_mod_gf2(f, g)
    return f

def poly_lcm_gf2(f: int, g: int) -> int:
    """Calculates the Least Common Multiple of f(x) and g(x)."""
    gcd = poly_gcd_gf2(f, g)
    div = poly_div_gf2(g, gcd)
    return poly_mul_gf2(f, div)

def poly_egcd_gf2(f: int, g: int) -> tuple[int, int, int]:
    """Calculates a(x), b(x) and d(x) such that af(x) + bg(x) = d(x) = gcd(f(x), g(x)) using the extended Euclidean algorithm."""
    if g == 0:
        return (int(f != 0), 0, f)
    
    prev_d, d = f, g
    prev_a, a = 1, 0

    while d:
        q, d_ = poly_divmod_gf2(prev_d, d)
        prev_d, d = d, d_
        prev_a, a = a, prev_a ^ poly_mul_gf2(q, a)
    
    prev_b = poly_div_gf2(prev_d ^ poly_mul_gf2(prev_a, f), g)

    return (prev_a, prev_b, prev_d)

def poly_mod_inv_gf2(f: int, m: int) -> int:
    """Calculates the modular multiplicative inverse of f(x) modulo m(x)."""
    inv, _, gcd = poly_egcd_gf2(f, m)
    assert gcd == 1, "f(x) and m(x) must be relatively prime over GF(2)."
    return poly_mod_gf2(inv, m)

def distinct_primes(n: int) -> Iterator[int]:   
    """Yields the distinct prime factors of the given integer using iterative division."""
    if n <= 1:
        return
    
    for p in (2, 3, 5):
        if n % p == 0:
            yield p
            while n % p == 0:
                n //= p
    
    p = 7
    s = isqrt(n)
    i = 1
    gap = (6, 4, 2, 4, 2, 4, 6, 2) # gaps between prime numbers greater than 5 modulo 30 

    while p <= s:
        if n % p == 0:
            yield p
            while n % p == 0: 
                n //= p
            s = isqrt(n)
        
        p += gap[i & 7] 
        i += 1

    if n != 1:
        yield n

def poly_irreducibility_gf2(f: int) -> bool:
    """Checks if the polynomial f(x) is irreducible using Rabin's algorithm."""
    if f <= 3:
        return f == 2 or f == 3
    
    # all irreductible polynomials of degree >= 2 are congruent to 1 modulo x^2 + x
    if poly_mod_gf2(f, 6) != 1:
        return False
     
    d = poly_deg_gf2(f)
 
    for p in distinct_primes(d):
        g = poly_pow_mod_gf2(2, 1 << (d // p), f)
        if poly_gcd_gf2(f, g ^ 2) != 1:
            return False
     
    return poly_pow_mod_gf2(2, 1 << d, f) == 2