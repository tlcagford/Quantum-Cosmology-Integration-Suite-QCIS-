class SmartQFTToCosmology:
    """Intelligent QFT evaluation for cosmology"""
    
    def __init__(self, qft_engine):
        self.qft = qft_engine
        self.cache = {}
        self.approximation_regimes = {
            'early_inflation': self._inflation_approximation,
            'radiation_dominated': self._radiation_era_approx,
            'matter_dominated': self._matter_era_approx,
            'lambda_dominated': self._lambda_era_approx,
        }
    
    def get_Omega_ent(self, a, params):
        """Smart routing to appropriate calculation"""
        
        # Check cache first
        cache_key = (a, tuple(params.items()))
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Determine which regime we're in
        regime = self._identify_regime(a, params)
        
        if regime in self.approximation_regimes:
            # Use analytic approximation
            Omega = self.approximation_regimes[regime](a, params)
        else:
            # Need full numerical calculation
            if self._should_compute_full(a, params):
                Omega = self._compute_full_qft(a, params)
            else:
                # Interpolate from nearby points
                Omega = self._interpolate(a, params)
        
        # Cache result
        self.cache[cache_key] = Omega
        return Omega
    
    def _should_compute_full(self, a, params):
        """Decide if we need full QFT calculation"""
        # Criteria:
        # 1. No nearby points in parameter space
        # 2. High curvature regime where approximations fail
        # 3. First time seeing these parameters
        return len(self.cache) < 100 or a < 1e-3
