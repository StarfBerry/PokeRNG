from typing import Iterator

# Seeds recovering for LCGs based on integer lattice basis reduction (https://en.wikipedia.org/wiki/Lattice_reduction).
# Here is an example of lattice reduction applied to an LCG: https://gist.github.com/EDDxample/38a9acddcd29f15af034fd91da93b8fa
# And a video if you'd like to learn more: https://www.youtube.com/watch?v=gsaV9gcLntM

# The constants in the code were computed using this Sage script: https://gist.github.com/StarfBerry/6473c4e33ae73fc5b370530f694d47ab
# Basically, the idea behind the script is to track where the vertices of a hypercube (representing the ranges of desired outputs) are sent into a reduced lattice.
# Next, we look at the minimum and maximum coordinates in all dimensions to find the endpoints of the resulting parallelepiped.
# Moreover, the user's desired outputs can be interpreted as a vertex of the hypercube, and we calculate the differences between the vector coordinates of the endpoints of the
# parallelepiped and those of the user's vertex that was sent into the reduced lattice.
# As long as the lengths of the output ranges provided by the user remain the same, the differences will remain unchanged and can be expressed as integer constants.
# These integer constants can be added when calculating the coordinates of the user's vertex in the reduced lattice to obtain the extreme coordinates in each dimension.
# In other words, we can bound the variables in the linear combinations to find all the solutions without resorting to matrix calculations or floating-point numbers at runtime.

# In two dimensions, we use modular arithmetic and the fact that we know the strict upper bound of the unknowns (2^16 in our case), to avoid bounding one of the two variables in 
# the linear combinations and, on average, perform fewer iterations than if we had calculated these linear combinations.
# To compute the shortest basis roughly orthogonal in 2D, we can use Lagrange's algorithm: https://cryptohack.gitbook.io/cryptobook/lattices/lll-reduction/gaussian-reduction
# In the Sage script, a different lattice reduction algorithm is used, the BKZ algorithm, which can be applied to any dimension and will produce the same results in 2D. 
# However, Lagrange's algorithm was the first to be used during the implementation of the code, and it's also the oldest lattice reduction algorithm ever documented.
# This is why Lagrange's name has been retained in the name of certain constants, as well as to name and illustrate the reduced matrices in the comments.
# To begin computing the constants, we construct the matrix representing the lattice on which we will work, and then we apply Lagrange's algorithm to it.
# Next, we choose the variable to bound by looking for the one that minimizes the average number of iterations based on its range (which can be determined with the Sage script)
# and the coefficient with the highest absolute value in the adjacent column, which will serve as the modulus.
# The average number of iterations can be estimated with the following formula: range * 2^16 / abs(modulus).
# To ensure that the calculations in the code are performed correctly, the modulus must be positive and located on the first row of the Lagrange-reduced matrix.
# If the modulus is on the second row, we can swap the rows by constructing the lattice matrix from the reversed version of the LCG, while applying Lagrange's algorithm to it.
# In the case where the modulus is negative, we multiply the Lagrange-reduced matrix by -1 to obtain a positive modulus.
# At the end, LAG0 and LAG1 are respectively the top left and top right coefficients of the resulting matrix.
# If we bound the first variable, LAG1 is the modulus and LAG0 is reduced modulo LAG1, and vice-versa for the second variable.
# Furthermore, our calculations involve integer divisions by the determinant of the Lagrange-reduced matrices.
# In our case, these determinants are always powers of 2, which can be positive or negative.
# If the determinant is positive, the integer division can be performed using a right bit shift.
# To take advantage of this even when the determinant is negative, we transfer the sign of the determinant to the constant involved in the multiplication just before the modulo.
# Thus, if the determinant of a Lagrange-reduced matrix is negative, the opposite of LAG0 or LAG1 (not the modulus) is used to compensate.

# LOWER and UPPER constants are used to bound the variables in linear combinations in order to calculate potential solutions.
# In the 2-dimension case, the constants returned by the Sage script have been divided by 2^16, and extra values were added to most of them.
# The division by 2^16 is due to the fact that the divisions by the determinant of the Lagrange-reduced matrices have been split into 2 subdivisions, and we assume that the 
# constants have already been divided during the first subdivision. 
# The extra values were added to prevent unsigned integer overflow (for programming languages such as C++, Rust, C#, etc.) while maintaining consistency with the moduli, or to 
# allow division rounded up to the nearest integer.
# If the determinant of the Lagrange-reduced matrix is negative, the constants displayed by the script must be swaped and multiplied by -1.

