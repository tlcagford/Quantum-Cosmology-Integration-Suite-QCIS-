    def solve_tensor_perturbations(self) -> Dict:
        """
        Solve tensor perturbation equations (gravitational waves) with quantum sources
        
        Equation: h_ij'' + 2H h_ij' + k^2 h_ij = 16πG a^2 Π_ij^quantum
        """
        print("Solving tensor perturbations with quantum sources...")
        
        n_k = len(self.k_modes)
        n_a = len(self.a)
        
        tensor_results = {
            'k_modes': self.k_modes,
            'scale_factor': self.a,
            'h_plus': np.zeros((n_k, n_a), dtype=complex),
            'h_cross': np.zeros((n_k, n_a), dtype=complex),
            'quantum_sources': np.zeros((n_k, n_a), dtype=complex)
        }
        
        for i_k, k in enumerate(self.k_modes):
            if i_k % 10 == 0:
                print(f"  Processing k = {k:.2e} Mpc⁻¹ ({i_k+1}/{n_k})")
            
            # Quantum anisotropic stress source
            Pi_quantum = self._compute_quantum_anisotropic_stress(k)
            
            # Solve GW equation for plus and cross polarizations
            h_plus = self._solve_gw_equation(k, Pi_quantum, polarization='plus')
            h_cross = self._solve_gw_equation(k, Pi_quantum, polarization='cross')
            
            tensor_results['h_plus'][i_k] = h_plus
            tensor_results['h_cross'][i_k] = h_cross
            tensor_results['quantum_sources'][i_k] = Pi_quantum
        
        # Compute tensor power spectrum
        tensor_results['power_spectrum'] = self._compute_tensor_power_spectrum(tensor_results)
        
        self.results['tensor'] = tensor_results
        return tensor_results
    
    def _solve_gw_equation(self, k: float, Pi_source: np.ndarray, 
                          polarization: str = 'plus') -> np.ndarray:
        """
        Solve gravitational wave equation with quantum source
        
        h'' + 2H h' + k^2 h = 16πG a^2 Π
        """
        from scipy.integrate import solve_ivp
        
        def gw_ode(eta, y):
            """GW equation in conformal time"""
            i = np.searchsorted(self.eta, eta)
            i = min(i, len(self.eta)-1)
            a = self.a[i]
            H = self.H[i]
            a_prime = a * H  # da/dη = a^2 H
            
            h, h_prime = y[0], y[1]
            
            # Damping term: 2H h' = 2(a'/a) h'
            damping = 2 * (a_prime / a) * h_prime
            
            # Source term: 16πG a^2 Π
            source = 16 * np.pi * self.G * a**2 * Pi_source[i]
            
            # Return derivatives
            return [h_prime, -damping - k**2 * h + source]
        
        # Initial conditions (Bunch-Davies vacuum)
        eta0 = self.eta[0]
        h0 = 1/np.sqrt(2*k) * np.exp(-1j*k*eta0)
        h_prime0 = -1j*k * h0
        
        # Solve ODE
        sol = solve_ivp(
            gw_ode,
            [eta0, self.eta[-1]],
            [h0, h_prime0],
            method='RK45',
            t_eval=self.eta,
            rtol=self.config.rtol,
            atol=self.config.atol
        )
        
        return sol.y[0]
