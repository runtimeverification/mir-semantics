default: mir executables

all: mir executables

clean:
	rm -f *.mir
	rm -f *.out

RUSTC:=rustc
RUST_SOURCES=$(wildcard *.rs)
RUSTC_OPTIONS=-C overflow-checks=off

mir: $(RUST_SOURCES:%.rs=%.mir)
%.mir : %.rs
	$(RUSTC) --emit mir $(RUSTC_OPTIONS) $< -o $@

executables: $(RUST_SOURCES:%.rs=%.out)
%.out : %.rs
	$(RUSTC) $(RUSTC_OPTIONS) $< -o $@
