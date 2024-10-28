.SUFFIXES:  # no built-in rules
DIR=build

$(info $(shell mkdir -p $(DIR)))

# used to update  std_lib.XX.asm
std_lib.32.asm: std_lib.c
	../FrontEndC/translate.py --mode 32 std_lib.c  > std_lib.32.asm

std_lib.64.asm: std_lib.c
	../FrontEndC/translate.py --mode 64 std_lib.c  > std_lib.64.asm

############################################################
# Misc
############################################################

clean:
	rm -f  $(DIR)/*
