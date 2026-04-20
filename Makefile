.PHONY: test_nna clean

bin/vm_nna: src/VM/utils.c src/VM/algorithmique.c src/VM/main.c src/VM/utils.h src/VM/algorithmique.h
	gcc -o $@ src/VM/utils.c src/VM/algorithmique.c src/VM/main.c

test_nna: bin/vm_nna
	./$< tests/code_objet/exemple_nna

clean:
	rm -f bin/vm_nna