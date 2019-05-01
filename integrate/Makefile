.PHONY: check test

check:
	+./check

testA:
	+pytest -s -p no:xdist

testB:
	+pytest -s -p no:xdist

test: testA
	

test2: testA testB
	
