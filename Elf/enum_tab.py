#!/usr/bin/python3

"""ELF Enums - mostly lifted from pyelftools (public domain)

When symbol starts with a digit we prepend X_ to make it a valid identifier.
We do not aim for completeness as this is will be used only with supported
ISAs.

"""

import enum
from Util import cgen


@enum.unique
class EI_CLASS(enum.IntEnum):
    """e_ident[EI_CLASS] in the ELF header"""
    NONE = 0
    X_32 = 1
    X_64 = 2


@enum.unique
class EI_DATA(enum.IntEnum):
    """e_ident[EI_DATA] in the ELF header"""
    NONE = 0
    LSB2 = 1  # 2's complement
    MSB2 = 2  # 2's complement


@enum.unique
class EI_VERSION(enum.IntEnum):
    """ e_version in the ELF header"""
    NONE = 0
    CURRENT = 1


@enum.unique
class EI_OSABI(enum.IntEnum):
    """e_ident[EI_OSABI] in the ELF header"""
    SYSV = 0
    HPUX = 1
    NETBSD = 2
    LINUX = 3
    HURD = 4
    SOLARIS = 6
    AIX = 7
    IRIX = 8
    FREEBSD = 9
    TRU64 = 10
    MODESTO = 11
    OPENBSD = 12
    OPENVMS = 13
    NSK = 14
    AROS = 15
    FENIXOS = 16
    CLOUD = 17
    SORTIX = 53
    ARM_AEABI = 64
    ARM = 97
    # STANDALONE = 255


@enum.unique
class E_TYPE(enum.IntEnum):
    """e_type in the ELF header"""
    NONE = 0
    REL = 1
    EXEC = 2
    DYN = 3
    CORE = 4


