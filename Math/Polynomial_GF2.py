# Polynomials over GF(2) can be encoded as positive integers where each bit is a coefficient.
# For example: x^3 + x^2 + 1 can be represented as 0b1101 = 13.
# Then, we can implement operations on them using bitwise operators.

def poly_deg_gf2(p: int) -> int:
    """Returns the degree of p(x)."""
    return p.bit_length() - 1

def poly_mul_gf2(p: int, q: int) -> int:    
    """Calculates p(x) * q(x)."""
    if p > q:
        p, q = q, p
    
    res = 0
    
    while p:
        if p & 1:
            res ^= q 
        p >>= 1
        q <<= 1
    
    return res

# This one is faster for high-degree polynomials
def poly_mul_gf2_bis(p: int, q: int) -> int:
    """Calculates p(x) * q(x) by skipping zeros."""
    if p.bit_count() > q.bit_count():
        p, q = q, p
    
    res = 0

    while p:
        d = p.bit_length() - 1
        res ^= q << d
        p ^= 1 << d # skip zeros (at the cost of calling the bit_length method on p)
        
    return res

def poly_pow_gf2(p: int, n: int) -> int:
    """Calculates p(x)^n, using binary exponentiation."""
    res = 1
    
    while n:
        if n & 1:
            res = poly_mul_gf2_bis(res, p)
        p = poly_mul_gf2_bis(p, p)
        n >>= 1
    
    return res

def poly_divmod_gf2(a: int, b: int) -> tuple[int, int]:
    """Calculates the quotient and the remainder in the Euclidean divison of a(x) by b(x)."""
    assert b != 0, "division by zero"
    
    al = a.bit_length()
    bl = b.bit_length()
    q = 0 
    
    while al >= bl:
        diff = al - bl
        q ^= 1 << diff
        a ^= b << diff
        al = a.bit_length()
    
    return (q, a)

def poly_div_gf2(a: int, b: int) -> int:
    """Calculates the quotient in the Euclidean divison of a(x) by b(x)."""
    return poly_divmod_gf2(a, b)[0]

def poly_mod_gf2(p: int, m: int) -> int:
    """Calculates the remainder in the Euclidean divison of p(x) by m(x)."""
    assert m != 0, "modulo by zero"
    
    pl = p.bit_length()
    ml = m.bit_length()
    
    while pl >= ml: 
        p ^= m << (pl - ml)
        pl = p.bit_length()
    
    return p

def poly_mul_mod_gf2(p: int, q: int, m: int) -> int:
    """Calculates p(x) * q(x) modulo m(x)."""        
    p = poly_mod_gf2(p, m)
    q = poly_mod_gf2(q, m)
    
    if p > q:
        p, q = q, p
    
    ql = q.bit_length()
    ml = m.bit_length()
    res = 0
    
    while p:
        if p & 1:
            res ^= q
        p >>= 1
        q <<= 1
        ql += 1
        if ql == ml:
            q ^= m
            ql = q.bit_length()
    
    return res

def poly_pow_mod_gf2(p: int, n: int, m: int) -> int:
    """Calculates p(x)^n modulo m(x), using binary exponentiation."""
    res = 1
    
    while n:
        if n & 1:
            res = poly_mul_mod_gf2(res, p, m)
        p = poly_mul_mod_gf2(p, p, m)
        n >>= 1
    
    return res

def poly_gcd_gf2(p: int, q: int) -> int:
    """Calculates the Greatest Common Divisor of p(x) and q(x)."""
    while q:
        p, q = q, poly_mod_gf2(p, q)
    return p

def poly_egcd_gf2(a: int, b: int) -> tuple[int, int, int]:
    """Calculates x, y and d such that ax + by = d = gcd(a, b), using the extended Euclidean algorithm."""
    if b == 0:
        return (1, 0, a)
    
    prev_r, r = a, b
    prev_x, x = 1, 0

    while r:
        q, r_ = poly_divmod_gf2(prev_r, r)
        prev_r, r = r, r_
        prev_x, x = x, prev_x ^ poly_mul_gf2(q, x)
    
    prev_y = poly_div_gf2(prev_r ^ poly_mul_gf2(prev_x, a), b)

    return (prev_x, prev_y, prev_r)

def poly_inverse_mod_gf2(p: int, m: int) -> int:
    """Calculates the modular multiplicative inverse of p(x) modulo m(x)."""
    x, _, gcd = poly_egcd_gf2(p, m)
    assert gcd == 1, "p(x) and m(x) must be relatively prime over GF(2)."
    return poly_mod_gf2(x, m)
