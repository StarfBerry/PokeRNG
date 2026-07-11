from typing import Sequence

def tinymt_equation(s0: int, s1: int, s2: int, s3: int) -> int:
    """Equation to check if a state can be generated from the recurrence relation of the TinyMT."""
    eq = (s0 >> 31) ^ (s1 >> 31) ^ s2.bit_count() ^ (s3 & 0x3fffff).bit_count()
    return eq & 1

def tinymt_prev(s0: int, s1: int, s2: int, s3: int) -> tuple[int, int, int, int]:
    if s3 & 1:
        s1 ^= 0x8F7011EE
        s2 ^= 0xFC78FF1F
    
    y = s3
    x = s2 ^ (y << 10) & 0xffffffff
    s2 = s1
    s1 = s0
    
    y ^= x
    y ^= y >> 1
    y ^= y >> 2
    y ^= y >> 4
    y ^= y >> 8
    y ^= y >> 16

    x ^= x << 1
    x ^= x << 2
    x ^= x << 4
    x ^= x << 8
    x ^= x << 16
    x &= 0xffffffff
    
    s3 = y
    s0 ^= x ^ s2

    if tinymt_equation(s0, s1, s2, s3) != 0:
        s0 ^= 0x80000000
    
    return (s0, s1, s2, s3)

def tinymt_reversed_init_loop(s0: int, s1: int, s2: int, s3: int) -> tuple[int, int, int, int]:
    s3 ^= (0x6C078965 * (s2 ^ (s2 >> 30)) + 7) & 0xffffffff
    s2 ^= (0x6C078965 * (s1 ^ (s1 >> 30)) + 6) & 0xffffffff
    s1 ^= (0x6C078965 * (s0 ^ (s0 >> 30)) + 5) & 0xffffffff
    s0 ^= (0x6C078965 * (s3 ^ (s3 >> 30)) + 4) & 0xffffffff
    s3 ^= (0x6C078965 * (s2 ^ (s2 >> 30)) + 3) & 0xffffffff
    s2 ^= (0x6C078965 * (s1 ^ (s1 >> 30)) + 2) & 0xffffffff
    s1 ^= (0x6C078965 * (s0 ^ (s0 >> 30)) + 1) & 0xffffffff
    return (s0, s1, s2, s3)

def tinymt_recover_seed_from_state(s0: int, s1: int, s2: int, s3: int, max_advc: int = 10_000) -> int | None:
    for _ in range(8 + max_advc):
        s3_ = s3 ^ (0x6C078965 * (s2 ^ (s2 >> 30)) + 7) & 0xffffffff
        s2_ = s2 ^ (0x6C078965 * (s1 ^ (s1 >> 30)) + 6) & 0xffffffff
        s3_ ^= (0x6C078965 * (s2_ ^ (s2_ >> 30)) + 3) & 0xffffffff

        if s3_ == 0x3793FDFF:
            s0_, s1_, s2_, _ = tinymt_reversed_init_loop(s0, s1, s2, s3)
            if s1_ == 0x8F7011EE and s2_ == 0xFC78FF1F:
                return s0_
            # s3_ persists in both cases
            s0_, s1_, s2_, _ = tinymt_reversed_init_loop(s0 ^ 0x80000000, s1, s2, s3)
            if s1_ == 0x8F7011EE and s2_ == 0xFC78FF1F:
                return s0_
        
        s0, s1, s2, s3 = tinymt_prev(s0, s1, s2, s3)
    
    return None

def tinymt_recover_state_from_127_lsb_sequence(bits: Sequence[int]) -> tuple[int, int, int, int]:
    """Recovers the internal state of a TinyMT instance thanks to the least significant bit of 127 consecutive outputs."""
    if len(bits) != 127:
        raise ValueError("127 bits are needed to run the algorithm.")
    
    s0 = s1 = s2 = s3 = 0
    for i in range(127):
        if bits[i] == 1:
            s0 ^= TINYMT_127_LSB_INV_X_ADVC_124[i][0]
            s1 ^= TINYMT_127_LSB_INV_X_ADVC_124[i][1]
            s2 ^= TINYMT_127_LSB_INV_X_ADVC_124[i][2]
            s3 ^= TINYMT_127_LSB_INV_X_ADVC_124[i][3]
    
    return (s0, s1, s2, s3)

