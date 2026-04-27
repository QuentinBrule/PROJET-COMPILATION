.PHONY: all test_nna test_nnp clean

CC := gcc
CFLAGS := -Wall -Wextra -std=c11

all: bin/vm_nna bin/vm_nnp

bin/vm_nna: src/VM/utils.c src/VM/algorithmique.c src/VM/main.c src/VM/utils.h src/VM/algorithmique.h
	$(CC) $(CFLAGS) -DVM_NNA -o $@ src/VM/utils.c src/VM/algorithmique.c src/VM/main.c

bin/vm_nnp: src/VM/utils.c src/VM/procedural.c src/VM/main.c src/VM/utils.h src/VM/procedural.h
	$(CC) $(CFLAGS) -DVM_NNP -o $@ src/VM/utils.c src/VM/procedural.c src/VM/main.c

test_nna: bin/vm_nna
	./$< tests/code_objet/exemple_nna

test_nnp: bin/vm_nnp
	./$< tests/code_objet/exemple_nnp

clean:
	rm -f bin/vm_nna bin/vm_nnp