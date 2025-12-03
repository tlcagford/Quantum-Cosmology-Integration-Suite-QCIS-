# Run these to audit your code:
$ find . -name "*.py" -type f | wc -l
# Expected: ~50-100 files

$ cloc . --exclude-dir=venv,__pycache__,.git
# Expected: ~10,000-15,000 lines of code

$ pylint quantum_perturbation_solver.py
# Aim for >8.0 score

$ mypy quantum_perturbation_solver.py --strict
# Type checking
