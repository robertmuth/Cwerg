;; Test globals

(module

  (import "wasi" "print_i32_ln" (func $wasi$print_i32_ln (param i32)))
  (import "wasi" "print_i64_ln" (func $wasi$print_i64_ln (param i64)))

  (global $0 i32 (i32.const 0))
  (global $1 i64 (i64.const 0))
  (global $a i32 (i32.const -2))
  (global $3 f32 (f32.const -3))
  (global $4 f64 (f64.const -4))
  (global $b i64 (i64.const -5))

  (global $x (mut i32) (i32.const -12))
  (global $7 (mut f32) (f32.const -13))
  (global $8 (mut f64) (f64.const -14))
  (global $y (mut i64) (i64.const -15))

  (global $z1 i32 (i32.const 0))
  (global $z2 i64 (i64.const 0))

;;  (global $r externref (ref.null extern))
;;  (global $mr (mut externref) (ref.null extern))
;;  (global funcref (ref.null func))

  (func $get_a (export "get_a") (result i32) (global.get $a))
  (func $get_b (export "get_b") (result i64) (global.get $b))
;;  (func (export "get-r") (result externref) (global.get $r))
;;  (func (export "get-mr") (result externref) (global.get $mr))
  (func $get_x (export "get_x") (result i32) (global.get $x))
  (func $get_y (export "get_y") (result i64) (global.get $y))
  (func $get_z1 (export "get_z1") (result i32) (global.get $z1))
  (func $get_z2 (export "get_z2") (result i64) (global.get $z2))
  (func $set_x (export "set_x") (param i32) (global.set $x (local.get 0)))
  (func $set_y (export "set_y") (param i64) (global.set $y (local.get 0)))
;;  (func $set_mr (export "set_mr") (param externref) (global.set $mr (local.get 0)))

  (func $get_3 (export "get_3") (result f32) (global.get $3))
  (func $get_4 (export "get_4") (result f64) (global.get $4))
  (func $get_7 (export "get_7") (result f32) (global.get $7))
  (func $get_8 (export "get_8") (result f64) (global.get $8))
  (func $set_7 (export "set_7") (param f32) (global.set $7 (local.get 0)))
  (func $set_8 (export "set_8") (param f64) (global.set $8 (local.get 0)))

  ;; As the argument of control constructs and instructions

  (memory 1)

  (func $dummy)

  (func $as_select_first (export "as_select_first") (result i32)
    (select (global.get $x) (i32.const 2) (i32.const 3))
  )
  (func $as_select_mid (export "as_select_mid") (result i32)
    (select (i32.const 2) (global.get $x) (i32.const 3))
  )
  (func $as_select_last (export "as_select_last") (result i32)
    (select (i32.const 2) (i32.const 3) (global.get $x))
  )

  (func $as_loop_first (export "as_loop_first") (result i32)
    (loop (result i32)
      (global.get $x) (call $dummy) (call $dummy)
    )
  )
  (func $as_loop_mid (export "as_loop_mid") (result i32)
    (loop (result i32)
      (call $dummy) (global.get $x) (call $dummy)
    )
  )
  (func $as_loop_last (export "as_loop_last") (result i32)
    (loop (result i32)
      (call $dummy) (call $dummy) (global.get $x)
    )
  )

  (func $as_if_condition (export "as_if_condition") (result i32)
    (if (result i32) (global.get $x)
      (then (call $dummy) (i32.const 2))
      (else (call $dummy) (i32.const 3))
    )
  )
  (func $as_if_then (export "as_if_then") (result i32)
    (if (result i32) (i32.const 1)
      (then (global.get $x)) (else (i32.const 2))
    )
  )
  (func $as_if_else (export "as_if_else") (result i32)
    (if (result i32) (i32.const 0)
      (then (i32.const 2)) (else (global.get $x))
    )
  )

  (func $as_br_if_first (export "as_br_if_first") (result i32)
    (block (result i32)
      (br_if 0 (global.get $x) (i32.const 2))
      (return (i32.const 3))
    )
  )
  (func $as_br_if_last (export "as_br_if_last") (result i32)
    (block (result i32)
      (br_if 0 (i32.const 2) (global.get $x))
      (return (i32.const 3))
    )
  )

  (func $as_br_table_first (export "as_br_table_first") (result i32)
    (block (result i32)
      (global.get $x) (i32.const 2) (br_table 0 0)
    )
  )
  (func $as_br_table_last (export "as_br_table_last") (result i32)
    (block (result i32)
      (i32.const 2) (global.get $x) (br_table 0 0)
    )
  )

  (func $func (param i32 i32) (result i32) (local.get 0))
  (type $check (func (param i32 i32) (result i32)))
  (table funcref (elem $func))
  (func $as_call_indirect_first (export "as_call_indirect_first") (result i32)
    (block (result i32)
      (call_indirect (type $check)
        (global.get $x) (i32.const 2) (i32.const 0)
      )
    )
  )
  (func $as_call_indirect_mid (export "as_call_indirect_mid") (result i32)
    (block (result i32)
      (call_indirect (type $check)
        (i32.const 2) (global.get $x) (i32.const 0)
      )
    )
  )
 (func $as_call_indirect_last (export "as_call_indirect_last") (result i32)
    (block (result i32)
      (call_indirect (type $check)
        (i32.const 2) (i32.const 0) (global.get $x)
      )
    )
  )

  (func $as_store_first (export "as_store_first")
    (global.get $x) (i32.const 1) (i32.store)
  )
  (func $as_store_last (export "as_store_last")
    (i32.const 0) (global.get $x) (i32.store)
  )
  (func $as_load_operand (export "as_load_operand") (result i32)
    (i32.load (global.get $x))
  )
  (func $as_memory_grow_value (export "as_memory_grow_value") (result i32)
    (memory.grow (global.get $x))
  )

  (func $f (param i32) (result i32) (local.get 0))
  (func $as_call_value (export "as_call_value") (result i32)
    (call $f (global.get $x))
  )

  (func $as_return_value (export "as_return_value") (result i32)
    (global.get $x) (return)
  )
  (func $as_drop_operand (export "as_drop_operand")
    (drop (global.get $x))
  )
  (func $as_br_value (export "as_br_value") (result i32)
    (block (result i32) (br 0 (global.get $x)))
  )

  (func $as_local_set_value (export "as_local_set_value") (param i32) (result i32)
    (local.set 0 (global.get $x))
    (local.get 0)
  )
  (func $as_local_tee_value (export "as_local_tee_value") (param i32) (result i32)
    (local.tee 0 (global.get $x))
  )
  (func $as_global_set_value (export "as_global_set_value") (result i32)
    (global.set $x (global.get $x))
    (global.get $x)
  )

  (func $as_unary_operand (export "as_unary_operand") (result i32)
    (i32.eqz (global.get $x))
  )
  (func $as_binary_operand (export "as_binary_operand") (result i32)
    (i32.mul
      (global.get $x) (global.get $x)
    )
  )
 ;;(func $as_compare_operand (export "as_compare_operand") (result i32)
 ;;  (i32.gt_u
 ;;    (global.get 0) (i32.const 1)
 ;;  )
 ;;)


(func $assert_eq_i32 (param $line i32) (param $x i32) (param $y i32)
       (if (i32.ne (local.get 1) (local.get 2))
           (then
	       (call $wasi$print_i32_ln  (local.get 0))
	       (call $wasi$print_i32_ln  (local.get 1))
	       (call $wasi$print_i32_ln  (local.get 2))
	       (unreachable))
       )
 )

(func $assert_eq_f32 (param $line i32) (param $x f32) (param $y f32)
       (if (f32.ne (local.get 1) (local.get 2))
           (then
	       (call $wasi$print_i32_ln  (local.get 0))
	       (call $wasi$print_i32_ln  (i32.reinterpret_f32 (local.get 1)))
	       (call $wasi$print_i32_ln  (i32.reinterpret_f32 (local.get 2)))
	       (unreachable))
       )
 )

 (func $assert_eq_i64 (param $line i32) (param $x i64) (param $y i64)
       (if (i64.ne (local.get 1) (local.get 2))
           (then
	       (call $wasi$print_i32_ln  (local.get 0))
	       (call $wasi$print_i64_ln  (local.get 1))
	       (call $wasi$print_i64_ln  (local.get 2))
	       (unreachable))
       )
 )

(func $assert_eq_f64 (param $line i32) (param $x f64) (param $y f64)
       (if (f64.ne (local.get 1) (local.get 2))
           (then
	       (call $wasi$print_i32_ln  (local.get 0))
	       (call $wasi$print_i64_ln  (i64.reinterpret_f64 (local.get 1)))
	       (call $wasi$print_i64_ln  (i64.reinterpret_f64 (local.get 2)))
	       (unreachable))
       )
 )


(func $main (export "_start")

(call $assert_eq_i32 (i32.const 1101) (call $get_a ) (i32.const -2))
(call $assert_eq_i64 (i32.const 1201) (call $get_b ) (i64.const -5))
;;(assert_return (invoke "get-r") (ref.null extern))
;;(assert_return (invoke "get-mr") (ref.null extern))
(call $assert_eq_i32 (i32.const 1301) (call $get_x ) (i32.const -12))
(call $assert_eq_i64 (i32.const 1401) (call $get_y ) (i64.const -15))
;; (call $assert_eq_i32 (i32.const 1501) (call $get_z1 ) (i32.const 666))
;; (call $assert_eq_i64 (i32.const 1601) (call $get_z2 ) (i64.const 666))

(call $assert_eq_f32 (i32.const 1701) (call $get_3 ) (f32.const -3))
(call $assert_eq_f64 (i32.const 1801) (call $get_4 ) (f64.const -4))
(call $assert_eq_f32 (i32.const 1901) (call $get_7 ) (f32.const -13))
(call $assert_eq_f64 (i32.const 2001) (call $get_8 ) (f64.const -14))

(call $set_x (i32.const 6))
(call $set_y (i64.const 7))

(call $set_7 (f32.const 8))
(call $set_8 (f64.const 9))

(call $assert_eq_i32 (i32.const 2501) (call $get_x ) (i32.const 6))
(call $assert_eq_i64 (i32.const 2601) (call $get_y ) (i64.const 7))
(call $assert_eq_f32 (i32.const 2701) (call $get_7 ) (f32.const 8))
(call $assert_eq_f64 (i32.const 2801) (call $get_8 ) (f64.const 9))

(call $set_7 (f32.const 8))
(call $set_8 (f64.const 9))
;;(call $set_mr (ref.extern 10))

(call $assert_eq_i32 (i32.const 3201) (call $get_x ) (i32.const 6))
(call $assert_eq_i64 (i32.const 3301) (call $get_y ) (i64.const 7))
(call $assert_eq_f32 (i32.const 3401) (call $get_7 ) (f32.const 8))
(call $assert_eq_f64 (i32.const 3501) (call $get_8 ) (f64.const 9))
;;(call $assert_eq_ref (i32.const 3601) (call $get_mr ) (ref.extern 10))

(call $assert_eq_i32 (i32.const 3701) (call $as_select_first ) (i32.const 6))
(call $assert_eq_i32 (i32.const 3801) (call $as_select_mid ) (i32.const 2))
(call $assert_eq_i32 (i32.const 3901) (call $as_select_last ) (i32.const 2))

(call $assert_eq_i32 (i32.const 4001) (call $as_loop_first ) (i32.const 6))
(call $assert_eq_i32 (i32.const 4101) (call $as_loop_mid ) (i32.const 6))
(call $assert_eq_i32 (i32.const 4201) (call $as_loop_last ) (i32.const 6))

(call $assert_eq_i32 (i32.const 4301) (call $as_if_condition ) (i32.const 2))
(call $assert_eq_i32 (i32.const 4401) (call $as_if_then ) (i32.const 6))
(call $assert_eq_i32 (i32.const 4501) (call $as_if_else ) (i32.const 6))

(call $assert_eq_i32 (i32.const 4601) (call $as_br_if_first ) (i32.const 6))
(call $assert_eq_i32 (i32.const 4701) (call $as_br_if_last ) (i32.const 2))

(call $assert_eq_i32 (i32.const 4801) (call $as_br_table_first ) (i32.const 6))
(call $assert_eq_i32 (i32.const 4901) (call $as_br_table_last ) (i32.const 2))

(call $assert_eq_i32 (i32.const 5001) (call $as_call_indirect_first ) (i32.const 6))
(call $assert_eq_i32 (i32.const 5101) (call $as_call_indirect_mid ) (i32.const 2))

(call $as_store_first )
(call $as_store_last )
(call $assert_eq_i32 (i32.const 5401) (call $as_load_operand ) (i32.const 1))
(call $assert_eq_i32 (i32.const 5501) (call $as_memory_grow_value ) (i32.const 1))

(call $assert_eq_i32 (i32.const 5601) (call $as_call_value ) (i32.const 6))

(call $assert_eq_i32 (i32.const 5701) (call $as_return_value ) (i32.const 6))
(call $as_drop_operand )
(call $assert_eq_i32 (i32.const 5901) (call $as_br_value ) (i32.const 6))

(call $assert_eq_i32 (i32.const 6001) (call $as_local_set_value (i32.const 1)) (i32.const 6))
(call $assert_eq_i32 (i32.const 6101) (call $as_local_tee_value (i32.const 1)) (i32.const 6))
(call $assert_eq_i32 (i32.const 6201) (call $as_global_set_value ) (i32.const 6))

(call $assert_eq_i32 (i32.const 6301) (call $as_unary_operand ) (i32.const 0))
(call $assert_eq_i32 (i32.const 6401) (call $as_binary_operand ) (i32.const 36))
;; (call $assert_eq_i32 (i32.const 6501) (call $as_compare_operand ) (i32.const 1))

  (call $wasi$print_i32_ln  (i32.const 666))
)
)