# Seed to time for older versions of Dolphin that allow manipulating the initial seed for Pokémon Colosseum and XD.

from datetime import datetime, timedelta

##### Edit your parameters here #####
CALIBRATION_SEED = 0x26acbb6
DT_CALIBRATION = datetime(2000, 1, 1, 0, 0, 0)
DT_LIMIT = datetime(2000, 5, 1, 0, 0, 0)

TARGET_SEED = 0xc0cac01a
MIN_ADVC = 10_000
MAX_ADVC = 15_000
#####################################

'''
seed = (calibration_seed + 40_500_000 * seconds) mod 2^32

seed - calibration_seed = (40_500_000 * seconds) mod 2^32

gcd(40_500_000, 2^32) = 32 so we can divide both sides by 32 and let D = 40_500_000 / 32.

(seed - calibration_seed) >> 5 = (D * seconds) mod 2^27

Since gcd(D, 2^27) = 1, D has a multiplicative inverse modulo 2^27, which is equal to 0x4e4069.

0x4e4069 * ((seed - calibration_seed) >> 5) = seconds mod 2^27

If the number of seconds is smaller than 2^27, this is equivalent to calculating its real value.
'''
def dolphin_seconds_distance(calibration_seed: int, seed: int) -> int:
    if (seed & 0x1f) != (calibration_seed & 0x1f):
        return -1 
    return (0x4e4069 * ((seed - calibration_seed) >> 5)) & 0x7ffffff

def gcrng_prev(seed: int) -> int:
    return (seed * 0xb9b33155 + 0xa170f641) & 0xffffffff

def gcrng_prev2(seed: int) -> int:
    return (seed * 0xe05fa639 + 0x3882ad6) & 0xffffffff

def gcrng_jump_backward(seed: int, n: int) -> int:
    mult = pow(0xb9b33155, n, 1 << 32)
    incr = (0xa170f641 * (pow(0xb9b33155, n, 0xb9b33154 << 32) - 1) // 0xb9b33154) & 0xffffffff
    return (mult * seed + incr) & 0xffffffff

if __name__ == "__main__":
    delta_dt = DT_LIMIT - DT_CALIBRATION
    delta_sec = int(delta_dt.total_seconds())
    assert delta_sec < 2**27, "The seconds range must be smaller than 2^27."

    seed = gcrng_jump_backward(TARGET_SEED, MIN_ADVC)
    
    # Different parity, LCGs alternate between odd and even states.
    # With this, the least significant bit matches, and we will able to advance through the RNG sequence 2 by 2.
    if (seed & 1) != (CALIBRATION_SEED & 1):
        seed = gcrng_prev(seed)
        MIN_ADVC += 1

    res = False

    l = len(str(MAX_ADVC))

    for advc in range(MIN_ADVC, MAX_ADVC + 1, 2):
        dist = dolphin_seconds_distance(CALIBRATION_SEED, seed)
        if 0 <= dist <= delta_sec:            
            dt = DT_CALIBRATION + timedelta(seconds = dist)
            print(f"Initial Seed: {seed:08X} | Advances: {advc:<{l}} | Date-Time: {dt}")
            res = True
        seed = gcrng_prev2(seed)
    
    if not res:
        print("No results.")