PYTHON=python3
SRC=src

game: $(SRC)/game.py
	@$(PYTHON) $^

stats: $(SRC)/stats.py
	@mkdir -p charts
	@$(PYTHON) $^