@enum.unique
class E_MACHINE(enum.IntEnum):
    """e_machine in the ELF header"""
    NONE = 0  # No machine
    M32 = 1  # AT&T WE 32100
    SPARC = 2  # SPARC
    X_386 = 3  # Intel 80386
    X_68K = 4  # Motorola 68000
    X_88K = 5  # Motorola 88000
    IAMCU = 6  # Intel MCU
    X_860 = 7  # Intel 80860
    MIPS = 8  # MIPS I Architecture
    S370 = 9  # IBM System/370 Processor
    MIPS_RS3_LE = 10  # MIPS RS3000 Little-endian
    PARISC = 15  # Hewlett-Packard PA-RISC
    VPP500 = 17  # Fujitsu VPP500
    SPARC32PLUS = 18  # Enhanced instruction set SPARC
    X_960 = 19  # Intel 80960
    PPC = 20  # PowerPC
    PPC64 = 21  # 64-bit PowerPC
    S390 = 22  # IBM System/390 Processor
    SPU = 23  # IBM SPU/SPC
    V800 = 36  # NEC V800
    FR20 = 37  # Fujitsu FR20
    RH32 = 38  # TRW RH-32
    RCE = 39  # Motorola RCE
    ARM = 40  # ARM 32-bit architecture (AARCH32)
    ALPHA = 41  # Digital Alpha
    SH = 42  # Hitachi SH
    SPARCV9 = 43  # SPARC Version 9
    TRICORE = 44  # Siemens TriCore embedded processor
    ARC = 45  # Argonaut RISC Core, Argonaut Technologies Inc.
    H8_300 = 46  # Hitachi H8/300
    H8_300H = 47  # Hitachi H8/300H
    H8S = 48  # Hitachi H8S
    H8_500 = 49  # Hitachi H8/500
    IA_64 = 50  # Intel IA-64 processor architecture
    MIPS_X = 51  # Stanford MIPS-X
    COLDFIRE = 52  # Motorola ColdFire
    X_68HC12 = 53  # Motorola M68HC12
    MMA = 54  # Fujitsu MMA Multimedia Accelerator
    PCP = 55  # Siemens PCP
    NCPU = 56  # Sony nCPU embedded RISC processor
    NDR1 = 57  # Denso NDR1 microprocessor
    STARCORE = 58  # Motorola Star*Core processor
    ME16 = 59  # Toyota ME16 processor
    ST100 = 60  # STMicroelectronics ST100 processor
    TINYJ = 61  # Advanced Logic Corp. TinyJ embedded processor family
    X86_64 = 62  # AMD x86-64 architecture
    PDSP = 63  # Sony DSP Processor
    PDP10 = 64  # Digital Equipment Corp. PDP-10
    PDP11 = 65  # Digital Equipment Corp. PDP-11
    FX66 = 66  # Siemens FX66 microcontroller
    ST9PLUS = 67  # STMicroelectronics ST9+ 8/16 bit microcontroller
    ST7 = 68  # STMicroelectronics ST7 8-bit microcontroller
    X_68HC16 = 69  # Motorola MC68HC16 Microcontroller
    X_68HC11 = 70  # Motorola MC68HC11 Microcontroller
    X_68HC08 = 71  # Motorola MC68HC08 Microcontroller
    X_68HC05 = 72  # Motorola MC68HC05 Microcontroller
    SVX = 73  # Silicon Graphics SVx
    ST19 = 74  # STMicroelectronics ST19 8-bit microcontroller
    VAX = 75  # Digital VAX
    CRIS = 76  # Axis Communications 32-bit embedded processor
    JAVELIN = 77  # Infineon Technologies 32-bit embedded processor
    FIREPATH = 78  # Element 14 64-bit DSP Processor
    ZSP = 79  # LSI Logic 16-bit DSP Processor
    MMIX = 80  # Donald Knuth's educational 64-bit processor
    HUANY = 81  # Harvard University machine-independent object files
    PRISM = 82  # SiTera Prism
    AVR = 83  # Atmel AVR 8-bit microcontroller
    FR30 = 84  # Fujitsu FR30
    D10V = 85  # Mitsubishi D10V
    D30V = 86  # Mitsubishi D30V
    V850 = 87  # NEC v850
    M32R = 88  # Mitsubishi M32R
    MN10300 = 89  # Matsushita MN10300
    MN10200 = 90  # Matsushita MN10200
    PJ = 91  # picoJava
    OPENRISC = 92  # OpenRISC 32-bit embedded processor
    # ARC International ARCompact processor (old spelling/synonym: ARC_A5)
    ARC_COMPACT = 93
    XTENSA = 94  # Tensilica Xtensa Architecture
    VIDEOCORE = 95  # Alphamosaic VideoCore processor
    TMM_GPP = 96  # Thompson Multimedia General Purpose Processor
    NS32K = 97  # National Semiconductor 32000 series
    TPC = 98  # Tenor Network TPC processor
    SNP1K = 99  # Trebia SNP 1000 processor
    ST200 = 100  # STMicroelectronics (www.st.com) ST200 microcontroller
    IP2K = 101  # Ubicom IP2xxx microcontroller family
    MAX = 102  # MAX Processor
    CR = 103  # National Semiconductor CompactRISC microprocessor
    F2MC16 = 104  # Fujitsu F2MC16
    MSP430 = 105  # Texas Instruments embedded microcontroller msp430
    BLACKFIN = 106  # Analog Devices Blackfin (DSP) processor
    SE_C33 = 107  # S1C33 Family of Seiko Epson processors
    SEP = 108  # Sharp embedded microprocessor
    ARCA = 109  # Arca RISC Microprocessor
    UNICORE = 110  # Microprocessor series from PKU-Unity Ltd. and MPRC of Peking University
    EXCESS = 111  # eXcess: 16/32/64-bit configurable embedded CPU
    DXP = 112  # Icera Semiconductor Inc. Deep Execution Processor
    ALTERA_NIOS2 = 113  # Altera Nios II soft-core processor
    CRX = 114  # National Semiconductor CompactRISC CRX microprocessor
    XGATE = 115  # Motorola XGATE embedded processor
    C166 = 116  # Infineon C16x/XC16x processor
    M16C = 117  # Renesas M16C series microprocessors
    DSPIC30F = 118  # Microchip Technology dsPIC30F Digital Signal Controller
    CE = 119  # Freescale Communication Engine RISC core
    M32C = 120  # Renesas M32C series microprocessors
    TSK3000 = 131  # Altium TSK3000 core
    RS08 = 132  # Freescale RS08 embedded processor
    SHARC = 133  # Analog Devices SHARC family of 32-bit DSP processors
    ECOG2 = 134  # Cyan Technology eCOG2 microprocessor
    SCORE7 = 135  # Sunplus S+core7 RISC processor
    DSP24 = 136  # New Japan Radio (NJR) 24-bit DSP Processor
    VIDEOCORE3 = 137  # Broadcom VideoCore III processor
    LATTICEMICO32 = 138  # RISC processor for Lattice FPGA architecture
    SE_C17 = 139  # Seiko Epson C17 family
    TI_C6000 = 140  # The Texas Instruments TMS320C6000 DSP family
    TI_C2000 = 141  # The Texas Instruments TMS320C2000 DSP family
    TI_C5500 = 142  # The Texas Instruments TMS320C55x DSP family
    TI_ARP32 = 143  # Texas Instruments Application Specific RISC Processor, 32bit fetch
    TI_PRU = 144  # Texas Instruments Programmable Realtime Unit
    MMDSP_PLUS = 160  # STMicroelectronics 64bit VLIW Data Signal Processor
    CYPRESS_M8C = 161  # Cypress M8C microprocessor
    R32C = 162  # Renesas R32C series microprocessors
    TRIMEDIA = 163  # NXP Semiconductors TriMedia architecture family
    QDSP6 = 164  # QUALCOMM DSP6 Processor
    X_8051 = 165  # Intel 8051 and variants
    STXP7X = 166  # STMicroelectronics STxP7x family of configurable and extensible RISC processors
    NDS32 = 167  # Andes Technology compact code size embedded RISC processor family
    ECOG1 = 168  # Cyan Technology eCOG1X family
    MAXQ30 = 169  # Dallas Semiconductor MAXQ30 Core Micro-controllers
    XIMO16 = 170  # New Japan Radio (NJR) 16-bit DSP Processor
    MANIK = 171  # M2000 Reconfigurable RISC Microprocessor
    CRAYNV2 = 172  # Cray Inc. NV2 vector architecture
    RX = 173  # Renesas RX family
    METAG = 174  # Imagination Technologies META processor architecture
    MCST_ELBRUS = 175  # MCST Elbrus general purpose hardware architecture
    ECOG16 = 176  # Cyan Technology eCOG16 family
    CR16 = 177  # National Semiconductor CompactRISC CR16 16-bit microprocessor
    ETPU = 178  # Freescale Extended Time Processing Unit
    SLE9X = 179  # Infineon Technologies SLE9X core
    L10M = 180  # Intel L10M
    K10M = 181  # Intel K10M
    AARCH64 = 183  # ARM 64-bit architecture (AARCH64)
    AVR32 = 185  # Atmel Corporation 32-bit microprocessor family
    STM8 = 186  # STMicroeletronics STM8 8-bit microcontroller
    TILE64 = 187  # Tilera TILE64 multicore architecture family
    TILEPRO = 188  # Tilera TILEPro multicore architecture family
    MICROBLAZE = 189  # Xilinx MicroBlaze 32-bit RISC soft processor core
    CUDA = 190  # NVIDIA CUDA architecture
    TILEGX = 191  # Tilera TILE-Gx multicore architecture family
    CLOUDSHIELD = 192  # CloudShield architecture family
    COREA_1ST = 193  # KIPO-KAIST Core-A 1st generation processor family
    COREA_2ND = 194  # KIPO-KAIST Core-A 2nd generation processor family
    ARC_COMPACT2 = 195  # Synopsys ARCompact V2
    OPEN8 = 196  # Open8 8-bit RISC soft processor core
    RL78 = 197  # Renesas RL78 family
    VIDEOCORE5 = 198  # Broadcom VideoCore V processor
    X_78KOR = 199  # Renesas 78KOR family
    X_56800EX = 200  # Freescale 56800EX Digital Signal Controller (DSC)
    BA1 = 201  # Beyond BA1 CPU architecture
    BA2 = 202  # Beyond BA2 CPU architecture
    XCORE = 203  # XMOS xCORE processor family
    MCHP_PIC = 204  # Microchip 8-bit PIC(r) family
    INTEL205 = 205  # Reserved by Intel
    INTEL206 = 206  # Reserved by Intel
    INTEL207 = 207  # Reserved by Intel
    INTEL208 = 208  # Reserved by Intel
    INTEL209 = 209  # Reserved by Intel
    KM32 = 210  # KM211 KM32 32-bit processor
    KMX32 = 211  # KM211 KMX32 32-bit processor
    KMX16 = 212  # KM211 KMX16 16-bit processor
    KMX8 = 213  # KM211 KMX8 8-bit processor
    KVARC = 214  # KM211 KVARC processor
    CDP = 215  # Paneve CDP architecture family
    COGE = 216  # Cognitive Smart Memory Processor
    COOL = 217  # Bluechip Systems CoolEngine
    NORC = 218  # Nanoradio Optimized RISC
    CSR_KALIMBA = 219  # CSR Kalimba architecture family
    Z80 = 220  # Zilog Z80
    VISIUM = 221  # Controls and Data Services VISIUMcore processor
    FT32 = 222  # FTDI Chip FT32 high performance 32-bit RISC architecture
    MOXIE = 223  # Moxie processor family
    AMDGPU = 224  # AMD GPU architecture
    RISCV = 243  # RISC-V


