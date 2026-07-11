from typing import Iterator, Sequence

XOROSHIRO_CONST = 0x82A2B175229D6A5B

def xoroshiro_recover_seeds(first: int, second: int) -> Iterator[int]:
    """
    Recovers the 64-bit seeds of Xoroshiro128+ from two consecutive 32-bit outputs.

    The algorithm solves equations by brute-forcing 6 bits of the seeds and 1 carry bit. 
    """
    # 0-31
    base_seed = (first - XOROSHIRO_CONST) & 0xffff_ffff

    x0 = base_seed ^ XOROSHIRO_CONST

    # 40-44
    base_seed |= (((second - (x0 >> 27)) ^ x0) & 0x1f) << 40

    x1 = (base_seed << 6) ^ (x0 >> 18) ^ (x0 >> 2)

    s = second >> 18

    for a in range(64):
        # assume 58-63
        assume = (a << 58) | base_seed

        sub = s - (x1 ^ a)

        for carry in range(2):
            r = (sub - carry) & 0x3fff

            if (a & 1) != (r >> 13):
                # assumed and recovered bits 58 don't match
                continue
            
            # the xor operation to recover the bits can be applied after the check because ((XOROSHIRO_CONST >> 45) >> 13) & 1 == 0

            # 45-57
            seed = assume | ((r ^ 0x1515) << 45) # 0x1515 = (XOROSHIRO_CONST >> 45) & 0x3fff

            # 32-39
            seed |= (((((second - ((seed >> 40) ^ x0))) >> 5) ^ 0x75) & 0xff) << 32 # 0x75 = (XOROSHIRO_CONST >> 32) & 0xff

            # check
            s1 = seed ^ XOROSHIRO_CONST
            test = ((((seed << 24) | seed >> 40) ^ s1 ^ (s1 << 16)) + ((s1 << 37) | (s1 >> 27))) & 0xffff_ffff

            if test == second:
                # at most 33 solutions ???
                yield seed

def xoroshiro_recover_seeds_with_skip(first: int, third: int) -> Iterator[int]:
    """
    Recovers the 64-bit seeds of Xoroshiro128+ from two 32-bit outputs with a skip in between.

    The algorithm solves equations by brute-forcing 8 bits of the seeds and 2 carry bits.   
    """
    # 0-31
    base_seed = (first - XOROSHIRO_CONST) & 0xffff_ffff

    bits_check = base_seed & 7

    x0 = base_seed ^ XOROSHIRO_CONST

    x1_ = (base_seed >> 19) ^ (x0 >> 6) ^ 0x56 # 0x56 = (XOROSHIRO_CONST >> 43) & 0xff

    x2_ = (x0 >> 16) ^ 0x65 # 0x65 = ((XOROSHIRO_CONST >> 40) ^ (XOROSHIRO_CONST >> 43) ^ (XOROSHIRO_CONST >> 56)) & 0xff
    
    x3_ = x1_ ^ (x0 >> 27)

    x4_ = x2_ ^ (x0 >> 27)
    
    x5 = (base_seed >> 16) ^ x0 ^ 0x2b1 # 0x2b1 = (XOROSHIRO_CONST >> 40) & 0x1fff

    x6 = (base_seed >> 3) ^ (x0 >> 11) ^ 0xe0a # 0xe0a = (XOROSHIRO_CONST >> 54) | ((XOROSHIRO_CONST & 7) << 10)

    x7 = XOROSHIRO_CONST ^ (x0 >> 24)

    t0 = third >> 16

    t1 = third >> 27

    for a in range(256):
        # assume 43-50
        assume = (a << 43) | base_seed

        x1 = x1_ ^ a

        x2 = x2_ ^ a

        x3 = x3_ ^ a

        x4 = x4_ ^ a

        for carry0 in range(2):
            sub0 = t0 - carry0

            # 32-36
            tmp = ((((sub0 - x3) ^ x4) & 0x1f) << 32) | assume
            
            x0 = tmp ^ XOROSHIRO_CONST

            # 37-39
            tmp |= (((sub0 - (x1 ^ (x0 >> 27))) ^ x2 ^ (x0 >> 27)) & 0xff) << 32

            x0 = tmp ^ XOROSHIRO_CONST
                
            r = ((third - (x5 ^ (x0 >> 27) ^ (x0 >> 24))) ^ x6 ^ (x0 >> 27)) & 0x1fff

            if (r >> 10) != bits_check:
                # recovered bits 37-39 cannot yield a solution
                continue
            
            # 54-63
            tmp |= (r & 0x3ff) << 54

            x0 = tmp ^ XOROSHIRO_CONST
            
            x8 = (tmp >> 30) ^ (x0 >> 17) ^ (x0 >> 54)

            x9 = (tmp >> 43) ^ (tmp >> 51) ^ (x0 >> 27) ^ (x0 >> 54) ^ 3 # 3 = (XOROSHIRO_CONST >> 3) & 7
            
            x10 = x8 ^ (x0 >> 38)

            x11 = x9 ^ (x0 >> 38)

            x12 = x7 ^ (x0 >> 35) ^ (tmp >> 48)

            x13 = (tmp >> 19) ^ (x0 >> 6)

            x14 = x13 ^ (x0 >> 27)

            for carry1 in range(2):
                sub1 = t1 - carry1
                
                # 51-52
                seed = ((((sub1 - x10) ^ x11) & 3) << 51) | tmp

                x0 = seed ^ XOROSHIRO_CONST
                
                # 40-41 
                seed |= ((((sub0 - (x14 ^ (x0 >> 43))) >> 8) ^ x12 ^ (x0 >> 51)) & 3) << 40

                x0 = seed ^ XOROSHIRO_CONST

                # 53
                seed |= (((sub1 - (x8 ^ (x0 >> 38))) ^ x9 ^ (x0 >> 38)) & 7) << 51

                x0 = seed ^ XOROSHIRO_CONST

                r = (((sub0 - (x13 ^ (x0 >> 27) ^ (x0 >> 43))) >> 8) ^ x7 ^ (x0 >> 35) ^ (seed >> 48) ^ (x0 >> 51)) & 0x7f

                if (a & 0xf) != (r >> 3):
                    # assumed and recovered bits 43-46 don't match
                    continue
                
                # 42
                seed |= r << 40

                # check
                s1 = seed ^ XOROSHIRO_CONST
                s0 = (((seed << 24) | (seed >> 40)) ^ s1 ^ (s1 << 16)) & 0xffff_ffff_ffff_ffff
                s1 = (s0 ^ ((s1 << 37) | (s1 >> 27))) & 0xffff_ffff_ffff_ffff
                test = ((((s0 << 24) | (s0 >> 40)) ^ s1 ^ (s1 << 16)) + ((s1 << 37) | (s1 >> 27))) & 0xffff_ffff

                if test == third:
                    yield seed

