# Xorshift128

from typing import Sequence

class Xorshift128:
    def __init__(self, init: int | Sequence[int]):
        if isinstance(init, int):
            self.reseed(init)
        else:
            self.restate(init)
                                           
    @property
    def state(self) -> tuple[int, int, int, int]:
        return (self.s0, self.s1, self.s2, self.s3)
    
    def reseed(self, seed: int):
        self.s0 = seed & 0xffffffff
        self.s1 = (self.s0 * 0x6C078965 + 1) & 0xffffffff
        self.s2 = (self.s1 * 0x6C078965 + 1) & 0xffffffff
        self.s3 = (self.s2 * 0x6C078965 + 1) & 0xffffffff
    
    def restate(self, state: Sequence[int]):        
        self.s0 = state[0] & 0xffffffff
        self.s1 = state[1] & 0xffffffff
        self.s2 = state[2] & 0xffffffff
        self.s3 = state[3] & 0xffffffff
        
        assert self.s0 | self.s1 | self.s2 | self.s3

    def next_state(self):
        t = self.s0
        t ^= (t << 11) & 0xffffffff
        t ^= t >> 8
        t ^= self.s3 ^ (self.s3 >> 19) 
 
        self.s0 = self.s1
        self.s1 = self.s2
        self.s2 = self.s3
        self.s3 = t
    
    def prev_state(self):
        t = self.s3
        self.s3 = self.s2
        self.s2 = self.s1
        self.s1 = self.s0
        
        t ^= self.s3 ^ (self.s3 >> 19)
        t ^= t >> 8
        t ^= t >> 16
        t ^= t << 11
        t ^= t << 22
        self.s0 = t & 0xffffffff

    def next(self) -> int:
        self.next_state()
        return self.s3

    def next_u32(self) -> int:
        return (self.next() % 0xffffffff) ^ 0x80000000 # <==> ((self.next() % 0xffffffff) + 0x80000000) & 0xffffffff

    def rand(self, maximum: int) -> int:
        return self.next_u32() % maximum
    
    def rand_range(self, minimum: int, maximum: int) -> int:
        diff = (maximum - minimum) & 0xffffffff
        return minimum + (self.next() % diff)

    def advance(self, n: int):
        for _ in range(n):
            self.next_state()
    
    def reverse(self, n: int):
        for _ in range(n):
            self.prev_state()

    def jump_2_pow(self, n: int):
        s0 = s1 = s2 = s3 = 0
        poly = XORSHIFT_JUMP_TABLE[n]
        
        while poly:
            if poly & 1:
                s0 ^= self.s0
                s1 ^= self.s1
                s2 ^= self.s2
                s3 ^= self.s3

            self.next_state()
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

