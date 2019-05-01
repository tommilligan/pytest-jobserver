.PHONY: check test

testA:
	+pytest -s -p no:xdist test_long.py

testB:
	+pytest -s -p no:xdist test_long.py

test: testA
	

test2: testA testB
	