class SH_TYPE(enum.IntEnum):
    X_NULL = 0
    PROGBITS = 1
    SYMTAB = 2
    STRTAB = 3
    RELA = 4
    HASH = 5
    DYNAMIC = 6
    NOTE = 7
    NOBITS = 8
    REL = 9
    SHLIB = 10
    DYNSYM = 11
    INIT_ARRAY = 14
    FINI_ARRAY = 15
    PREINIT_ARRAY = 16
    GROUP = 17
    SYMTAB_SHNDX = 18
    NUM = 19
    GNU_ATTRIBUTES = 0x6ffffff5
    GNU_HASH = 0x6ffffff6
    GNU_LIBLIST = 0x6ffffff7
    GNU_verdef = 0x6ffffffd  # also SUNW_verdef
    GNU_verneed = 0x6ffffffe  # also SUNW_verneed
    GNU_versym = 0x6fffffff  # also SUNW_versym, HIOS

    ARM_EXIDX = 0x70000001
    ARM_PREEMPTMAP = 0x70000002
    ARM_ATTRIBUTES = 0x70000003
    ARM_DEBUGOVERLAY = 0x70000004

    AMD64_UNWIND = 0x70000001


@enum.unique
class ELF_COMPRESS(enum.IntEnum):
    ZLIB = 1


# p_type in the program header
# some values scavenged from the ELF headers in binutils-2.21
#
# Using the same base + per-processor augmentation technique as in sh_type.
class P_TYPE(enum.IntEnum):
    X_NULL = 0
    LOAD = 1
    DYNAMIC = 2
    INTERP = 3
    NOTE = 4
    SHLIB = 5
    PHDR = 6
    TLS = 7

    GNU_EH_FRAME = 0x6474e550
    GNU_STACK = 0x6474e551
    GNU_RELRO = 0x6474e552
    GNU_PROPERTY = 0x6474e553

    ARM_ARCHEXT = 0x70000000
    ARM_EXIDX = 0x70000001

    AARCH64_ARCHEXT = 0x70000000
    AARCH64_UNWIND = 0x70000001

    ABIFLAGS = 0x70000003


@enum.unique
class ST_INFO_BIND(enum.IntEnum):
    """st_info bindings in the symbol header"""
    LOCAL = 0
    GLOBAL = 1
    WEAK = 2
    NUM = 3


@enum.unique
class ST_INFO_TYPE(enum.IntEnum):
    """st_info type in the symbol header"""
    NOTYPE = 0
    OBJECT = 1
    FUNC = 2
    SECTION = 3
    FILE = 4
    COMMON = 5
    TLS = 6
    NUM = 7
    RELC = 8
    SRELC = 9
    LOOS = 10
    HIOS = 12
    LOPROC = 13
    HIPROC = 15


@enum.unique
class ST_VISIBILITY(enum.IntEnum):
    """visibility from st_other"""
    DEFAULT = 0
    INTERNAL = 1
    HIDDEN = 2
    PROTECTED = 3
    EXPORTED = 4
    SINGLETON = 5
    ELIMINATE = 6


# d_tag


