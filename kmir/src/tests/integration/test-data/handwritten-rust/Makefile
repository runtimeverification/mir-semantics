default: mir executables

all: mir executables

clean:
	rm -f *.mir
	rm -f *.out

RUSTC:=rustc
RUST_SOURCES=$(wildcard *.rs)

mir: $(RUST_SOURCES:%.rs=%.mir)
%.mir : %.rs
	$(RUSTC) --emit mir $< -o $@

executables: $(RUST_SOURCES:%.rs=%.out)
%.out : %.rs
	$(RUSTC) $< -o $@
