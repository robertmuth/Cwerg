module:

import cmp

import fmt

import string

import parse_real

import random

import test

import v64 = vec_gen (r64)

fun Test_Dim2() void:
    test::AssertTrue#(
                      v64::eq(v64::ID_mat2,
                        {v64::mat2: v64::X_vec2, v64::Y_vec2}))
    test::AssertTrue#(
                      v64::eq(v64::ONES_vec2, v64::add(v64::X_vec2, v64::Y_vec2)
                        ))
    test::AssertTrue#(
                      v64::eq(v64::X_vec2, v64::sub(v64::ONES_vec2, v64::Y_vec2)
                        ))
    test::AssertEq#(1_r64, v64::dot(v64::ONES_vec2, v64::Y_vec2))
    test::AssertEq#(2_r64, v64::dot(v64::ONES_vec2, v64::ONES_vec2))
    test::AssertEq#(20_r64,
                    v64::dot(v64::ONES_vec2, v64::scaled(v64::ONES_vec2, 10)))
    test::AssertTrue#(
                      v64::eq(v64::ONES_vec2,
                        v64::pmax(v64::X_vec2, v64::Y_vec2)))
    test::AssertTrue#(
                      v64::eq(v64::ONES_vec2,
                        v64::pmax(v64::ONES_vec2, v64::Y_vec2)))
    test::AssertTrue#(
                      v64::eq(v64::ZERO_vec2,
                        v64::pmin(v64::X_vec2, v64::Y_vec2)))
    test::AssertTrue#(
                      v64::eq(v64::Y_vec2,
                        v64::pmin(v64::ONES_vec2, v64::Y_vec2)))
    let m_1 = {v64::mat2: v64::Y_vec2, v64::X_vec2}
    let m_2 = {v64::mat2:
               {: 1, 3}, {: 5, 7}}
    let m_3 = {v64::mat2:
               {: 5, 7}, {: 1, 3}}
    let m_4 = {v64::mat2:
               {: 3, 1}, {: 7, 5}}
    test::AssertTrue#(
                      v64::eq(v64::X_vec2, v64::mulmv(v64::ID_mat2, v64::X_vec2)
                        ))
    test::AssertTrue#(
                      v64::eq(v64::X_vec2, v64::mulvm(v64::X_vec2, v64::ID_mat2)
                        ))
    test::AssertTrue#(v64::eq(v64::Y_vec2, v64::mulmv(m_1, v64::X_vec2)))
    test::AssertTrue#(v64::eq(v64::Y_vec2, v64::mulvm(v64::X_vec2, m_1)))
    ; row major
    test::AssertEq#(1_r64, m_2[0][0])
    test::AssertEq#(3_r64, m_2[0][1])
    test::AssertEq#(5_r64, m_2[1][0])
    test::AssertEq#(7_r64, m_2[1][1])
    test::AssertTrue#(
                      v64::eq(v64::ID_mat2,
                        v64::mulmm(v64::ID_mat2, v64::ID_mat2)))
    test::AssertTrue#(v64::eq(m_2, v64::mulmm(m_2, v64::ID_mat2)))
    test::AssertTrue#(v64::eq(m_2, v64::mulmm(v64::ID_mat2, m_2)))
    test::AssertTrue#(v64::eq(m_3, v64::mulmm(m_1, m_2)))
    test::AssertTrue#(v64::eq(m_4, v64::mulmm(m_2, m_1)))

