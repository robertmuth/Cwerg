
CONCRETE=wordcount.concrete.cw \
    fibonacci.concrete.cw \
	sieve.concrete.cw \
    print_argv.concrete.cw

all: $(CONCRETE)

clean:
	rm -f $(CONCRETE)

%.concrete.cw: ../TestData/%.cw
	@echo "[concrete-syntax $@]"
	../pp.py -mode concrete  $< > $@
