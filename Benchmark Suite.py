class QFTCosmologyBenchmarks:
    """Validation against known results"""
    
    def test_de_sitter_exact(self):
        """For m=0, ξ=1/6 in de Sitter: ⟨T_μν⟩ = 0"""
        T_munu = qft.compute_RSET(de_sitter_metric)
        assert np.allclose(T_munu, 0, atol=1e-12)
        
    def test_conformal_anomaly(self):
        """Trace anomaly: ⟨T^μ_μ⟩ = anomalies"""
        expected = (a * R^2 + b * R_μνR^μν + c * R_μνρσR^μνρσ)
        computed = np.trace(T_munu)
        assert relative_error < 1e-8
        
    def test_late_time_wkb(self):
        """Late times match WKB approximation"""
        a_late = 1000
        T_exact = qft.compute_RSET(metric_at_a)
        T_wkb = compute_wkb_approximation(a_late)
        assert relative_error < 0.01  # 1% accuracy sufficient
