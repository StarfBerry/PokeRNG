import numpy as np
from typing import Callable
from itertools import chain
from GF2_Polynomial import gf2x_mul_skip, gf2x_divmod

type Vector = np.ndarray[tuple[int], np.uint8]        # 1DArray
type Matrix = np.ndarray[tuple[int, int], np.uint8]   # 2DArray
type MatrixPoly = np.ndarray[tuple[int, int], object] # 2DArray

def gf2vec_from_int(n: int, coords: int) -> Vector:
    """Generates a GF(2) vector from the binary representation of the given integer and a specified number of coordinates."""
    return np.array([(n >> i) & 1 for i in range(coords)], np.uint8)

def gf2vec_to_int(vec: Vector) -> int:
    """Converts a GF(2) vector into its corresponding integer value via binary decoding."""
    return sum((int(b) & 1) << i for i, b in enumerate(vec))

def gf2mat_from_func(f: Callable[[int], int], row: int, col: int) -> Matrix:
    """Returns the matrix representation of the function f, assuming f is linear over GF(2)."""
    mat = np.zeros((row, col), np.uint8)

    for i in range(col):
        im = f(1 << i) # images of the canonical basis by the function f
        mat[:, i] = gf2vec_from_int(im, row)

    return mat

def gf2mat_reduced_row_echelon_form(mat: Matrix) -> tuple[Matrix, list[int], int]:
    """Computes the reduced row echelon form, the list of elementary operations required to obtain it, and the rank of the given matrix."""
    row, col = mat.shape
    reduced = mat & 1 # mat's copy
    operations = [1 << i for i in range(row)]

    # row and column pivots
    pr = pc = 0

    while pr < row and pc < col:
        pivot = next((i for i in range(pr, row) if reduced[i, pc]), None)
        if pivot is None:
            pc += 1
            continue
        for i in chain(range(pr), range(pivot + 1, row)):
            if reduced[i, pc]:
                reduced[i] ^= reduced[pivot]
                operations[i] ^= operations[pivot]
        if pivot != pr:
            # swap rows
            reduced[[pr, pivot]] = reduced[[pivot, pr]]
            operations[pr], operations[pivot] = operations[pivot], operations[pr]
        pr += 1 # at the the end, it will be the rank of the matrix
        pc += 1

    return (reduced, operations, pr)

def gf2mat_inverse(mat: Matrix) -> Matrix:
    """Computes the inverse of the given matrix."""
    n = mat.shape[0]
    assert n == mat.shape[1], "The matrix must be square."

    _, operations, rank = gf2mat_reduced_row_echelon_form(mat)
    assert rank == n, f"The matrix is not full rank ({rank = } while {n = })."

    inv = np.zeros((n, n), np.uint8)

    for i in range(n):
        inv[i] = gf2vec_from_int(operations[i], n)

    return inv

def gf2mat_generalized_inverse(mat: Matrix) -> Matrix:
    """Computes a generalized inverse of the given matrix."""
    row, col = mat.shape
    reduced, operations, rank = gf2mat_reduced_row_echelon_form(mat)

    pivot = 0
    swaps = []
    g_inv = np.zeros((col, row), np.uint8)

    for i in range(rank):
        g_inv[i] = gf2vec_from_int(operations[i], row)     
        while reduced[i, pivot] == 0:
            pivot += 1
        if pivot != i:
            swaps.append((i, pivot))
        pivot += 1

    for i, j in reversed(swaps):
        g_inv[[i, j]] = g_inv[[j, i]]

    return g_inv

def gf2mat_kernel(mat: Matrix) -> Matrix:
    """Computes a basis for the kernel of the given matrix."""
    col = mat.shape[1]
    _, operations, rank = gf2mat_reduced_row_echelon_form(mat.T)

    ker = np.zeros((col, col - rank), np.uint8)

    for c, i in enumerate(range(rank, col)):
        ker[:, c] = gf2vec_from_int(operations[i], col)

    return ker

def gf2mat_pow(mat: Matrix, n: int) -> Matrix: 
    """Computes the given matrix raised to the power of n using binary exponentiation."""
    assert mat.shape[0] == mat.shape[1], "The matrix must be square."

    base = mat & 1 # mat's copy
    res = np.identity(mat.shape[0], np.uint8)

    while n:
        if n & 1:
            res @= base
        base @= base
        n >>= 1

    res &= 1

    return res

def gf2mat_constraints(mat: Matrix) -> tuple[int, int]:   
    """Computes the constraints to check if a vector belongs to the column space of the given matrix."""
    _, terms, rank = gf2mat_reduced_row_echelon_form(mat)

    zeros = cartesian_eq = 0

    for i in range(rank, mat.shape[0]):
        if terms[i].bit_count() == 1:
            zeros |= terms[i]
        else:
            cartesian_eq ^= terms[i]

    # These constraints can be checked using bitmasks and a XOR sum over a vector represented as an integer.
    # Like this: (vec & zeros) == 0 and ((vec & cartesian_eq).bit_count() & 1) == 0
    return (zeros, cartesian_eq)

def gf2xmat_det(mat: MatrixPoly, in_place: bool = False, max_degree: int = -1) -> int:
    """
    Computes the determinant of the given matrix over GF(2)[X].
    
    The algorithm uses successive polynomial divisions and subtractions (like in the Euclid's algorithm) to nullify all coefficients above the main diagonal.
    
    At the end, the matrix is triangular and its determinant can be calculated by multiplying the coefficients on the main diagonal.

    The `max_degree` parameter aims to ensure that the coefficients do not exceed this degree during the calculations.
    """
    n = mat.shape[0]    
    assert n == mat.shape[1], "The matrix must be square."

    P = mat.copy() if not in_place else mat

    if max_degree != -1:
        # To make computations modulo x^(max_degree + 1) more quickly
        mask = (1 << (max_degree + 1)) - 1

        # The `gf2x_mul_skip` function can output polynomials of degree <= `2 * max_degree`, assuming the initial coefficients have a degree <= `max_degree`.
        # This temporary degree overflow is compensated by the function's speed and the modular reduction of the result using a bitmask.
        poly_mul = lambda f, g: gf2x_mul_skip(f, g) & mask
    else:
        poly_mul = gf2x_mul_skip

    det = 1

    for i in range(n):
        pivot = next((j for j in range(i, n) if P[i, j]), None)
        if pivot is None:
            return 0
        for j in range(pivot + 1, n):
            if P[i, j] == 0:
                continue

            x, y = (pivot, j) if P[i, pivot] >= P[i, j] else (j, pivot)

            while P[i, x] and P[i, y]:
                q, P[i, x] = gf2x_divmod(P[i, x], P[i, y])
                for k in range(i + 1, n):
                    P[k, x] ^= poly_mul(P[k, y], q)
                x, y = y, x

            if P[i, pivot] == 0:
                pivot = j

        if pivot != i:
            # swap columns
            P[i:n, [i, pivot]] = P[i:n, [pivot, i]]

        det = poly_mul(det, P[i, i])

    return det

def gf2mat_charpoly(mat: Matrix) -> int:
    """Computes the characteristic polynomial of the given matrix."""
    n = mat.shape[0]
    assert n == mat.shape[1], "The matrix must be square."

    # conversion from GF(2) to GF(2)[X]
    P = mat.astype(object)

    # P - xI
    for i in range(n):
        P[i, i] ^= 2

    return gf2xmat_det(P, True, n)