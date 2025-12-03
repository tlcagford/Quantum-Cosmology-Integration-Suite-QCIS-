def validate_qft_cosmology_integration():
    """Comprehensive validation"""
    
    # 1. Test known analytic limits
    # Conformally coupled massless field: ⟨T_μν⟩ = 0
    qft = QuantumFieldTheorySimulator(field_type='scalar', m=0, xi=1/6)
    assert np.allclose(qft.compute_RSET(de_Sitter), 0, rtol=1e-10)
    
    # 2. Test conservation: ∇_μ⟨T^μν⟩ = 0
    T_munu = qft.compute_RSET(FLRW_metric)
    assert check_conservation(T_munu) < 1e-8
    
    # 3. Test correspondence principle
    # For ℏ → 0, recover classical
    classical = compute_classical_stress_energy()
    quantum = qft.compute_RSET(metric, hbar=0.1)
    assert np.abs(quantum - classical) < 0.1 * classical
