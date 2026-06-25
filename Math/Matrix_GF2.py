import numpy as np
from typing import Callable
from itertools import chain
from Polynomial_GF2 import poly_mul_gf2_bis, poly_divmod_gf2

type Vector = np.ndarray[tuple[int], np.uint8]      # 1DArray
type Matrix = np.ndarray[tuple[int, int], np.uint8] # 2DArray

def int_to_bit_vector(x: int, coords: int) -> Vector:
    """Converts an integer into a vector over GF(2) with a specified number of coordinates."""
    return np.array([(x >> i) & 1 for i in range(coords)], np.uint8)

def bit_vector_to_int(vec: Vector) -> int:
    """Converts a GF(2) vector into an integer."""
    return sum((int(b) & 1) << i for i, b in enumerate(vec))

def function_to_matrix_gf2(f: Callable[[int], int], row: int, col: int) -> Matrix:
    """Returns the function f encoded as a matrix, assuming f is linear over GF(2)."""
    mat = np.zeros((row, col), np.uint8)
    
    for i in range(col):
        im = f(1 << i) # images of the canonical basis by the function f
        mat[:, i] = int_to_bit_vector(im, row)
    
    return mat

def matrix_reduced_row_echelon_form_gf2(mat: Matrix) -> tuple[Matrix, list[int], int]:
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

def matrix_inverse_gf2(mat: Matrix) -> Matrix:
    """Computes the inverse of the given matrix, assuming the matrix is invertible over GF(2)."""
    n = mat.shape[0]
    assert n == mat.shape[1], "The matrix must be square."

    _, operations, rank = matrix_reduced_row_echelon_form_gf2(mat)
    assert rank == n, f"The matrix is not full rank ({rank = } while {n = })."

    inv = np.zeros((n, n), np.uint8)
    
    for i in range(n):
        inv[i] = int_to_bit_vector(operations[i], n)
    
    return inv

def matrix_generalized_inverse_gf2(mat: Matrix) -> Matrix:
    """Computes a generalized inverse of the given matrix."""
    row, col = mat.shape
    reduced, operations, rank = matrix_reduced_row_echelon_form_gf2(mat)

    pivot = 0
    swaps = []
    g_inv = np.zeros((col, row), np.uint8)
    
    for i in range(rank):
        g_inv[i] = int_to_bit_vector(operations[i], row)     
        while reduced[i, pivot] == 0:
            pivot += 1
        if pivot != i:
            swaps.append((i, pivot))
        pivot += 1

    for i, j in reversed(swaps):
        g_inv[[i, j]] = g_inv[[j, i]]
    
    return g_inv

def matrix_kernel_gf2(mat: Matrix) -> Matrix:
    """Computes a basis for the kernel of the given matrix."""
    col = mat.shape[1]
    _, operations, rank = matrix_reduced_row_echelon_form_gf2(mat.T)

    ker = np.zeros((col, col - rank), np.uint8)
    
    for c, i in enumerate(range(rank, col)):
        ker[:, c] = int_to_bit_vector(operations[i], col)

    return ker

def matrix_pow_gf2(mat: Matrix, n: int) -> Matrix: 
    """Computes the given matrix raised to the power of n, using binary exponentiation."""
    assert mat.shape[0] == mat.shape[1], "The matrix must be square."

    base = mat & 1 # mat's copy
    res = np.identity(mat.shape[0], np.uint8)
    
    while n:
        if n & 1:
            res = (res @ base) & 1
        base = (base @ base) & 1
        n >>= 1
    
    return res

def matrix_equation_gf2(mat: Matrix) -> tuple[int, int]:   
    """Computes the zeros and the equation to check if a vector lives in the column space of the given matrix."""
    _, terms, rank = matrix_reduced_row_echelon_form_gf2(mat)

    zeros = equation = 0
    
    for i in range(rank, mat.shape[0]):
        if terms[i].bit_count() == 1:
            zeros |= terms[i]
        else:
            equation ^= terms[i]
    
    # To evaluate them on a vector represented as an integer ===> (vec & zeros) == 0 and ((vec & equation).bit_count() & 1) == 0
    return (zeros, equation)

# This algorithm is not suitable for large matrices, such as the Mersenne Twister matrix.
# However, for 128-bit (or even 256-bit) PRNGs matrices, which are relatively small and empty, the algo is quite fast.
def matrix_charpoly_gf2(mat: Matrix) -> int:
    """
    Computes the characteristic polynomial of the given matrix over GF(2).
    
    The algorithm uses successive polynomial divisions and subtractions (like in the Euclid's algorithm) to nullify all coefficients above the main diagonal.
    
    At the end, the matrix is triangular and its determinant can be calculated by multiplying the coefficients on the main diagonal.
    """
    
    n = mat.shape[0]    
    assert n == mat.shape[1], "The matrix must be square."

    # P =  mat - xI
    P = (mat & 1).tolist()
    for i in range(n):
        P[i][i] ^= 2

    # To make computations modulo x^(n + 1) easier
    mask = (1 << (n + 1)) - 1

    charpoly = 1
    
    for i in range(n):
        pivot = next(j for j in range(i, n) if P[i][j] != 0) # pivot guaranteed
        for j in range(pivot + 1, n):
            if P[i][j] == 0:
                continue

            x, y = (pivot, j) if P[i][pivot] >= P[i][j] else (j, pivot)
            while P[i][x] and P[i][y]:
                q, P[i][x] = poly_divmod_gf2(P[i][x], P[i][y])
                for k in range(i + 1, n):
                    P[k][x] ^= poly_mul_gf2_bis(P[k][y], q) & mask
                x, y = y, x
            
            if P[i][pivot] == 0:
                pivot = j
        
        if pivot != i:
            # swap columns
            for j in range(i, n):
                P[j][i], P[j][pivot] = P[j][pivot], P[j][i]
                
        charpoly = poly_mul_gf2_bis(charpoly, P[i][i]) & mask

    return charpoly