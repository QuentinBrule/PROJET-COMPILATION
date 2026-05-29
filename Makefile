# Utilisation du makefile :
# make TARGET=tests/nnp/correct1.nno

.PHONY: all test_nna test_nnp clean

CC := gcc
CFLAGS := -Wall -Wextra -std=c11
LFAGS := -lm

NAME := $(basename $(notdir $(TARGET)))

run: build/$(NAME) bin/vm_nnp
	./bin/vm_nnp build/$(NAME)

build/$(NAME): $(TARGET) build
	python3 src/anasyn.py $(TARGET) -o build/$(NAME)

build/table_identificateurs_$(NAME): $(TARGET) build
	python3 src/anasyn.py -o $@ $(TARGET)

bin/vm_nna: bin src/VM/utils.c src/VM/commun.c src/VM/algorithmique.c src/VM/main.c src/VM/utils.h src/VM/commun.h src/VM/algorithmique.h
	$(CC) $(CFLAGS) -DVM_NNA -o $@ src/VM/utils.c src/VM/commun.c src/VM/algorithmique.c src/VM/main.c $(LFAGS)

bin/vm_nnp: bin src/VM/utils.c src/VM/commun.c src/VM/procedural.c src/VM/main.c src/VM/utils.h src/VM/commun.h src/VM/procedural.h
	$(CC) $(CFLAGS) -DVM_NNP -o $@ src/VM/utils.c src/VM/commun.c src/VM/procedural.c src/VM/main.c $(LFAGS)

bin:
	mkdir -p bin

build:
	mkdir -p build

test_nna: bin/vm_nna
	./$< tests/code_objet/exemple_nna -d

test_nnp: bin/vm_nnp
	./$< tests/code_objet/exemple_nnp -d

clean:
	rm -f bin/vm_nna bin/vm_nnp
	rm -f build/*