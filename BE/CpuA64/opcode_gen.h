#pragma once
// (c) Robert Muth - see LICENSE for more info
// NOTE: this file is PARTIALLY autogenerated via: ./opcode_tab.py gen_h

#include "BE/Elf/enum_gen.h"  // for reloc types

#include <cstdint>
#include <string_view>

namespace cwerg::a64 {
using namespace cwerg;

/* @AUTOGEN-START@ */
constexpr const unsigned MAX_OPERANDS = 5;
constexpr const unsigned MAX_BIT_RANGES = 2;

enum class FK : uint8_t {
    NONE = 0,
    LIST = 1,
    INT = 2,
    INT_HEX = 3,
    INT_SIGNED = 4,
    INT_HEX_CUSTOM = 5,
    FLT_CUSTOM = 6,
};

enum class OK : uint8_t {
    Invalid = 0,
    WREG_0_4 = 1,
    WREG_5_9 = 2,
    WREG_10_14 = 3,
    WREG_16_20 = 4,
    XREG_0_4 = 5,
    XREG_5_9 = 6,
    XREG_10_14 = 7,
    XREG_16_20 = 8,
    SREG_0_4 = 9,
    SREG_5_9 = 10,
    SREG_10_14 = 11,
    SREG_16_20 = 12,
    DREG_0_4 = 13,
    DREG_5_9 = 14,
    DREG_10_14 = 15,
    DREG_16_20 = 16,
    BREG_0_4 = 17,
    BREG_5_9 = 18,
    BREG_10_14 = 19,
    BREG_16_20 = 20,
    HREG_0_4 = 21,
    HREG_5_9 = 22,
    HREG_10_14 = 23,
    HREG_16_20 = 24,
    QREG_0_4 = 25,
    QREG_5_9 = 26,
    QREG_10_14 = 27,
    QREG_16_20 = 28,
    VREG_0_4 = 29,
    VREG_5_9 = 30,
    VREG_10_14 = 31,
    VREG_16_20 = 32,
    WREG_0_4_SP = 33,
    WREG_5_9_SP = 34,
    XREG_0_4_SP = 35,
    XREG_5_9_SP = 36,
    SHIFT_22_23 = 37,
    SHIFT_22_23_NO_ROR = 38,
    SHIFT_15_W = 39,
    SHIFT_15_X = 40,
    SIMM_PCREL_0_25 = 41,
    SIMM_12_20 = 42,
    SIMM_15_21_TIMES_16 = 43,
    SIMM_15_21_TIMES_4 = 44,
    SIMM_15_21_TIMES_8 = 45,
    SIMM_PCREL_5_18 = 46,
    SIMM_PCREL_5_23 = 47,
    SIMM_PCREL_5_23_29_30 = 48,
    IMM_10_12_LIMIT4 = 49,
    IMM_10_15 = 50,
    IMM_10_15_16_22_W = 51,
    IMM_10_15_16_22_X = 52,
    IMM_10_21 = 53,
    IMM_SHIFTED_10_21_22 = 54,
    IMM_10_21_TIMES_16 = 55,
    IMM_10_21_TIMES_2 = 56,
    IMM_10_21_TIMES_4 = 57,
    IMM_10_21_TIMES_8 = 58,
    IMM_12_MAYBE_SHIFT_0 = 59,
    IMM_12_MAYBE_SHIFT_1 = 60,
    IMM_12_MAYBE_SHIFT_2 = 61,
    IMM_12_MAYBE_SHIFT_3 = 62,
    IMM_12_MAYBE_SHIFT_4 = 63,
    IMM_16_20 = 64,
    IMM_16_21 = 65,
    IMM_19_23_31 = 66,
    IMM_5_20 = 67,
    IMM_COND_0_3 = 68,
    IMM_FLT_ZERO = 69,
    IMM_SHIFTED_5_20_21_22 = 70,
    SHIFT_21_22_TIMES_16 = 71,
    IMM_FLT_13_20 = 72,
    IMM_BIT_EXPLODE_5_9_16_18 = 73,
};

enum class MEM_WIDTH : uint8_t {
    NA = 0,
    W1 = 1,
    W2 = 2,
    W4 = 3,
    W8 = 4,
    W16 = 5,
    W32 = 6,
};

enum OPC_FLAG {
    RESULT_64BIT = 1,
    SRC_DST_0_1 = 2,
    DST_0_1 = 4,
    DIV = 8,
    MUL = 16,
    MULACC = 32,
    LOAD = 64,
    STORE = 128,
    ATOMIC = 0x100,
    ATOMIC_WITH_STATUS = 0x200,
    COND_BRANCH = 0x800,
    BRANCH = 0x1000,
    BRANCH_INDIRECT = 0x2000,
    CALL = 0x8000,
    CALL_INDIRECT = 0x100000,
    TEST = 0x20000,
    PREFETCH = 0x40000,
    MULTIPLE = 0x80000,
    SYSCALL = 0x200000,
    IMPLICIT_LINK_REG = 0x800000,
    SR_UPDATE = 0x1000000,
    REG_PAIR = 0x2000000,
    COND_PARAM = 0x4000000,
    DOMAIN_PARAM = 0x8000000,
    EXTENSION_PARAM = 0x10000000,
    STACK_OPS = 0x20000000,
};

enum class SHIFT : uint8_t {
    lsl = 0,
    lsr = 1,
    asr = 2,
    ror = 3,
};

enum class OPC : uint16_t {
    invalid,
    adc_w,
    adc_x,
    adcs_w,
    adcs_x,
    add_w_imm,
    add_w_reg,
    add_w_reg_sxtb,
    add_w_reg_sxth,
    add_w_reg_sxtw,
    add_w_reg_sxtx,
    add_w_reg_uxtb,
    add_w_reg_uxth,
    add_w_reg_uxtw,
    add_w_reg_uxtx,
    add_x_imm,
    add_x_reg,
    add_x_reg_sxtb,
    add_x_reg_sxth,
    add_x_reg_sxtw,
    add_x_reg_sxtx,
    add_x_reg_uxtb,
    add_x_reg_uxth,
    add_x_reg_uxtw,
    add_x_reg_uxtx,
    adds_w_imm,
    adds_w_reg,
    adds_w_reg_sxtb,
    adds_w_reg_sxth,
    adds_w_reg_sxtw,
    adds_w_reg_sxtx,
    adds_w_reg_uxtb,
    adds_w_reg_uxth,
    adds_w_reg_uxtw,
    adds_w_reg_uxtx,
    adds_x_imm,
    adds_x_reg,
    adds_x_reg_sxtb,
    adds_x_reg_sxth,
    adds_x_reg_sxtw,
    adds_x_reg_sxtx,
    adds_x_reg_uxtb,
    adds_x_reg_uxth,
    adds_x_reg_uxtw,
    adds_x_reg_uxtx,
    adr,
    adrp,
    and_16b,
    and_8b,
    and_w_imm,
    and_w_reg,
    and_x_imm,
    and_x_reg,
    ands_w_imm,
    ands_w_reg,
    ands_x_imm,
    ands_x_reg,
    asrv_w,
    asrv_x,
    b,
    b_cc,
    b_cs,
    b_eq,
    b_ge,
    b_gt,
    b_hi,
    b_le,
    b_ls,
    b_lt,
    b_mi,
    b_ne,
    b_pl,
    b_vc,
    b_vs,
    bfm_w,
    bfm_x,
    bic_16b,
    bic_8b,
    bic_w_reg,
    bic_x_reg,
    bics_w_reg,
    bics_x_reg,
    bit_16b,
    bit_8b,
    bl,
    blr,
    br,
    brk,
    cbnz_w,
    cbnz_x,
    cbz_w,
    cbz_x,
    ccmn_w_imm_cc,
    ccmn_w_imm_cs,
    ccmn_w_imm_eq,
    ccmn_w_imm_ge,
    ccmn_w_imm_gt,
    ccmn_w_imm_hi,
    ccmn_w_imm_le,
    ccmn_w_imm_ls,
    ccmn_w_imm_lt,
    ccmn_w_imm_mi,
    ccmn_w_imm_ne,
    ccmn_w_imm_pl,
    ccmn_w_imm_vc,
    ccmn_w_imm_vs,
    ccmn_w_reg_cc,
    ccmn_w_reg_cs,
    ccmn_w_reg_eq,
    ccmn_w_reg_ge,
    ccmn_w_reg_gt,
    ccmn_w_reg_hi,
    ccmn_w_reg_le,
    ccmn_w_reg_ls,
    ccmn_w_reg_lt,
    ccmn_w_reg_mi,
    ccmn_w_reg_ne,
    ccmn_w_reg_pl,
    ccmn_w_reg_vc,
    ccmn_w_reg_vs,
    ccmn_x_imm_cc,
    ccmn_x_imm_cs,
    ccmn_x_imm_eq,
    ccmn_x_imm_ge,
    ccmn_x_imm_gt,
    ccmn_x_imm_hi,
    ccmn_x_imm_le,
    ccmn_x_imm_ls,
    ccmn_x_imm_lt,
    ccmn_x_imm_mi,
    ccmn_x_imm_ne,
    ccmn_x_imm_pl,
    ccmn_x_imm_vc,
    ccmn_x_imm_vs,
    ccmn_x_reg_cc,
    ccmn_x_reg_cs,
    ccmn_x_reg_eq,
    ccmn_x_reg_ge,
    ccmn_x_reg_gt,
    ccmn_x_reg_hi,
    ccmn_x_reg_le,
    ccmn_x_reg_ls,
    ccmn_x_reg_lt,
    ccmn_x_reg_mi,
    ccmn_x_reg_ne,
    ccmn_x_reg_pl,
    ccmn_x_reg_vc,
    ccmn_x_reg_vs,
    ccmp_w_imm_cc,
    ccmp_w_imm_cs,
    ccmp_w_imm_eq,
    ccmp_w_imm_ge,
    ccmp_w_imm_gt,
    ccmp_w_imm_hi,
    ccmp_w_imm_le,
    ccmp_w_imm_ls,
    ccmp_w_imm_lt,
    ccmp_w_imm_mi,
    ccmp_w_imm_ne,
    ccmp_w_imm_pl,
    ccmp_w_imm_vc,
    ccmp_w_imm_vs,
    ccmp_w_reg_cc,
    ccmp_w_reg_cs,
    ccmp_w_reg_eq,
    ccmp_w_reg_ge,
    ccmp_w_reg_gt,
    ccmp_w_reg_hi,
    ccmp_w_reg_le,
    ccmp_w_reg_ls,
    ccmp_w_reg_lt,
    ccmp_w_reg_mi,
    ccmp_w_reg_ne,
    ccmp_w_reg_pl,
    ccmp_w_reg_vc,
    ccmp_w_reg_vs,
    ccmp_x_imm_cc,
    ccmp_x_imm_cs,
    ccmp_x_imm_eq,
    ccmp_x_imm_ge,
    ccmp_x_imm_gt,
    ccmp_x_imm_hi,
    ccmp_x_imm_le,
    ccmp_x_imm_ls,
    ccmp_x_imm_lt,
    ccmp_x_imm_mi,
    ccmp_x_imm_ne,
    ccmp_x_imm_pl,
    ccmp_x_imm_vc,
    ccmp_x_imm_vs,
    ccmp_x_reg_cc,
    ccmp_x_reg_cs,
    ccmp_x_reg_eq,
    ccmp_x_reg_ge,
    ccmp_x_reg_gt,
    ccmp_x_reg_hi,
    ccmp_x_reg_le,
    ccmp_x_reg_ls,
    ccmp_x_reg_lt,
    ccmp_x_reg_mi,
    ccmp_x_reg_ne,
    ccmp_x_reg_pl,
    ccmp_x_reg_vc,
    ccmp_x_reg_vs,
    clrex,
    cls_w,
    cls_x,
    clz_w,
    clz_x,
    cnt_16b,
    cnt_4h,
    cnt_4s,
    cnt_8b,
    cnt_8h,
    csel_w_cc,
    csel_w_cs,
    csel_w_eq,
    csel_w_ge,
    csel_w_gt,
    csel_w_hi,
    csel_w_le,
    csel_w_ls,
    csel_w_lt,
    csel_w_mi,
    csel_w_ne,
    csel_w_pl,
    csel_w_vc,
    csel_w_vs,
    csel_x_cc,
    csel_x_cs,
    csel_x_eq,
    csel_x_ge,
    csel_x_gt,
    csel_x_hi,
    csel_x_le,
    csel_x_ls,
    csel_x_lt,
    csel_x_mi,
    csel_x_ne,
    csel_x_pl,
    csel_x_vc,
    csel_x_vs,
    csinc_w_cc,
    csinc_w_cs,
    csinc_w_eq,
    csinc_w_ge,
    csinc_w_gt,
    csinc_w_hi,
    csinc_w_le,
    csinc_w_ls,
    csinc_w_lt,
    csinc_w_mi,
    csinc_w_ne,
    csinc_w_pl,
    csinc_w_vc,
    csinc_w_vs,
    csinc_x_cc,
    csinc_x_cs,
    csinc_x_eq,
    csinc_x_ge,
    csinc_x_gt,
    csinc_x_hi,
    csinc_x_le,
    csinc_x_ls,
    csinc_x_lt,
    csinc_x_mi,
    csinc_x_ne,
    csinc_x_pl,
    csinc_x_vc,
    csinc_x_vs,
    csinv_w_cc,
    csinv_w_cs,
    csinv_w_eq,
    csinv_w_ge,
    csinv_w_gt,
    csinv_w_hi,
    csinv_w_le,
    csinv_w_ls,
    csinv_w_lt,
    csinv_w_mi,
    csinv_w_ne,
    csinv_w_pl,
    csinv_w_vc,
    csinv_w_vs,
    csinv_x_cc,
    csinv_x_cs,
    csinv_x_eq,
    csinv_x_ge,
    csinv_x_gt,
    csinv_x_hi,
    csinv_x_le,
    csinv_x_ls,
    csinv_x_lt,
    csinv_x_mi,
    csinv_x_ne,
    csinv_x_pl,
    csinv_x_vc,
    csinv_x_vs,
    csneg_w_cc,
    csneg_w_cs,
    csneg_w_eq,
    csneg_w_ge,
    csneg_w_gt,
    csneg_w_hi,
    csneg_w_le,
    csneg_w_ls,
    csneg_w_lt,
    csneg_w_mi,
    csneg_w_ne,
    csneg_w_pl,
    csneg_w_vc,
    csneg_w_vs,
    csneg_x_cc,
    csneg_x_cs,
    csneg_x_eq,
    csneg_x_ge,
    csneg_x_gt,
    csneg_x_hi,
    csneg_x_le,
    csneg_x_ls,
    csneg_x_lt,
    csneg_x_mi,
    csneg_x_ne,
    csneg_x_pl,
    csneg_x_vc,
    csneg_x_vs,
    dmb_ish,
    dmb_ishld,
    dmb_ishst,
    dsb_ish,
    dsb_ishld,
    dsb_ishst,
    eon_w_reg,
    eon_x_reg,
    eor_16b,
    eor_8b,
    eor_w_imm,
    eor_w_reg,
    eor_x_imm,
    eor_x_reg,
    eret,
    extr_w,
    extr_x,
    fabd_d,
    fabd_s,
    fabs_d,
    fabs_s,
    fadd_2d,
    fadd_2s,
    fadd_4s,
    fadd_d,
    fadd_s,
    faddp_2d,
    faddp_2s,
    faddp_4s,
    fccmp_d_cc,
    fccmp_d_cs,
    fccmp_d_eq,
    fccmp_d_ge,
    fccmp_d_gt,
    fccmp_d_hi,
    fccmp_d_le,
    fccmp_d_ls,
    fccmp_d_lt,
    fccmp_d_mi,
    fccmp_d_ne,
    fccmp_d_pl,
    fccmp_d_vc,
    fccmp_d_vs,
    fccmp_s_cc,
    fccmp_s_cs,
    fccmp_s_eq,
    fccmp_s_ge,
    fccmp_s_gt,
    fccmp_s_hi,
    fccmp_s_le,
    fccmp_s_ls,
    fccmp_s_lt,
    fccmp_s_mi,
    fccmp_s_ne,
    fccmp_s_pl,
    fccmp_s_vc,
    fccmp_s_vs,
    fcmge_d,
    fcmge_s,
    fcmgt_d,
    fcmgt_s,
    fcmp_d,
    fcmp_d_zero,
    fcmp_s,
    fcmp_s_zero,
    fcmpe_d,
    fcmpe_d_zero,
    fcmpe_s,
    fcmpe_s_zero,
    fcsel_d_cc,
    fcsel_d_cs,
    fcsel_d_eq,
    fcsel_d_ge,
    fcsel_d_gt,
    fcsel_d_hi,
    fcsel_d_le,
    fcsel_d_ls,
    fcsel_d_lt,
    fcsel_d_mi,
    fcsel_d_ne,
    fcsel_d_pl,
    fcsel_d_vc,
    fcsel_d_vs,
    fcsel_s_cc,
    fcsel_s_cs,
    fcsel_s_eq,
    fcsel_s_ge,
    fcsel_s_gt,
    fcsel_s_hi,
    fcsel_s_le,
    fcsel_s_ls,
    fcsel_s_lt,
    fcsel_s_mi,
    fcsel_s_ne,
    fcsel_s_pl,
    fcsel_s_vc,
    fcsel_s_vs,
    fcvt_d_h,
    fcvt_d_s,
    fcvt_h_d,
    fcvt_h_s,
    fcvt_s_d,
    fcvt_s_h,
    fcvtas_w_d,
    fcvtas_w_s,
    fcvtas_x_d,
    fcvtas_x_s,
    fcvtau_w_d,
    fcvtau_w_s,
    fcvtau_x_d,
    fcvtau_x_s,
    fcvtms_w_d,
    fcvtms_w_s,
    fcvtms_x_d,
    fcvtms_x_s,
    fcvtmu_w_d,
    fcvtmu_w_s,
    fcvtmu_x_d,
    fcvtmu_x_s,
    fcvtns_w_d,
    fcvtns_w_s,
    fcvtns_x_d,
    fcvtns_x_s,
    fcvtnu_w_d,
    fcvtnu_w_s,
    fcvtnu_x_d,
    fcvtnu_x_s,
    fcvtps_w_d,
    fcvtps_w_s,
    fcvtps_x_d,
    fcvtps_x_s,
    fcvtpu_w_d,
    fcvtpu_w_s,
    fcvtpu_x_d,
    fcvtpu_x_s,
    fcvtzs_w_d,
    fcvtzs_w_s,
    fcvtzs_x_d,
    fcvtzs_x_s,
    fcvtzu_w_d,
    fcvtzu_w_s,
    fcvtzu_x_d,
    fcvtzu_x_s,
    fdiv_d,
    fdiv_s,
    fldp_d_imm,
    fldp_d_imm_post,
    fldp_d_imm_pre,
    fldp_q_imm,
    fldp_q_imm_post,
    fldp_q_imm_pre,
    fldp_s_imm,
    fldp_s_imm_post,
    fldp_s_imm_pre,
    fldr_b_imm,
    fldr_b_imm_post,
    fldr_b_imm_pre,
    fldr_b_reg_w,
    fldr_b_reg_x,
    fldr_d_imm,
    fldr_d_imm_post,
    fldr_d_imm_pre,
    fldr_d_reg_w,
    fldr_d_reg_x,
    fldr_h_imm,
    fldr_h_imm_post,
    fldr_h_imm_pre,
    fldr_h_reg_w,
    fldr_h_reg_x,
    fldr_q_imm,
    fldr_q_imm_post,
    fldr_q_imm_pre,
    fldr_q_reg_w,
    fldr_q_reg_x,
    fldr_s_imm,
    fldr_s_imm_post,
    fldr_s_imm_pre,
    fldr_s_reg_w,
    fldr_s_reg_x,
    fldur_b_imm,
    fldur_d_imm,
    fldur_h_imm,
    fldur_q_imm,
    fldur_s_imm,
    fmadd_d,
    fmadd_s,
    fmax_2d,
    fmax_2s,
    fmax_4s,
    fmax_d,
    fmax_s,
    fmaxnm_2d,
    fmaxnm_2s,
    fmaxnm_4s,
    fmaxnm_d,
    fmaxnm_s,
    fmaxp_2d,
    fmaxp_2s,
    fmaxp_4s,
    fmin_d,
    fmin_s,
    fminnm_d,
    fminnm_s,
    fmov_d_from_x,
    fmov_d_imm,
    fmov_d_reg,
    fmov_s_from_w,
    fmov_s_imm,
    fmov_s_reg,
    fmov_w_from_s,
    fmov_x_from_d,
    fmsub_d,
    fmsub_s,
    fmul_d,
    fmul_s,
    fneg_2d,
    fneg_2s,
    fneg_4s,
    fneg_d,
    fneg_s,
    fnmadd_d,
    fnmadd_s,
    fnmsub_d,
    fnmsub_s,
    fnmul_d,
    fnmul_s,
    frinta_d,
    frinta_s,
    frinti_d,
    frinti_s,
    frintm_d,
    frintm_s,
    frintn_d,
    frintn_s,
    frintp_d,
    frintp_s,
    frintx_d,
    frintx_s,
    frintz_d,
    frintz_s,
    fsqrt_d,
    fsqrt_s,
    fstp_d_imm,
    fstp_d_imm_post,
    fstp_d_imm_pre,
    fstp_q_imm,
    fstp_q_imm_post,
    fstp_q_imm_pre,
    fstp_s_imm,
    fstp_s_imm_post,
    fstp_s_imm_pre,
    fstr_b_imm,
    fstr_b_imm_post,
    fstr_b_imm_pre,
    fstr_b_reg_w,
    fstr_b_reg_x,
    fstr_d_imm,
    fstr_d_imm_post,
    fstr_d_imm_pre,
    fstr_d_reg_w,
    fstr_d_reg_x,
    fstr_h_imm,
    fstr_h_imm_post,
    fstr_h_imm_pre,
    fstr_h_reg_w,
    fstr_h_reg_x,
    fstr_q_imm,
    fstr_q_imm_post,
    fstr_q_imm_pre,
    fstr_q_reg_w,
    fstr_q_reg_x,
    fstr_s_imm,
    fstr_s_imm_post,
    fstr_s_imm_pre,
    fstr_s_reg_w,
    fstr_s_reg_x,
    fstur_b_imm,
    fstur_d_imm,
    fstur_h_imm,
    fstur_q_imm,
    fstur_s_imm,
    fsub_d,
    fsub_s,
    hlt,
    isb,
    ldar_b,
    ldar_h,
    ldar_w,
    ldar_x,
    ldaxr_b,
    ldaxr_h,
    ldaxr_w,
    ldaxr_x,
    ldp_sw_imm,
    ldp_sw_imm_post,
    ldp_sw_imm_pre,
    ldp_w_imm,
    ldp_w_imm_post,
    ldp_w_imm_pre,
    ldp_x_imm,
    ldp_x_imm_post,
    ldp_x_imm_pre,
    ldr_b_imm,
    ldr_b_imm_post,
    ldr_b_imm_pre,
    ldr_b_reg_w,
    ldr_b_reg_x,
    ldr_h_imm,
    ldr_h_imm_post,
    ldr_h_imm_pre,
    ldr_h_reg_w,
    ldr_h_reg_x,
    ldr_w_imm,
    ldr_w_imm_post,
    ldr_w_imm_pre,
    ldr_w_reg_w,
    ldr_w_reg_x,
    ldr_x_imm,
    ldr_x_imm_post,
    ldr_x_imm_pre,
    ldr_x_reg_w,
    ldr_x_reg_x,
    ldrsb_w_imm,
    ldrsb_w_imm_post,
    ldrsb_w_imm_pre,
    ldrsb_w_reg_w,
    ldrsb_w_reg_x,
    ldrsb_x_imm,
    ldrsb_x_imm_post,
    ldrsb_x_imm_pre,
    ldrsb_x_reg_w,
    ldrsb_x_reg_x,
    ldrsh_w_imm,
    ldrsh_w_imm_post,
    ldrsh_w_imm_pre,
    ldrsh_w_reg_w,
    ldrsh_w_reg_x,
    ldrsh_x_imm,
    ldrsh_x_imm_post,
    ldrsh_x_imm_pre,
    ldrsh_x_reg_w,
    ldrsh_x_reg_x,
    ldrsw_imm,
    ldrsw_imm_post,
    ldrsw_imm_pre,
    ldrsw_reg_w,
    ldrsw_reg_x,
    ldur_b_imm,
    ldur_h_imm,
    ldur_w_imm,
    ldur_x_imm,
    ldursb_w_imm,
    ldursb_x_imm,
    ldursh_w_imm,
    ldursh_x_imm,
    ldursw_imm_post,
    ldxr_b,
    ldxr_h,
    ldxr_w,
    ldxr_x,
    lslv_w,
    lslv_x,
    lsrv_w,
    lsrv_x,
    madd_w,
    madd_x,
    movi_2d,
    movk_w_imm,
    movk_x_imm,
    movn_w_imm,
    movn_x_imm,
    movz_w_imm,
    movz_x_imm,
    msub_w,
    msub_x,
    nop,
    orn_16b,
    orn_8b,
    orn_w_reg,
    orn_x_reg,
    orr_16b,
    orr_8b,
    orr_w_imm,
    orr_w_reg,
    orr_x_imm,
    orr_x_reg,
    pmull2_16b,
    pmull2_2d,
    pmull_1d,
    pmull_8b,
    rbit_w,
    rbit_x,
    ret,
    rev16_w,
    rev16_x,
    rev32,
    rev_w,
    rev_x,
    rorv_w,
    rorv_x,
    sbc_w,
    sbc_x,
    sbcs_w,
    sbcs_x,
    sbfm_w,
    sbfm_x,
    scvtf_d_from_w,
    scvtf_d_from_x,
    scvtf_s_from_w,
    scvtf_s_from_x,
    sdiv_w,
    sdiv_x,
    smaddl,
    smsubl,
    smulh,
    stlr_b,
    stlr_h,
    stlr_w,
    stlr_x,
    stlxr_b,
    stlxr_h,
    stlxr_w,
    stlxr_x,
    stp_w_imm,
    stp_w_imm_post,
    stp_w_imm_pre,
    stp_x_imm,
    stp_x_imm_post,
    stp_x_imm_pre,
    str_b_imm,
    str_b_imm_post,
    str_b_imm_pre,
    str_b_reg_w,
    str_b_reg_x,
    str_h_imm,
    str_h_imm_post,
    str_h_imm_pre,
    str_h_reg_w,
    str_h_reg_x,
    str_w_imm,
    str_w_imm_post,
    str_w_imm_pre,
    str_w_reg_w,
    str_w_reg_x,
    str_x_imm,
    str_x_imm_post,
    str_x_imm_pre,
    str_x_reg_w,
    str_x_reg_x,
    stur_b_imm,
    stur_h_imm,
    stur_w_imm,
    stur_x_imm,
    stxr_b,
    stxr_h,
    stxr_w,
    stxr_x,
    sub_w_imm,
    sub_w_reg,
    sub_w_reg_sxtb,
    sub_w_reg_sxth,
    sub_w_reg_sxtw,
    sub_w_reg_sxtx,
    sub_w_reg_uxtb,
    sub_w_reg_uxth,
    sub_w_reg_uxtw,
    sub_w_reg_uxtx,
    sub_x_imm,
    sub_x_reg,
    sub_x_reg_sxtb,
    sub_x_reg_sxth,
    sub_x_reg_sxtw,
    sub_x_reg_sxtx,
    sub_x_reg_uxtb,
    sub_x_reg_uxth,
    sub_x_reg_uxtw,
    sub_x_reg_uxtx,
    subs_w_imm,
    subs_w_reg,
    subs_w_reg_sxtb,
    subs_w_reg_sxth,
    subs_w_reg_sxtw,
    subs_w_reg_sxtx,
    subs_w_reg_uxtb,
    subs_w_reg_uxth,
    subs_w_reg_uxtw,
    subs_w_reg_uxtx,
    subs_x_imm,
    subs_x_reg,
    subs_x_reg_sxtb,
    subs_x_reg_sxth,
    subs_x_reg_sxtw,
    subs_x_reg_sxtx,
    subs_x_reg_uxtb,
    subs_x_reg_uxth,
    subs_x_reg_uxtw,
    subs_x_reg_uxtx,
    svc,
    tbnz,
    tbz,
    uaddlv_16b,
    uaddlv_4h,
    uaddlv_4s,
    uaddlv_8b,
    uaddlv_8h,
    ubfm_w,
    ubfm_x,
    ucvtf_d_from_w,
    ucvtf_d_from_x,
    ucvtf_s_from_w,
    ucvtf_s_from_x,
    udiv_w,
    udiv_x,
    umaddl,
    umsubl,
    umulh,
    yield,
};
/* @AUTOGEN-END@ */

// Describes a class of instructions structurally (read-only data).
struct Opcode {
  std::string_view name;  // base name + variant
  uint32_t bit_mask;
  uint32_t bit_value;
  uint8_t num_fields;
  OK fields[MAX_OPERANDS];
  uint32_t classes;
};

// Indexed by OPC
extern const Opcode OpcodeTable[];

// Find the Opcode or null for a 32 bit instruction word
extern const Opcode* FindOpcode(uint32_t bit_value);

// Find the Opcode or null with the given name
extern const Opcode* FindOpcodeForMnemonic(std::string_view name);

// Decoded representation of the instruction word
struct Ins {
  const Opcode* opcode;
  // number of used entries is ArmOpcode.num_fields
  uint32_t operands[MAX_OPERANDS];
  // Relocation info
  std::string_view reloc_symbol;
  elf::RELOC_TYPE_AARCH64 reloc_kind = elf::RELOC_TYPE_AARCH64::NONE;
  uint8_t reloc_pos;  // index into  operands
  bool is_local_sym = false;
  bool has_reloc() const { return reloc_kind != elf::RELOC_TYPE_AARCH64::NONE; }