#################################################################################################################################################################

'''
|          1     0 |   Lagrange   |  32471  -68321 |     Det
|                  | ===========> |                | ===========> 2^32
| 0xEEB9EB65  2^32 |              |  26579   76347 |
'''

# LCRNG PID Constants
R_MULT  = 0xEEB9EB65 # reverse multiplier constant
R_INC   = 0xA3561A1  # reverse increment constant
R_LAG0  = 0x7ED7     # 32471
R_LAG1  = 0x71A4     # -68321 mod 32471
R_LOWER = 0x79C8BF4A # ((-0x50F40B53C37 + 0xffff_ffff) >> 16) + (32471 << 16)
R_UPPER = 0x79C8A5F4 # (-0x50E5A0B3C37 >> 16) + (32471 << 16)

'''
|          1     0 |   Lagrange   |  26579  -51463 |    *(-1)     | -26579   51463 |     Det
|                  | ===========> |                | ===========> |                | ===========> 2^31
| 0x41C64E6D  2^31 |              |  32471   17925 |              | -32471  -17925 |
'''

# LCRNG IVs Constants
MULT  = 0x41C64E6D # multiplier constant
INC   = 0x6073     # increment constant
LAG0  = 0x6134     # -26579 mod 51463
LAG1  = 0xC907     # 51463
# The following two must be declared to 64 bits in order to prevent integer overflow in the operations where they are used.
LOWER = 0x64833CB0 # ((-0xC34F11DB + 0x7fff_ffff) >> 16) + (51463 << 15)
UPPER = 0x6483CBBC # (0x4BBCEE25 >> 16) + (51463 << 15)

# The range of the second variable is smaller than one.
# So, in some cases, we can predict that there will be no solutions without having to enter the loop.
def LCRNG_recover_pid_seeds(pid: int) -> Iterator[int]:
    first = (pid & 0xffff) << 16
    second = pid & 0xffff0000
    
    tmp = (((first - second * R_MULT) >> 16) & 0xffff) * R_LAG0
    lo = (tmp + R_LOWER) >> 16
    up = (tmp + R_UPPER) >> 16

    # true in around 10% of cases
    if lo != up: 
        return
    
    # at most 3 iterations (around 2.02 in average)
    for lbits in range((lo * R_LAG1) % R_LAG0, 0x10000, R_LAG0):
        seed = ((second | lbits) * R_MULT + R_INC) & 0xffffffff
        if (seed & 0xffff0000) == first:
            yield seed

# around 2.70 iterations in average
def LCRNG_recover_ivs_seeds(hp: int, atk: int, dfs: int, spa: int, spd: int, spe: int) -> Iterator[int]:
    first  = ((dfs << 10) | (atk << 5) | hp ) << 16
    second = ((spd << 10) | (spa << 5) | spe) << 16

    tmp = (((MULT * first - second) >> 16) & 0xffff) * LAG1
    lo = ((tmp + LOWER) >> 15) * LAG0
    mi = lo + LAG0
    up = ((tmp + UPPER) >> 15) * LAG0

    # each loop performs at most 2 iterations
    for lbits in range(lo % LAG1, 0x10000, LAG1):
        seed = first | lbits
        if ((seed * MULT + INC) & 0x7fff0000) == second:
            yield seed
            yield seed ^ 0x80000000
    
    for lbits in range(mi % LAG1, 0x10000, LAG1):
        seed = first | lbits
        if ((seed * MULT + INC) & 0x7fff0000) == second:
            yield seed
            yield seed ^ 0x80000000
    
    # true in around 12% of cases
    if mi != up:
        for lbits in range(up % LAG1, 0x10000, LAG1):
            seed = first | lbits
            if ((seed * MULT + INC) & 0x7fff0000) == second:
                yield seed
                yield seed ^ 0x80000000

#################################################################################################################################################################

