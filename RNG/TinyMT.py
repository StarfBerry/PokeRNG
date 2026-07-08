# Tiny Mersenne Twister

from typing import Sequence

class TinyMT:        
    def __init__(self, init: int | Sequence[int]):      
        if isinstance(init, int):
            self.reseed(init)
        else:
            self.state = init

    @property
    def state(self) -> tuple[int, int, int, int]:
        return (self.s0, self.s1, self.s2, self.s3)

    @state.setter
    def state(self, seq: Sequence[int]):
        self.restate(seq[0], seq[1], seq[2], seq[3])

    def period_certification(self):
        if self.s1 == 0 and self.s2 == 0 and self.s3 == 0 and (self.s0 & 0x7fffffff) == 0:
            self.s0 = ord('T') # 84
            self.s1 = ord('I') # 73
            self.s2 = ord('N') # 78
            self.s3 = ord('Y') # 89

    def reseed(self, seed: int):
        s0, s1, s2, s3 = seed & 0xffffffff, 0x8F7011EE, 0xFC78FF1F, 0x3793FDFF
        
        s1 ^= (0x6C078965 * (s0 ^ (s0 >> 30)) + 1) & 0xffffffff
        s2 ^= (0x6C078965 * (s1 ^ (s1 >> 30)) + 2) & 0xffffffff
        s3 ^= (0x6C078965 * (s2 ^ (s2 >> 30)) + 3) & 0xffffffff
        s0 ^= (0x6C078965 * (s3 ^ (s3 >> 30)) + 4) & 0xffffffff
        s1 ^= (0x6C078965 * (s0 ^ (s0 >> 30)) + 5) & 0xffffffff
        s2 ^= (0x6C078965 * (s1 ^ (s1 >> 30)) + 6) & 0xffffffff
        s3 ^= (0x6C078965 * (s2 ^ (s2 >> 30)) + 7) & 0xffffffff

        self.s0 = s0
        self.s1 = s1
        self.s2 = s2
        self.s3 = s3

        self.advance(8)

    def restate(self, s0: int, s1: int, s2: int, s3: int):        
        self.s0 = s0 & 0xffffffff
        self.s1 = s1 & 0xffffffff
        self.s2 = s2 & 0xffffffff
        self.s3 = s3 & 0xffffffff
        
        self.period_certification()

    def twist(self):
        x = (self.s0 & 0x7fffffff) ^ self.s1 ^ self.s2
        y = self.s3

        x ^= (x << 1) & 0xffffffff
        y ^= (y >> 1) ^ x

        self.s0 = self.s1
        self.s1 = self.s2
        self.s2 = x ^ (y << 10) & 0xffffffff
        self.s3 = y

        if y & 1:
            self.s1 ^= 0x8F7011EE
            self.s2 ^= 0xFC78FF1F
    
    def untwist(self):
        """
        Technically the TinyMT next state function is not bijective so it doesn't have an inverse.
        
        However, the current state reveals 127 bits of the previous state.
        
        Then we can recover the last bit by checking if the obtained state/vector lives in the TinyMT's vector space thanks to it's equation.
        """
        if self.s3 & 1:
            self.s1 ^= 0x8F7011EE
            self.s2 ^= 0xFC78FF1F
        
        y = self.s3
        x = self.s2 ^ (y << 10) & 0xffffffff
        self.s2 = self.s1
        self.s1 = self.s0
        
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
        
        self.s3 = y
        self.s0 ^= x ^ self.s2

        # Evaluation of the equation
        eq = (self.s0 >> 31) ^ (self.s1 >> 31) ^ self.s2.bit_count() ^ (self.s3 & 0x3fffff).bit_count()
        if (eq & 1) != 0: 
            self.s0 ^= 0x80000000

    def next_u32(self) -> int:
        self.twist()
        
        # temper
        t = (self.s0 + (self.s2 >> 8)) & 0xffffffff
        if t & 1: 
            t ^= 0x3793FDFF
        t ^= self.s3
        
        return t
    
    def next_u16(self) -> int:
        return self.next_u32() >> 16

    def rand(self, maximum: int) -> int:
        return self.next_u32() % maximum

    def advance(self, n: int):
        for _ in range(n): 
            self.twist()
    
    def reverse(self, n: int):
        for _ in range(n): 
            self.untwist()

    def jump_2_pow(self, n: int):
        s0 = s1 = s2 = s3 = 0
        poly = TINYMT_JUMP_TABLE[n]
        
        while poly:
            if poly & 1:
                s0 ^= self.s0
                s1 ^= self.s1
                s2 ^= self.s2
                s3 ^= self.s3
            
            self.twist()
            poly >>= 1
        
        self.s0 = s0
        self.s1 = s1
        self.s2 = s2
        self.s3 = s3

    def jump(self, n: int):
        self.advance(n & 0x7f)
        n >>= 7
        
        while n:
            i = n.bit_length() - 1
            self.jump_2_pow(i + 7)
            n ^= 1 << i # skip zeros (at the cost of calling the bit_length method on n)     

