    def _compute_scalar_power_spectrum(self, scalar_results: Dict) -> Dict:
        """Compute scalar power spectrum P_ζ(k) and matter power spectrum P(k)"""
        k_modes = scalar_results['k_modes']
        Phi = scalar_results['Phi']
        z = scalar_results['redshift']
        
        # Curvature perturbation ζ = -Φ - (2/3) [(1+w)^-1] (Φ' + HΨ)/H
        # For super-horizon, ζ ≈ -Φ - (2/3) (Φ' + HΨ)/[H(1+w)]
        
        # Compute ζ at late times (a ≈ 1)
        idx_late = len(self.a) - 1
        zeta = -Phi[:, idx_late]  # Approximate
        
        # Power spectrum P_ζ(k) = k^3/(2π^2) |ζ_k|^2
        P_zeta = k_modes**3/(2*np.pi**2) * np.abs(zeta)**2
        
        # Matter power spectrum P(k) = ⟨|δ_m(k)|^2⟩
        # δ_m = (Ω_cdm δ_cdm + Ω_b δ_b) / (Ω_cdm + Ω_b)
        Omega_total = self.config.Omega_cdm + self.config.Omega_b
        delta_m = (
            self.config.Omega_cdm * scalar_results['delta_cdm'][:, idx_late] +
            self.config.Omega_b * scalar_results['delta_b'][:, idx_late]
        ) / Omega_total
        
        P_matter = k_modes**3/(2*np.pi**2) * np.abs(delta_m)**2
        
        # Transfer function T(k) = δ_m(k)/δ_m(k_large)
        # Normalize to large scales
        k_large = 1e-3  # Mpc^-1
        idx_large = np.argmin(np.abs(k_modes - k_large))
        T_k = np.abs(delta_m) / np.abs(delta_m[idx_large])
        
        return {
            'P_zeta': P_zeta,
            'P_matter': P_matter,
            'transfer_function': T_k,
            'sigma_8': self._compute_sigma8(P_matter, k_modes),
            'n_s': self._compute_spectral_index(P_zeta, k_modes)
        }
    
    def _compute_sigma8(self, P_k: np.ndarray, k_modes: np.ndarray) -> float:
        """Compute σ_8 from matter power spectrum"""
        # Top-hat window function W(kR) = 3/(kR)^3 [sin(kR) - kR cos(kR)]
        R = 8.0  # 8 Mpc/h
        kR = k_modes * R
        
        # Avoid division by zero
        kR[kR == 0] = 1e-10
        W = 3/(kR**3) * (np.sin(kR) - kR * np.cos(kR))
        
        # σ^2(R) = ∫ dk/k P(k) W^2(kR)
        integrand = P_k * W**2 / k_modes
        sigma2 = integrate.trapezoid(integrand, np.log(k_modes))
        
        return np.sqrt(sigma2)