'''
|          1     0 |   Lagrange   |  27697   59251 |     Det
|                  | ===========> |                | ===========> -2^32
| 0xDC6C95D9  2^32 |              |  14985 -123013 |


|          1     0 |   Lagrange   | -27697   43474 |    *(-1)     |  27697  -43474 |     Det
|                  | ===========> |                | ===========> |                | ===========> 2^31
| 0x5C6C95D9  2^31 |              | -14985  -54014 |              |  14985   54014 |
'''

# LCRNG^2 PID/IVs Constants
R_MULT_2  = 0xDC6C95D9 # reverse multiplier constant
R_INC_2   = 0x4D3CB126 # reverse increment constant
R_LAG0_2  = 0x6C31     # 27697
R_LAG1_PID_2 = 0x5D20  # -59251 mod 27697
R_LAG1_IVS_2 = 0x2E90  # -43474 mod 27697
R_LOWER_PID_2 = 0x4B8D621D # ((-0x20A49DE2F046 + 0xffff_ffff) >> 16) + (27697 << 16)
R_LOWER_IVS_2 = 0x4B8CE21D # ((-0x20A49DE2F046 + 0x7fff_ffff) >> 16) + (27697 << 16)
R_UPPER_2     = 0x4B8D08D7 # (-0x20A3F728F046 >> 16) + (27697 << 16)

# The range of the second variable is smaller than one.
# So, in some cases, we can predict that there will be no solutions without having to enter the loop.
def LCRNG_recover_pid_seeds_with_skip(pid: int) -> Iterator[int]:
    first = (pid & 0xffff) << 16
    third = pid & 0xffff0000
    
    tmp = (((first - third * R_MULT_2) >> 16) & 0xffff) * R_LAG0_2
    lo = (tmp + R_LOWER_PID_2) >> 16
    up = (tmp + R_UPPER_2) >> 16

    # true in around 35% of cases
    if lo != up:
        return

    # at most 3 iterations (around 2.37 in average)
    for lbits in range((lo * R_LAG1_PID_2) % R_LAG0_2, 0x10000, R_LAG0_2):
        seed = ((third | lbits) * R_MULT_2 + R_INC_2) & 0xffffffff
        if (seed & 0xffff0000) == first:
            yield seed

# around 3.08 iterations in average
def LCRNG_recover_ivs_seeds_with_skip(hp: int, atk: int, dfs: int, spa: int, spd: int, spe: int) -> Iterator[int]:
    first = ((dfs << 10) | (atk << 5) | hp ) << 16
    third = ((spd << 10) | (spa << 5) | spe) << 16
    
    tmp = (((first - third * R_MULT_2) >> 16) & 0xffff) * R_LAG0_2
    lo = (tmp + R_LOWER_IVS_2) >> 15
    up = (tmp + R_UPPER_2) >> 15

    # each loop performs at most 3 iterations
    for lbits in range((lo * R_LAG1_IVS_2) % R_LAG0_2, 0x10000, R_LAG0_2):
        seed = ((third | lbits) * R_MULT_2 + R_INC_2) & 0xffffffff
        if (seed & 0x7fff0000) == first:
            yield seed
            yield seed ^ 0x80000000
    
    # true in around 30% of cases
    if lo != up:
        for lbits in range((up * R_LAG1_IVS_2) % R_LAG0_2, 0x10000, R_LAG0_2):
            seed = ((third | lbits) * R_MULT_2 + R_INC_2) & 0xffffffff
            if (seed & 0x7fff0000) == first:
                yield seed
                yield seed ^ 0x80000000

#################################################################################################################################################################

'''
|          1     0 |   Lagrange   | -59601 -35210 |    *(-1)     | 59601   35210 |     Det
|                  | ===========> |               | ===========> |               | ===========> -2^32
| 0xB9B33155  2^32 |              | -20069  60206 |              | 20069  -60206 |
'''

# GCRNG PID Constants
GC_R_MULT  = 0xB9B33155 # reverse multiplier constant
GC_R_INC   = 0xA170F641 # reverse increment constant
GC_R_LAG0  = 0xE8D1     # 59601
GC_R_LAG1  = 0x5F47     # -35210 mod 59601
# The following two must be declared to 64 bits in order to prevent integer overflow in the operations where they are used.
GC_R_LOWER = 0x55FF8537 # ((-0x92D27AC8F311 + 0xffff_ffff) >> 16) + (59601 << 16)
GC_R_UPPER = 0x55FFBC6D # (-0x92D14392F311 >> 16) + (59601 << 16)

