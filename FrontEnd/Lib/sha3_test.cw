(module main [] :
(import test)
(import fmt)

(import sha3)

(global limerick auto """
A lim'rick's not hard to define
But it needs to do more than just rhyme
It's the meter that matters
The pitters and patters
If not you're just wasting my time
""")

(fun test_Keccak512 [] void :
    (test::AssertSliceEq#
    x"""82368d4d74e4c746 389c75d720159d61
        3ad18ffd6624ac12 c032008cf4bb83cf
        8bd7d351b1613001 48d7daed629703ed
        743f690c44dff4a0 e115c46338a115a0"""
         (sha3::Keccak512 [limerick])
        )

    (test::AssertSliceEq#
    x"""96ee4718dcba3c74 619ba1fa7f57dfe7
        769d3f6698a8b33f a101838970a131e6
        21ccfd05feffbc11 80f263c27f1adab4
        6095d6f125331472 4b5cbf7828658e6a"""
         (sha3::Keccak512 ["Keccak-512 Test Hash"])
        )

    (test::AssertSliceEq#
    x"""0eab42de4c3ceb92 35fc91acffe746b2
        9c29a8c366b7c60e 4e67c466f36a4304
        c00fa9caf9d87976 ba469bcbe06713b4
        35f091ef2769fb16 0cdab33d3670680e"""
         (sha3::Keccak512 [""])
        )
)

(fun test_Sha3512 [] void :
    (test::AssertSliceEq#
    x"""c48266f826ef5181 866b7a9c4ce4a7ce
        49279ea71d8d5783 56348f565154f906
        3111cb978fd2c49f e4877b7369ff7260
        264f2af56b034f9d 2345185b48b0fa7f"""
         (sha3::Sha3512 [limerick])
        )

    (test::AssertSliceEq#
    x"""2a2aadf8fd39288e c6e19e1c1d09c4b4
        a4cab5a232803b1f 383ea81f8deac480
        f33e4ec76faf617c 84d5275c13763e90
        3094903a436249bd 4db1fcde08be3b5e"""
         (sha3::Sha3512 ["Sha3-512 Test Hash"])
        )

    (test::AssertSliceEq#
    x"""a69f73cca23a9ac5 c8b567dc185a756e
        97c982164fe25859 e0d1dcc1475c80a6
        15b2123af1f5f94c 11e3e9402c3ac558
        f500199d95b6d3e3 01758586281dcd26"""
         (sha3::Sha3512 [""])
        )
)

@cdecl (fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    @doc ""
    (shed (test_Keccak512 []))
    (shed (test_Sha3512 []))

    @doc """(let hash auto  (sha3::Keccak512 [limerick]))
    (fmt::print# (wrap hash fmt::str_hex) "\n")"""
    (test::Success#)
    (return 0))
)
