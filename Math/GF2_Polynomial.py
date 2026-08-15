# Polynomials over GF(2), formally written as GF(2)[X], can be encoded as positive integers where each bit is a coefficient.
# For example: x^3 + x^2 + 1 can be represented as 0b1101 = 13.
# Then we can implement arithmetic operations on them using bitwise operators.

from typing import Iterator, Sequence
from math import isqrt

def gf2x_deg(f: int) -> int:
    """Returns the degree of f(x)."""
    return f.bit_length() - 1

def gf2x_mul(f: int, g: int) -> int:    
    """Calculates f(x) * g(x)."""
    # f > g implies f.bit_length() >= g.bit_length()
    if f > g:
        f, g = g, f

    res = 0

    while f:
        if f & 1:
            res ^= g 
        f >>= 1
        g <<= 1

    return res

def gf2x_mul_skip(f: int, g: int) -> int:
    """Calculates f(x) * g(x) by skipping zeros."""
    if f.bit_count() > g.bit_count():
        f, g = g, f

    res = 0

    while f:
        d = f.bit_length() - 1
        res ^= g << d
        f ^= 1 << d

    return res

def gf2x_prod(*args: int) -> int:
    """Calculates the product of the polynomials passed as arguments."""
    p = 1

    for f in args:
        p = gf2x_mul_skip(p, f)

    return p

def gf2x_square(f: int):
    """Calculates the square of f(x)."""
    res = 0

    while f:
        d = f.bit_length() - 1
        res ^= 1 << (d << 1) # f^2(x) = f(x^2) in GF(2)[X]
        f ^= 1 << d

    return res

def gf2x_pow(f: int, n: int) -> int:
    """Calculates f(x) raised to the power of n using binary exponentiation."""
    res = 1

    while n:
        if n & 1:
            res = gf2x_mul_skip(res, f)
        f = gf2x_square(f)
        n >>= 1

    return res

def gf2x_divmod(f: int, g: int) -> tuple[int, int]:
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

def gf2x_div(f: int, g: int) -> int:
    """Calculates the quotient in the Euclidean divison of f(x) by g(x)."""
    return gf2x_divmod(f, g)[0]

def gf2x_mod(f: int, m: int) -> int:
    """Calculates the remainder in the Euclidean divison of f(x) by m(x)."""
    assert m != 0, "modulo by zero"

    fl = f.bit_length()
    ml = m.bit_length()

    while fl >= ml: 
        f ^= m << (fl - ml)
        fl = f.bit_length()

    return f

def gf2x_barrett_consts(m: int) -> tuple[int, int]:
    """Calculates the constants involved in the Barrett reduction."""
    k = gf2x_deg(m) << 1
    mu = gf2x_div(1 << k, m)
    return (k, mu)

def gf2x_barrett_reduction(f: int, mu: int, k: int, m: int):
    """Calculates f(x) mod m(x) using Barrett reduction, assuming deg(f) <= 2 * deg(m)."""
    q = gf2x_mul_skip(f, mu) >> k # <==> gf2x_div(f, m), no correction is necessary in GF(2)[X]
    return f ^ gf2x_mul_skip(q, m)

def gf2x_mul_mod(f: int, g: int, m: int) -> int:
    """Calculates f(x) * g(x) modulo m(x)."""
    f = gf2x_mod(f, m)
    g = gf2x_mod(g, m)
    fg = gf2x_mul_skip(f, g)
    return gf2x_mod(fg, m)

def gf2x_bounded_mul_mod(f: int, g: int, m: int) -> int:
    """Calculates f(x) * g(x) modulo m(x) by immediately reducing the partial product to prevent bit lengths from exceeding the length of m(x)."""        
    f = gf2x_mod(f, m)
    g = gf2x_mod(g, m)

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

def gf2x_pow_mod(f: int, n: int, m: int) -> int:
    """Calculates f^n(x) modulo m(x) using binary exponentiation."""
    f = gf2x_mod(f, m)
    res = 1

    while n:
        if n & 1:
            res = gf2x_mod(gf2x_mul_skip(res, f), m)
        f = gf2x_mod(gf2x_square(f), m)
        n >>= 1

    return res

def gf2x_gcd(f: int, g: int) -> int:
    """Calculates the Greatest Common Divisor of f(x) and g(x) using Euclid's algorithm."""
    while g:
        f, g = g, gf2x_mod(f, g)
    return f

def gf2x_lcm(f: int, g: int) -> int:
    """Calculates the Least Common Multiple of f(x) and g(x)."""
    gcd = gf2x_gcd(f, g)
    div = gf2x_div(g, gcd)
    return gf2x_mul_skip(f, div)

def gf2x_egcd(f: int, g: int) -> tuple[int, int, int]:
    """Calculates a(x), b(x) and d(x) such that af(x) + bg(x) = d(x) = gcd(f(x), g(x)) using the extended Euclidean algorithm."""
    if g == 0:
        return (int(f != 0), 0, f)

    prev_d, d = f, g
    prev_a, a = 1, 0

    while d:
        q, d_ = gf2x_divmod(prev_d, d)
        prev_d, d = d, d_
        prev_a, a = a, prev_a ^ gf2x_mul_skip(q, a)

    prev_b = gf2x_div(prev_d ^ gf2x_mul_skip(prev_a, f), g)

    return (prev_a, prev_b, prev_d)

def gf2x_mod_inv(f: int, m: int) -> int:
    """Calculates the modular multiplicative inverse of f(x) modulo m(x)."""
    inv, _, gcd = gf2x_egcd(f, m)
    assert gcd == 1, "f(x) and m(x) must be relatively prime over GF(2)[X]."
    return gf2x_mod(inv, m)

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

def gf2x_is_irreducible(f: int) -> bool:
    """Checks if the polynomial f(x) is irreducible using Rabin's algorithm."""
    if f <= 3:
        return f == 2 or f == 3

    # all irreductible polynomials of degree >= 2 are congruent to 1 modulo x^2 + x
    if gf2x_mod(f, 6) != 1:
        return False

    d = gf2x_deg(f)

    for p in distinct_primes(d):
        g = gf2x_pow_mod(2, 1 << (d // p), f)
        if gf2x_gcd(f, g ^ 2) != 1:
            return False

    return gf2x_pow_mod(2, 1 << d, f) == 2

def gf2_berlekamp_massey(bits: Sequence[int]) -> int:
    """Calculates the shortest linear-feedback shift register (LFSR) of the given binary output sequence."""
    assert len(bits) & 1 == 0, "The length of the bits sequence must be even."

    C = B = m = 1
    L = mask = 0

    for n, i in enumerate(reversed(range(len(bits)))):
        d = bits[i] ^ ((C >> 1) & mask).bit_count() & 1
        mask = (mask << 1) | bits[i]

        if d == 0:
            m += 1
            continue

        T = C
        C ^= B << m

        if 2 * L <= n:
            L = n + 1 - L
            B = T
            m = 1
        else:
            m += 1

    return C