'''
|          1     0 |   Lagrange   | -17605  59601 |     Det
|                  | ===========> |               | ===========> -2^31
| 0x39B33155  2^31 |              |  30103  20069 |


|          1     0 |   Lagrange   |  30103  20069 |     Det
|                  | ===========> |               | ===========> 2^31
|    0x343FD  2^31 |              | -17605  59601 |
'''

# GCRNG IVs Constants (bounding the first variable)
GC_R_LAG0_IVS  = 0x44C5     # 17605
GC_R_LAG1_IVS  = 0xE8D1     # 59601
# The following two must be declared to 64 bits in order to prevent integer overflow in the operations where they are used.
GC_R_LOWER_IVS = 0x1E694392 # (0x1E68C392F311 + 0x7fff_ffff) >> 16
GC_R_UPPER_IVS = 0x1E69FAC8 # (0x1E69FAC8F311 >> 16)

# GCRNG IVs Constants (bounding the second variable)
GC_MULT  = 0x343FD    # multiplier constant
GC_INC   = 0x269EC3   # increment constant
GC_LAG0  = 0x7597     # 30103
GC_LAG1  = 0x4E65     # 20069
GC_LOWER = 0x3ABA42A9 # ((-0x11BD56C405 + 0x7fff_ffff) >> 16) + (30103 << 15)
GC_UPPER = 0x3ABA7D05 # (-0x1102FAC405 >> 16) + (30103 << 15)

# around 1.34 iterations in average
def GCRNG_recover_pid_seeds(pid: int) -> Iterator[int]:
    first = pid & 0xffff0000
    second = (pid & 0xffff) << 16
    
    tmp = (((first - second * GC_R_MULT) >> 16) & 0xffff) * GC_R_LAG0
    lo = (tmp + GC_R_LOWER) >> 16
    up = (tmp + GC_R_UPPER) >> 16

    # each loop performs at most 2 iterations
    for lbits in range((lo * GC_R_LAG1) % GC_R_LAG0, 0x10000, GC_R_LAG0):
        seed = ((second | lbits) * GC_R_MULT + GC_R_INC) & 0xffffffff
        if (seed & 0xffff0000) == first:
            yield seed
    
    # true in around 22% of cases
    if lo != up:
        for lbits in range((up * GC_R_LAG1) % GC_R_LAG0, 0x10000, GC_R_LAG0):
            seed = ((second | lbits) * GC_R_MULT + GC_R_INC) & 0xffffffff
            if (seed & 0xffff0000) == first:
                yield seed

def channel_recover_pid_seeds(pid: int) -> Iterator[int]:
    x = 40122 ^ (pid >> 16) ^ ((pid & 0xffff) < 8) # failed implementation of the shiny lock due to operator precedence
    for seed in GCRNG_recover_pid_seeds(pid): 
        sid = ((seed * GC_R_MULT + GC_R_INC) >> 16) & 0xffff
        if x == sid:
            yield seed
    
    x ^= 0x8000
    for seed in GCRNG_recover_pid_seeds(pid ^ 0x80000000): 
        sid = ((seed * GC_R_MULT + GC_R_INC) >> 16) & 0xffff
        if x != sid:
            yield seed