@enum.unique
class D_TAG_COMMON(enum.IntEnum):
    X_NULL = 0
    NEEDED = 1
    PLTRELSZ = 2
    PLTGOT = 3
    HASH = 4
    STRTAB = 5
    SYMTAB = 6
    RELA = 7
    RELASZ = 8
    RELAENT = 9
    STRSZ = 10
    SYMENT = 11
    INIT = 12
    FINI = 13
    SONAME = 14
    RPATH = 15
    SYMBOLIC = 16
    REL = 17
    RELSZ = 18
    RELENT = 19
    PLTREL = 20
    DEBUG = 21
    TEXTREL = 22
    JMPREL = 23
    BIND_NOW = 24
    INIT_ARRAY = 25
    FINI_ARRAY = 26
    INIT_ARRAYSZ = 27
    FINI_ARRAYSZ = 28
    RUNPATH = 29
    FLAGS = 30
    ENCODING = 31
    PREINIT_ARRAY = 32
    PREINIT_ARRAYSZ = 33
    NUM = 34
    PROCNUM = 0x35
    VALRNGLO = 0x6ffffd00
    GNU_PRELINKED = 0x6ffffdf5
    GNU_CONFLICTSZ = 0x6ffffdf6
    GNU_LIBLISTSZ = 0x6ffffdf7
    CHECKSUM = 0x6ffffdf8
    PLTPADSZ = 0x6ffffdf9
    MOVEENT = 0x6ffffdfa
    MOVESZ = 0x6ffffdfb
    SYMINSZ = 0x6ffffdfe
    SYMINENT = 0x6ffffdff
    GNU_HASH = 0x6ffffef5
    TLSDESC_PLT = 0x6ffffef6
    TLSDESC_GOT = 0x6ffffef7
    GNU_CONFLICT = 0x6ffffef8
    GNU_LIBLIST = 0x6ffffef9
    CONFIG = 0x6ffffefa
    DEPAUDIT = 0x6ffffefb
    AUDIT = 0x6ffffefc
    PLTPAD = 0x6ffffefd
    MOVETAB = 0x6ffffefe
    SYMINFO = 0x6ffffeff
    VERSYM = 0x6ffffff0
    RELACOUNT = 0x6ffffff9
    RELCOUNT = 0x6ffffffa
    FLAGS_1 = 0x6ffffffb
    VERDEF = 0x6ffffffc
    VERDEFNUM = 0x6ffffffd
    VERNEED = 0x6ffffffe
    VERNEEDNUM = 0x6fffffff
    AUXILIARY = 0x7ffffffd


# Above are the dynamic tags which are valid always.
# Below are the dynamic tags which are only valid in certain contexts.

@enum.unique
class D_TAG_MIPS(enum.IntEnum):
    RLD_VERSION = 0x70000001
    TIME_STAMP = 0x70000002
    ICHECKSUM = 0x70000003
    IVERSION = 0x70000004
    FLAGS = 0x70000005
    BASE_ADDRESS = 0x70000006
    CONFLICT = 0x70000008
    LIBLIST = 0x70000009
    LOCAL_GOTNO = 0x7000000a
    CONFLICTNO = 0x7000000b
    LIBLISTNO = 0x70000010
    SYMTABNO = 0x70000011
    UNREFEXTNO = 0x70000012
    GOTSYM = 0x70000013
    HIPAGENO = 0x70000014
    RLD_MAP = 0x70000016
    RLD_MAP_REL = 0x70000035


@enum.unique
class DT_FLAGS(enum.IntEnum):
    ORIGIN = 0x1
    SYMBOLIC = 0x2
    TEXTREL = 0x4
    BIND_NOW = 0x8
    STATIC_TLS = 0x10


@enum.unique
class DT_FLAGS_1(enum.Flag):
    NOW = 0x1
    GLOBAL = 0x2
    GROUP = 0x4
    NODELETE = 0x8
    LOADFLTR = 0x10
    INITFIRST = 0x20
    NOOPEN = 0x40
    ORIGIN = 0x80
    DIRECT = 0x100
    TRANS = 0x200
    INTERPOSE = 0x400
    NODEFLIB = 0x800
    NODUMP = 0x1000
    CONFALT = 0x2000
    ENDFILTEE = 0x4000
    DISPRELDNE = 0x8000
    DISPRELPND = 0x10000
    NODIRECT = 0x20000
    IGNMULDEF = 0x40000
    NOKSYMS = 0x80000
    NOHDR = 0x100000
    EDITED = 0x200000
    NORELOC = 0x400000
    SYMINTPOSE = 0x800000
    GLOBAUDIT = 0x1000000
    SINGLETON = 0x2000000
    STUB = 0x4000000
    PIE = 0x8000000


@enum.unique
class RELOC_TYPE_MIPS(enum.IntEnum):
    NONE = 0
    X_16 = 1
    X_32 = 2
    REL32 = 3
    X_26 = 4
    HI16 = 5
    LO16 = 6
    GPREL16 = 7
    LITERAL = 8
    GOT16 = 9
    PC16 = 10
    CALL16 = 11
    GPREL32 = 12
    SHIFT5 = 16
    SHIFT6 = 17
    X_64 = 18
    GOT_DISP = 19
    GOT_PAGE = 20
    GOT_OFST = 21
    GOT_HI16 = 22
    GOT_LO16 = 23
    SUB = 24
    INSERT_A = 25
    INSERT_B = 26
    DELETE = 27
    HIGHER = 28
    HIGHEST = 29
    CALL_HI16 = 30
    CALL_LO16 = 31
    SCN_DISP = 32
    REL16 = 33
    ADD_IMMEDIATE = 34
    PJUMP = 35
    RELGOT = 36
    JALR = 37
    TLS_DTPMOD32 = 38
    TLS_DTPREL32 = 39
    TLS_DTPMOD64 = 40
    TLS_DTPREL64 = 41
    TLS_GD = 42
    TLS_LDM = 43
    TLS_DTPREL_HI16 = 44
    TLS_DTPREL_LO16 = 45
    TLS_GOTTPREL = 46
    TLS_TPREL32 = 47
    TLS_TPREL64 = 48
    TLS_TPREL_HI16 = 49
    TLS_TPREL_LO16 = 50
    GLOB_DAT = 51
    COPY = 126
    JUMP_SLOT = 127


