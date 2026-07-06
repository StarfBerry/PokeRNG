from typing import Sequence
from Matrix_GF2 import *
from Polynomial_GF2 import *

def rotl(n: int, k: int) -> int:
    return ((n << k) | (n >> (64 - k))) & 0xffffffffffffffff

def tinymt_next(state128: int) -> int:
    s0 = state128 & 0xffffffff
    s1 = (state128 >> 32) & 0xffffffff
    s2 = (state128 >> 64) & 0xffffffff
    s3 = (state128 >> 96) & 0xffffffff

    x = (s0 & 0x7fffffff) ^ s1 ^ s2
    y = s3

    x ^= (x << 1) & 0xffffffff
    y ^= (y >> 1) ^ x

    s0 = s1
    s1 = s2
    s2 = x ^ (y << 10) & 0xffffffff
    s3 = y

    if y & 1:
        s1 ^= 0x8F7011EE
        s2 ^= 0xFC78FF1F

    return (s3 << 96) | (s2 << 64) | (s1 << 32) | s0

def xoroshiro128plus_next(state128: int) -> int:
    s0 = state128 & 0xffffffffffffffff
    s1 = (state128 >> 64) ^ s0

    s0 = rotl(s0, 24) ^ s1 ^ (s1 << 16) & 0xffffffffffffffff
    s1 = rotl(s1, 37)

    return (s1 << 64) | s0

def xorshift128_next(state128: int) -> int:
    s0 = state128 & 0xffffffff
    s1 = (state128 >> 32) & 0xffffffff
    s2 = (state128 >> 64) & 0xffffffff
    s3 = (state128 >> 96) & 0xffffffff

    t = s0 ^ (s0 << 11) & 0xffffffff
    t ^= (t >> 8) ^ s3 ^ (s3 >> 19)

    s0, s1, s2, s3 = s1, s2, s3, t

    return (s3 << 96) | (s2 << 64) | (s1 << 32) | s0

def tinymt_127_bits_sequence(state128: int) -> int:
    bits = 0
    for i in range(127):
        state128 = tinymt_next(state128)
        b = (state128 >> 96) & 1 # temper(state) & 1 == state[3] & 1
        bits |= b << i
    return bits

def xoroshiro128plus_128_bits_sequence(state128: int) -> int:
    bits = 0
    for i in range(128):
        b = (state128 ^ (state128 >> 64)) & 1 # <==> (s0 + s1) & 1
        bits |= b << i
        state128 = xoroshiro128plus_next(state128)
    return bits

# intervals = [0, 11, 7, ...]
# f = lambda vec: xorshift128_bdsp_blinks(vec, intervals)
# mat = function_to_matrix_gf2(f, len(intervals) * 4, 128)
# check if rank(mat) == 128 to determine if there is a unique solution
# g_inv = matrix_generalized_inverse_gf2(mat)
def xorshift128_bdsp_blinks(state128: int, intervals: Sequence[int]) -> int:
    bits = 0
    for i in range(len(intervals)):
        for _ in range(intervals[i]):
            state128 = xorshift128_next(state128)
        bits |= ((state128 >> 96) & 0xf) << (4 * i) # blink = rand(16) <= 1 <==> state[3] & 0xf <= 1 (0 for double, 1 for single)
    return bits

def print_bit_matrix_in_hex(mat: Matrix, axis: int, per_line: int):
    if axis == 0:
        # rows
        get_axis = lambda i: mat[i]
        axis_length = mat.shape[0]
    else:
        # columns
        get_axis = lambda i: mat[:, i]
        axis_length = mat.shape[1]

    hex_size = (axis_length + 3) // 4

    for i in range(axis_length):
        a = bit_vector_to_int(get_axis(i))
        print(f"0x{a:0{hex_size}x},", end = " " if (i + 1) % per_line else "\n")
    
    if axis_length % per_line:
        print()

def print_jump_table_in_hex(apoly: int, size: int, per_line: int):
    hex_size = (apoly.bit_length() - 1 + 3) // 4

    for i in range(size):
        poly = poly_pow_mod_gf2(2, 1 << i, apoly)
        print(f"0x{poly:0{hex_size}x},", end = " " if (i + 1) % per_line else "\n")
    
    if size % per_line:
        print()

if __name__ == "__main__":
    '''
    mat = function_to_matrix_gf2(tinymt_next, 128, 128)
    charpoly = matrix_charpoly_gf2(mat)
    print(hex(charpoly)) # 0x1b0a48045db1bfe951b98a18f31f57486
    eq = matrix_equation_gf2(mat)
    print(hex(eq[0]), hex(eq[1])) # 0x0 0x3fffffffffffff8000000080000000
    '''

    '''
    mat = function_to_matrix_gf2(xoroshiro128plus_next, 128, 128)
    charpoly = matrix_charpoly_gf2(mat)
    print(hex(charpoly)) # 0x10008828e513b43d5095b8f76579aa001
    '''

    '''
    mat = function_to_matrix_gf2(xorshift128_next, 128, 128)
    charpoly = matrix_charpoly_gf2(mat)
    print(hex(charpoly)) # 0x1000000010046d8b3f985d65ffd3c8001
    '''
    
    #print_jump_table_in_hex(0x1b0a48045db1bfe951b98a18f31f57486, 127, 4)

    # The characteristic polynomial of the TinyMT can be factored by the monomial x to obtain an annihilating polynomial of lower degree.
    # However, if we call the jump function on a state that cannot be generated from the recurrence relation, the most significant bit of state[0] may differ from the one obtained if
    # we had used the characteristic polynomial.
    # This has no impact on the outputs, since the next state function is called just before they are calculated.
    print_jump_table_in_hex(0x1b0a48045db1bfe951b98a18f31f57486 >> 1, 127, 4)

    #print_jump_table_in_hex(0x10008828e513b43d5095b8f76579aa001, 128, 4)

    #print_jump_table_in_hex(0x1000000010046d8b3f985d65ffd3c8001, 128, 4)

    '''B = function_to_matrix_gf2(tinymt_127_bits_sequence, 127, 128)
    B = np.delete(B, 31, 1) # delete the 31st column to make the matrix invertible
    A = function_to_matrix_gf2(tinymt_next, 128, 128)
    A_124 = matrix_pow_gf2(A, 124)
    A_124 = np.delete(A_124, 31, 0)
    A_124 = np.delete(A_124, 31, 1)
    P = (A_124 @ matrix_inverse_gf2(B)) & 1
    print_bit_matrix_in_hex(P, 1, 4)'''

    '''B = function_to_matrix_gf2(xoroshiro128plus_128_bits_sequence, 128, 128)
    A = function_to_matrix_gf2(xoroshiro128plus_next, 128, 128)
    P = (matrix_pow_gf2(A, 128) @ matrix_inverse_gf2(B)) & 1
    print_bit_matrix_in_hex(P, 1, 4)'''