# around 2.63 iterations in average
def GCRNG_recover_ivs_seeds(hp: int, atk: int, dfs: int, spa: int, spd: int, spe: int) -> Iterator[int]:
    first  = ((dfs << 10) | (atk << 5) | hp ) << 16
    second = ((spd << 10) | (spa << 5) | spe) << 16

    tmp = (((GC_R_MULT * second - first) >> 16) & 0xffff) * GC_R_LAG1_IVS
    lo = ((tmp + GC_R_LOWER_IVS) >> 15) * GC_R_LAG0_IVS
    mi = lo + GC_R_LAG0_IVS
    up = ((tmp + GC_R_UPPER_IVS) >> 15) * GC_R_LAG0_IVS

    # each loop performs at most 2 iterations
    for lbits in range(lo % GC_R_LAG1_IVS, 0x10000, GC_R_LAG1_IVS):
        seed = ((second | lbits) * GC_R_MULT + GC_R_INC) & 0xffffffff
        if (seed & 0x7fff0000) == first:
            yield seed
            yield seed ^ 0x80000000
    
    for lbits in range(mi % GC_R_LAG1_IVS, 0x10000, GC_R_LAG1_IVS):
        seed = ((second | lbits) * GC_R_MULT + GC_R_INC) & 0xffffffff
        if (seed & 0x7fff0000) == first:
            yield seed
            yield seed ^ 0x80000000
    
    # true in around 43% of cases
    if mi != up:
        for lbits in range(up % GC_R_LAG1_IVS, 0x10000, GC_R_LAG1_IVS):
            seed = ((second | lbits) * GC_R_MULT + GC_R_INC) & 0xffffffff
            if (seed & 0x7fff0000) == first:
                yield seed
                yield seed ^ 0x80000000

# around 3.17 iterations in average
def GCRNG_recover_ivs_seeds_bis(hp: int, atk: int, dfs: int, spa: int, spd: int, spe: int) -> Iterator[int]:
    first  = ((dfs << 10) | (atk << 5) | hp ) << 16
    second = ((spd << 10) | (spa << 5) | spe) << 16

    tmp = (((second - first * GC_MULT) >> 16) & 0xffff) * GC_LAG0 
    lo = (tmp + GC_LOWER) >> 15
    up = (tmp + GC_UPPER) >> 15

    # each loop performs at most 3 iterations
    for lbits in range((lo * GC_LAG1) % GC_LAG0, 0x10000, GC_LAG0):
        seed = first | lbits
        if ((seed * GC_MULT + GC_INC) & 0x7fff0000) == second:
            yield seed
            yield seed ^ 0x80000000
    
    # true in around 46% of cases
    if lo != up:
        for lbits in range((up * GC_LAG1) % GC_LAG0, 0x10000, GC_LAG0):
            seed = first | lbits
            if ((seed * GC_MULT + GC_INC) & 0x7fff0000) == second:
                yield seed
                yield seed ^ 0x80000000

#################################################################################################################################################################

'''
In DPPt and HGSS, lottery numbers are generated using 2 different LCGs, as following:

Let n0 and n1 be two consecutive lottery numbers, and x the group seed we are searching for.

n0 = MRNG(x) >> 16

Let X = MRNG(x), and assume that all calculations are performed modulo 2^32.

n1 = MRNG(ARNG(x)) >> 16 
   = MRNG(ARNG(MRNGR(X))) >> 16
   = (0x41C64E6D * (0x6C078965 * (0xEEB9EB65 * X + 0xFC77A683) + 0x1) + 0x3039) >> 16
   = (0x6C078965 * X + 0xCA55F729) >> 16

In this way, the LCGs were combined into a single one, which can be used to build the lattice matrix.
However, it's more advantageous to work with the reversed version of this new LCG, since it yields the smallest average number of iterations.


|          1     0 |   Lagrange   | -46423 -63468 |    *(-1)     | 46423   63468 |     Det
|                  | ===========> |               | ===========> |               | ===========> -2^32
| 0x9638806D  2^32 |              | -46603  28804 |              | 46603  -28804 |
'''

LOTTO_R_MULT  = 0x9638806D # reverse multiplier constant
LOTTO_R_INC   = 0xC6D9438B # reverse increment constant
LOTTO_R_LAG0  = 0x4295     # -46423 mod 63468
LOTTO_R_LAG1  = 0xF7EC     # 63468
# The following two must be declared to 64 bits in order to prevent integer overflow in the operations where they are used.
LOTTO_R_LOWER = 0xC0928805 # (0xC09188056124 + 0xffff_ffff) >> 16
LOTTO_R_UPPER = 0xC092F075 # (0xC092F0756124 >> 16)