fun Test_Dim3() void:
    test::AssertTrue#(
                      v64::eq(v64::ID_mat3,
                        {v64::mat3: v64::X_vec3, v64::Y_vec3, v64::Z_vec3}))
    test::AssertTrue#(
                      v64::eq(v64::ONES_vec3,
                        v64::add(v64::add(v64::X_vec3, v64::Y_vec3),
                          v64::Z_vec3)))
    test::AssertTrue#(
                      v64::eq(v64::X_vec3,
                        v64::sub(v64::sub(v64::ONES_vec3, v64::Y_vec3),
                          v64::Z_vec3)))
    test::AssertEq#(1_r64, v64::dot(v64::ONES_vec3, v64::Y_vec3))
    test::AssertEq#(3_r64, v64::dot(v64::ONES_vec3, v64::ONES_vec3))
    test::AssertEq#(30_r64,
                    v64::dot(v64::ONES_vec3, v64::scaled(v64::ONES_vec3, 10)))
    test::AssertTrue#(
                      v64::eq(v64::ONES_vec3,
                        v64::pmax(v64::pmax(v64::X_vec3, v64::Y_vec3),
                          v64::Z_vec3)))
    test::AssertTrue#(
                      v64::eq(v64::ONES_vec3,
                        v64::pmax(v64::ONES_vec3, v64::Y_vec3)))
    test::AssertTrue#(
                      v64::eq(v64::ZERO_vec3,
                        v64::pmin(v64::X_vec3, v64::Y_vec3)))
    test::AssertTrue#(
                      v64::eq(v64::Y_vec3,
                        v64::pmin(v64::ONES_vec3, v64::Y_vec3)))
    let m_1 = {v64::mat3: v64::Z_vec3, v64::Y_vec3, v64::X_vec3}
    let m_2 = {v64::mat3:
               {: 1, 3, 5}, {: 7, 11, 13}, {: 17, 19, 23}}
    let m_3 = {v64::mat3:
               {: 17, 19, 23}, {: 7, 11, 13}, {: 1, 3, 5}}
    let m_4 = {v64::mat3:
               {: 5, 3, 1}, {: 13, 11, 7}, {: 23, 19, 17}}
    test::AssertTrue#(
                      v64::eq(v64::X_vec3, v64::mulmv(v64::ID_mat3, v64::X_vec3)
                        ))
    test::AssertTrue#(
                      v64::eq(v64::X_vec3, v64::mulvm(v64::X_vec3, v64::ID_mat3)
                        ))
    test::AssertTrue#(v64::eq(v64::Z_vec3, v64::mulmv(m_1, v64::X_vec3)))
    test::AssertTrue#(v64::eq(v64::Z_vec3, v64::mulvm(v64::X_vec3, m_1)))
    ; row major
    test::AssertEq#(1_r64, m_2[0][0])
    test::AssertEq#(3_r64, m_2[0][1])
    test::AssertEq#(5_r64, m_2[0][2])
    test::AssertEq#(7_r64, m_2[1][0])
    test::AssertEq#(11_r64, m_2[1][1])
    test::AssertEq#(13_r64, m_2[1][2])
    test::AssertEq#(17_r64, m_2[2][0])
    test::AssertEq#(19_r64, m_2[2][1])
    test::AssertEq#(23_r64, m_2[2][2])
    test::AssertTrue#(
                      v64::eq(v64::ID_mat3,
                        v64::mulmm(v64::ID_mat3, v64::ID_mat3)))
    test::AssertTrue#(v64::eq(m_2, v64::mulmm(m_2, v64::ID_mat3)))
    test::AssertTrue#(v64::eq(m_2, v64::mulmm(v64::ID_mat3, m_2)))
    test::AssertTrue#(v64::eq(m_3, v64::mulmm(m_1, m_2)))
    test::AssertTrue#(v64::eq(m_4, v64::mulmm(m_2, m_1)))
    ;
    test::AssertTrue#(v64::eq(v64::Z_vec3, v64::cross(v64::X_vec3, v64::Y_vec3))
                      )
    test::AssertTrue#(
                      v64::eq(v64::scaled(v64::Z_vec3, -1),
                        v64::cross(v64::Y_vec3, v64::X_vec3)))

fun Test_HitDim3() void:
    ref let! hit v64::HitInfo
    let ray_orig = {v64::vec3: 1, 1, 1}
    let ray_dir = {v64::vec3: 0, 1, 0}
    let REL_ERR r64 = 0.000000001
    ; inside
    test::AssertTrue#(
                      v64::CheckRayHitsSphere(ray_orig, ray_dir, {: 2, 1, 1}, 2,
                        REL_ERR, @!hit))
    test::AssertGenericEq#({cmp::r64r: hit.distance * hit.distance},
                           {cmp::r64r: 3, REL_ERR})
    if false:
        test::AssertTrue#(
                          v64::CheckRayHitsSphere(ray_orig, ray_dir,
                            {: 2.5, 4.5, 1}, 2, REL_ERR, @!hit))
    if false:
        ; test::AssertTrue#(v64::CheckRayHitsSphere(
        ;      ray_orig, ray_dir, {: 0, 5, 1}, 1, REL_ERR, @!hit))
        fmt::print#(hit, "\n")
    if false:
        test::AssertFalse#(
                           v64::CheckRayHitsSphere(ray_orig, ray_dir,
                             {: -2.5, 1, 1}, 1, REL_ERR, @!hit))
        test::AssertFalse#(
                           v64::CheckRayHitsSphere(ray_orig, ray_dir,
                             {: 1, -1, 1}, 1, REL_ERR, @!hit))

fun main(argc s32, argv ^^u8) s32:
    do Test_Dim2()
    do Test_Dim3()
    do Test_HitDim3()
    ; test end
    test::Success#()
    return 0
