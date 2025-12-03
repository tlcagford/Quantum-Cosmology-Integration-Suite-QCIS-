from qcis import early_universe_evolution

evolution = early_universe_evolution(
    a_range=(1e-30, 1e-10),
    inflation_model='slow_roll',
    quantum_corrections=True
)