# around 1.46 iterations in averages
def recover_group_seeds_from_2_lotto_numbers(n0: int, n1: int) -> Iterator[int]:    
    tmp = ((LOTTO_R_MULT * n1 - n0) & 0xffff) * LOTTO_R_LAG1
    lo = (tmp + LOTTO_R_LOWER) >> 16 
    up = (tmp + LOTTO_R_UPPER) >> 16

    n1 <<= 16

    # each loop performs at most 2 iterations
    for lbits in range((lo * LOTTO_R_LAG0) % LOTTO_R_LAG1, 0x10000, LOTTO_R_LAG1):
        seed = ((n1 | lbits) * LOTTO_R_MULT + LOTTO_R_INC) & 0xffffffff
        if (seed >> 16) == n0:
            yield (seed * R_MULT + 0xFC77A683) & 0xffffffff

    # true in around 41% of cases
    if lo != up:
        for lbits in range((up * LOTTO_R_LAG0) % LOTTO_R_LAG1, 0x10000, LOTTO_R_LAG1):
            seed = ((n1 | lbits) * LOTTO_R_MULT + LOTTO_R_INC) & 0xffffffff
            if (seed >> 16) == n0:
                yield (seed * R_MULT + 0xFC77A683) & 0xffffffff

#################################################################################################################################################################

'''
|                  1     0 |   Lagrange   | -3070150413  3572620529 |    *(-1)     | 3070150413 -3572620529 |     Det
|                          | ===========> |                         | ===========> |                        | ===========> 2^64
| 0xDEDCEDAE9638806D  2^64 |              | -1993949321 -3688131939 |              | 1993949321  3688131939 |
'''

# Proof of concept for 64-bit LCGs
BW_R_MULT  = 0xDEDCEDAE9638806D # reverse multiplier constant
BW_R_INC   = 0x9B1AE6E9A384E6F9 # reverse increment constant
BW_R_LAG0  = 0xB6FEC70D         # 3070150413
BW_R_LAG1  = 0x990BB129         # -3572620529 mod 3070150413
BW_R_LOWER = 0x481F49988938ADF4 # ((-0x6EDF7D7576C7520BCE5949A5 + 0xffff_ffff_ffff_ffff) >> 32) + (3070150413 << 32)
BW_R_UPPER = 0x481F4998B710B5F4 # (-0x6EDF7D7448EF4A0BCE5949A5 >> 32) + (3070150413 << 32)

# around 1.65 iterations in average
def BWRNG_recover_states_from_2x32_bits(out0: int, out1: int) -> Iterator[int]:
    tmp = ((out0 - out1 * BW_R_MULT) & 0xffff_ffff) * BW_R_LAG0
    lo = (tmp + BW_R_LOWER) >> 32
    up = (tmp + BW_R_UPPER) >> 32

    out1 <<= 32

    # each loop performs at most 2 iterations
    for lbits in range((lo * BW_R_LAG1) % BW_R_LAG0, 0x1_0000_0000, BW_R_LAG0):
        state = ((out1 | lbits) * BW_R_MULT + BW_R_INC) & 0xffff_ffff_ffff_ffff
        if (state >> 32) == out0:
            yield state
    
    # true in around 18% of cases
    if lo != up:
        for lbits in range((up * BW_R_LAG1) % BW_R_LAG0, 0x1_0000_0000, BW_R_LAG0):
            state = ((out1 | lbits) * BW_R_MULT + BW_R_INC) & 0xffff_ffff_ffff_ffff
            if (state >> 32) == out0:
                yield state

#################################################################################################################################################################

'''
|          1    0    0    0    0    0 |           |  -2528644 -24142902  52961366   7565619  24945956 -99942057 |            | -10  23  -1 -15  52 -53 |
|    0x343FD 2^32    0    0    0    0 |           |   3190924 -49228638   2127614 -61851545 114532500  37689339 |            | -14   7 -18 -21 -26 -24 |
| 0xA9FC6809    0 2^32    0    0    0 |    BKZ    |   -582052 -13727206  70521606  54506187  65564228  59925519 |  Inverse   |  24  -5  22  15  -5 -15 |
| 0x45C82BE5    0    0 2^32    0    0 | ========> | -12643092 -42907214  25386734 -98577505 -61029068  67751891 | =========> |  -5 -24  26 -12   9  14 | * 1/2^32
| 0xDDFF5051    0    0    0 2^32    0 |           |  43348284 -61510934 -42525898  11780387 -18382748 -24142713 |            |   0  27   0 -18  -8  -1 |
| 0x284A930D    0    0    0    0 2^32 |           | -33055668 -64755902 -59308450  10160279  42995412  -8780181 |            | -27   0  18   8   1   0 |
'''

