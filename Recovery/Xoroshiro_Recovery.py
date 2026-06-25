from typing import Iterator, Sequence

XOROSHIRO_CONST = 0x82A2B175229D6A5B

def xoroshiro_recover_seeds(first: int, second: int) -> Iterator[int]:
    """
    Recovers the seeds of a Xoroshiro128+ instance from two consecutive 32-bit outputs, assuming that s1 was initially equal to 0x82A2B175229D6A5B.

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
    Recovers the seeds of a Xoroshiro128+ instance from two 32-bit outputs with a skip in between, assuming that s1 was initially equal to 0x82A2B175229D6A5B.

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

def xoroshiro_recover_state_from_128_bits(bits: Sequence[int]) -> tuple[int, int]:
    """Recovers the internal state of a Xoroshiro128+ instance thanks to the least significant bit of 128 consecutive outputs."""
    if len(bits) != 128:
        raise ValueError("128 bits are needed to run the algorithm.")
    
    s0 = s1 = 0
    for i in range(128):
        if bits[i] == 1:
            s0 ^= XOROSHIRO_128_LSB_INV[i][0]
            s1 ^= XOROSHIRO_128_LSB_INV[i][1]
    
    return (s0, s1)

XOROSHIRO_128_LSB_INV = (
    (0x03ac280f24470247, 0xee877b8ab9aaf07c), (0xef399b01e298f8f8, 0xbaf4cc8205ecc324), 
    (0x2b5e9c990fd8cf61, 0x3b71fa802a0f6905), (0xd740b55146ce0aa9, 0xd610ce196f15857d), 
    (0x0e8cd9b013f7ca2e, 0xc5f4759bfd474c5e), (0x746982eb0415fd46, 0xab83b889f23a5eea), 
    (0x8de082e90f05404c, 0xc271501e5a595d88), (0x96caccb5de0e16c3, 0x64180659981d9c43), 
    (0x1cd6f1b6e83b7705, 0xd0161d54f31bb737), (0x51c7ef66f7928fe6, 0xf65f32df49123f0c), 
    (0xb676703a77192c69, 0x4c3ee1c210abd5ff), (0x76db67f85cd4f47a, 0x665e3957a6b50374), 
    (0x2c05b063f56cd10e, 0x91301878565e20c4), (0x25fde5109522ee16, 0x0a6447932c469cee), 
    (0x4dcc2a8878a1a4c7, 0xd4ae1e6f08f286fb), (0xf4781cae98271891, 0x6114db1cdb6f9a59), 
    (0xf7be496e71ab74f5, 0x116535bcbaa3d22d), (0x8ef17003de787677, 0x860f3d172b1eade1), 
    (0xa00f9fc2c6895cab, 0x19576aadcab92543), (0x154bd60854092022, 0x96354ca7d12e694c), 
    (0xde266f57ac86f1dd, 0x0d844f9855daa983), (0x96d3a1c9c4a27796, 0x547d7485dcce55ea), 
    (0xa59c32ca9a81c57d, 0x8b7a4065c8222ed9), (0xdabb56958fa8e5c3, 0x19d11466de1ec5fb), 
    (0xc6c14815403f7698, 0x1d1aedbf051c0c00), (0xb90dddd1adef9fd0, 0xac0e6e3430eaba86), 
    (0xfd4089427afa67ac, 0xb1ec8f13d277e6e6), (0x0d03d4dce403fa2b, 0x93906bebd18c9e53), 
    (0xc3d55c38596bb0bc, 0x70726b4f581ac1d8), (0xb223e66f1b49b509, 0xc8e33061d8ca2653), 
    (0x8e00a2e2f36e18db, 0x6deda055f0c4f363), (0x0375d9061d9e1685, 0xacf3fe9d06f17b87), 
    (0x0d8971609e6fbdbf, 0xe5befabca308224b), (0x94e642a6a7285d71, 0x9cd5503165e8589f), 
    (0x4c5bd85229bb86b6, 0x2a5fc91348b0de0c), (0xa178fe50ee3ff0b6, 0x3b3d78a08f6d0efe), 
    (0x20b75bc25020fcb3, 0xc9e760303c14e54d), (0x6d6b9a0959d5a542, 0x01a06ea6aa776c78), 
    (0xae0a1fec7fa665dd, 0x7672f70a22469493), (0xadf265cbbcb0fb73, 0xfce0516f27036ccb), 
    (0xdf55d0c0886648a6, 0x4b4698234a6cb816), (0xfed04fafe2405849, 0x09a879eacdf79eb3), 
    (0xc1b7ae1b6e2c157e, 0x7af3416b6b8ca48a), (0xf3235df0ebdfeae0, 0x45546b5125e582d0), 
    (0xaf49ba561af3ccca, 0x2666964098d96f90), (0x72f87860f3f019af, 0x763eb31c72c32d1d), 
    (0xd9ec3788068ab9ed, 0x3a7a2ee0ed3b4c75), (0x2dc4b20bc2033a39, 0xc7863bedf63d1975), 
    (0xe3a7cea59ab3fe1a, 0x613d75eba9623dfe), (0x16b99da0276b41c5, 0xa6d9dfca498f5851), 
    (0xa38f3b3e376a5464, 0xf1c341fcba5c9a9a), (0xe8e243adad4f66bd, 0xe01bf4fce72c8e89), 
    (0xeb1532648b2fdb7a, 0xe107059559c2f6e6), (0x0be356566c12db84, 0xa12d41e15b1ae3a8), 
    (0x171da3d902834004, 0xf0ee2741da67d830), (0x3e313e270f1a9ff4, 0x30e200e6889deece), 
    (0x9923dbea27e7d429, 0x404c6719cb8d3615), (0xddb7113ecf1858ee, 0x13eb788e651a3bd6), 
    (0x43032a7f41707f24, 0x302bfba1f1ef24e0), (0x2f8cd13a8f15db58, 0xcd28fb98137976be), 
    (0xa09c8424a2ece63e, 0x60074f915485a1e2), (0x90dc420737ba2b8b, 0x1a786f0824ba11f7), 
    (0x11e8f301762a5b4c, 0x50cd238ecef99834), (0xb03250ab5e9d46bd, 0xc6459c6afc1b2fa1), 
    (0x4fc676318bc0e63b, 0xf50dfcc9181f38e3), (0x8e89ddfec1905efb, 0xc6492439de38311d), 
    (0x80bbf28ed4b54621, 0xa3616083a76afd3b), (0xaa4d25ca69787c02, 0xb7767223b4637706), 
    (0x5163bba3724ccba8, 0xa1ebf39eda1a8a02), (0xdf943473e37afc38, 0x2944e023f675a3a4), 
    (0x327711621eff26a2, 0xc0efeffaa258f398), (0x84f5f52fdd57fbe0, 0xbccc613686bd76a4), 
    (0xbb34c1d4517c7edc, 0xe22a79e4e977efee), (0xa1813b2c244eb832, 0x6be1d7d6ceb219c6), 
    (0xafb68c873a98bd19, 0x19c31c4909c7b3a7), (0xb4a5fbda6589d41a, 0xfcebc6475d47ccf8), 
    (0x5c8a28b028025afc, 0x666016d7efe504ce), (0x875a4acbd373a55b, 0x382562eda040a5ed), 
    (0xa62264e0536127d6, 0x260b324aa74dfefa), (0xc37e449cefda27db, 0x96442b6b3eea7e49), 
    (0x30aaa8c65f1cdec5, 0x8476a8b18e430da5), (0x79c7a8ab91db8a81, 0x189ee3432015cdff), 
    (0x057d9bcea8fe009e, 0x1c7d35a1503af784), (0xb3451bd7642b9326, 0x54ef9feed92588b0), 
    (0x7043f1e6edf237dd, 0xeba18e26f2b8b919), (0xdd97848d3abc7169, 0x072912c0680c8f23), 
    (0x1339ffbaaef8cd6a, 0x10799bc3b6c185fc), (0xa501b402a0131682, 0xb8b7b82d4090da5c), 
    (0x14076b46f39017bf, 0x9328be118bb85845), (0xf9524f5a98851d9a, 0x750f8d98b41c586a), 
    (0x4161f6de31fe31b7, 0x84c1141d62564ddb), (0x783917181d9896e5, 0x932ba576c1be9e45), 
    (0x2967e635e288712b, 0x7241414253fcde3b), (0x107b21dd09db5633, 0x02e4c72cd2495c39), 
    (0xf6dc22332ce429a0, 0x7d653b57791efda2), (0xd5007abaf9c63516, 0x6ec88d57ea2d1ccc), 
    (0xda717c02b7712ade, 0x652014e4d4076eb4), (0xfc8651c880a35c53, 0x370d3938be67aecf), 
    (0xd199b20b275204d7, 0xf941dcf8c3079f25), (0x7ca618245ce63a41, 0x57957758eec1c69d), 
    (0xe091fbb5e4fcac1d, 0x27e7f5810e4007a7), (0x6f93b1e8dec2b7e2, 0x67e1b1d5e7fd884e), 
    (0x73ba6c2cee2e95a0, 0xdc85806e9d11982e), (0xca158b84b7d10bf3, 0x53d654c05cd8d5cb), 
    (0xe9b9550e5d17b45f, 0xeb5f93a0078906f9), (0xd3e4eaae96956129, 0x3ef3f11cc4226f8f), 
    (0xeafea126b9802570, 0x0cdfb25ac077baf8), (0x74d8e2812adc9784, 0xa2db5f56eaba6a16), 
    (0x304d7e10dd84c745, 0x8718ad4068921dbf), (0xd6022fa3e412c5e4, 0xd546bf4e182a008e), 
    (0x42f01ef6c7090da7, 0x32314ef2b1a3385d), (0xec2bf8c19ba9a7e3, 0x948db286efd5dfaf), 
    (0x99ca7775a82a988a, 0xaeb4d988d48ef51e), (0x933e46a8c6f5a8fb, 0xd59a310033800e37), 
    (0xd1797392d3f875a9, 0xd0e573e36d54a421), (0xe3f21e60169f36b1, 0x15b3e8c485f5ef15), 
    (0x74a9f768a519b521, 0x508658100db42a67), (0x5d87e155976cbfad, 0xddea4006ade88d6d), 
    (0x83edad2c83cbd1ab, 0xb682e947ed2483ab), (0x35c6e19899d485c9, 0x0aafc585c4609283), 
    (0xadfbe51f71fd59ff, 0x83d8e18b69a827d3), (0xef9ef3b788383f2a, 0xb4d3b2891426f826), 
    (0x0aa2be90fef1d020, 0x42038951cb574db4), (0xabcc6a3e95a6ed40, 0x2596d05337b6f10a), 
    (0x085bc285f98c9a72, 0x91e6750da8a02cf0), (0xaba9da6479476d4e, 0xc6ecdb03fdc85ee6), 
    (0xa80b96f6b0aea429, 0xb7e5d4018699c2f1), (0xb18a896a28d55e13, 0xbdbe477da56a70b3),
)