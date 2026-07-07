# Xoroshiro128+ (+ splitmix seeding variant)

from typing import Sequence

def rotl(n: int, k: int) -> int:
    return ((n << k) | (n >> (64 - k))) & 0xffffffffffffffff

def splitmix(seed: int) -> int:
    seed &= 0xffffffffffffffff
    seed = (0xBF58476D1CE4E5B9 * (seed ^ (seed >> 30))) & 0xffffffffffffffff
    seed = (0x94D049BB133111EB * (seed ^ (seed >> 27))) & 0xffffffffffffffff
    return seed ^ (seed >> 31)

XOROSHIRO_S1_CONST = 0x82A2B175229D6A5B

class Xoroshiro128Plus:    
    def __init__(self, s0: int, s1: int = XOROSHIRO_S1_CONST):       
        self.restate(s0, s1)
    
    @property
    def state(self) -> tuple[int, int]:
        return (self.s0, self.s1)
    
    @state.setter
    def state(self, seq: Sequence[int]):
        self.restate(seq[0], seq[1])

    def reseed(self, seed: int):
        self.s0 = seed & 0xffffffffffffffff
        self.s1 = XOROSHIRO_S1_CONST
    
    def restate(self, s0: int, s1: int):
        self.s0 = s0 & 0xffffffffffffffff
        self.s1 = s1 & 0xffffffffffffffff

    def next_state(self):
        self.s1 ^= self.s0
        self.s0 = rotl(self.s0, 24) ^ self.s1 ^ (self.s1 << 16) & 0xffffffffffffffff
        self.s1 = rotl(self.s1, 37)

    def prev_state(self):
        self.s1 = rotl(self.s1, 27)
        self.s0 = rotl(self.s0 ^ self.s1 ^ (self.s1 << 16) & 0xffffffffffffffff, 40)
        self.s1 ^= self.s0

    def next_u64(self) -> int:
        out = (self.s0 + self.s1) & 0xffffffffffffffff
        self.next_state()        
        return out
    
    def next_u32(self) -> int:
        return self.next_u64() & 0xffffffff

    def rand(self, maximum: int) -> int:
        mask = (1 << (maximum - 1).bit_length()) - 1
        while 1:
            rnd = self.next_u64() & mask
            if rnd < maximum:
                return rnd

    def advance(self, n: int):
        for _ in range(n):
            self.next_state()
    
    def reverse(self, n: int):
        for _ in range(n):
            self.prev_state()

    def jump_2_pow(self, n: int):
        s0 = s1 = 0
        poly = XOROSHIRO_JUMP_TABLE[n]
        
        while poly:
            if poly & 1:
                s0 ^= self.s0
                s1 ^= self.s1
            
            self.next_state()
            poly >>= 1
        
        self.s0 = s0
        self.s1 = s1

    def jump(self, n: int):
        self.advance(n & 0x7f)
        n >>= 7
        
        while n:
            i = n.bit_length() - 1
            self.jump_2_pow(i + 7)
            n ^= 1 << i # skip zeros (at the cost of calling the bit_length method on n)

class XoroshiroBDSP(Xoroshiro128Plus):
    def __init__(self, s0: int, s1: int | None = None):
        if s1 is None:
            self.reseed(s0)
        else:
            self.restate(s0, s1)

    def reseed(self, seed: int):
        self.s0 = splitmix(seed + 0x9E3779B97F4A7C15)
        self.s1 = splitmix(seed + 0x3C6EF372FE94F82A)

    def next_u32(self) -> int:
        return self.next_u64() >> 32
 
    def rand(self, maximum: int) -> int:
        return self.next_u32() % maximum

