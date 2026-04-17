.PHONY: test_nna

bin/vm: src/vm/*.c src/vm/*.h
	gcc -o $@ src/vm/*.c

test_nna: bin/vm
	./$< test/code_objet/exemple_nna