@enum.unique
class RELOC_TYPE_i386(enum.IntEnum):
    NONE = 0
    X_32 = 1
    PC32 = 2
    GOT32 = 3
    PLT32 = 4
    COPY = 5
    GLOB_DAT = 6
    JUMP_SLOT = 7
    RELATIVE = 8
    GOTOFF = 9
    GOTPC = 10
    X_32PLT = 11
    TLS_TPOFF = 14
    TLS_IE = 15
    TLS_GOTIE = 16
    TLS_LE = 17
    TLS_GD = 18
    TLS_LDM = 19
    X_16 = 20
    PC16 = 21
    X_8 = 22
    PC8 = 23
    TLS_GD_32 = 24
    TLS_GD_PUSH = 25
    TLS_GD_CALL = 26
    TLS_GD_POP = 27
    TLS_LDM_32 = 28
    TLS_LDM_PUSH = 29
    TLS_LDM_CALL = 30
    TLS_LDM_POP = 31
    TLS_LDO_32 = 32
    TLS_IE_32 = 33
    TLS_LE_32 = 34
    TLS_DTPMOD32 = 35
    TLS_DTPOFF32 = 36
    TLS_TPOFF32 = 37
    TLS_GOTDESC = 39
    TLS_DESC_CALL = 40
    TLS_DESC = 41
    IRELATIVE = 42
    USED_BY_INTEL_200 = 200
    GNU_VTINHERIT = 250
    GNU_VTENTRY = 251


@enum.unique
class RELOC_TYPE_X86_64(enum.IntEnum):
    NONE = 0
    X_64 = 1
    PC32 = 2
    GOT32 = 3
    PLT32 = 4
    COPY = 5
    GLOB_DAT = 6
    JUMP_SLOT = 7
    RELATIVE = 8
    GOTPCREL = 9
    X_32 = 10
    X_32S = 11
    X_16 = 12
    PC16 = 13
    X_8 = 14
    PC8 = 15
    DTPMOD64 = 16
    DTPOFF64 = 17
    TPOFF64 = 18
    TLSGD = 19
    TLSLD = 20
    DTPOFF32 = 21
    GOTTPOFF = 22
    TPOFF32 = 23
    PC64 = 24
    GOTOFF64 = 25
    GOTPC32 = 26
    GOT64 = 27
    GOTPCREL64 = 28
    GOTPC64 = 29
    GOTPLT64 = 30
    PLTOFF64 = 31
    GOTPC32_TLSDESC = 34
    TLSDESC_CALL = 35
    TLSDESC = 36
    IRELATIVE = 37
    REX_GOTPCRELX = 42
    GNU_VTINHERIT = 250
    GNU_VTENTRY = 251


@enum.unique
class VERSYM_NDX(enum.IntEnum):
    """Versym section version dependency index"""
    LOCAL = 0
    GLOBAL = 1
    LORESERVE = 0xff00
    ELIMINATE = 0xff01


# PT_NOTE section types for all ELF types except ET_CORE
@enum.unique
class NOTE_N_TYPE(enum.IntEnum):
    NT_GNU_ABI_TAG = 1
    NT_GNU_HWCAP = 2
    NT_GNU_BUILD_ID = 3
    NT_GNU_GOLD_VERSION = 4


# PT_NOTE section types for ET_CORE
@enum.unique
class CORE_NOTE_N_TYPE(enum.IntEnum):
    NT_PRSTATUS = 1
    NT_FPREGSET = 2
    NT_PRPSINFO = 3
    NT_TASKSTRUCT = 4
    NT_AUXV = 6
    NT_SIGINFO = 0x53494749
    NT_FILE = 0x46494c45


# Values in GNU .note.ABI-tag notes (n_type=='NT_GNU_ABI_TAG')
@enum.unique
class ELF_NOTE_ABI_TAG_OS(enum.IntEnum):
    LINUX = 0
    GNU = 1
    SOLARIS2 = 2
    FREEBSD = 3
    NETBSD = 4
    SYLLABLE = 5