def xoroshiro_recover_state_from_128_lsb_sequence(bits: Sequence[int]) -> tuple[int, int]:
    """Recovers the internal state of a Xoroshiro128+ instance thanks to the least significant bit of 128 consecutive outputs."""
    if len(bits) != 128:
        raise ValueError("128 bits are needed to run the algorithm.")
    
    s0 = s1 = 0
    for i in range(128):
        if bits[i] == 1:
            s0 ^= XOROSHIRO_128_LSB_INV_X_ADVC_128[i][0]
            s1 ^= XOROSHIRO_128_LSB_INV_X_ADVC_128[i][1]
    
    return (s0, s1)

# XOROSHIRO^128 * XOROSHIRO_128_LSB_INV
XOROSHIRO_128_LSB_INV_X_ADVC_128 = (
    (0xbc3a7223e4917777, 0x7e20dc0c3a48212e), (0x8071979ce140db91, 0xe1a3d69592b1dd71),
    (0xf9c525a20f967a70, 0x5550ab49809b64c4), (0x66ff2a6ee7dc2ea8, 0x2afbf148c576abf2),
    (0x01f122958b0e66a9, 0x47da97ca1a59b923), (0x8eb2179ceaf56245, 0xde60da55f0cbb6fb),
    (0xd464977c8394d832, 0x7be2cacb5d67dee0), (0x1dce64b078aa5496, 0x47255a477b7542c0),
    (0x417e448c03cc9f50, 0x7aa5ee9a01f5b582), (0x6db0243cddfaf53f, 0xbdbf8990ce2fda4b),
    (0x5b0973951307037c, 0xdd780d474eeaff30), (0x86c3163687a28755, 0xbcb441cf0149473f),
    (0x49255bb4f0a1ead8, 0x312f118d0d4448d6), (0x18a82620ed590c4e, 0xb2d8aa498209229b),
    (0x9dc91c1dacb2a2f5, 0xd1d95509712467a7), (0x28522fd69990d92f, 0xa1c1a2c479c745de),
    (0x88d43931b2e0f661, 0xab1a031f47eefb77), (0x1c1c0b26d462c5a8, 0x2439d2d2b7e343e9),
    (0xd50b3e93bc581853, 0x40b4248cf579d6c5), (0xc583055ff24b5740, 0x603265c60697a03d),
    (0xd8fe1c6b52c228fd, 0x2ad00f45671aed8a), (0xeea88724aa9a5183, 0xc5905048fbccd1f9),
    (0x34d301cff92f87e6, 0x730d674037030564), (0x31d6ae0ea4ab0bc6, 0xf274180a59ea36a5),
    (0x4491741148415f5c, 0xd4448b8bb90ba9c5), (0x03417267f3968a35, 0x9c93810603edf830),
    (0xc62c4f7f7b08359c, 0x34298e912135ffcd), (0xdd79e8e0db89205e, 0x5470471eb2286c2a),
    (0xae9814486d68557c, 0x9913f906e112811d), (0x68cab40d986c881e, 0x5fc2200574a417d6),
    (0x2ea36c4035b73a4c, 0xc71ce2d159907d15), (0x99dd5a278741907c, 0x1311d9cf2979776a),
    (0x171eb22b2dc10459, 0x6e5579907d598a97), (0xc395e77b44547a4a, 0x8265850021ff87df),
    (0xd36c101d407621e3, 0x1079420c62bc5b92), (0xe5ebf352a562421a, 0x86fe118e35e1880a),
    (0x6588e4bbe03a5276, 0xd63d46d46ad4f4a3), (0x018232429fccd863, 0x60ce3bc85fa4640c),
    (0xa893cf43bbe313fa, 0x2874424c063c347d), (0xb2b1e82901c7a3f0, 0xd280098ae88401e2),
    (0xa399cee61e4fc560, 0x36c740c6d6029375), (0x43c514a256e2bcfa, 0xb76fae16218dd0a5),
    (0x95fbf8bfa8c6eb71, 0xe6ed38155ba4c058), (0x8db8c33ac088fd71, 0xe57f4b17d966c2e8),
    (0xfb07290564b2067d, 0x45cc1f122399fc25), (0x646685a5faccca2e, 0xf57a4a44d0e2aad6),
    (0x35187c57b727589f, 0x139f6901008c8acd), (0x4f99a57aaee1ea53, 0x85876f0318a44742),
    (0x09eb595682021bf6, 0xd334d54348f776d7), (0x8d872e8bfecd0eed, 0x55da3b129e8dfe1e),
    (0xbbdf357683b3d5dd, 0x2f2b5a86711d0405), (0xa2b57b4393655887, 0x53273d4c64c5540a),
    (0xaa5b1fc8d7920d8f, 0x0b679b475bd2623c), (0x13315503946c820b, 0x29efc6127437bed1),
    (0xafc6491e82f0cd14, 0xfe7d5ac7d566e57d), (0xd527c2a64691c687, 0xeb8cf58da9622c51),
    (0xdd9b598aeacdefd9, 0x72cae6c7bb48de2c), (0x6db8efa6b07cedde, 0x5062a957d3eabae8),
    (0xb5f89486f0f8f2e7, 0x0b67c151b27be7ad), (0x15f69fc4b2b297d1, 0x5a7feed60430ff82),
    (0x1768a7222b0aeb5f, 0xa74920de39d91429), (0x36a2592e0722b92f, 0xc76c918f4a18f029),
    (0x95dda38b73d0942d, 0xef8d640a3debf0a1), (0x8cff0d9bb7f37217, 0xdd10521eb88f1937),
    (0x37caf522165acdfc, 0x001423c4766b1935), (0x446ce24cb005eb1f, 0x67dfba8518054a01),
    (0x532cb96518525531, 0xb9f63d1acdb5febc), (0x75e4d92ab4f35f4c, 0xa38976df513ceea4),
    (0xe52e884bfc8a34ad, 0xddbdc111074f2942), (0x6fdaa5145ee7ec04, 0xe7e0dc5e480a020c),
    (0x86d094ee6e034c48, 0xb68a6ad1d7e51cf3), (0x5d256c036cb0cad7, 0x1180eacb2fddcfd8),
    (0xd6f7f3c9c1d386dc, 0x4d93b398df86d7d3), (0x9f21320551ce6cb1, 0x9bc7aa94157ba774),
    (0x4451e5e2b14be0c8, 0xe4fa38d91595dd9c), (0xaa310e2211ac2987, 0x629da0cef68bf841),
    (0xbec48182475af4f7, 0xc970de404c4e19f1), (0xe37205cc697f064f, 0xe1107503e73480bd),
    (0x63bf957baadfb672, 0xbe9c9f519b0e6383), (0xd152889c7bfb9353, 0x5d8afb80660f77a9),
    (0x77fefd8a3b28ba11, 0xb6d42818af1dbb94), (0x6221237cbe249748, 0x6543608fc54b6051),
    (0x0a8c4c4709f3542e, 0x74a6174582d94f2a), (0x505ee6cf0744ec1d, 0xbe5282998a388afe),
    (0x1e427b7bbc461d11, 0x10091103976ddf5c), (0xf26feb4fe7647663, 0x2cce2b9ad93d68b2),
    (0x5e073fcfe3916c07, 0x88ced48a72f71d5b), (0x731aa3b57a5b6349, 0x208d1b5fa61d15ed),
    (0x3931e14561b3690c, 0x061ba7c5d66e578f), (0xbdb432653eebc9c4, 0x930740d946db14fa),
    (0x75f3c2af253e5ad0, 0xbfc51a08f1a660d6), (0x10720001784457b8, 0x57ff3307cdba7f68),
    (0xdf9452de000032b4, 0x23e32f0a9c669d75), (0x672bccbf9ccf2ab0, 0x33c8f85435d033c8),
    (0x2f570064ff9dc8ed, 0x4ce32fd560dad976), (0x84d193529a64c854, 0x2fd745992803d12a),
    (0x3672785318dca571, 0xff3266da49a21f5d), (0xaf0c35d721162713, 0xbf5b8b021036e27c),
    (0x08c1392b7af6496f, 0xda5a201741d5c36e), (0x98a21d3f307095aa, 0xe0b61d0b987b12f3),
    (0x9d25421cf65aad1f, 0xc1e69a8b695f1df7), (0x8199cb3e8004fc7c, 0xdad333d13e0bc8a8),
    (0x4c65e2562cd3ad5f, 0xc595bc136a0534c1), (0xa33acddd7754abf8, 0xfa704a54a7a15041),
    (0xd529aa0c85c88cfa, 0x7014a08e8a1b0ea8), (0xf0138c5ae8a08e14, 0x4659fa0075f97d49),
    (0x4241c438560d826d, 0x41ee0fd21c3f4dbd), (0x7cf21328cdd45acc, 0xec13e94527db2ab2),
    (0xfec5868c995d1dc5, 0xd7fb5fd90e3d828f), (0x1cc73bdaa014273d, 0xd4b6d7cedeabfdc3),
    (0x0f918335dc7a9108, 0x7964dcdbc2df27b6), (0xeb8d9c0b5e58b43e, 0xf781cb19334ac481),
    (0xbcba667433c5935f, 0x752030503c799d07), (0xee92ddf1b1913509, 0x6f7111198a38348b),
    (0x62bd81e367472e62, 0xaeec40473c3ca6ea), (0x8e76129d8fa0d427, 0x758d5985040ee07c),
    (0xc0beebd155863206, 0xe89e9cd2b62a58ca), (0x24c6e007c9ee53f6, 0xb177b2c19eaaa710),
    (0xf3ee607d0b30b4f1, 0xff1b35458ebb0967), (0x626d5b07d087ceed, 0x4e18834cef7f1747),
    (0xed0af7fdac99cd2e, 0x8a710f4796e90934), (0xb0455499f41be780, 0x8cf21cd050486ffa),
    (0x9a776671b8c381b0, 0x18f5250e6ca41156), (0x2c2898c998f63ca1, 0x5f4db84328319589),
    (0xce5163b9c55e9fbf, 0xd710ef158fa4f27d), (0x9e18c745bfaa92ac, 0x3265e0d6511215d4),
    (0x3fbdaabc3ef67831, 0x8d353a129f655737), (0x4fd1e181ff3c6c2b, 0xdb2acb384355c5fb)
)

