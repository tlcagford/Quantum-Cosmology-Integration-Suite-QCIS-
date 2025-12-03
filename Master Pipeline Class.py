class QuantumCosmologyPipeline:
    """
    Complete pipeline from QFT to CMB predictions
    
    Steps:
    1. Background with quantum corrections ✓
    2. Perturbation theory with quantum backreaction ✓
    3. Boltzmann integration with quantum scattering ✓
    4. CMB power spectra with quantum effects ✓
    5. Comparison with Planck and other data
    """
    
    def __init__(self, config):
        self.config = config
        
        # Initialize all components
        self.background_solver = UnifiedQCISSolver(config)
        self.perturbation_solver = QuantumCosmologicalPerturbations(self.background_solver)
        self.boltzmann_solver = QuantumBoltzmannSolver(self.perturbation_solver)
        self.spacetime_solver = DynamicalSpacetimeSolver(config.initial_data, 
                                                       config.quantum_fields)
        self.holographic_calculator = HolographicCausalWedge(self.spacetime_solver,
                                                           config.entanglement_calc)
        
    def run_full_pipeline(self):
        """Execute complete quantum cosmology pipeline"""
        
        print("="*60)
        print("QUANTUM COSMOLOGY PIPELINE")
        print("="*60)
        
        # Step 1: Background with quantum corrections
        print("\n1. Computing background with quantum corrections...")
        background_results = self.background_solver.solve_unified()
        
        # Step 2: Perturbation theory
        print("\n2. Solving perturbation equations with quantum backreaction...")
        k_modes = np.logspace(-4, 2, 200)  # Mpc^{-1}
        scalar_pert = self.perturbation_solver.compute_scalar_perturbations(k_modes)
        tensor_pert = self.perturbation_solver.compute_tensor_perturbations(k_modes)
        
        # Step 3: Boltzmann integration
        print("\n3. Running Boltzmann solver with quantum scattering...")
        boltzmann_results = self.boltzmann_solver.solve_multipole_hierarchy(k_modes)
        
        # Step 4: CMB power spectra
        print("\n4. Computing CMB power spectra with quantum effects...")
        cmb_spectra = self.boltzmann_solver.compute_cmb_power_spectra(boltzmann_results)
        
        # Step 5: Spacetime evolution (optional, computationally intensive)
        if self.config.compute_dynamical_spacetime:
            print("\n5. Evolving dynamical spacetime with quantum sources...")
            spacetime_history = self.spacetime_solver.evolve(
                t_final=self.config.t_final,
                dt=self.config.dt
            )
        
        # Step 6: Holographic reconstruction (advanced)
        if self.config.compute_holographic:
            print("\n6. Performing holographic reconstruction...")
            boundary_data = self._extract_boundary_data(boltzmann_results)
            holographic_results = self.holographic_calculator.reconstruct_bulk_from_boundary(
                boundary_data, self.config.time_range
            )
        
        # Step 7: Compare with observational data
        print("\n7. Comparing with observational data...")
        comparison = self._compare_with_observations(cmb_spectra)
        
        # Package results
        results = {
            'background': background_results,
            'scalar_perturbations': scalar_pert,
            'tensor_perturbations': tensor_pert,
            'boltzmann': boltzmann_results,
            'cmb_spectra': cmb_spectra,
            'data_comparison': comparison,
            'config': self.config.__dict__
        }
        
        if self.config.compute_dynamical_spacetime:
            results['spacetime_evolution'] = spacetime_history
        
        if self.config.compute_holographic:
            results['holographic_reconstruction'] = holographic_results
        
        print("\n✓ Pipeline complete!")
        return results
    
    def _compare_with_observations(self, cmb_spectra):
        """Compare predictions with Planck, ACT, SPT, etc."""
        
        # Load observational data
        planck_data = self._load_planck_data()
        bao_data = self._load_bao_data()
        sn_data = self._load_supernova_data()
        
        # Compute chi-squared
        chi2_cmb = self._compute_chi2_cmb(cmb_spectra, planck_data)
        chi2_bao = self._compute_chi2_bao(bao_data)
        chi2_sn = self._compute_chi2_sn(sn_data)
        
        # Bayesian evidence
        evidence = self._compute_bayesian_evidence(chi2_cmb + chi2_bao + chi2_sn)
        
        return {
            'chi2_cmb': chi2_cmb,
            'chi2_bao': chi2_bao,
            'chi2_sn': chi2_sn,
            'chi2_total': chi2_cmb + chi2_bao + chi2_sn,
            'bayesian_evidence': evidence,
            'tension_with_lcdm': self._compute_hubble_tension(),
            's8_tension': self._compute_s8_tension()
        }