  void clear_reloc() {
    if (has_reloc()) {
      reloc_kind = elf::RELOC_TYPE_AARCH64::NONE;
      operands[reloc_pos] = 0;
    }
  }

  void set_reloc(elf::RELOC_TYPE_AARCH64 kind,
                 bool is_local,
                 uint8_t pos,
                 std::string_view symbol) {
    reloc_kind = kind;
    is_local_sym = is_local;
    reloc_pos = pos;
    reloc_symbol = symbol;
  }
};

// Decode the instruction word `data`
// Returns true if successful
extern bool Disassemble(Ins* ins, uint32_t data);

// Encode the instruction
// Returns the instruction word. Asserts if unsuccessful
extern uint32_t Assemble(const Ins& ins);

extern uint32_t Patch(uint32_t data, unsigned pos, int32_t value);

struct BitRange {
  uint8_t width;  // if this is zero , the bitrange is invalid
  uint8_t position;
};

struct FieldInfo {
  BitRange ranges[MAX_BIT_RANGES];
  const char* const* names;  // points  PRED_ToStringMap, SHIFT_ToStringMap etc
  uint64_t (*decoder)(uint32_t);
  uint32_t (*encoder)(uint64_t);
  uint8_t bitwidth;
  FK kind;
  uint8_t scale;
  uint8_t num_names;
};

// Indexed by OK
extern const FieldInfo FieldInfoTable[];

const uint32_t kEncodeFailure = 0xffffffff;

// Note, this returns the unsigned equivalent of the signed quantity
extern uint64_t SignedInt64FromBits(uint64_t data, unsigned n_bits);

extern uint64_t Decode_10_15_16_22_W(uint32_t x);
extern uint64_t Decode_10_15_16_22_X(uint32_t x);

// will return  kEncodeFailure if the value cannot be encoded
extern uint32_t Encode_10_15_16_22_W(uint64_t x);
extern uint32_t Encode_10_15_16_22_X(uint64_t x);

// will return  kEncodeFailure if the value cannot be encoded
extern uint32_t Encode8BitFlt(uint64_t ieee64);

extern uint64_t Decode8BitFlt(uint32_t x);

extern uint64_t DecodeOperand(OK ok, uint32_t data);

// will return  kEncodeFailure if the value cannot be encoded
extern uint32_t EncodeOperand(OK ok, uint64_t data);

extern const char* EnumToString(SHIFT x);
extern const char* EnumToString(OK x);

}  // namespace cwerg::a64