@enum.unique
class RELOC_TYPE_ARM(enum.IntEnum):
    NONE = 0
    PC24 = 1
    ABS32 = 2
    REL32 = 3
    LDR_PC_G0 = 4
    ABS16 = 5
    ABS12 = 6
    THM_ABS5 = 7
    ABS8 = 8
    SBREL32 = 9
    THM_CALL = 10
    THM_PC8 = 11
    BREL_ADJ = 12
    SWI24 = 13
    THM_SWI8 = 14
    XPC25 = 15
    THM_XPC22 = 16
    TLS_DTPMOD32 = 17
    TLS_DTPOFF32 = 18
    TLS_TPOFF32 = 19
    COPY = 20
    GLOB_DAT = 21
    JUMP_SLOT = 22
    RELATIVE = 23
    GOTOFF32 = 24
    BASE_PREL = 25
    GOT_BREL = 26
    PLT32 = 27
    CALL = 28
    JUMP24 = 29
    THM_JUMP24 = 30
    BASE_ABS = 31
    ALU_PCREL_7_0 = 32
    ALU_PCREL_15_8 = 33
    ALU_PCREL_23_15 = 34
    LDR_SBREL_11_0_NC = 35
    ALU_SBREL_19_12_NC = 36
    ALU_SBREL_27_20_CK = 37
    TARGET1 = 38
    SBREL31 = 39
    V4BX = 40
    TARGET2 = 41
    PREL31 = 42
    MOVW_ABS_NC = 43
    MOVT_ABS = 44
    MOVW_PREL_NC = 45
    MOVT_PREL = 46
    THM_MOVW_ABS_NC = 47
    THM_MOVT_ABS = 48
    THM_MOVW_PREL_NC = 49
    THM_MOVT_PREL = 50
    THM_JUMP19 = 51
    THM_JUMP6 = 52
    THM_ALU_PREL_11_0 = 53
    THM_PC12 = 54
    ABS32_NOI = 55
    REL32_NOI = 56
    ALU_PC_G0_NC = 57
    ALU_PC_G0 = 58
    ALU_PC_G1_NC = 59
    ALU_PC_G1 = 60
    ALU_PC_G2 = 61
    LDR_PC_G1 = 62
    LDR_PC_G2 = 63
    LDRS_PC_G0 = 64
    LDRS_PC_G1 = 65
    LDRS_PC_G2 = 66
    LDC_PC_G0 = 67
    LDC_PC_G1 = 68
    LDC_PC_G2 = 69
    ALU_SB_G0_NC = 70
    ALU_SB_G0 = 71
    ALU_SB_G1_NC = 72
    ALU_SB_G1 = 73
    ALU_SB_G2 = 74
    LDR_SB_G0 = 75
    LDR_SB_G1 = 76
    LDR_SB_G2 = 77
    LDRS_SB_G0 = 78
    LDRS_SB_G1 = 79
    LDRS_SB_G2 = 80
    LDC_SB_G0 = 81
    LDC_SB_G1 = 82
    LDC_SB_G2 = 83
    MOVW_BREL_NC = 84
    MOVT_BREL = 85
    MOVW_BREL = 86
    THM_MOVW_BREL_NC = 87
    THM_MOVT_BREL = 88
    THM_MOVW_BREL = 89
    PLT32_ABS = 94
    GOT_ABS = 95
    GOT_PREL = 96
    GOT_BREL12 = 97
    GOTOFF12 = 98
    GOTRELAX = 99
    GNU_VTENTRY = 100
    GNU_VTINHERIT = 101
    THM_JUMP11 = 102
    THM_JUMP8 = 103
    TLS_GD32 = 104
    TLS_LDM32 = 105
    TLS_LDO32 = 106
    TLS_IE32 = 107
    TLS_LE32 = 108
    TLS_LDO12 = 109
    TLS_LE12 = 110
    TLS_IE12GP = 111
    PRIVATE_0 = 112
    PRIVATE_1 = 113
    PRIVATE_2 = 114
    PRIVATE_3 = 115
    PRIVATE_4 = 116
    PRIVATE_5 = 117
    PRIVATE_6 = 118
    PRIVATE_7 = 119
    PRIVATE_8 = 120
    PRIVATE_9 = 121
    PRIVATE_10 = 122
    PRIVATE_11 = 123
    PRIVATE_12 = 124
    PRIVATE_13 = 125
    PRIVATE_14 = 126
    PRIVATE_15 = 127
    ME_TOO = 128
    THM_TLS_DESCSEQ16 = 129
    THM_TLS_DESCSEQ32 = 130
    THM_GOT_BREL12 = 131
    IRELATIVE = 140


