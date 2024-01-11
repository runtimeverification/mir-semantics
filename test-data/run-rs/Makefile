default: mir

all: mir exe

clean:
	find . -name "*.mir" -type f -delete
	find . -name "*.out" -type f -delete

RUSTC:=rustc
RUST_SOURCES=$(shell find . -name '*.rs')
RUSTC_OPTIONS=-C overflow-checks=off -Zmir-enable-passes=-ConstDebugInfo,-PromoteTemps

mir: $(patsubst %.rs,%.mir,${RUST_SOURCES})
%.mir: %.rs
	$(RUSTC) --emit mir $(RUSTC_OPTIONS) -o $@ $*.rs

exe: $(patsubst %.rs,%.out,${RUST_SOURCES})
%.out: %.rs
	$(RUSTC) $(RUSTC_OPTIONS) -o $@ $*.rs
