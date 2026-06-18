from typing import Sequence
from Matrix_GF2 import *
from Polynomial_GF2 import *

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
        s1 ^= 0x8f7011ee
        s2 ^= 0xfc78ff1f

    return (s3 << 96) | (s2 << 64) | (s1 << 32) | s0

def xoroshiro128plus_next(state128: int) -> int:
    def rotl(n: int, k: int) -> int:
        return ((n << k) | (n >> (64 - k))) & 0xffffffffffffffff
    
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

def tinymt_127bits_sequence(state128: int) -> int:
    bits = 0
    for i in range(127):
        state128 = tinymt_next(state128)
        b = (state128 >> 96) & 1 # the output reveals the least significant bit of state[3]
        bits |= b << i
    return bits

def xoroshiro128plus_128bits_sequence(state128: int) -> int:
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

def prng_jump_table_gf2(charpoly: int, size: int) -> list[int]:
    return [poly_pow_mod_gf2(2, 1 << i, charpoly) for i in range(size)]

def print_bit_matrix_in_hex(mat: Matrix, axis: int = 0, per_line: int = 1):
    if axis == 0:
        # rows
        get_axis = lambda i: mat[i]
        axis_length = mat.shape[0]
    else:
        # columns
        get_axis = lambda i: mat[:, i]
        axis_length = mat.shape[1]

    hex_size = (axis_length + 3) // 4

    for i in range(0, axis_length, per_line):
        line = (f"0x{bit_vector_to_int(get_axis(j)):0{hex_size}x}" for j in range(i, min(i + per_line, axis_length)))
        print(", ".join(line), end=",\n")

def print_jump_table_in_hex(charpoly: int, size: int, per_line: int = 1):
    jump_table = prng_jump_table_gf2(charpoly, size)
    hex_size = (poly_deg_gf2(charpoly) + 3) // 4
    
    for i in range(0, size, per_line):
        line = (f"0x{jump_table[j]:0{hex_size}x}" for j in range(i, min(i + per_line, size)))
        print(", ".join(line), end=",\n")

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

    #print_jump_table_in_hex(0x10008828e513b43d5095b8f76579aa001, 128, 4)

    #print_jump_table_in_hex(0x1000000010046d8b3f985d65ffd3c8001, 128, 4)

    '''
    mat = function_to_matrix_gf2(tinymt_127bits_sequence, 127, 128)
    mat = np.delete(mat, 31, 1) # delete the 31st column to make the matrix invertible
    inv = matrix_inverse_gf2(mat)
    print_bit_matrix_in_hex(inv, 1, 4)
    '''

    '''
    mat = function_to_matrix_gf2(xoroshiro128plus_128bits_sequence, 128, 128)
    inv = matrix_inverse_gf2(mat)
    print_bit_matrix_in_hex(inv, 1, 4)
    '''