# TINYMT^124 * TINYMT_127_LSB_INV
TINYMT_127_LSB_INV_X_ADVC_124 = (
    (0x5bad2a66, 0x680d9666, 0x78978f33, 0x48fc5d16), (0x90acdb77, 0x33a0bc00, 0x109a1955, 0xc916aed0),
    (0xe5135044, 0x90acdb77, 0x33a0bc00, 0xfddaa506), (0x42ac1733, 0xe5135044, 0x90acdb77, 0xc74bfe04),
    (0xb28cfe5a, 0x42ac1733, 0xe5135044, 0x5015d9a2), (0x61f3a155, 0xb28cfe5a, 0x42ac1733, 0xbc400144),
    (0x494a8878, 0x09fe3733, 0xca1b7169, 0xe3b2594c), (0x419e806c, 0x494a8878, 0x09fe3733, 0xbf77efc6),
    (0xc514ed05, 0x419e806c, 0x494a8878, 0x4e2480a6), (0x69e0b727, 0xad197b63, 0x39090f5f, 0xaeb4bd82),
    (0x62533171, 0x69e0b727, 0xad197b63, 0x798d2c96), (0x27784d11, 0x0a5ea717, 0x11773814, 0xf73857b0),
    (0xa693686c, 0x4f75db77, 0x72c92824, 0x4d1d682e), (0xcf6ce961, 0xce9efe0a, 0x37e25444, 0x3b5b0d1a),
    (0xb7400357, 0xcf6ce961, 0xce9efe0a, 0x40f62194), (0x2e765a56, 0xdf4d9531, 0xb7fb6652, 0x2c48a802),
    (0x7df2eaa9, 0x2e765a56, 0xdf4d9531, 0xd1e28460), (0x3b1d9676, 0x15ff7ccf, 0x56e1d565, 0xb028bc88),
    (0xfd13b99a, 0x3b1d9676, 0x15ff7ccf, 0x782d8eb6), (0x031f99cf, 0x951e2ffc, 0x438a1945, 0xda4c6eb8),
    (0x1c433496, 0x6b120fa9, 0xed89a0cf, 0x8754b840), (0x4624711c, 0x744ea2f0, 0x1385809a, 0x672bb21c),
    (0x02fca9fc, 0x2e29e77a, 0x0cd92dc3, 0xdb47de12), (0x79e747a1, 0x6af13f9a, 0x56be6849, 0xc7b88f88),
    (0xff69bffc, 0x79e747a1, 0x6af13f9a, 0x5dd0857e), (0x612d452b, 0xff69bffc, 0x79e747a1, 0x59d87cb8),
    (0x69b79848, 0x612d452b, 0xff69bffc, 0x7e896dee), (0x9a820a51, 0x01ba0e2e, 0x19baca18, 0x8f66110a),
    (0xc03f7011, 0xf28f9c37, 0x792d811d, 0x43ecff0a), (0xf4ff8b2d, 0xc03f7011, 0xf28f9c37, 0xf1d6641a),
    (0x5235a8d1, 0xf4ff8b2d, 0xc03f7011, 0x6c8ee036), (0x540d9195, 0x3a383eb7, 0x8c68041e, 0xad222d2c),
    (0xb62ce94e, 0x3c0007f3, 0x42afb184, 0x86574cca), (0xa4f5b3a7, 0xde217f28, 0x449788c0, 0xa6713b62),
    (0xdeafe6a9, 0xccf825c1, 0xa6b6f01b, 0x730e702a), (0xe77a0b61, 0xdeafe6a9, 0xccf825c1, 0xb7afcfde),
    (0x1768d977, 0xe77a0b61, 0xdeafe6a9, 0x87b0e3ea), (0x04f2e871, 0x1768d977, 0xe77a0b61, 0xece0c982),
    (0xebfce5bf, 0x6cff7e17, 0x6fff5644, 0xb82b2e54), (0x626cb3f2, 0x83f173d9, 0x1468f124, 0x1ab592f6),
    (0x5f832737, 0x626cb3f2, 0x83f173d9, 0x90e4d29c), (0x32796a72, 0x5f832737, 0x626cb3f2, 0xff956186),
    (0xff5c2beb, 0x32796a72, 0x5f832737, 0x8faa8c58), (0xe1b48374, 0xff5c2beb, 0x32796a72, 0x53ef724a),
    (0x3fd5bcd7, 0x89b91512, 0x87cba4d8, 0xdf6982c6), (0x56d33d8d, 0x3fd5bcd7, 0x89b91512, 0xab31d414),
    (0x08f36832, 0x3edeabeb, 0x474233e4, 0xf1934312), (0xb017ea85, 0x08f36832, 0x3edeabeb, 0xad69d0a4),
    (0x306f6bee, 0xb017ea85, 0x08f36832, 0x27594d8a), (0x5b3bbe85, 0x306f6bee, 0xb017ea85, 0x7317f6d0),
    (0x6a42668e, 0x333628e3, 0x48f8e4dd, 0xa06e3570), (0x52c27840, 0x024ff0e8, 0x4ba1a7d0, 0x2881bc20),
    (0xebbd6a18, 0x52c27840, 0x024ff0e8, 0x469f12a0), (0xec83c200, 0xebbd6a18, 0x52c27840, 0x2f13bc70),
    (0xd77d15be, 0x848e5466, 0x932ae52b, 0x6ac3a536), (0xfccb80a7, 0xbf7083d8, 0xfc19db55, 0xed554d00),
    (0xff0d602a, 0x94c616c1, 0xc7e70ceb, 0x30acb970), (0xc73532b2, 0xff0d602a, 0x94c616c1, 0x79345912),
    (0x5f0b4d41, 0xaf38a4d4, 0x879aef19, 0x60185874), (0x89c82904, 0x3706db27, 0xd7af2be7, 0xb3be18a0),
    (0xdb8a6b7e, 0x89c82904, 0x3706db27, 0xe85d227a), (0x6cc75367, 0xdb8a6b7e, 0x89c82904, 0xcd63e196),
    (0x4a88e8e5, 0x6cc75367, 0xdb8a6b7e, 0x8dc91f1c), (0xa8b098ce, 0x22857e83, 0x1450dc54, 0x14d65aaa),
    (0x4edc3581, 0xa8b098ce, 0x22857e83, 0x6eb7cb54), (0x16a662a8, 0x26d1a3e7, 0xd02717fd, 0xaae91b8c),
    (0x1c4f23e4, 0x16a662a8, 0x26d1a3e7, 0x94c0285e), (0xcc942277, 0x7442b582, 0x6e31ed9b, 0x94230038),
    (0x1939937c, 0xcc942277, 0x7442b582, 0x5be3f6c2), (0xfcdada75, 0x1939937c, 0xcc942277, 0xc0538d80),
    (0xbfd07d42, 0x94d74c13, 0x61ae1c4f, 0x345d684c), (0x27022a94, 0xbfd07d42, 0x94d74c13, 0x3f9c7802),
    (0xe06dbe41, 0x4f0fbcf2, 0xc747f271, 0xdbce7508), (0x5ebe66fa, 0x88602827, 0x379833c1, 0x716a98b8),
    (0x06252a04, 0x36b3f09c, 0xf0f7a714, 0xffe3d0b8), (0xc1a8cdf2, 0x6e28bc62, 0x4e247faf, 0xb76747de),
    (0x453ba693, 0xa9a55b94, 0x16bf3351, 0x0f6bdd48), (0xa075d9ae, 0x2d3630f5, 0xd132d4a7, 0x93c2d6f8),
    (0xe0c9d0a0, 0xc8784fc8, 0x55a1bfc6, 0x39cee17c), (0x56ff704c, 0x88c446c6, 0xb0efc0fb, 0x2db0963a),
    (0x5404fb45, 0x3ef2e62a, 0xf053c9f5, 0x22f97668), (0x66703a3c, 0x5404fb45, 0x3ef2e62a, 0x25a21516),
    (0x04447ef9, 0x0e7dac5a, 0x2c937476, 0xaafb6f3e), (0x11718317, 0x6c49e89f, 0x76ea2369, 0x059b1f66),
    (0xf4b502af, 0x11718317, 0x6c49e89f, 0x15f7380a), (0xf5a3c1cd, 0xf4b502af, 0x11718317, 0xc66b50e6),
    (0xeaf8ca6f, 0xf5a3c1cd, 0xf4b502af, 0x53918d5e), (0x2a89f7a1, 0x82f55c09, 0x8d344efe, 0xf6e2f848),
    (0x8e62a464, 0x428461c7, 0xfa62d33a, 0xe8d94632), (0x4630ccb5, 0x8e62a464, 0x428461c7, 0x5ac269f0),
    (0x551e220a, 0x2e3d5ad3, 0xf6f52b57, 0x5642d2cc), (0x741ba472, 0x3d13b46c, 0x56aad5e0, 0x85ab2c04),
    (0x1f01acbe, 0x741ba472, 0x3d13b46c, 0x55214eb8), (0xd8afee8e, 0x770c3ad8, 0x0c8c2b41, 0xfef3b18e),
    (0x4a370f0f, 0xb0a278e8, 0x0f9bb5eb, 0x602d619c), (0x37331ed8, 0x223a9969, 0xc835f7db, 0xdb23654c),
    (0x29963af8, 0x37331ed8, 0x223a9969, 0xeb02c31a), (0xdde5a161, 0x419bac9e, 0x4fa491eb, 0xcb247eb4),
    (0xa9b432a6, 0xdde5a161, 0x419bac9e, 0x19ac2a6a), (0x24bf904d, 0xa9b432a6, 0xdde5a161, 0xb0ebcb58),
    (0x5cb3e234, 0x24bf904d, 0xa9b432a6, 0x83c20c2e), (0xc322de7d, 0x34be7452, 0x5c281f7e, 0x748759e6),
    (0xb759d705, 0xc322de7d, 0x34be7452, 0x268f6b10), (0xf3751ab6, 0xb759d705, 0xc322de7d, 0x35166a7c),
    (0xb255d798, 0xf3751ab6, 0xb759d705, 0xcae987fe), (0xce1d282d, 0xb255d798, 0xf3751ab6, 0x92cacf52),
    (0xb470ce27, 0xce1d282d, 0xb255d798, 0x730316b8), (0x1068f482, 0xb470ce27, 0xce1d282d, 0x89f7c1c0),
    (0xd4ee22be, 0x1068f482, 0xb470ce27, 0xef494eb6), (0xcbbf2421, 0xd4ee22be, 0x1068f482, 0x54026f1e),
    (0xcc4fa887, 0xa3b2b247, 0xac79ad8d, 0x3e671ffe), (0x7fff29bb, 0xcc4fa887, 0xa3b2b247, 0x0bbe73a2),
    (0xfa649701, 0x7fff29bb, 0xcc4fa887, 0x617c7146), (0xb54f04a1, 0x92690167, 0x0768a688, 0x2058dc68),
    (0x04d107be, 0xb54f04a1, 0x92690167, 0x787e9340), (0x698203c2, 0x04d107be, 0xb54f04a1, 0x1f931c3a),
    (0xe1eb7585, 0x018f95a4, 0x7c46888d, 0xf3cb0204), (0x2fa1685a, 0xe1eb7585, 0x018f95a4, 0xc2f9130e),
    (0xb6a65325, 0x47acfe3c, 0x997cfab6, 0x72d089da), (0xc7c3dc8b, 0xb6a65325, 0x47acfe3c, 0xcef21248),
    (0x8bc6c5ba, 0xc7c3dc8b, 0xb6a65325, 0x7e1a8858), (0x0787f7d2, 0x8bc6c5ba, 0xc7c3dc8b, 0xc316d256),
    (0x07c74e11, 0x0787f7d2, 0x8bc6c5ba, 0x6ae86496), (0x4221e733, 0x6fcad877, 0x7f1078e1, 0x37d4f321),
    (0xc955fa66, 0x2a2c7155, 0x982d46aa, 0xf2a3027c), (0x109a1955, 0xc955fa66, 0x2a2c7155, 0xbb052764),
    (0x680d9666, 0x78978f33, 0xb1c27555, 0xb1db26c8)
)

