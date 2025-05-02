PYTHON=python3
SRC=src

play: $(SRC)/game.py
	$(PYTHON) $^

test: $(SRC)/test_solver.py
	$(PYTHON) $^
