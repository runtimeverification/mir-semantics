 
.PHONY: clean clean-mir default ui-mir

default: clean-mir ui-mir

clean: clean-mir

RUSTC:=rustc
RUSTC_OPTIONS=-C overflow-checks=off -Zmir-enable-passes=-ConstDebugInfo,-PromoteTemps

UI_RS=$(shell find ui -name '*.rs')
UI_MIR=$(patsubst %.rs,%.mir,${UI_RS})

# Remove MIR files
clean-mir:
	find . -name "*.mir" -type f -delete

ui-mir: ${UI_MIR}

# Default MIR generation
ui/%.mir: ui/%.rs
	-$(RUSTC) --emit mir $(RUSTC_OPTIONS) -o $@ ui/$*.rs
	
# # 'async-await' tests use 2021 ed. 
# ui/async-await/%.mir: ui/async-await/%.rs 
# 	rustc --edition 2021 \
# 	      --emit mir \
# 		  -o $@ ui/async-await/$*.rs 

# # 'try-block' tests use 2018 ed. 
# ui/try-block/%.mir: ui/try-block/%.rs 
# 	rustc --edition 2018 \
# 	      --emit mir \
# 		  -o $@ ui/try-block/$*.rs 

# # 'closures/2229_closure_analysis/run_pass' tests use 2021 ed. 
# ui/closures/2229_closure_analysis/run_pass/%.mir: ui/closures/2229_closure_analysis/run_pass/%.rs 
# 	rustc --edition 2021 \
# 	      --emit mir \
# 		  -o $@ ui/closures/2229_closure_analysis/run_pass/$*.rs

# # 'closures/2229_closure_analysis/optimization' tests use 2021 ed. 
# ui/closures/2229_closure_analysis/optimization/%.mir: ui/closures/2229_closure_analysis/optimization/%.rs 
# 	rustc --edition 2021 \
# 	      --emit mir \
# 		  -o $@ ui/closures/2229_closure_analysis/optimization/$*.rs

# # 'test-attrs' tests use the '--test' flag. 
# ui/test-attrs/%.mir: ui/test-attrs/%.rs 
# 	rustc --test --emit mir -o $@ ui/test-attrs/$*.rs 

# # 'try-block/try-is-identifier-edition2015.rs' use 2015 ed. 
# ui/try-block/try-is-identifier-edition2015.mir: ui/try-block/try-is-identifier-edition2015.rs
# 	rustc --edition 2015 \
# 	      --emit mir \
# 		  -o ui/try-block/try-is-identifier-edition2015.mir \
# 		  ui/try-block/try-is-identifier-edition2015.rs

# # 'numbers-arithmetic/promoted_overflow_opt.rs' use the '-O' flag. 
# ui/numbers-arithmetic/promoted_overflow_opt.mir: ui/numbers-arithmetic/promoted_overflow_opt.rs
# 	rustc --emit mir \
# 	      -O \
# 		  -o ui/numbers-arithmetic/promoted_overflow_opt.mir \
# 		  ui/numbers-arithmetic/promoted_overflow_opt.rs

#####################################
# Execution outputs


UI_EXE=$(patsubst %.rs,%.exe,${UI_RS})
ui-exe: ${UI_EXE}

# Default compilation
ui/%.exe: ui/%.rs
	-$(RUSTC) $(RUSTC_OPTIONS) -o $@ ui/$*.rs

# # 'async-await' tests use 2021 ed. 
# ui/async-await/%.exe: ui/async-await/%.rs 
# 	rustc --edition 2021 \
# 	      -o $@ ui/async-await/$*.rs 

# # 'try-block' tests use 2018 ed. 
# ui/try-block/%.exe: ui/try-block/%.rs 
# 	rustc --edition 2018 \
# 	      -o $@ ui/try-block/$*.rs 


# # 'closures/2229_closure_analysis/run_pass' tests use 2021 ed. 
# ui/closures/2229_closure_analysis/run_pass/%.exe: ui/closures/2229_closure_analysis/run_pass/%.rs 
# 	rustc --edition 2021 \
# 	      -o $@ ui/closures/2229_closure_analysis/run_pass/$*.rs

# # 'closures/2229_closure_analysis/optimization' tests use 2021 ed. 
# ui/closures/2229_closure_analysis/optimization/%.exe: ui/closures/2229_closure_analysis/optimization/%.rs 
# 	rustc --edition 2021 \
# 	      -o $@ ui/closures/2229_closure_analysis/optimization/$*.rs

# # 'test-attrs' tests use the '--test' flag. 
# ui/test-attrs/%.exe: ui/test-attrs/%.rs 
# 	rustc --test -o $@ ui/test-attrs/$*.rs 

# # 'try-block/try-is-identifier-edition2015.rs' use 2015 ed. 
# ui/try-block/try-is-identifier-edition2015.exe: ui/try-block/try-is-identifier-edition2015.rs
# 	rustc --edition 2015 \
# 	      -o $@ \
# 		  ui/try-block/try-is-identifier-edition2015.rs

# # 'numbers-arithmetic/promoted_overflow_opt.rs' use the '-O' flag. 
# ui/numbers-arithmetic/promoted_overflow_opt.exe: ui/numbers-arithmetic/promoted_overflow_opt.rs
# 	rustc -O \
# 		  -o $@ \
# 		  ui/numbers-arithmetic/promoted_overflow_opt.rs

UI_OUT=$(patsubst %.exe,%.run.stdout,${UI_EXE})
UI_ERR=$(patsubst %.exe,%.run.stderr,${UI_EXE})

ui-out: ${UI_OUT}

ui/%.run.stdout: ui/%.exe
	timeout 10s ui/$*.exe > $@ 2> ui/$*.run.stderr || true

# Remove exe files
clean-exe:
	find . -name "*.exe" -type f -delete

echo:
	echo ${UI_OUT}