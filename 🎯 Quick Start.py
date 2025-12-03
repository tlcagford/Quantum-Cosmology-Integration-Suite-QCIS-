from qcis import UnifiedQCISSolver, quick_solve

# One-line solution
results = quick_solve({
    'H0': 67.4,
    'Omega_m0': 0.315,
    'field_type': 'scalar',
    'mass': 0.0
})

# Or use full solver
solver = UnifiedQCISSolver()
solver.solve_unified()
solver.compute_observables()
solver.plot_results('results.png')