if __name__ == "__main__":
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from RNG import Xoroshiro128Plus

    from random import getrandbits

    def test_xoroshiro_recover_seeds(n: int = 10_000):
        rng = Xoroshiro128Plus(0)

        for _ in range(n):
            seed = getrandbits(64)

            rng.reseed(seed)
            out0 = rng.next_u32()
            out1 = rng.next_u32()

            assert seed in xoroshiro_recover_seeds(out0, out1), f"{seed = :016X}, {out0 = :08X}, {out0 = :08X}"

    def test_xoroshiro_recover_seeds_with_skip(n: int = 10_000):
        rng = Xoroshiro128Plus(0)

        for _ in range(n):
            seed = getrandbits(64)

            rng.reseed(seed)
            ec = rng.next_u32()
            rng.next_state() # fake ids
            pid = rng.next_u32()

            assert seed in xoroshiro_recover_seeds_with_skip(ec, pid), f"{seed = :016X}, {ec = :08X}, {pid = :08X}"

    def test_xoroshiro_recover_state_from_128_lsb_sequence(n: int = 10_000):
        rng = Xoroshiro128Plus(0)
        bits = [0] * 128

        for _ in range(n):
            rng.reseed(getrandbits(64))
            rng.jump(getrandbits(16))
            
            # https://billo-guides.github.io/retail/swsh/overworld/seed-finding-and-monitoring#seedfinder-overview
            for i in range(128): 
                bits[i] = rng.next_u64() & 1 # attack animation from the summary of a Pokémon (0 for physical, 1 for special)
            
            state = rng.state

            state_ = xoroshiro_recover_state_from_128_lsb_sequence(bits)
            assert state == state_, f"{state = }, {state_ = }"

    
    #test_xoroshiro_recover_seeds()

    #test_xoroshiro_recover_seeds_with_skip()

    #test_xoroshiro_recover_state_from_128_lsb_sequence()