XORSHIFT_JUMP_TABLE = (
    0x00000000000000000000000000000002, 0x00000000000000000000000000000004, 0x00000000000000000000000000000010, 0x00000000000000000000000000000100,
    0x00000000000000000000000000010000, 0x00000000000000000000000100000000, 0x00000000000000010000000000000000, 0x000000010046d8b3f985d65ffd3c8001,
    0x956c89fbfa6b67e9a42ca9aeb1e10da6, 0xff7aa97c47ec17c71a0988e988f8a56e, 0x9dff33679bd01948fb6668ff443b16f0, 0xbd36a1d3e3b212da46a4759b1dc83ce2,
    0x6d2f354b8b0e3c0b9640bc4ca0cbaa6c, 0xecf6383dca4f108f947096c72b4d52fb, 0xe1054e817177890a0daf32f04ddca12e, 0x02ae1912115107c6b9fa05aab78641a5,
    0x59981d3df81649be382fa5aa95f950e3, 0x6644b35f0f8cee00dba31d29fc044fdb, 0xecff213c169fd4553ca16b953c338c19, 0xa9dfd9fb0a0949393ffdcb096a60ecbe,
    0x079d7462b16c479ffd6aef50f8c0b5fa, 0x03896736d707b6b69148889b8269b55d, 0xdea22e8899dbbeaa4c6ac659b91ef36a, 0xc1150ddd5ae7d32067ccf586cddb0649,
    0x5f0be91ac7e9c38133c8177d6b2cc0f0, 0x0cd15d2ba212e5734a5f78fc104e47b9, 0xab586674147dec3ed69063e6e8a0b936, 0x4bfd9d67ed3728667071114af22d34f5,
    0xdaf387cab4ef5c18686287302b5cd38c, 0xffaf82745790af3ebb7d371f547cca1e, 0x7b932849fe573afaeb96acd6c88829f9, 0x8cedf8dfe2d6e821b4fd2c6573bf7047,
    0xb067cc93d37390513532e5f33a883107, 0xfe1a817d36419baa9682c4c3023090e7, 0xafdcbf8b4555ed5fae6d35e0269db445, 0xcd0dc146540609a174a47ec949a2536b,
    0xf0bf2d2cdc59ebb01809f899e9e69f80, 0x6f82ddb5abc7d64d15f1121fefb4f4dc, 0xdc0b508281574220e6cba91144cbbbe6, 0xb04bed1cd5ba396ea2c0a5a1d95aeb31,
    0x862f99d765fcb394ccb635f89186d420, 0xdbb253dade5aae15a5b598875bfaef90, 0x14136de0a527d5f106f04c1d1f94aa7c, 0xb9acc1c3a2e84c2ec06b983cdc17108b,
    0x286c710524d0b048795d42886e61c7b7, 0x969493371d04723885658fa74f66ef2b, 0x228dc4710d53fbc84e89af13d636befb, 0x0cceb170a295da669d022830d50df99d,
    0xddc435583e0a2da1f88c1cf697e0579a, 0xb3360ec1cb3043da6ebd25b376ed1362, 0x665d04ad04e9dd37a6486f63ebcf8d60, 0xa9fdd1c73437fb2a11da01041533b855,
    0x12659e0e814a99258aece6b835a3a0f0, 0xbc2b6ecd67109d0974dd61db2cd1f179, 0x5596f764b9f024c6a3382fadbc64a64e, 0x2e619bbd5c61c40f36b3d3a34a3a51eb,
    0xad17c26ff61ddb9af9220668547d1fb2, 0x8768b12bd95d4a24ba45341289f8cf2d, 0xda050f7d87b5d735660b2988413894b1, 0x98d18bf7c6fc9c795577abce14157c23,
    0xba46c07ccbfa874b95ea3ab49a46f6dc, 0xb3f66a175d848e85449da58268dbbb93, 0x29cb68289069c270f973f85ebc0ee1be, 0xc5d522132349bf61ea3bcf8ee7deff39,
    0xd8cd644ef52e65c4821e534335aac71c, 0x06d992569a61a161d2c1ecef023e487b, 0x29c23f71037ecb6f04193a0c13b7ff17, 0xdd86dbb37c7393b34ab914f1cc67a971,
    0x4f8c624e45559be0d85688f4ea5f6513, 0x3682f88e03cd644a28e99d0cc6a2c63c, 0x1a7632f601a7630b27690a8fdb447239, 0x208e7b1a72bd44e68587b2073d9487b4,
    0x7b01deb53bfd70d1022e8de3f4d585a8, 0xe4b29364c9b2ec7ce3b7ddb95fa88846, 0x0f51758987ec6f749145059c01fc548d, 0x303c817cb27551df4ddb8ca5d40c20c2,
    0xe9f1697fda14ddd3e795d59d4d1343ef, 0xb9eeec6b433dc852b60b5d2becbbdfd3, 0x6bb3b410caaa66deeddc01a55c6caf41, 0xe44b795191c21cef6fd25c2fccc4c92c,
    0x9b306b19f81ce25cfe113b9aac588c17, 0xc5f9b7800be81e29539cee04b38fbefc, 0x1e5c87ef4abb97807e70aa88bcff3655, 0x76633cb7da0df635e2b030d25d458961,
    0x662921ba0ccad483bff754cec95d5ff3, 0xa56529b955637be63b1d7328eb3ef2e8, 0x631231baf441cfd7cade09b55bbc21e5, 0x8ea70bd1786fab7dffaa419d769cf298,
    0x810881ee0b2bcdbe22b7f6aedb26a041, 0x27e1d81b54e6b7edcde2b549d2a36b50, 0xf8f97377345656238fea4223882c8963, 0x1bc3e4e6ba6a1f16936349e37c20a404,
    0x6f01d7f36b187c991e5293c0880e89c7, 0xb60f1c3028a32ae4f1ddc55a8b46d420, 0x90e457646ae8c38d8e3cad40086d105e, 0xe85346eabf5120726f3ba07ac555249b,
    0x32e5cf7230ff27cbcf407dcc3fe5f618, 0x118012ef704b515f9c869a9ed1cdcdb5, 0xdc3ed9f394c1ef63317d4e063e956d2b, 0xc489c7f3a2d968b82cb2bd2156ec0d3c,
    0xa6de0f9aa3fa48365f740a6c803e5a4a, 0xb584748d4624bc113cf8318c8498f41c, 0x48b1a2a8f4eaf2b383829b068c970a74, 0xc4417e2ad0eaea052cbdc7f4c2ac7c91,
    0x0c675fb0976b1595c4c8bc1ed88650b7, 0x04dccd187067dd8990b8fcb34a1eeb79, 0xeedf835055e9742e482269daea523cf8, 0xac11bf4793485ec2728bd207baa40d16,
    0xeda4600d68f7e41e049b2e897cb3015b, 0xdfef2a85ce12c0228ffbe1c00fe85999, 0x4a46a25e3de228f560f71a4753ebbcf6, 0x6c54373e5a67f34f002d52f95fcf8d67,
    0xba57f82a1d29d4262e516844721503f0, 0x721db46e483c68027f8b0da24e87e946, 0x89b0625303c74f0b118c55636c7b0ba7, 0xbadd34856e872354e1998f3494b875bd,
    0x68c3afdd3ba4c42d850702ceecad8500, 0xf36fde34b48fbba426e4433aa692c9d5, 0x539fdc541bb3fc038bc1482ff3783bcc, 0xbb00fa4ebec0f6b538b5ffcc66884ae6,
    0xebcf83d233a66f96a46944f11f2b2fc8, 0xf7d46c3248fc046192a9db106cd5d704, 0x18c8c81b338708f78da3e03e43b215dd, 0xba28ba9cf175ea1c00e3e1a37ac657f6,
    0x3de53fa1e9b03cafd0a5f82f1e00df0b, 0xe112aed18898d49a7b4c0943015b33df, 0xd9e63ec817bf84e121702c522010c0e0, 0x4d59e5d1e22db1bfa86b1b09fe3fdbf4,
)