@enum.unique
class RELOC_TYPE_AARCH64(enum.IntEnum):
    NONE = 256
    ABS64 = 257
    ABS32 = 258
    ABS16 = 259
    PREL64 = 260
    PREL32 = 261
    PREL16 = 262
    MOVW_UABS_G0 = 263
    MOVW_UABS_G0_NC = 264
    MOVW_UABS_G1 = 265
    MOVW_UABS_G1_NC = 266
    MOVW_UABS_G2 = 267
    MOVW_UABS_G2_NC = 268
    MOVW_UABS_G3 = 269
    MOVW_SABS_G0 = 270
    MOVW_SABS_G1 = 271
    MOVW_SABS_G2 = 272
    LD_PREL_LO19 = 273
    ADR_PREL_LO21 = 274
    ADR_PREL_PG_HI21 = 275
    ADR_PREL_PG_HI21_NC = 276
    ADD_ABS_LO12_NC = 277
    LDST8_ABS_LO12_NC = 278
    TSTBR14 = 279
    CONDBR19 = 280
    JUMP26 = 282
    CALL26 = 283
    LDST16_ABS_LO12_NC = 284
    LDST32_ABS_LO12_NC = 285
    LDST64_ABS_LO12_NC = 286
    MOVW_PREL_G0 = 287
    MOVW_PREL_G0_NC = 288
    MOVW_PREL_G1 = 289
    MOVW_PREL_G1_NC = 290
    MOVW_PREL_G2 = 291
    MOVW_PREL_G2_NC = 292
    MOVW_PREL_G3 = 293
    MOVW_GOTOFF_G0 = 300
    MOVW_GOTOFF_G0_NC = 301
    MOVW_GOTOFF_G1 = 302
    MOVW_GOTOFF_G1_NC = 303
    MOVW_GOTOFF_G2 = 304
    MOVW_GOTOFF_G2_NC = 305
    MOVW_GOTOFF_G3 = 306
    GOTREL64 = 307
    GOTREL32 = 308
    GOT_LD_PREL19 = 309
    LD64_GOTOFF_LO15 = 310
    ADR_GOT_PAGE = 311
    LD64_GOT_LO12_NC = 312
    TLSGD_ADR_PREL21 = 512
    TLSGD_ADR_PAGE21 = 513
    TLSGD_ADD_LO12_NC = 514
    TLSGD_MOVW_G1 = 515
    TLSGD_MOVW_G0_NC = 516
    TLSLD_ADR_PREL21 = 517
    TLSLD_ADR_PAGE21 = 518
    TLSLD_ADD_LO12_NC = 519
    TLSLD_MOVW_G1 = 520
    TLSLD_MOVW_G0_NC = 521
    TLSLD_LD_PREL19 = 522
    TLSLD_MOVW_DTPREL_G2 = 523
    TLSLD_MOVW_DTPREL_G1 = 524
    TLSLD_MOVW_DTPREL_G1_NC = 525
    TLSLD_MOVW_DTPREL_G0 = 526
    TLSLD_MOVW_DTPREL_G0_NC = 527
    TLSLD_ADD_DTPREL_HI12 = 528
    TLSLD_ADD_DTPREL_LO12 = 529
    TLSLD_ADD_DTPREL_LO12_NC = 530
    TLSLD_LDST8_DTPREL_LO12 = 531
    TLSLD_LDST8_DTPREL_LO12_NC = 532
    TLSLD_LDST16_DTPREL_LO12 = 533
    TLSLD_LDST16_DTPREL_LO12_NC = 534
    TLSLD_LDST32_DTPREL_LO12 = 535
    TLSLD_LDST32_DTPREL_LO12_NC = 536
    TLSLD_LDST64_DTPREL_LO12 = 537
    TLSLD_LDST64_DTPREL_LO12_NC = 538
    TLSIE_MOVW_GOTTPREL_G1 = 539
    TLSIE_MOVW_GOTTPREL_G0_NC = 540
    TLSIE_ADR_GOTTPREL_PAGE21 = 541
    TLSIE_LD64_GOTTPREL_LO12_NC = 542
    TLSIE_LD_GOTTPREL_PREL19 = 543
    TLSLE_MOVW_TPREL_G2 = 544
    TLSLE_MOVW_TPREL_G1 = 545
    TLSLE_MOVW_TPREL_G1_NC = 546
    TLSLE_MOVW_TPREL_G0 = 547
    TLSLE_MOVW_TPREL_G0_NC = 548
    TLSLE_ADD_TPREL_HI12 = 549
    TLSLE_ADD_TPREL_LO12 = 550
    TLSLE_ADD_TPREL_LO12_NC = 551
    TLSLE_LDST8_TPREL_LO12 = 552
    TLSLE_LDST8_TPREL_LO12_NC = 553
    TLSLE_LDST16_TPREL_LO12 = 554
    TLSLE_LDST16_TPREL_LO12_NC = 555
    TLSLE_LDST32_TPREL_LO12 = 556
    TLSLE_LDST32_TPREL_LO12_NC = 557
    TLSLE_LDST64_TPREL_LO12 = 558
    TLSLE_LDST64_TPREL_LO12_NC = 559
    COPY = 1024
    GLOB_DAT = 1025
    JUMP_SLOT = 1026
    RELATIVE = 1027
    TLS_DTPREL64 = 1028
    TLS_DTPMOD64 = 1029
    TLS_TPREL64 = 1030
    TLS_DTPREL32 = 1031
    TLS_DTPMOD32 = 1032
    TLS_TPREL32 = 1033


@enum.unique
class ATTR_ARM(enum.IntEnum):
    FILE = 1
    SECTION = 2
    SYMBOL = 3
    CPU_RAW_NAME = 4
    CPU_NAME = 5
    CPU_ARCH = 6
    CPU_ARCH_PROFILE = 7
    ARM_ISA_USE = 8
    THUMB_ISA_USE = 9
    FP_ARCH = 10
    WMMX_ARCH = 11
    ADVANCED_SIMD_ARCH = 12
    PCS_CONFIG = 13
    ABI_PCS_R9_USE = 14
    ABI_PCS_RW_DATA = 15
    ABI_PCS_RO_DATA = 16
    ABI_PCS_GOT_USE = 17
    ABI_PCS_WCHAR_T = 18
    ABI_FP_ROUNDING = 19
    ABI_FP_DENORMAL = 20
    ABI_FP_EXCEPTIONS = 21
    ABI_FP_USER_EXCEPTIONS = 22
    ABI_FP_NUMBER_MODEL = 23
    ABI_ALIGN_NEEDED = 24
    ABI_ALIGN_PRESERVED = 25
    ABI_ENUM_SIZE = 26
    ABI_HARDFP_USE = 27
    ABI_VFP_ARGS = 28
    ABI_WMMX_ARGS = 29
    ABI_OPTIMIZATION_GOALS = 30
    ABI_FP_OPTIMIZATION_GOALS = 31
    COMPATIBILITY = 32
    CPU_UNALIGNED_ACCESS = 34
    FP_HP_EXTENSION = 36
    ABI_FP_16BIT_FORMAT = 38
    MPEXTENSION_USE = 42
    DIV_USE = 44
    NODEFAULTS = 64
    ALSO_COMPATIBLE_WITH = 65
    T2EE_USE = 66
    CONFORMANCE = 67
    VIRTUALIZATION_USE = 68
    MPEXTENSION_USE_OLD = 70


@enum.unique
class E_FLAGS_ARM(enum.Flag):
    """ Flag values for the e_flags field of the ELF header."""

    RELEXEC = 0x01
    HASENTRY = 0x02
    SYMSARESORTED = 0x04
    DYNSYMSUSESEGIDX = 0x8
    MAPSYMSFIRST = 0x10
    ABI_FLOAT_SOFT = 0x200
    ABI_FLOAT_HARD = 0x400
    LE8 = 0x400000
    BE8 = 0x800000
    EABI_VER1 = 0x1000000  # these can be added
    EABI_VER2 = 0x2000000  # these can be added
    EABI_VER4 = 0x4000000  # these can be added


@enum.unique
class SHN_INDICES(enum.IntEnum):
    """ Special section indices"""
    UNDEF = 0
    ABS = 0xfff1
    COMMON = 0xfff2
    HIRESERVE = 0xffff


