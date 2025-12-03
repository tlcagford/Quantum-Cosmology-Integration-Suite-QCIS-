"""
QCIS Unified Solver: First-principles quantum-cosmology integration
"""

import numpy as np
from typing import Dict, List, Optional, Union, Callable
from dataclasses import dataclass
import yaml

@dataclass
class QCISConfig:
    """Configuration for the unified solver"""
    # Cosmology parameters
    H0: float = 67.4
    Omega_m0: float = 0.315
    Omega_b0: float = 0.049
    Omega_r0: float = 9.24e-5
    Omega_Lambda0: float = 0.685
    
    # QFT parameters
    field_type: str = "scalar"  # scalar, fermion, vector
    mass: float = 0.0  # Field mass
    coupling: float = 0.0  # Coupling constant
    cutoff_scale: float = 1e19  # Planck scale in GeV
    
    # Numerical parameters
    a_range: tuple = (1e-10, 2.0)
    n_points: int = 1000
    interpolation_method: str = "cubic"
    
    # Computation mode
    mode: str = "unified"  # unified, qft_only, ecc_only
    
    # Output options
    save_results: bool = True
    output_format: str = "hdf5"

class UnifiedQCISSolver:
    """
    Unified solver for first-principles quantum cosmology.
    
    This class integrates:
    1. QFT simulations to compute quantum corrections
    2. Modified Friedmann equations with entanglement corrections
    3. Observational predictions and constraints
    
    Example:
    ```python
    solver = UnifiedQCISSolver()
    results = solver.solve()
    solver.plot_comparison()
    ```
    """
    
    def __init__(self, config: Optional[QCISConfig] = None):
        """Initialize unified solver"""
        self.config = config or QCISConfig()
        
        # Import components
        from qcis.qft_engine.simulator import QFTSimulator
        from qcis.cosmology.friedmann_solver import ModifiedFriedmannSolver
        from qcis.bridge.qft_to_cosmology import QFT2CosmoBridge
        
        # Initialize components
        self.qft_sim = QFTSimulator(
            field_type=self.config.field_type,
            mass=self.config.mass,
            cutoff=self.config.cutoff_scale
        )
        
        self.cosmo_solver = ModifiedFriedmannSolver(
            H0=self.config.H0,
            Omega_m0=self.config.Omega_m0,
            Omega_b0=self.config.Omega_b0,
            Omega_r0=self.config.Omega_r0,
            Omega_Lambda0=self.config.Omega_Lambda0
        )
        
        self.bridge = QFT2CosmoBridge(
            qft_simulator=self.qft_sim,
            cosmo_solver=self.cosmo_solver,
            interpolation=self.config.interpolation_method
        )
        
        # Results storage
        self.results = {}
        
    def compute_entanglement_corrections(self, a: np.ndarray) -> Dict:
        """
        Compute entanglement corrections from first principles.
        
        Parameters
        ----------
        a : np.ndarray
            Scale factors at which to compute corrections
            
        Returns
        -------
        dict
            Dictionary with:
            - Omega_ent(a): Entanglement density
            - w_ent(a): Equation of state
            - T_ent_munu(a): Stress-energy tensor components
        """
        results = {}
        
        # For each scale factor, compute QFT vacuum expectation values
        for i, scale_factor in enumerate(a):
            # Set up spacetime metric for this scale factor
            metric = self._create_FLRW_metric(scale_factor)
            
            # Compute renormalized stress-energy tensor
            T_munu = self.qft_sim.compute_RSET(
                metric=metric,
                renormalization_scheme="adiabatic",
                order=4  # 4th order adiabatic regularization
            )
            
            # Extract energy density and pressure
            rho_ent = T_munu[0, 0]  # T_00 component
            p_ent = np.mean(T_munu[1:4, 1:4])  # Spatial diagonal average
            
            # Store results
            results[scale_factor] = {
                'rho_ent': rho_ent,
                'p_ent': p_ent,
                'w_ent': p_ent / rho_ent if rho_ent != 0 else -1,
                'T_munu': T_munu
            }
        
        # Convert to Omega_ent (dimensionless density parameter)
        rho_crit0 = 3 * self.cosmo_solver.H0**2 / (8 * np.pi * 6.67430e-11)
        Omega_ent = {a: r['rho_ent'] / rho_crit0 for a, r in results.items()}
        
        return {
            'Omega_ent': Omega_ent,
            'w_ent': {a: r['w_ent'] for a, r in results.items()},
            'raw_results': results
        }
    
    def solve_unified(self, a_range: Optional[tuple] = None) -> Dict:
        """
        Solve the coupled quantum-cosmological system.
        
        Uses iterative approach:
        1. Start with ΛCDM background
        2. Compute QFT corrections on this background
        3. Solve modified Friedmann equations
        4. Repeat until convergence
        """
        a_range = a_range or self.config.a_range
        a_min, a_max = a_range
        n_points = self.config.n_points
        
        # Create scale factor array (log spacing for early times)
        if a_min < 0.01:
            a = np.logspace(np.log10(a_min), np.log10(a_max), n_points)
        else:
            a = np.linspace(a_min, a_max, n_points)
        
        # Initial guess: ΛCDM background
        H_lcdm = self.cosmo_solver.H(a, model_name='lcdm')
        
        # Iterative solution
        max_iterations = 10
        tolerance = 1e-6
        
        for iteration in range(max_iterations):
            print(f"Iteration {iteration + 1}/{max_iterations}")
            
            # Step 1: Compute QFT corrections on current background
            corrections = self.compute_entanglement_corrections(a)
            Omega_ent = corrections['Omega_ent']
            
            # Step 2: Create interpolator for Omega_ent(a)
            from scipy import interpolate
            a_values = np.array(list(Omega_ent.keys()))
            Omega_ent_values = np.array(list(Omega_ent.values()))
            Omega_ent_interp = interpolate.interp1d(
                a_values, Omega_ent_values,
                kind=self.config.interpolation_method,
                fill_value="extrapolate"
            )
            
            # Step 3: Solve modified Friedmann equations
            def custom_entanglement(a):
                return Omega_ent_interp(a)
            
            H_new = self.cosmo_solver.H(
                a,
                model_name='custom',
                custom_function=custom_entanglement
            )
            
            # Check convergence
            diff = np.max(np.abs(H_new - H_lcdm) / H_lcdm)
            print(f"  Max relative change: {diff:.2e}")
            
            if diff < tolerance:
                print(f"Converged after {iteration + 1} iterations")
                H_lcdm = H_new
                break
            
            H_lcdm = H_new
        
        # Package results
        self.results = {
            'scale_factor': a,
            'Hubble': H_lcdm,
            'corrections': corrections,
            'Omega_ent': Omega_ent,
            'converged': diff < tolerance,
            'iterations': iteration + 1
        }
        
        return self.results
    
    def compute_observables(self) -> Dict:
        """Compute cosmological observables from solution"""
        if not self.results:
            raise ValueError("Run solve_unified() first")
        
        a = self.results['scale_factor']
        H = self.results['Hubble']
        z = 1/a - 1
        
        # Luminosity distance
        from qcis.cosmology.observables import LuminosityDistance
        dL_calc = LuminosityDistance(H_func=lambda z: np.interp(z, z[::-1], H[::-1]))
        dL = dL_calc.compute(z)
        
        # Angular diameter distance
        dA = dL / (1 + z)**2
        
        # Comoving distance
        dc = dL / (1 + z)
        
        # Growth factor (approximate)
        Omega_m = self.cosmo_solver.Omega_m0 / a**3
        Omega_ent = np.array(list(self.results['Omega_ent'].values()))
        Omega_total = Omega_m + self.cosmo_solver.Omega_Lambda0 + Omega_ent
        
        # Growth ODE: f' + f^2 + (2 - 3Ω_m/2)f - 3Ω_m/2 = 0
        # Simplified calculation
        f = Omega_m**0.55  # Approximate growth rate
        
        observables = {
            'redshift': z,
            'luminosity_distance': dL,
            'angular_diameter_distance': dA,
            'comoving_distance': dc,
            'growth_factor': f,
            'Omega_m_z': Omega_m,
            'Omega_ent_z': Omega_ent
        }
        
        self.results['observables'] = observables
        return observables
    
    def compare_with_data(self, dataset: str = 'planck2018') -> Dict:
        """Compare predictions with observational data"""
        from qcis.cosmology.data_fitting import DataComparer
        
        comparer = DataComparer(dataset=dataset)
        
        # Get observables if not already computed
        if 'observables' not in self.results:
            self.compute_observables()
        
        # Compute chi-squared
        chi2 = comparer.compute_chi2(
            redshifts=self.results['observables']['redshift'],
            dL_pred=self.results['observables']['luminosity_distance'],
            H_pred=self.results['Hubble']
        )
        
        # Bayesian evidence (approximate)
        n_params = 6  # Cosmological + QFT parameters
        n_data = comparer.n_data_points
        dof = n_data - n_params
        
        comparison = {
            'chi2': chi2,
            'chi2_per_dof': chi2 / dof,
            'dof': dof,
            'n_data': n_data,
            'p_value': 1 - stats.chi2.cdf(chi2, dof),
            'dataset': dataset,
            'parameters': self.config.__dict__
        }
        
        self.results['data_comparison'] = comparison
        return comparison
    
    def plot_results(self, save_path: Optional[str] = None):
        """Generate comprehensive plots"""
        import matplotlib.pyplot as plt
        from qcis.visualization.plotter import QCISPlotter
        
        plotter = QCISPlotter()
        
        fig = plt.figure(figsize=(16, 10))
        
        # Plot 1: Hubble parameter evolution
        ax1 = plt.subplot(2, 3, 1)
        plotter.plot_H_z(self.results, ax=ax1)
        
        # Plot 2: Density parameters
        ax2 = plt.subplot(2, 3, 2)
        plotter.plot_density_parameters(self.results, ax=ax2)
        
        # Plot 3: Entanglement correction
        ax3 = plt.subplot(2, 3, 3)
        plotter.plot_entanglement_correction(self.results, ax=ax3)
        
        # Plot 4: Distance modulus comparison
        ax4 = plt.subplot(2, 3, 4)
        plotter.plot_distance_modulus(self.results, ax=ax4)
        
        # Plot 5: Growth factor
        ax5 = plt.subplot(2, 3, 5)
        plotter.plot_growth_factor(self.results, ax=ax5)
        
        # Plot 6: Parameter constraints
        ax6 = plt.subplot(2, 3, 6)
        if 'data_comparison' in self.results:
            plotter.plot_parameter_space(self.results, ax=ax6)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig
    
    def save_results(self, filename: str = "qcis_results.h5"):
        """Save results to HDF5 file"""
        import h5py
        
        with h5py.File(filename, 'w') as f:
            # Save arrays
            for key, value in self.results.items():
                if isinstance(value, np.ndarray):
                    f.create_dataset(key, data=value)
                elif isinstance(value, dict):
                    grp = f.create_group(key)
                    for subkey, subvalue in value.items():
                        if isinstance(subvalue, np.ndarray):
                            grp.create_dataset(subkey, data=subvalue)
            
            # Save config
            config_grp = f.create_group('config')
            for key, value in self.config.__dict__.items():
                if isinstance(value, (int, float, str)):
                    config_grp.attrs[key] = value
    
    @classmethod
    def load_results(cls, filename: str) -> 'UnifiedQCISSolver':
        """Load results from file"""
        import h5py
        
        with h5py.File(filename, 'r') as f:
            # Load config
            config_dict = dict(f['config'].attrs)
            solver = cls(config=QCISConfig(**config_dict))
            
            # Load results
            solver.results = {}
            for key in f.keys():
                if key != 'config':
                    if isinstance(f[key], h5py.Group):
                        solver.results[key] = {}
                        for subkey in f[key].keys():
                            solver.results[key][subkey] = f[key][subkey][:]
                    else:
                        solver.results[key] = f[key][:]
        
        return solver
    
    def _create_FLRW_metric(self, a: float) -> np.ndarray:
        """Create FLRW metric for given scale factor"""
        # Flat FLRW metric in conformal coordinates
        # ds² = a²(η)[-dη² + δ_ij dx^i dx^j]
        metric = np.zeros((4, 4))
        metric[0, 0] = -a**2
        metric[1, 1] = a**2
        metric[2, 2] = a**2
        metric[3, 3] = a**2
        
        return metric


