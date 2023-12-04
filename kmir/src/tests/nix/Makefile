TEST_DIR := src/tests/integration/test-data/run-rs/functions/

default: mir-outputs

all: mir-outputs

clean:
	rm -f *.out

mir-outputs:
	(cd ../../.. && poetry run kmir parse --output pretty $(TEST_DIR)sum-to-n.mir) > sum-to-n.parse.out  
	(cd ../../.. && poetry run kmir run   --output pretty $(TEST_DIR)sum-to-n.mir) > sum-to-n.run.out  