# Tiny Mersenne Twister

from typing import Sequence

class TinyMT:        
    def __init__(self, init: int | Sequence[int]):      
        if isinstance(init, int):
            self.reseed(init)
        else:
            self.restate(init)

    @property
    def state(self) -> tuple[int, int, int, int]:
        return (self.s0, self.s1, self.s2, self.s3)

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

        # Period certification is not necessary when seeded with a 32-bit integer.
        #self.period_certification()

        self.advance(8)

    def restate(self, state: Sequence[int]):        
        self.s0 = state[0] & 0xffffffff
        self.s1 = state[1] & 0xffffffff
        self.s2 = state[2] & 0xffffffff
        self.s3 = state[3] & 0xffffffff
        
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
        
        However the current state reveals 127 bits of the previous state.
        
        Then, we can recover the last bit by checking if the obtained state/vector lives in the TinyMT's vector space thanks to it's equation.
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

    def rand(self, maximum: int) -> int:
        return (self.next_u32() * maximum) >> 32

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
        
        i = 7
        while n:
            if n & 1:
                self.jump_2_pow(i)
            n >>= 1
            i += 1         

TINYMT_JUMP_TABLE = (
    0x00000000000000000000000000000002, 0x00000000000000000000000000000004, 0x00000000000000000000000000000010, 0x00000000000000000000000000000100,
    0x00000000000000000000000000010000, 0x00000000000000000000000100000000, 0x00000000000000010000000000000000, 0xb0a48045db1bfe951b98a18f31f57486,
    0xe29d1503ee564039342d0c6dc777e228, 0xfd7a37b1acaa78239951a06456708b7e, 0x5ab81fcd13ccd9face6673b3d158340e, 0xe7d0c5907aee0eea090d98e45a895878,
    0x2e1bd6473d09382661def4964ec4ab34, 0x33ae14e5d2005a71334a0fe77ab182de, 0xd654b5930b12fe3e3794cc23a5de8a5e, 0x0586e1d6b2670a7586bf0979d37c9a1e,
    0x8d859b2a345b1a3fe2d08ec75db83196, 0x9d2132eac57edc3ad8731c41bcf9f318, 0xa5c8c0d51e1123352ebb41367c1e3386, 0x7c5c99ea483c815a9f1173b680f6752e,
    0x658cd2f421d18c0441fbd20233bcb628, 0x694898799783db46c8fc1f0f485cc220, 0x4cf6c5ecc4826e0b8e695f0109724eb6, 0xf20cef18f4cd9a967478b18cfd3ccb36,
    0x9f0de9fe452bc1107feb70c475efda16, 0xabf913e20fcbe6351ad541a07a6c610a, 0x20999170716ca869203777ca7d356342, 0x5dcb2d78b3e9ca0f7222f0529a9dd99c,
    0x197365ac9569a8b46dd7a644730f081a, 0xf2156d44b37e61be80bfd2b6153ed5cc, 0xac7a0ab2f43b15a9227df3de640734f4, 0x40afea91e9ad4b2c58440d15ded1d336,
    0x67d91ea8c53eb5a1f87cccc392bd556e, 0xeadbdfd3910f33e8eb165d1a12900918, 0x60817118082207809d84e21d927f8f48, 0xf3f4c9156771a41bda996196759f4c32,
    0x12e70cff669915f0e53b60ce75bd230c, 0x55f7abc7dca69d74ddf5dcc069db2e2e, 0x4d082e8ac46696ccc3fc01335d682176, 0x11c01e9679393de79a81b519a7cb9050,
    0xffaccd348466efa086aa4eb1cc018fe2, 0x1d597217142ac79ea9a13e6e73e761a6, 0x833069b6ffa50324d7e92697c2916d9e, 0x9aff858c3190e72cd61721f48eccca54,
    0xf03383d90915d86a7878f99255e87b10, 0x8686515401a99862c91b2ad5ee85cdcc, 0x4559986d0c4932034704825523a9354a, 0x402b157281a72980494823eab3fbcddc,
    0xb225d3ed9dfe42fd4e985ba913081146, 0x8cf6eac53b7b0f4b250a0ce568f2e4e4, 0xbd2a30f31380273075a7aecb11236afc, 0x9a6ea9058bfb6132a0677dc0a40d42dc,
    0x131e3edb0796ae4763cb26b386c95300, 0xa88f683284e84cc6ed1a3b499633c7c0, 0x4e1503a664debe8fae907bfd7708a50c, 0x38b88e42bf48f09ecbddd8075fa90ef8,
    0xb189deba695d57f3516021387e0ccd40, 0xb9900a3296ca282c74119bc384e0680c, 0x93404466589fbbf7db94454ece93784a, 0xe4399b4aeb7af4753e9d67f6af77d6a0,
    0xd534d9fde02158fa1dd34bd302b66808, 0xde0759d5d5d275db2e8d4e926741396a, 0xb99e6f50492821009a9a7fafb1bcdcd6, 0x9c4a2173bfb29456dda015850a11fea0,
    0xd443589a277a5cad3463de5c5092bcaa, 0x53c7bf9374228b0185930921a6001b74, 0x4d17039cb927e1094118ba45757bff06, 0x88337f9f252804ebfc7ecf95cfc51384,
    0xcfb77887458d80f11c560aea4307da9e, 0x4a4fbc21e46f396985397bafe4f9cba2, 0x27ed464113f0af2ee773322fc53cd3dc, 0x21038341ce7a3322386c38ed64340258,
    0xefc58f4df9745deb300ed4d484456ede, 0x3de86881cd4aae323b6bdb6df7e2f5fe, 0x35d662333b14448867cbdc2f03431360, 0xdb2abd83a3ef957807247ff310f2e986,
    0xec0c8a7c6440f1a6f49c5bd84957de64, 0xc0eda41733f0c388c730a1cd9a6b93a6, 0x7958e7f96303e82ff036c0a953c3102a, 0x4669e0fb176b212b5ebb6693c3fae610,
    0x6a2eaee5590d7af04ac65910189f7db4, 0x74cc70546b5753ab8d4d69a77aa67982, 0x9709d8a82cb62991fdac3b1f90d1f3a0, 0xb1e7f085468a4c0aae64da2455938668,
    0x2555a7147faae588d9f5d1467766cf9e, 0xaa6870f64edc65262ac0622807ae8af8, 0x666f76384a5bf3d243b1ca60cdf6d95e, 0x97714fbb14c73f08ad7a9b1490373ece,
    0x248f00f3f6001b256fdd7e547d34e020, 0xcbb9d190f0d4062ab96e35331837b954, 0xb498da5f2f1616c27c6531a8fad996de, 0xf3cb9438e8b2e41e279f38fc837ae126,
    0x791e369c5543c473dd72211bf31657a8, 0x3cb2278054aaf5d6a623f5dc36d1aaa2, 0x12673d2d555e927c4101d6c2964005f6, 0x9b0f7ac0cb3acd7fb39270b4f6c9d82e,
    0x0bad719ca5746382808aa43b6a459a4e, 0x13c4dacf957d524da1a049931a695794, 0x784cf616ada5e3b564c4ef17422ad818, 0xafb88704cbe2a6b350273ee9b4362eea,
    0x90b072af7ca177a33bd4d3e5120738a6, 0x446d5ce91994ce74d0e2fc227be175e4, 0x91b3d6a65bea6b297f705faa49b8638c, 0xbbb7e4f2fdeb46549e45a22c8512456e,
    0xefd6ca37fc2ebd047f02f6ad8737b00a, 0xfcb7bd9cd3641ddc8b3091882f9db150, 0x68b8272bb1e8dd7e92049d350e47acb0, 0x1de6058c35791cf7360aa7b535aa7c00,
    0xdf446a0e6a947495cc537bd99907ea5e, 0xa74793aacf29ae3674b9ec1a7475858a, 0xc9e2b998caf2e031024b9aface91a8ca, 0xa3a8c14cba62de212a99511b1c543178,
    0xad8b2fa72588f3f3e73bffcabbba0a40, 0xaaf4544fcd5f81be4d3c54a05d45cd62, 0x3f00cdc5b57d07650a01dd22ea44ad88, 0x144c81b476ca3c3b8399cb43aea8b2a6,
    0xcd16aafa413f07d7971fa4c56600d664, 0x26c3a79369e2d08a098c7abca4ffee70, 0xdf8a90b8e784692c71f6a93a1957ecc8, 0x5cf1603cb8e824e19a19be32a0b924f4,
    0xf7b5cc51e054a38d50683b9062b53ae2, 0xfac3e457758f997275976cbba9ba6970, 0x8b03548b533293c951ecd2e2e1a2f124, 0xcf64a3ae991aeef8e4d35e65629e8fac,
    0x2c757add73cabe4a686d548ac27641c4, 0xe7a83e8a4b179f48aeec0ab3e7829b7e, 0x7621d50d52c16ca9ec42d129dc8927e4,
)