@enum.unique
class SH_FLAGS(enum.Flag):
    """ Flag values for the sh_flags field of section headers"""
    WRITE = 0x1
    ALLOC = 0x2
    EXECINSTR = 0x4
    MERGE = 0x10
    STRINGS = 0x20
    INFO_LINK = 0x40
    LINK_ORDER = 0x80
    OS_NONCONFORMING = 0x100
    GROUP = 0x200
    TLS = 0x400
    COMPRESSED = 0x800


@enum.unique
class RH_FLAGS(enum.Flag):
    """ Flag values for the DT_MIPS_FLAGS dynamic table entries"""
    NONE = 0x00000000
    QUICKSTART = 0x00000001
    NOTPOT = 0x00000002
    NO_LIBRARY_REPLACEMENT = 0x00000004
    NO_MOVE = 0x00000008
    SGI_ONLY = 0x00000010
    GUARANTEE_INIT = 0x00000020
    DELTA_C_PLUS_PLUS = 0x00000040
    GUARANTEE_START_INIT = 0x00000080
    PIXIE = 0x00000100
    DEFAULT_DELAY_LOAD = 0x00000200
    REQUICKSTART = 0x00000400
    REQUICKSTARTED = 0x00000800
    CORD = 0x00001000
    NO_UNRES_UNDEF = 0x00002000
    RLD_ORDER_SAFE = 0x00004000


@enum.unique
class P_FLAGS(enum.Flag):
    """ Flag values for the p_flags field of program headers"""
    X = 0x1
    W = 0x2
    R = 0x4


@enum.unique
class VER_FLAGS(enum.Flag):
    BASE = 0x1
    WEAK = 0x2
    INFO = 0x4


ENUM = "enum"
FLAG = "flag"
UNSUPPORTED = "unsuported"

# List of all classes in this file
CLASSES = {
    EI_CLASS: (ENUM, 8),
    EI_DATA: (ENUM, 8),
    EI_VERSION: (ENUM, 8),
    EI_OSABI: (ENUM, 8),
    #
    E_TYPE: (ENUM, 16),
    E_MACHINE: (ENUM, 16),
    E_FLAGS_ARM: (FLAG, 32),
    #
    SH_TYPE: (ENUM, 32, (0, 0x6ffffff5, -1)),
    SH_FLAGS: (FLAG, 32),
    #
    P_TYPE: (ENUM, 32, (0, 0x6474e550, 0x70000000, -1)),
    P_FLAGS: (FLAG, 32),
    #
    ST_INFO_BIND: (ENUM, 8),
    ST_INFO_TYPE: (ENUM, 8),
    ST_VISIBILITY: (ENUM, 8),

    RELOC_TYPE_ARM: (ENUM, 8),
    #
    # enums marked UNSUPPORTED are currently not exported to C++
    #
    D_TAG_COMMON: (UNSUPPORTED,),
    D_TAG_MIPS: (UNSUPPORTED,),
    DT_FLAGS: (UNSUPPORTED,),
    DT_FLAGS_1: (UNSUPPORTED,),
    RELOC_TYPE_MIPS: (UNSUPPORTED,),
    RELOC_TYPE_i386: (UNSUPPORTED,),
    RELOC_TYPE_X86_64: (ENUM, 8),
    VERSYM_NDX: (UNSUPPORTED,),
    NOTE_N_TYPE: (UNSUPPORTED,),
    CORE_NOTE_N_TYPE: (UNSUPPORTED,),
    ELF_NOTE_ABI_TAG_OS: (UNSUPPORTED,),
    RELOC_TYPE_AARCH64: (ENUM, 16),
    ATTR_ARM: (UNSUPPORTED,),

    SHN_INDICES: (UNSUPPORTED,),
    ELF_COMPRESS: (UNSUPPORTED,),
    RH_FLAGS: (UNSUPPORTED,),
    VER_FLAGS: (UNSUPPORTED,),
}

# magic values for st_shndx
ST_SHNDX_UNDEF = 0
ST_SHNDX_ABS = 0xfff1
ST_SHNDX_COMMON = 0xfff2


def _EnumGenerator(cls, first, last):
    pos = first
    for sym in cls:
        val = sym.value
        if val < first: continue
        if val >= last >= 0: return
        yield sym.name, val


def EmitEnumsH(fout):
    for cls, info in CLASSES.items():
        if info[0] is UNSUPPORTED: continue
        name = f"class {cls.__name__} : uint{info[1]}_t"
        cgen.RenderEnum(cgen.NameValues(cls), name, fout)


def EmitEnumsC(fout):
    for cls, info in CLASSES.items():
        if info[0] is UNSUPPORTED: continue
        if info[0] is FLAG:
            cgen.RenderEnumToStringMapFlag(
                cgen.NameValues(cls), cls.__name__, fout)
            cgen.RenderEnumToStringFun(cls.__name__, fout)
        elif info[1] in {8, 16}:
            cgen.RenderEnumToStringMap(
                cgen.NameValues(cls), cls.__name__, fout)
            cgen.RenderEnumToStringFun(cls.__name__, fout)
        elif info[1] == 32:
            for n, first in enumerate(info[2]):
                if first == -1: continue
                last = info[2][n + 1]
                cgen.RenderEnumToStringMap(_EnumGenerator(cls, first, last),
                                           f"{cls.__name__ }_{first:x}",
                                           fout, first)


if __name__ == "__main__":
    import sys

    if len(sys.argv) <= 1:
        EmitEnumsH(sys.stdout)
    elif sys.argv[1] == "gen_h":
        cgen.ReplaceContent(EmitEnumsH, sys.stdin, sys.stdout)
    elif sys.argv[1] == "gen_c":
        cgen.ReplaceContent(EmitEnumsC, sys.stdin, sys.stdout)