XOROSHIRO_JUMP_TABLE = (
    0x00000000000000000000000000000002, 0x00000000000000000000000000000004, 0x00000000000000000000000000000010,
    0x00000000000000000000000000000100, 0x00000000000000000000000000010000, 0x00000000000000000000000100000000,
    0x00000000000000010000000000000000, 0x0008828e513b43d5095b8f76579aa001, 0x7a8ff5b1c465a931162ad6ec01b26eae,
    0xb18b0d36cd81a8f5b4fbaa5c54ee8b8f, 0x23ac5e0ba1cecb291207a1706bebb202, 0xbb18e9c8d463bb1b2c88ef71166bc53d,
    0xe3fbe606ef4e8e09c3865bb154e9be10, 0x28faaaebb31ee2db1a9fc99fa7818274, 0x30a7c4eef203c7eb588abd4c2ce2ba80,
    0xa425003f3220a91d9c90debc053e8cef, 0x81e1dd96586cf985b82ca99a09a4e71e, 0x4f7fd3dfbb820bfb35d69e118698a31d,
    0xfee2760ef3a900b349613606c466efd3, 0xf0df0531f434c57dbd031d011900a9e5, 0x442576715266740c235e761b3b378590,
    0x1e8bae8f680d2b353710a7ae7945df77, 0xfd7027fe6d2f676475d8e7dbceda609c, 0x28eff231ad438124de2cba60cd3332b5,
    0x1808760d0a0909a1377e64c4e80a06fa, 0xb9a362fafedfe9d20cf0a2225da7fb95, 0xf57881ab117349fd2bab58a3cadfc0a3,
    0x849272241425c9968d51ecdb9ed82455, 0xf1ccb8898cbc07cd521b29d0a57326c1, 0x61179e44214caafafbe65017abec72dd,
    0xd9aa6b1e93fbb6e46c446b9bc95c267b, 0x86e3772194563f6d64f80248d23655c6, 0xd4e95eef9edbdbc6fad843622b252c78,
    0x05667023c584a68a598742bbfddde630, 0x401aacf87a5e21ee3a9d7dce072134a6, 0xe114b1e65a950e43f0cc32eaf522f0e0,
    0x905dff85834fb8d1eb2beaa80d3fd8a7, 0xc449c069734817cb61f29536e1bb6b99, 0x1e5bc0fe7032f3df390cd235d35187da,
    0x3f399e6f1ea22dbc744e5f1168ba3345, 0xd47a02636f041cca8cc9aa88a153f5f8, 0xf83c06b106d3b7ab08d037056c80b9e0,
    0x14223eedae116a834ce3c123d196bf7a, 0x24bfd164204335aeb1b206870da4e89a, 0x4a5953c8f4bc2a51207bb2453717cf67,
    0xf6b3f196dc551ccfa14e342bb11ff7e6, 0x5b6233b76fa214d75422bca5015dd3b7, 0xf20d7136458bd924ede7341c00c65b85,
    0x9b19ba6b3752065ad769cfc9028deb78, 0x4f27796502238c48c7b0e531abe7e4bd, 0xb7b17dcd250033051c6d3ba4bb94182a,
    0xaaae579366147d073ae9471d0e2d0bcf, 0x0d56bb288c661ccf8f9cd3794ca46fbf, 0x0402342eedff424cdb2ad4e9c15a9d4e,
    0x4e71559e6d0e7f0079e061af5be21395, 0x8367af1c9d6c140696e7d88c0794e785, 0x0dbfcd2453d1d33fccdda809db64b3e7,
    0x3309e57f180d4ff66c64681c21cd0286, 0xb439f330ab3b9715acb8d4c6ba67113e, 0xc58f079d0205bcf3bad04ca5d96e2cd3,
    0x09417d8c80a37aa7ebfbc2723a906760, 0x52f51ac639e0971238ac01316167183d, 0xf37ead6ea53b96ba7a134006d4efa484,
    0xdc1c01799cb8d734351561e58f8572d4, 0x170865df4b3201fcdf900294d8f554a5, 0xb2a7b279a8cb1f502992ead4972eaed2,
    0xe7859c665be57882c026a7d9e04a7700, 0x4b4a7aa8c389701cb4cb6197dea2b1fe, 0xadb7753d55646eef0dcfc5b909e7df4d,
    0xc80926301806a352468431669864f789, 0xc05da051ec96af1d22b6c1736285fcc8, 0xf88f6bac8fd3044874c1daac8729d8bb,
    0x752b98d002c408f7847757c126b23e45, 0x1aa7bc96dbace1100f9eaa62d0c9e2a3, 0xc469b29353a4984b7475d71b98314377,
    0x4b6dd41bce3bb499bbb7d266d61c85ea, 0xe023777e70b3a2f8c419b3742570e16f, 0x131e94fb35203d802a71db3a3ce8b968,
    0x9240c95b1e7fa08b2897bb8961b4dce9, 0xb879fca0915f893ff0fc3553d7881d5f, 0x2adca86fbefe1366e754db3fbc7536bc,
    0x0a40a688d77855ba0a9e201adfe7baa9, 0x17771c905e0775a81d0d601e49c35837, 0x2cf775e419a607e09b031395aec7b584,
    0x93a7cf27dec9b30679ead2eeddf66699, 0x93615189fe85b7d5e1b9805c107679fc, 0x466421124b50fbfb2c3925dcd790e3d6,
    0x1cda7bd04e3bb94bdca9b0fa4e95600e, 0x5ec431d73bbfe49fefc7905e1cbb5ffb, 0x31a1f85fd532f302854414811d534483,
    0xed9b991c09177e2fadb9ba2958f30b6e, 0x38d9e87dffdfca7076f8fdf26b0d1cbb, 0xd8e9e7254052af4d51f21cddcebdb8c7,
    0x62769780d13fbc08a03f796efb295305, 0x66e5456c2eaedbff4f2083f6b19e628a, 0xace8d6ce8e3fba178b2be9cd79734bed,
    0xdddf9b1090aa7ac1d2a98b26625eee7b, 0x00d67dc46ad286954fff128094edd94c, 0xf9540570703e7cf3726438e9a1d3c6ea,
    0x066a9599766619b592cc6a0937c9d34e, 0xa4e540c7ac49aa1bc5730de058e1047f, 0xc2edfc1ab51c00ade408bbecda066551,
    0xf11753a4339e78c3c5477ea8821ce588, 0xbb42e906efb125403c6058e633063180, 0x4e86f36c495eeedbbec40e0518086e21,
    0xe8345a7c487fefd6465276434fd98954, 0x688b7628742214343adaea5cdfe12e3b, 0x833801923a05f253c9dffa95904e99b1,
    0x58a00d23a8086646a10c3fb0b18df787, 0xec69708d487dbfc4a4e41f760281c3d0, 0x47176f17de7ff0e9b8880fff0e41261c,
    0x4f40c533643920ea58ee3b30f542767e, 0x83fd48d6b962058415f2d25b60c5acd7, 0x0ce303c7d3aabbc8e448c83950a687ea,
    0x1746715df0dd8fe3a6ff7863c363cfd4, 0xc00185964caef8bb7e9d8517b195d9c9, 0xb6bde02bd004b14440ddb4daf3fbdda8,
    0xba43c63ec5a9f1877a794b820672a49b, 0x2467071b1d261621c1be31e7536236fb, 0x5a6fc0435f011daaf0eec34daea486fb,
    0xa5af34331c044d81f42c01a2a3815db4, 0xdb43b553cd16ea44df7964c343b312de, 0x432c2bbcd03e65f68454182464c29903,
    0xcdf56412d1e7ba6e7b6c0ecc6cb5adbb, 0xac13c8b2ff838036380b97764c9f7748, 0x71d208cc2e5c56e91868a9f5a4fd4d64,
    0xd1d08a01b73de005e89f5fe075d74a79, 0xa9495c12936ad0fd25aa87f3c2704c69
)