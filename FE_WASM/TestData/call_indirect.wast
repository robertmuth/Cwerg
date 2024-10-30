;; Test `call_indirect` operator

(module
  (import "wasi" "print_i32_ln" (func $wasi$print_i32_ln (param i32)))
  (import "wasi" "print_i64_ln" (func $wasi$print_i64_ln (param i64)))

  ;; Auxiliary definitions
  (type $proc (func))
  (type $out_i32 (func (result i32)))
  (type $out_i64 (func (result i64)))
  (type $out_f32 (func (result f32)))
  (type $out_f64 (func (result f64)))
  (type $out_f64_i32 (func (result f64 i32)))
  (type $over_i32 (func (param i32) (result i32)))
  (type $over_i64 (func (param i64) (result i64)))
  (type $over_f32 (func (param f32) (result f32)))
  (type $over_f64 (func (param f64) (result f64)))
  (type $over_i32_f64 (func (param i32 f64) (result i32 f64)))
  (type $swap_i32_i64 (func (param i32 i64) (result i64 i32)))
  (type $f32_i32 (func (param f32 i32) (result i32)))
  (type $i32_i64 (func (param i32 i64) (result i64)))
  (type $f64_f32 (func (param f64 f32) (result f32)))
  (type $i64_f64 (func (param i64 f64) (result f64)))
  (type $over_i32_duplicate (func (param i32) (result i32)))
  (type $over_i64_duplicate (func (param i64) (result i64)))
  (type $over_f32_duplicate (func (param f32) (result f32)))
  (type $over_f64_duplicate (func (param f64) (result f64)))

  (func $const_i32 (type $out_i32) (i32.const 0x132))
  (func $const_i64 (type $out_i64) (i64.const 0x164))
  (func $const_f32 (type $out_f32) (f32.const 0xf32))
  (func $const_f64 (type $out_f64) (f64.const 0xf64))
  (func $const_f64_i32 (type $out_f64_i32) (f64.const 0xf64) (i32.const 32))

  (func $id_i32 (type $over_i32) (local.get 0))
  (func $id_i64 (type $over_i64) (local.get 0))
  (func $id_f32 (type $over_f32) (local.get 0))
  (func $id_f64 (type $over_f64) (local.get 0))
  (func $id_i32_f64 (type $over_i32_f64) (local.get 0) (local.get 1))
  (func $swap_i32_i64 (type $swap_i32_i64) (local.get 1) (local.get 0))

  (func $i32_i64 (type $i32_i64) (local.get 1))
  (func $i64_f64 (type $i64_f64) (local.get 1))
  (func $f32_i32 (type $f32_i32) (local.get 1))
  (func $f64_f32 (type $f64_f32) (local.get 1))

  (func $over_i32_duplicate (type $over_i32_duplicate) (local.get 0))
  (func $over_i64_duplicate (type $over_i64_duplicate) (local.get 0))
  (func $over_f32_duplicate (type $over_f32_duplicate) (local.get 0))
  (func $over_f64_duplicate (type $over_f64_duplicate) (local.get 0))

  (table funcref
    (elem
      $const_i32 $const_i64 $const_f32 $const_f64  ;; 0..3
      $id_i32 $id_i64 $id_f32 $id_f64              ;; 4..7
      $f32_i32 $i32_i64 $f64_f32 $i64_f64          ;; 9..11
      $fac_i64 $fib_i64 $even $odd                 ;; 12..15
      $runaway $mutual_runaway1 $mutual_runaway2   ;; 16..18
      $over_i32_duplicate $over_i64_duplicate      ;; 19..20
      $over_f32_duplicate $over_f64_duplicate      ;; 21..22
      $fac_i32 $fac_f32 $fac_f64                   ;; 23..25
      $fib_i32 $fib_f32 $fib_f64                   ;; 26..28
      $const_f64_i32 $id_i32_f64 $swap_i32_i64     ;; 29..31
    )
  )

  ;; Syntax

  ;; (func
  ;;   (call_indirect (i32.const 0))
  ;;   (call_indirect (param i64) (i64.const 0) (i32.const 0))
  ;;   (call_indirect (param i64) (param) (param f64 i32 i64)
  ;;     (i64.const 0) (f64.const 0) (i32.const 0) (i64.const 0) (i32.const 0)
  ;;   )
  ;;   (call_indirect (result) (i32.const 0))
  ;;   (drop (i32.eqz (call_indirect (result i32) (i32.const 0))))
  ;;   (drop (i32.eqz (call_indirect (result i32) (result) (i32.const 0))))
  ;;   (drop (i32.eqz
  ;;     (call_indirect (param i64) (result i32) (i64.const 0) (i32.const 0))
  ;;   ))
  ;;   (drop (i32.eqz
  ;;     (call_indirect
  ;;       (param) (param i64) (param) (param f64 i32 i64) (param) (param)
  ;;       (result) (result i32) (result) (result)
  ;;       (i64.const 0) (f64.const 0) (i32.const 0) (i64.const 0) (i32.const 0)
  ;;     )
  ;;   ))
  ;;   (drop (i64.eqz
  ;;     (call_indirect (type $over_i64) (param i64) (result i64)
  ;;       (i64.const 0) (i32.const 0)
  ;;     )
  ;;   ))
  ;; )

  ;; Typing

  (func $type_i32 (export "$type_i32") (result i32)
    (call_indirect (type $out_i32) (i32.const 0))
  )
  (func $type_i64 (export "$type_i64") (result i64)
    (call_indirect (type $out_i64) (i32.const 1))
  )
  (func $type_f32 (export "$type_f32") (result f32)
    (call_indirect (type $out_f32) (i32.const 2))
  )
  (func $type_f64 (export "$type_f64") (result f64)
    (call_indirect (type $out_f64) (i32.const 3))
  )
  (func $type_f64_i32 (export "$type_f64_i32") (result f64 i32)
    (call_indirect (type $out_f64_i32) (i32.const 29))
  )

  (func $type_index (export "$type_index") (result i64)
    (call_indirect (type $over_i64) (i64.const 100) (i32.const 5))
  )

  (func $type_first_i32 (export "$type_first_i32") (result i32)
    (call_indirect (type $over_i32) (i32.const 32) (i32.const 4))
  )
  (func $type_first_i64 (export "$type_first_i64") (result i64)
    (call_indirect (type $over_i64) (i64.const 64) (i32.const 5))
  )
  (func $type_first_f32 (export "$type_first_f32") (result f32)
    (call_indirect (type $over_f32) (f32.const 1.32) (i32.const 6))
  )
  (func $type_first_f64 (export "$type_first_f64") (result f64)
    (call_indirect (type $over_f64) (f64.const 1.64) (i32.const 7))
  )

  (func $type_second_i32 (export "$type_second_i32") (result i32)
    (call_indirect (type $f32_i32) (f32.const 32.1) (i32.const 32) (i32.const 8))
  )
  (func $type_second_i64 (export "$type_second_i64") (result i64)
    (call_indirect (type $i32_i64) (i32.const 32) (i64.const 64) (i32.const 9))
  )
  (func $type_second_f32 (export "$type_second_f32") (result f32)
    (call_indirect (type $f64_f32) (f64.const 64) (f32.const 32) (i32.const 10))
  )
  (func $type_second_f64 (export "$type_second_f64") (result f64)
    (call_indirect (type $i64_f64) (i64.const 64) (f64.const 64.1) (i32.const 11))
  )

  (func $type_all_f64_i32 (export "$type_all_f64_i32") (result f64 i32)
    (call_indirect (type $out_f64_i32) (i32.const 29))
  )
  (func $type_all_i32_f64 (export "$type_all_i32_f64") (result i32 f64)
    (call_indirect (type $over_i32_f64)
      (i32.const 1) (f64.const 2) (i32.const 30)
    )
  )
  (func $type_all_i32_i64 (export "$type_all_i32_i64") (result i64 i32)
    (call_indirect (type $swap_i32_i64)
      (i32.const 1) (i64.const 2) (i32.const 31)
    )
  )

  ;; Dispatch

  (func $dispatch (export "$dispatch") (param i32 i64) (result i64)
    (call_indirect (type $over_i64) (local.get 1) (local.get 0))
  )

  (func $dispatch_structural_i64 (export "$dispatch_structural_i64") (param i32) (result i64)
    (call_indirect (type $over_i64_duplicate) (i64.const 9) (local.get 0))
  )
  (func $dispatch_structural_i32 (export "$dispatch_structural_i32") (param i32) (result i32)
    (call_indirect (type $over_i32_duplicate) (i32.const 9) (local.get 0))
  )
  (func $dispatch_structural_f32 (export "$dispatch_structural_f32") (param i32) (result f32)
    (call_indirect (type $over_f32_duplicate) (f32.const 9.0) (local.get 0))
  )
  (func $dispatch_structural_f64 (export "$dispatch_structural_f64") (param i32) (result f64)
    (call_indirect (type $over_f64_duplicate) (f64.const 9.0) (local.get 0))
  )

  ;; Recursion

  (func $fac_i64 (export "fac_i64") (type $over_i64)
    (if (result i64) (i64.eqz (local.get 0))
      (then (i64.const 1))
      (else
        (i64.mul
          (local.get 0)
          (call_indirect (type $over_i64)
            (i64.sub (local.get 0) (i64.const 1))
            (i32.const 12)
          )
        )
      )
    )
  )

  (func $fib_i64 (export "fib_i64") (type $over_i64)
    (if (result i64) (i64.le_u (local.get 0) (i64.const 1))
      (then (i64.const 1))
      (else
        (i64.add
          (call_indirect (type $over_i64)
            (i64.sub (local.get 0) (i64.const 2))
            (i32.const 13)
          )
          (call_indirect (type $over_i64)
            (i64.sub (local.get 0) (i64.const 1))
            (i32.const 13)
          )
        )
      )
    )
  )

  (func $fac_i32 (export "fac_i32") (type $over_i32)
    (if (result i32) (i32.eqz (local.get 0))
      (then (i32.const 1))
      (else
        (i32.mul
          (local.get 0)
          (call_indirect (type $over_i32)
            (i32.sub (local.get 0) (i32.const 1))
            (i32.const 23)
          )
        )
      )
    )
  )

  (func $fac_f32 (export "fac_f32") (type $over_f32)
    (if (result f32) (f32.eq (local.get 0) (f32.const 0.0))
      (then (f32.const 1.0))
      (else
        (f32.mul
          (local.get 0)
          (call_indirect (type $over_f32)
            (f32.sub (local.get 0) (f32.const 1.0))
            (i32.const 24)
          )
        )
      )
    )
  )

  (func $fac_f64 (export "fac_f64") (type $over_f64)
    (if (result f64) (f64.eq (local.get 0) (f64.const 0.0))
      (then (f64.const 1.0))
      (else
        (f64.mul
          (local.get 0)
          (call_indirect (type $over_f64)
            (f64.sub (local.get 0) (f64.const 1.0))
            (i32.const 25)
          )
        )
      )
    )
  )

  (func $fib_i32 (export "fib_i32") (type $over_i32)
    (if (result i32) (i32.le_u (local.get 0) (i32.const 1))
      (then (i32.const 1))
      (else
        (i32.add
          (call_indirect (type $over_i32)
            (i32.sub (local.get 0) (i32.const 2))
            (i32.const 26)
          )
          (call_indirect (type $over_i32)
            (i32.sub (local.get 0) (i32.const 1))
            (i32.const 26)
          )
        )
      )
    )
  )

  (func $fib_f32 (export "fib_f32") (type $over_f32)
    (if (result f32) (f32.le (local.get 0) (f32.const 1.0))
      (then (f32.const 1.0))
      (else
        (f32.add
          (call_indirect (type $over_f32)
            (f32.sub (local.get 0) (f32.const 2.0))
            (i32.const 27)
          )
          (call_indirect (type $over_f32)
            (f32.sub (local.get 0) (f32.const 1.0))
            (i32.const 27)
          )
        )
      )
    )
  )

  (func $fib_f64 (export "fib_f64") (type $over_f64)
    (if (result f64) (f64.le (local.get 0) (f64.const 1.0))
      (then (f64.const 1.0))
      (else
        (f64.add
          (call_indirect (type $over_f64)
            (f64.sub (local.get 0) (f64.const 2.0))
            (i32.const 28)
          )
          (call_indirect (type $over_f64)
            (f64.sub (local.get 0) (f64.const 1.0))
            (i32.const 28)
          )
        )
      )
    )
  )

  (func $even (export "even") (param i32) (result i32)
    (if (result i32) (i32.eqz (local.get 0))
      (then (i32.const 44))
      (else
        (call_indirect (type $over_i32)
          (i32.sub (local.get 0) (i32.const 1))
          (i32.const 15)
        )
      )
    )
  )
  (func $odd (export "odd") (param i32) (result i32)
    (if (result i32) (i32.eqz (local.get 0))
      (then (i32.const 99))
      (else
        (call_indirect (type $over_i32)
          (i32.sub (local.get 0) (i32.const 1))
          (i32.const 14)
        )
      )
    )
  )

  ;; Stack exhaustion

  ;; Implementations are required to have every call consume some abstract
  ;; resource towards exhausting some abstract finite limit, such that
  ;; infinitely recursive test cases reliably trap in finite time. This is
  ;; because otherwise applications could come to depend on it on those
  ;; implementations and be incompatible with implementations that don't do
  ;; it (or don't do it under the same circumstances).

  (func $runaway (export "runaway") (call_indirect (type $proc) (i32.const 16)))

  (func $mutual_runaway1 (export "mutual_runaway") (call_indirect (type $proc) (i32.const 18)))
  (func $mutual_runaway2 (call_indirect (type $proc) (i32.const 17)))

  ;; As parameter of control constructs and instructions

  (memory 1)

  (func $as_select_first (export "$as_select_first") (result i32)
    (select (call_indirect (type $out_i32) (i32.const 0)) (i32.const 2) (i32.const 3))
  )
  (func $as_select_mid (export "$as_select_mid") (result i32)
    (select (i32.const 2) (call_indirect (type $out_i32) (i32.const 0)) (i32.const 3))
  )
  (func $as_select_last (export "$as_select_last") (result i32)
    (select (i32.const 2) (i32.const 3) (call_indirect (type $out_i32) (i32.const 0)))
  )

  (func $as_if_condition (export "$as_if_condition") (result i32)
    (if (result i32) (call_indirect (type $out_i32) (i32.const 0)) (then (i32.const 1)) (else (i32.const 2)))
  )

  (func $as_br_if_first (export "$as_br_if_first") (result i64)
    (block (result i64) (br_if 0 (call_indirect (type $out_i64) (i32.const 1)) (i32.const 2)))
  )
  (func $as_br_if_last (export "$as_br_if_last") (result i32)
    (block (result i32) (br_if 0 (i32.const 2) (call_indirect (type $out_i32) (i32.const 0))))
  )

  (func $as_br_table_first (export "$as_br_table_first") (result f32)
    (block (result f32) (call_indirect (type $out_f32) (i32.const 2)) (i32.const 2) (br_table 0 0))
  )
  (func $as_br_table_last (export "$as_br_table_last") (result i32)
    (block (result i32) (i32.const 2) (call_indirect (type $out_i32) (i32.const 0)) (br_table 0 0))
  )

  (func $as_store_first (export "$as_store_first")
    (call_indirect (type $out_i32) (i32.const 0)) (i32.const 1) (i32.store)
  )
  (func $as_store_last (export "$as_store_last")
    (i32.const 10) (call_indirect (type $out_f64) (i32.const 3)) (f64.store)
  )

  (func $as_memory_grow_value (export "$as_memory_grow_value") (result i32)
    (memory.grow (call_indirect (type $out_i32) (i32.const 0)))
  )
  (func $as_return_value (export "$as_return_value") (result i32)
    (call_indirect (type $over_i32) (i32.const 1) (i32.const 4)) (return)
  )
  (func $as_drop_operand (export "$as_drop_operand")
    (call_indirect (type $over_i64) (i64.const 1) (i32.const 5)) (drop)
  )
  (func $as_br_value (export "$as_br_value") (result f32)
    (block (result f32) (br 0 (call_indirect (type $over_f32) (f32.const 1) (i32.const 6))))
  )
  (func $as_local_set_value (export "$as_local_set_value") (result f64)
    (local f64) (local.set 0 (call_indirect (type $over_f64) (f64.const 1) (i32.const 7))) (local.get 0)
  )
  (func $as_local_tee_value (export "$as_local_tee_value") (result f64)
    (local f64) (local.tee 0 (call_indirect (type $over_f64) (f64.const 1) (i32.const 7)))
  )
  (global $a (mut f64) (f64.const 10.0))
  (func $as_global_set_value (export "$as_global_set_value") (result f64)
    (global.set $a (call_indirect (type $over_f64) (f64.const 1.0) (i32.const 7)))
    (global.get $a)
  )

  (func $as_load_operand (export "$as_load_operand") (result i32)
    (i32.load (call_indirect (type $out_i32) (i32.const 0)))
  )

  (func $as_unary_operand (export "$as_unary_operand") (result f32)
    (block (result f32)
      (f32.sqrt
        (call_indirect (type $over_f32) (f32.const 0x0p+0) (i32.const 6))
      )
    )
  )

  (func $as_binary_left (export "$as_binary_left") (result i32)
    (block (result i32)
      (i32.add
        (call_indirect (type $over_i32) (i32.const 1) (i32.const 4))
        (i32.const 10)
      )
    )
  )
  (func $as_binary_right (export "$as_binary_right") (result i32)
    (block (result i32)
      (i32.sub
        (i32.const 10)
        (call_indirect (type $over_i32) (i32.const 1) (i32.const 4))
      )
    )
  )

  (func $as_test_operand (export "$as_test_operand") (result i32)
    (block (result i32)
      (i32.eqz
        (call_indirect (type $over_i32) (i32.const 1) (i32.const 4))
      )
    )
  )

  (func $as_compare_left (export "$as_compare_left") (result i32)
    (block (result i32)
      (i32.le_u
        (call_indirect (type $over_i32) (i32.const 1) (i32.const 4))
        (i32.const 10)
      )
    )
  )
  (func $as_compare_right (export "$as_compare_right") (result i32)
    (block (result i32)
      (i32.ne
        (i32.const 10)
        (call_indirect (type $over_i32) (i32.const 1) (i32.const 4))
      )
    )
  )

  (func $as_convert_operand (export "$as_convert_operand") (result i64)
    (block (result i64)
      (i64.extend_i32_s
        (call_indirect (type $over_i32) (i32.const 1) (i32.const 4))
      )
    )
  )

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
(call $assert_eq_i32 (i32.const 1101) (call $type_i32 ) (i32.const 0x132))
(call $assert_eq_i64 (i32.const 1201) (call $type_i64 ) (i64.const 0x164))
(call $assert_eq_f32 (i32.const 1301) (call $type_f32 ) (f32.const 0xf32))
(call $assert_eq_f64 (i32.const 1401) (call $type_f64 ) (f64.const 0xf64))
;; (call $assert_eq_f64 (i32.const 1501) (call $type_f64_i32 ) (f64.const 0xf64) (i32.const 32))

(call $assert_eq_i64 (i32.const 1601) (call $type_index ) (i64.const 100))

(call $assert_eq_i32 (i32.const 1701) (call $type_first_i32 ) (i32.const 32))
(call $assert_eq_i64 (i32.const 1801) (call $type_first_i64 ) (i64.const 64))
(call $assert_eq_f32 (i32.const 1901) (call $type_first_f32 ) (f32.const 1.32))
(call $assert_eq_f64 (i32.const 2001) (call $type_first_f64 ) (f64.const 1.64))

(call $assert_eq_i32 (i32.const 2101) (call $type_second_i32 ) (i32.const 32))
(call $assert_eq_i64 (i32.const 2201) (call $type_second_i64 ) (i64.const 64))
(call $assert_eq_f32 (i32.const 2301) (call $type_second_f32 ) (f32.const 32))
(call $assert_eq_f64 (i32.const 2401) (call $type_second_f64 ) (f64.const 64.1))

;; (call $assert_eq_f64 (i32.const 2501) (call $type_all_f64_i32 ) (f64.const 0xf64) (i32.const 32))
;; (call $assert_eq_i32 (i32.const 2601) (call $type_all_i32_f64 ) (i32.const 1) (f64.const 2))
;; (call $assert_eq_i64 (i32.const 2701) (call $type_all_i32_i64 ) (i64.const 2) (i32.const 1))

(call $assert_eq_i64 (i32.const 2801) (call $dispatch (i32.const 5) (i64.const 2)) (i64.const 2))
(call $assert_eq_i64 (i32.const 2802) (call $dispatch (i32.const 5) (i64.const 5)) (i64.const 5))
(call $assert_eq_i64 (i32.const 2803) (call $dispatch (i32.const 12) (i64.const 5)) (i64.const 120))
(call $assert_eq_i64 (i32.const 2804) (call $dispatch (i32.const 13) (i64.const 5)) (i64.const 8))
(call $assert_eq_i64 (i32.const 2805) (call $dispatch (i32.const 20) (i64.const 2)) (i64.const 2))

;;(assert_trap (invoke "dispatch" (i32.const 0) (i64.const 2)) "indirect call type mismatch")
;;(assert_trap (invoke "dispatch" (i32.const 15) (i64.const 2)) "indirect call type mismatch")
;;(assert_trap (invoke "dispatch" (i32.const 32) (i64.const 2)) "undefined element")
;;(assert_trap (invoke "dispatch" (i32.const _1) (i64.const 2)) "undefined element")
;;(assert_trap (invoke "dispatch" (i32.const 1213432423) (i64.const 2)) "undefined element")

(call $assert_eq_i64 (i32.const 2901) (call $dispatch_structural_i64 (i32.const 5)) (i64.const 9))
(call $assert_eq_i64 (i32.const 2902) (call $dispatch_structural_i64 (i32.const 12)) (i64.const 362880))
(call $assert_eq_i64 (i32.const 2903) (call $dispatch_structural_i64 (i32.const 13)) (i64.const 55))
(call $assert_eq_i64 (i32.const 2904) (call $dispatch_structural_i64 (i32.const 20)) (i64.const 9))

;;(assert_trap (invoke "dispatch_structural_i64" (i32.const 11)) "indirect call type mismatch")
;;(assert_trap (invoke "dispatch_structural_i64" (i32.const 22)) "indirect call type mismatch")

(call $assert_eq_i32 (i32.const 3001) (call $dispatch_structural_i32 (i32.const 4)) (i32.const 9))
(call $assert_eq_i32 (i32.const 3002) (call $dispatch_structural_i32 (i32.const 23)) (i32.const 362880))
(call $assert_eq_i32 (i32.const 3003) (call $dispatch_structural_i32 (i32.const 26)) (i32.const 55))
(call $assert_eq_i32 (i32.const 3004) (call $dispatch_structural_i32 (i32.const 19)) (i32.const 9))
;; (assert_trap (invoke "dispatch_structural_i32" (i32.const 9)) "indirect call type mismatch")
;; (assert_trap (invoke "dispatch_structural_i32" (i32.const 21)) "indirect call type mismatch")

(call $assert_eq_f32 (i32.const 3101) (call $dispatch_structural_f32 (i32.const 6)) (f32.const 9.0))
(call $assert_eq_f32 (i32.const 3102) (call $dispatch_structural_f32 (i32.const 24)) (f32.const 362880.0))
(call $assert_eq_f32 (i32.const 3103) (call $dispatch_structural_f32 (i32.const 27)) (f32.const 55.0))
(call $assert_eq_f32 (i32.const 3104) (call $dispatch_structural_f32 (i32.const 21)) (f32.const 9.0))
;; (assert_trap (invoke "dispatch_structural_f32" (i32.const 8)) "indirect call type mismatch")
;; (assert_trap (invoke "dispatch_structural_f32" (i32.const 19)) "indirect call type mismatch")

(call $assert_eq_f64 (i32.const 3201) (call $dispatch_structural_f64 (i32.const 7)) (f64.const 9.0))
(call $assert_eq_f64 (i32.const 3202) (call $dispatch_structural_f64 (i32.const 25)) (f64.const 362880.0))
(call $assert_eq_f64 (i32.const 3203) (call $dispatch_structural_f64 (i32.const 28)) (f64.const 55.0))
(call $assert_eq_f64 (i32.const 3204) (call $dispatch_structural_f64 (i32.const 22)) (f64.const 9.0))
;; (assert_trap (invoke "dispatch_structural_f64" (i32.const 10)) "indirect call type mismatch")
;; (assert_trap (invoke "dispatch_structural_f64" (i32.const 18)) "indirect call type mismatch")

(call $assert_eq_i64 (i32.const 3301) (call $fac_i64 (i64.const 0)) (i64.const 1))
(call $assert_eq_i64 (i32.const 3302) (call $fac_i64 (i64.const 1)) (i64.const 1))
(call $assert_eq_i64 (i32.const 3303) (call $fac_i64 (i64.const 5)) (i64.const 120))
(call $assert_eq_i64 (i32.const 3304) (call $fac_i64 (i64.const 25)) (i64.const 7034535277573963776))

(call $assert_eq_i32 (i32.const 3401) (call $fac_i32 (i32.const 0)) (i32.const 1))
(call $assert_eq_i32 (i32.const 3402) (call $fac_i32 (i32.const 1)) (i32.const 1))
(call $assert_eq_i32 (i32.const 3403) (call $fac_i32 (i32.const 5)) (i32.const 120))
(call $assert_eq_i32 (i32.const 3404) (call $fac_i32 (i32.const 10)) (i32.const 3628800))

(call $assert_eq_f32 (i32.const 3501) (call $fac_f32 (f32.const 0.0)) (f32.const 1.0))
(call $assert_eq_f32 (i32.const 3502) (call $fac_f32 (f32.const 1.0)) (f32.const 1.0))
(call $assert_eq_f32 (i32.const 3503) (call $fac_f32 (f32.const 5.0)) (f32.const 120.0))
(call $assert_eq_f32 (i32.const 3504) (call $fac_f32 (f32.const 10.0)) (f32.const 3628800.0))

(call $assert_eq_f64 (i32.const 3601) (call $fac_f64 (f64.const 0.0)) (f64.const 1.0))
(call $assert_eq_f64 (i32.const 3602) (call $fac_f64 (f64.const 1.0)) (f64.const 1.0))
(call $assert_eq_f64 (i32.const 3603) (call $fac_f64 (f64.const 5.0)) (f64.const 120.0))
(call $assert_eq_f64 (i32.const 3604) (call $fac_f64 (f64.const 10.0)) (f64.const 3628800.0))

(call $assert_eq_i64 (i32.const 3701) (call $fib_i64 (i64.const 0)) (i64.const 1))
(call $assert_eq_i64 (i32.const 3702) (call $fib_i64 (i64.const 1)) (i64.const 1))
(call $assert_eq_i64 (i32.const 3703) (call $fib_i64 (i64.const 2)) (i64.const 2))
(call $assert_eq_i64 (i32.const 3704) (call $fib_i64 (i64.const 5)) (i64.const 8))
(call $assert_eq_i64 (i32.const 3705) (call $fib_i64 (i64.const 20)) (i64.const 10946))

(call $assert_eq_i32 (i32.const 3801) (call $fib_i32 (i32.const 0)) (i32.const 1))
(call $assert_eq_i32 (i32.const 3802) (call $fib_i32 (i32.const 1)) (i32.const 1))
(call $assert_eq_i32 (i32.const 3803) (call $fib_i32 (i32.const 2)) (i32.const 2))
(call $assert_eq_i32 (i32.const 3804) (call $fib_i32 (i32.const 5)) (i32.const 8))
(call $assert_eq_i32 (i32.const 3805) (call $fib_i32 (i32.const 20)) (i32.const 10946))

(call $assert_eq_f32 (i32.const 3901) (call $fib_f32 (f32.const 0.0)) (f32.const 1.0))
(call $assert_eq_f32 (i32.const 3902) (call $fib_f32 (f32.const 1.0)) (f32.const 1.0))
(call $assert_eq_f32 (i32.const 3903) (call $fib_f32 (f32.const 2.0)) (f32.const 2.0))
(call $assert_eq_f32 (i32.const 3904) (call $fib_f32 (f32.const 5.0)) (f32.const 8.0))
(call $assert_eq_f32 (i32.const 3905) (call $fib_f32 (f32.const 20.0)) (f32.const 10946.0))

(call $assert_eq_f64 (i32.const 4001) (call $fib_f64 (f64.const 0.0)) (f64.const 1.0))
(call $assert_eq_f64 (i32.const 4002) (call $fib_f64 (f64.const 1.0)) (f64.const 1.0))
(call $assert_eq_f64 (i32.const 4003) (call $fib_f64 (f64.const 2.0)) (f64.const 2.0))
(call $assert_eq_f64 (i32.const 4004) (call $fib_f64 (f64.const 5.0)) (f64.const 8.0))
(call $assert_eq_f64 (i32.const 4005) (call $fib_f64 (f64.const 20.0)) (f64.const 10946.0))

(call $assert_eq_i32 (i32.const 4101) (call $even (i32.const 0)) (i32.const 44))
(call $assert_eq_i32 (i32.const 4102) (call $even (i32.const 1)) (i32.const 99))
(call $assert_eq_i32 (i32.const 4103) (call $even (i32.const 100)) (i32.const 44))
(call $assert_eq_i32 (i32.const 4104) (call $even (i32.const 77)) (i32.const 99))
(call $assert_eq_i32 (i32.const 4201) (call $odd (i32.const 0)) (i32.const 99))
(call $assert_eq_i32 (i32.const 4202) (call $odd (i32.const 1)) (i32.const 44))
(call $assert_eq_i32 (i32.const 4203) (call $odd (i32.const 200)) (i32.const 99))
(call $assert_eq_i32 (i32.const 4204) (call $odd (i32.const 77)) (i32.const 44))

;; (assert_exhaustion (invoke "runaway") "call stack exhausted")
;; (assert_exhaustion (invoke "mutual_runaway") "call stack exhausted")

(call $assert_eq_i32 (i32.const 4301) (call $as_select_first ) (i32.const 0x132))
(call $assert_eq_i32 (i32.const 4401) (call $as_select_mid ) (i32.const 2))
(call $assert_eq_i32 (i32.const 4501) (call $as_select_last ) (i32.const 2))

(call $assert_eq_i32 (i32.const 4601) (call $as_if_condition ) (i32.const 1))

(call $assert_eq_i64 (i32.const 4701) (call $as_br_if_first ) (i64.const 0x164))
(call $assert_eq_i32 (i32.const 4801) (call $as_br_if_last ) (i32.const 2))

(call $assert_eq_f32 (i32.const 4901) (call $as_br_table_first ) (f32.const 0xf32))
(call $assert_eq_i32 (i32.const 5001) (call $as_br_table_last ) (i32.const 2))

(call $as_store_first )
(call $as_store_last )

;; (call $assert_eq_i32 (i32.const 5301) (call $as_memory_grow_value ) (i32.const 1))
(call $assert_eq_i32 (i32.const 5401) (call $as_return_value ) (i32.const 1))
(call $as_drop_operand )
(call $assert_eq_f32 (i32.const 5601) (call $as_br_value ) (f32.const 1))
(call $assert_eq_f64 (i32.const 5701) (call $as_local_set_value ) (f64.const 1))
(call $assert_eq_f64 (i32.const 5801) (call $as_local_tee_value ) (f64.const 1))
(call $assert_eq_f64 (i32.const 5901) (call $as_global_set_value ) (f64.const 1.0))
(call $assert_eq_i32 (i32.const 6001) (call $as_load_operand ) (i32.const 1))

(call $assert_eq_f32 (i32.const 6101) (call $as_unary_operand ) (f32.const 0x0p+0))
(call $assert_eq_i32 (i32.const 6201) (call $as_binary_left ) (i32.const 11))
(call $assert_eq_i32 (i32.const 6301) (call $as_binary_right ) (i32.const 9))
(call $assert_eq_i32 (i32.const 6401) (call $as_test_operand ) (i32.const 0))
(call $assert_eq_i32 (i32.const 6501) (call $as_compare_left ) (i32.const 1))
(call $assert_eq_i32 (i32.const 6601) (call $as_compare_right ) (i32.const 1))
(call $assert_eq_i64 (i32.const 6701) (call $as_convert_operand ) (i64.const 1))

(call $wasi$print_i32_ln  (i32.const 666))
)
)
