# test_physics.py
def test_lcdm_limit():
    """Test that quantum corrections vanish when cutoff → ∞"""
    solver = UnifiedQCISSolver(cutoff_scale=1e100)  # Effectively no quantum corrections
    results = solver.solve_unified()
    # Should match ΛCDM to high precision
    assert np.allclose(results['H_QCIS'], results['H_ΛCDM'], rtol=1e-10)

def test_energy_conservation():
    """Test ∇_μ T^μν = 0"""
    solver = UnifiedQCISSolver()
    results = solver.solve_unified()
    # Check conservation equation
    # ∇_μ T^μν_matter + ∇_μ T^μν_entanglement = 0
    assert check_conservation(results['T_munu_matter'], results['T_munu_ent'])

def test_numerical_convergence():
    """Test convergence with resolution"""
    solver1 = UnifiedQCISSolver(n_points=100)
    solver2 = UnifiedQCISSolver(n_points=1000)
    results1 = solver1.solve_unified()
    results2 = solver2.solve_unified()
    # Should converge
    assert np.abs(results1['H'] - results2['H']).max() < 1e-4
