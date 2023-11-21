TEST_DIR := src/tests/integration/test-data/handwritten-mir/execution/

default: mir-outputs

all: mir-outputs

clean:
	rm -f *.out

mir-outputs:
	(cd ../../.. && poetry run kmir parse --output pretty $(TEST_DIR)arithm-simple.mir) > arithm-simple.parse.out  
	(cd ../../.. && poetry run kmir run   --output pretty $(TEST_DIR)arithm-simple.mir) > arithm-simple.run.out  