# Convenience functions
def quick_solve(config_dict: Optional[Dict] = None) -> Dict:
    """Quick one-line solution"""
    config = QCISConfig(**(config_dict or {}))
    solver = UnifiedQCISSolver(config)
    results = solver.solve_unified()
    observables = solver.compute_observables()
    return {**results, **observables}

def compare_with_lcdm(config_dict: Optional[Dict] = None) -> Dict:
    """Compare QCIS with ΛCDM"""
    from qcis.cosmology.friedmann_solver import ModifiedFriedmannSolver
    
    # QCIS solution
    qcis_results = quick_solve(config_dict)
    
    # ΛCDM solution
    lcdm_solver = ModifiedFriedmannSolver(
        H0=config_dict.get('H0', 67.4) if config_dict else 67.4,
        Omega_m0=config_dict.get('Omega_m0', 0.315) if config_dict else 0.315,
        Omega_Lambda0=config_dict.get('Omega_Lambda0', 0.685) if config_dict else 0.685
    )
    
    a = qcis_results['scale_factor']
    H_lcdm = lcdm_solver.H(a, model_name='lcdm')
    
    comparison = {
        'scale_factor': a,
        'H_QCIS': qcis_results['Hubble'],
        'H_ΛCDM': H_lcdm,
        'relative_difference': (qcis_results['Hubble'] - H_lcdm) / H_lcdm,
        'Omega_ent': qcis_results.get('Omega_ent', {}),
        'config': config_dict
    }
    
    return comparison
