import sys, os
from typing import Sequence

PATH = os.path.dirname(__file__)

sys.path.append(os.path.join(PATH, ".."))
from RNG import MT, TinyMT, SFMT, Xoroshiro128Plus, Xorshift128

from GF2_Matrix import *
from GF2_Polynomial import gf2x_pow_mod, gf2_berlekamp_massey

def tinymt_next(state128: int) -> int:
    if state128 == 0x8000_0000:
        return 0
    state = [(state128 >> (32 * i)) & 0xffff_ffff for i in range(4)]
    rng = TinyMT(state)
    rng.twist()
    s0, s1, s2, s3 = rng.state
    return (s3 << 96) | (s2 << 64) | (s1 << 32) | s0

def xoroshiro128plus_next(state128: int) -> int:
    s0 = state128 & 0xffff_ffff_ffff_ffff
    s1 = state128 >> 64
    rng = Xoroshiro128Plus(s0, s1)
    rng.next_state()
    s0, s1 = rng.state
    return (s1 << 64) | s0

def tinymt_127_lsb_sequence(state128: int) -> int:
    if state128 == 0x8000_0000:
        return 0
    state = [(state128 >> (32 * i)) & 0xffff_ffff for i in range(4)]
    rng = TinyMT(state)
    bits = 0
    for i in range(127):
        b = rng.next_u32() & 1 # temper(state) & 1 == state[3] & 1
        bits |= b << i
    return bits

def xoroshiro128plus_128_lsb_sequence(state128: int) -> int:
    s0 = state128 & 0xffff_ffff_ffff_ffff
    s1 = state128 >> 64
    rng = Xoroshiro128Plus(s0, s1)
    bits = 0
    for i in range(128):
        b = rng.next_u64() & 1 # (s0 + s1) & 1
        bits |= b << i
    return bits

# intervals = [0, 11, 7, ...]
# f = lambda vec: xorshift128_bdsp_blinks(vec, intervals)
# mat = gf2mat_from_func(f, len(intervals) * 4, 128)
# check if rank(mat) == 128 to determine if there is a unique solution
# g_inv = matrix_generalized_inverse_gf2(mat)
def xorshift128_bdsp_blinks(state128: int, intervals: Sequence[int]) -> int:
    state = [(state128 >> (32 * i)) & 0xffff_ffff for i in range(4)]
    rng = Xorshift128(state)
    bits = 0
    for i in range(len(intervals)):
        rng.advance(intervals[i])
        # blink = rand(16) <= 1 <==> state[3] & 0xf <= 1 (0 for double, 1 for single)
        # When state[3] == 0xffff_ffff, the equivalence above no longer holds due to a modulo operation by 0xffff_ffff
        # https://github.com/StarfBerry/PokeRNG/blob/193dd76a606014fe27d5d6e80ca5d12b4fd4e84c/RNG/Xorshift.py#L64
        b = rng.s3 & 0xf
        bits |= b << (4 * i)
    return bits

def print_bit_matrix_in_hex(mat: Matrix, axis: int, per_line: int, bits_slice: Sequence[int] = None):
    if axis == 0:
        # rows
        get_axis = lambda i: mat[i]
        axis_length = mat.shape[0]
    else:
        # columns
        get_axis = lambda i: mat[:, i]
        axis_length = mat.shape[1]

    if bits_slice:
        assert sum(bits_slice) == mat.shape[(axis & 1) ^ 1]
        hex_size = [(b + 3) >> 2 for b in bits_slice]
        mask = [(1 << b) - 1 for b in bits_slice]
        shift = [sh := 0] + [sh := sh + b for b in bits_slice[:-1]]
        fmt = lambda a: "({})".format(", ".join(f"0x{(a >> s) & m:0{h}x}" for s, m, h in zip(shift, mask, hex_size)))
    else:
        hex_size = (axis_length + 3) >> 2
        fmt = lambda a: f"0x{a:0{hex_size}x}"

    for i in range(axis_length):
        a = gf2vec_to_int(get_axis(i))
        print(fmt(a), end = "\n" if i == axis_length - 1 else ", " if (i + 1) % per_line else ",\n")