TINYMT_JUMP_TABLE = (
    0x00000000000000000000000000000002, 0x00000000000000000000000000000004, 0x00000000000000000000000000000010,
    0x00000000000000000000000000000100, 0x00000000000000000000000000010000, 0x00000000000000000000000100000000,
    0x00000000000000010000000000000000, 0x68f6c067369601df9654f148a90fcec5, 0x3acf552103dbbf73b9e15caa5f8d586b,
    0x2528779341278769149df0a3ce8a313d, 0x5ab81fcd13ccd9face6673b3d158340e, 0x3f8285b29763f1a084c1c823c273e23b,
    0x2e1bd6473d09382661def4964ec4ab34, 0x33ae14e5d2005a71334a0fe77ab182de, 0x0e06f5b1e69f0174ba589ce43d24301d,
    0x0586e1d6b2670a7586bf0979d37c9a1e, 0x55d7db08d9d6e5756f1cde00c5428bd5, 0x457372c828f3237055bf4c862403495b,
    0x7d9a80f7f39cdc7fa37711f1e4e489c5, 0x7c5c99ea483c815a9f1173b680f6752e, 0x658cd2f421d18c0441fbd20233bcb628,
    0x694898799783db46c8fc1f0f485cc220, 0x4cf6c5ecc4826e0b8e695f0109724eb6, 0x2a5eaf3a194065dcf9b4e14b65c67175,
    0x475fa9dca8a63e5af2272003ed156055, 0x73ab53c0e246197f97191167e296db49, 0x20999170716ca869203777ca7d356342,
    0x5dcb2d78b3e9ca0f7222f0529a9dd99c, 0x197365ac9569a8b46dd7a644730f081a, 0x2a472d665ef39ef40d7382718dc46f8f,
    0x74284a9019b6eae3afb1a319fcfd8eb7, 0x40afea91e9ad4b2c58440d15ded1d336, 0x67d91ea8c53eb5a1f87cccc392bd556e,
    0x32899ff17c82cca266da0ddd8a6ab35b, 0x60817118082207809d84e21d927f8f48, 0x2ba689378afc5b5157553151ed65f671,
    0x12e70cff669915f0e53b60ce75bd230c, 0x55f7abc7dca69d74ddf5dcc069db2e2e, 0x4d082e8ac46696ccc3fc01335d682176,
    0x11c01e9679393de79a81b519a7cb9050, 0x27fe8d1669eb10ea0b661e7654fb35a1, 0x1d597217142ac79ea9a13e6e73e761a6,
    0x5b6229941228fc6e5a2576505a6bd7dd, 0x42adc5aedc1d18665bdb713316367017, 0x2861c3fbe4982720f5b4a955cd12c153,
    0x5ed41176ec24672844d77a12767f778f, 0x4559986d0c4932034704825523a9354a, 0x402b157281a72980494823eab3fbcddc,
    0x6a7793cf7073bdb7c3540b6e8bf2ab05, 0x54a4aae7d6f6f001a8c65c22f0085ea7, 0x657870d1fe0dd87af86bfe0c89d9d0bf,
    0x423ce92766769e782dab2d073cf7f89f, 0x131e3edb0796ae4763cb26b386c95300, 0x70dd28106965b38c60d66b8e0ec97d83,
    0x4e1503a664debe8fae907bfd7708a50c, 0x38b88e42bf48f09ecbddd8075fa90ef8, 0x69db9e9884d0a8b9dcac71ffe6f67703,
    0x61c24a107b47d766f9ddcb041c1ad24f, 0x4b120444b51244bd565815895669c209, 0x3c6bdb6806f70b3fb3513731378d6ce3,
    0x0d6699df0daca7b0901f1b149a4cd24b, 0x065519f7385f8a91a3411e55ffbb8329, 0x61cc2f72a4a5de4a17562f6829466695,
    0x44186151523f6b1c506c454292eb44e3, 0x0c1118b8caf7a3e7b9af8e9bc86806e9, 0x53c7bf9374228b0185930921a6001b74,
    0x4d17039cb927e1094118ba45757bff06, 0x50613fbdc8a5fba171b29f52573fa9c7, 0x17e538a5a8007fbb919a5a2ddbfd60dd,
    0x4a4fbc21e46f396985397bafe4f9cba2, 0x27ed464113f0af2ee773322fc53cd3dc, 0x21038341ce7a3322386c38ed64340258,
    0x3797cf6f14f9a2a1bdc284131cbfd49d, 0x3de86881cd4aae323b6bdb6df7e2f5fe, 0x35d662333b14448867cbdc2f03431360,
    0x0378fda14e626a328ae82f34880853c5, 0x345eca5e89cd0eec79500b1fd1ad6427, 0x18bfe435de7d3cc24afcf10a029129e5,
    0x7958e7f96303e82ff036c0a953c3102a, 0x4669e0fb176b212b5ebb6693c3fae610, 0x6a2eaee5590d7af04ac65910189f7db4,
    0x74cc70546b5753ab8d4d69a77aa67982, 0x4f5b988ac13bd6db70606bd8082b49e3, 0x69b5b0a7ab07b34023a88ae3cd693c2b,
    0x2555a7147faae588d9f5d1467766cf9e, 0x723a30d4a3519a6ca70c32ef9f5430bb, 0x666f76384a5bf3d243b1ca60cdf6d95e,
    0x4f230f99f94ac04220b6cbd308cd848d, 0x248f00f3f6001b256fdd7e547d34e020, 0x13eb91b21d59f96034a265f480cd0317,
    0x6cca9a7dc29be988f1a9616f62232c9d, 0x2b99d41a053f1b54aa53683b1b805b65, 0x791e369c5543c473dd72211bf31657a8,
    0x3cb2278054aaf5d6a623f5dc36d1aaa2, 0x12673d2d555e927c4101d6c2964005f6, 0x435d3ae226b732353e5e20736e33626d,
    0x0bad719ca5746382808aa43b6a459a4e, 0x13c4dacf957d524da1a049931a695794, 0x784cf616ada5e3b564c4ef17422ad818,
    0x77eac726266f59f9ddeb6e2e2ccc94a9, 0x48e2328d912c88e9b61883228afd82e5, 0x446d5ce91994ce74d0e2fc227be175e4,
    0x49e19684b6679463f2bc0f6dd142d9cf, 0x63e5a4d01066b91e1389f2eb1de8ff2d, 0x37848a1511a3424ef2cea66a1fcd0a49,
    0x24e5fdbe3ee9e29606fcc14fb7670b13, 0x68b8272bb1e8dd7e92049d350e47acb0, 0x1de6058c35791cf7360aa7b535aa7c00,
    0x07162a2c87198bdf419f2b1e01fd501d, 0x7f15d38822a4517cf975bcddec8f3fc9, 0x11b0f9ba277f1f7b8f87ca3d566b1289,
    0x7bfa816e57ef216ba75501dc84ae8b3b, 0x75d96f85c8050cb96af7af0d2340b003, 0x72a6146d20d27ef4c0f00467c5bf7721,
    0x3f00cdc5b57d07650a01dd22ea44ad88, 0x144c81b476ca3c3b8399cb43aea8b2a6, 0x1544ead8acb2f89d1ad3f402fefa6c27,
    0x26c3a79369e2d08a098c7abca4ffee70, 0x07d8d09a0a099666fc3af9fd81ad568b, 0x5cf1603cb8e824e19a19be32a0b924f4,
    0x2fe78c730dd95cc7dda46b57fa4f80a1, 0x2291a47598026638f85b3c7c3140d333, 0x535114a9bebf6c83dc20822579584b67,
    0x1736e38c749711b2691f0ea2fa6435ef, 0x2c757add73cabe4a686d548ac27641c4, 0x3ffa7ea8a69a600223205a747f78213d,
    0x7621d50d52c16ca9ec42d129dc8927e4
)