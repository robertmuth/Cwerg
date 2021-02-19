
tests: tests_py tests_c
	@echo

tests_py: reaching_defs_test  liveness_test reg_alloc_test.py \
          opcode_contraints_test serialize_regression_test \
          cfg_regression_test cfg2_regression_test  \
          optlite_regression_test optimize_regression_test

tests_c:  serialize_regression_test_c  cfg_regression_test_c \
          cfg2_regression_test_c optlite_regression_test_c \
          optimize_regression_test_c

STDLIB64 = ../StdLib/std_lib.64.asm

############################################################
# Python Port
############################################################

reaching_defs_test:
	@echo "[$@]"
	$(PYPY) ./reaching_defs_test.py > $@.out 2>&1

liveness_test:
	@echo "[$@]"
	$(PYPY) ./liveness_test.py > $@.out 2>&1

reg_stats_test:
	@echo "[$@]"
	$(PYPY) ./reg_stats_test.py > $@.out 2>&1

opcode_contraints_test:
	@echo "[$@]"
	$(PYPY) ./opcode_contraints_test.py >@.out 2>&1

serialize_regression_test:
	@echo "[$@]"
	cat ${STDLIB64} ../TestData/nano_jpeg.64.asm | $(PYPY) ./optimize.py serialize > $@.1.out
	$(PYPY) ./optimize.py serialize < $@.1.out > $@.2.out
	diff  $@.1.out $@.2.out
	diff  $@.2.out ../TestData/nano_jpeg.nop.64.asm

cfg_regression_test:
	@echo "[$@]"
	cat ${STDLIB64} ../TestData/nano_jpeg.64.asm | $(PYPY) ./optimize.py cfg > $@.out
	diff  $@.out ../TestData/nano_jpeg.cfg.64.asm

cfg2_regression_test:
	@echo "[$@]"
	cat ${STDLIB64} ../TestData/nano_jpeg.64.asm | $(PYPY) ./optimize.py cfg2 > $@.out
	diff  $@.out ../TestData/nano_jpeg.cfg2.64.asm

optlite_regression_test:
	@echo "[$@]"
	cat ${STDLIB64} ../TestData/nano_jpeg.64.asm | $(PYPY) ./optimize.py optlite > $@.1.out
	diff  $@.1.out ../TestData/nano_jpeg.optlite.64.asm

optimize_regression_test:
	@echo "[$@]"
	cat ${STDLIB64} ../TestData/nano_jpeg.64.asm | $(PYPY) ./optimize.py optimize > $@.1.out
	diff  $@.1.out ../TestData/nano_jpeg.opt.64.asm

############################################################
# C++ Port
############################################################
BUILD_DIR=../build
OPTIMIZE_TOOL=$(BUILD_DIR)/optimize_tool.exe

$(OPTIMIZE_TOOL)::
	@cd $(BUILD_DIR); $(MAKE) -s optimize_tool.exe

opcode_gen.h: opcode_tab.py
	@echo "[$@]"
	$(PYPY) ./opcode_tab.py gen_h < opcode_gen.h > $@.tmp
	@mv $@.tmp $@

opcode_gen.cc: opcode_tab.py opcode_gen.h
	@echo "[$@]"
	$(PYPY) ./opcode_tab.py gen_c  < opcode_gen.cc > $@.tmp
	@mv $@.tmp $@

serialize_regression_test_c: opcode_gen.h opcode_gen.cc $(OPTIMIZE_TOOL)
	@echo "[$@]"
	cat ${STDLIB64} ../TestData/nano_jpeg.64.asm | $(OPTIMIZE_TOOL) -mode serialize > $@.1.out
	$(BUILD_DIR)/optimize_tool.exe  -mode serialize < $@.1.out > $@.2.out
	diff  $@.1.out $@.2.out
	diff  $@.2.out ../TestData/nano_jpeg.nop.64.asm

cfg_regression_test_c: $(OPTIMIZE_TOOL)
	@echo "[$@]"
	cat ${STDLIB64} ../TestData/nano_jpeg.64.asm | $(OPTIMIZE_TOOL) -mode cfg > $@.out
	diff  $@.out ../TestData/nano_jpeg.cfg.64.asm

cfg2_regression_test_c: $(OPTIMIZE_TOOL)
	@echo "[$@]"
	cat ${STDLIB64} ../TestData/nano_jpeg.64.asm | $(OPTIMIZE_TOOL) -mode cfg2 > $@.out
	diff  $@.out ../TestData/nano_jpeg.cfg2.64.asm

optlite_regression_test_c: $(OPTIMIZE_TOOL)
	@echo "[$@]"
	cat ${STDLIB64} ../TestData/nano_jpeg.64.asm | $(OPTIMIZE_TOOL) -mode optlite > $@.out
	diff  $@.out ../TestData/nano_jpeg.optlite.64.asm

optimize_regression_test_c:  $(OPTIMIZE_TOOL)
	@echo "[$@]"
	cat ${STDLIB64} ../TestData/nano_jpeg.64.asm | $(OPTIMIZE_TOOL) -mode optimize > $@.out
	diff  $@.out ../TestData/nano_jpeg.opt.64.asm

############################################################
# Misc
############################################################
clean:
	rm -f *.out *.exe 