# First row of the BKZ-reduced matrix
R = (-2528644, -24142902, 52961366, 7565619, 24945956, -99942057)

# Multiplier constants
M = (0x343FD, 0xA9FC6809, 0x45C82BE5, 0xDDFF5051, 0x284A930D)

# Increment constants
I = (0x269EC3, 0x1E278E7A, 0xD2F65B55, 0x98520C4, 0xA2974C77)

# Constants to bound the variables in the linear combinations for calculating potential solutions
CHANNEL_LOWER = (0x2AB966D1C2, 0x2169A3AA47, -0x5049D5FDC, -0x2AACDA387, 0xFE7FFFFFF, -0x898000001)
CHANNEL_UPPER = (0x2E8966D1C3, 0x23D9A3AA48, -0x3549D5FDB, -0xDACDA386, 0x1098000000, -0x7E8000000)

def channel_recover_ivs_seeds(hp: int, atk: int, dfs: int, spa: int, spd: int, spe: int) -> Iterator[int]:
    f0 = (-10 * hp + 23 * atk - dfs - 15 * spe + 52 * spa - 53 * spd) << 27
    x0_min = ((f0 + CHANNEL_UPPER[0]) >> 32) * R[0] # LOWER and UPPER are inverted relative to xmin and xmax because R0 is negative (same with R1 and R5)
    x0_max = ((f0 + CHANNEL_LOWER[0]) >> 32) * R[0]

    f1 = (-14 * hp + 7 * atk - 18 * dfs - 21 * spe - 26 * spa - 24 * spd) << 27
    x1_min = ((f1 + CHANNEL_UPPER[1]) >> 32) * R[1]
    x1_max = ((f1 + CHANNEL_LOWER[1]) >> 32) * R[1]

    f2 = (24 * hp - 5 * atk + 22 * dfs + 15 * spe - 5 * spa - 15 * spd) << 27
    x2_min = ((f2 + CHANNEL_LOWER[2]) >> 32) * R[2]
    x2_max = ((f2 + CHANNEL_UPPER[2]) >> 32) * R[2]

    f3 = (-5 * hp - 24 * atk + 26 * dfs - 12 * spe + 9 * spa + 14 * spd) << 27
    x3_min = ((f3 + CHANNEL_LOWER[3]) >> 32) * R[3]
    x3_max = ((f3 + CHANNEL_UPPER[3]) >> 32) * R[3]

    f4 = (27 * atk - 18 * spe - 8 * spa - spd) << 27
    x4_min = ((f4 + CHANNEL_LOWER[4]) >> 32) * R[4]
    x4_max = ((f4 + CHANNEL_UPPER[4]) >> 32) * R[4]

    f5 = (-27 * hp + 18 * dfs + 8 * spe + spa) << 27
    x5_min = ((f5 + CHANNEL_UPPER[5]) >> 32) * R[5]
    x5_max = ((f5 + CHANNEL_LOWER[5]) >> 32) * R[5]

    # at most 720 iterations in total (around 369 in average, 48 in the best case)
    for x5 in range(x5_min, x5_max + 1, -R[5]):
        for x4 in range(x4_min, x4_max + 1, R[4]):
            l4 = x5 + x4
            for x2 in range(x2_min, x2_max + 1, R[2]):
                l2 = l4 + x2
                for x3 in range(x3_min, x3_max + 1, R[3]):
                    l3 = l2 + x3
                    for x1 in range(x1_min, x1_max + 1, -R[1]):
                        l1 = l3 + x1
                        for x0 in range(x0_min, x0_max + 1, -R[0]):
                            seed = l1 + x0
                            if (
                                ((seed >> 27) & 31) == hp and 
                                (((seed * M[0] + I[0]) >> 27) & 31) == atk and 
                                (((seed * M[1] + I[1]) >> 27) & 31) == dfs and
                                (((seed * M[2] + I[2]) >> 27) & 31) == spe and 
                                (((seed * M[3] + I[3]) >> 27) & 31) == spa and
                                (((seed * M[4] + I[4]) >> 27) & 31) == spd
                            ):
                                yield seed