def print_jump_table_in_hex(charpoly: int, size: int, per_line: int, bits_slice: Sequence[int] = None):
    if bits_slice:
        assert sum(bits_slice) == charpoly.bit_length() - 1
        hex_size = [(b + 3) >> 2 for b in bits_slice]
        mask = [(1 << b) - 1 for b in bits_slice]
        shift = [sh := 0] + [sh := sh + b for b in bits_slice[:-1]]
        fmt = lambda p: "({})".format(", ".join(f"0x{(p >> s) & m:0{h}x}" for s, m, h in zip(shift, mask, hex_size)))
    else:
        hex_size = (charpoly.bit_length() - 1 + 3) >> 2
        fmt = lambda p: f"0x{p:0{hex_size}x}"

    for i in range(size):
        p = gf2x_pow_mod(2, 1 << i, charpoly)
        print(fmt(p), end = "\n" if i == size - 1 else ", " if (i + 1) % per_line else ",\n")

if __name__ == "__main__":
    '''
    rng = MT(0xdeadbeef)
    bits = [rng.next_u32() & 1 for _ in range(624 * 32 * 2)]
    charpoly = gf2_berlekamp_massey(bits)
    path = os.path.join(PATH, "charpoly_mt.txt")
    with open(path, "w") as file:
        file.write(hex(charpoly))
    '''

    '''
    rng = TinyMT(0xdeadbeef)
    bits = [rng.next_u32() & 1 for _ in range(127 * 2)]
    T = gf2mat_from_func(tinymt_next, 128, 128)
    charpoly = gf2_berlekamp_massey(bits)
    zeros, cartesian_eq = gf2mat_constraints(T)
    print(hex(zeros), hex(cartesian_eq)) # 0x0 0x3fffffffffffff8000000080000000
    print(hex(charpoly)) # 0xd8524022ed8dff4a8dcc50c798faba43
    '''

    '''
    rng = SFMT(0xdeadbeef)
    bits = []
    for _ in range(2 * 32 * 4):
        rng.twist()
        for i in range(0, 624, 4):
            bits.append(rng.state[i] & 1)
    charpoly = gf2_berlekamp_massey(bits)
    path = os.path.join(PATH, "charpoly_sfmt.txt")
    with open(path, "w") as file:
        file.write(hex(charpoly))
    '''

    '''
    rng = Xoroshiro128Plus(0xdeadbeef)
    bits = [rng.next_u64() & 1 for _ in range(128 * 2)]
    charpoly = gf2_berlekamp_massey(bits)
    print(hex(charpoly)) # 0x10008828e513b43d5095b8f76579aa001
    '''

    '''
    rng = Xorshift128(0xdeadbeef)
    bits = [rng.next() & 1 for _ in range(128 * 2)]
    charpoly = gf2_berlekamp_massey(bits)
    print(hex(charpoly)) # 0x1000000010046d8b3f985d65ffd3c8001
    '''

    #print_jump_table_in_hex(0xd8524022ed8dff4a8dcc50c798faba43, 127, 3)

    #print_jump_table_in_hex(0x10008828e513b43d5095b8f76579aa001, 128, 3)

    #print_jump_table_in_hex(0x1000000010046d8b3f985d65ffd3c8001, 128, 3)

    '''
    B = gf2mat_from_func(tinymt_127_lsb_sequence, 127, 128)
    B = np.delete(B, 31, 1) # delete the 31st column to make the matrix invertible
    T = gf2mat_from_func(tinymt_next, 128, 128)
    A = gf2mat_pow(T, 124)
    A = np.delete(A, 31, 1) # delete the 31st column to make the product between A and B^-1 consistent
    P = (A @ gf2mat_inverse(B)) & 1
    print_bit_matrix_in_hex(P, 1, 2, [32, 32, 32, 32])
    '''

    B = gf2mat_from_func(xoroshiro128plus_128_lsb_sequence, 128, 128)
    T = gf2mat_from_func(xoroshiro128plus_next, 128, 128)
    P = (gf2mat_pow(T, 128) @ gf2mat_inverse(B)) & 1
    print_bit_matrix_in_hex(P, 1, 2, [64, 64])