if __name__ == "__main__":
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from RNG import TinyMT

    from random import getrandbits, randrange
    
    def test_tinymt_recover_seed_from_state(n: int = 1_000):
        rng = TinyMT(0)
        
        for _ in range(n):
            seed = getrandbits(32)
            advc = randrange(0, 10_000)

            rng.reseed(seed)
            rng.jump(advc)

            seed_ = tinymt_recover_seed_from_state(*rng.state)
            assert seed == seed_, f"{seed = }, {seed_ = }, {advc = }"

    def test_tinymt_recover_state_from_127_lsb_sequence(n: int = 10_000):
        rng = TinyMT(0)
        bits = [0] * 127

        for _ in range(n):
            rng.restate(getrandbits(32), getrandbits(32), getrandbits(32), getrandbits(32))
            rng.jump(getrandbits(10))
            
            # https://github.com/wwwwwwzx/3DSRNGTool/blob/022e7352fd6096a6cb92d1c3d22877915563fe42/3DSRNGTool/Gen7/Egg7.cs#L22-L30
            for i in range(127): 
                # save, then accept the egg to hatch it
                rng.twist() # gender
                rng.twist() # nature
                bits[i] = rng.next_u32() & 1 # parent nature if both of them are holding the everstone (0 for male, 1 for female)
                rng.reverse(3) # soft reset
                if i != 126:
                    rng.twist() # discard the egg (not necessary for the last one)
            
            state = rng.state

            state_ = tinymt_recover_state_from_127_lsb_sequence(bits)
            assert state == state_, f"{state = }, {state_ = }"
    

    #test_tinymt_recover_seed_from_state()
    
    #test_tinymt_recover_state_from_127_lsb_sequence()