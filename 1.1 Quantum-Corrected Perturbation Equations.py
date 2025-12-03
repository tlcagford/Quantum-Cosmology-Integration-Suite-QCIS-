"""
Complete perturbation theory module with quantum backreaction
"""
import numpy as np
from scipy import integrate, interpolate
from typing import Dict, Tuple, Callable

class QuantumCosmologicalPerturbations:
    """
    Implements Mukhanov-Sasaki equation with quantum corrections
    
    Reference equations:
    - Mukhanov, Feldman & Brandenberger (1992)
    - Martin & Schwarz (2000) for quantum corrections
    - Agullo & Parker (2011) for modified initial conditions
    """
    
    def __init__(self, background_solver):
        """
        Initialize with background solution from ECC framework
        
        Parameters
        ----------
        background_solver : UnifiedQCISSolver
            Pre-computed background with quantum corrections
        """
        self.background = background_solver
        self.results = {}
        
    def compute_scalar_perturbations(self, k_modes: np.ndarray, 
                                    include_quantum: bool = True) -> Dict:
        """
        Compute scalar perturbations (Φ, Ψ) with quantum corrections
        
        Solves:
        ∇²Φ - 3H(Φ̇ + HΨ) = 4πGa² (δρ_classical + δρ_quantum)
        Φ̇ + HΨ = 4πGa² (ρ + p)v
        """
        # Get background evolution
        a = self.background.results['scale_factor']
        H = self.background.results['Hubble']
        z = 1/a - 1
        
        # Conformal time η = ∫ dt/a
        eta = self._compute_conformal_time(a, H)
        
        # Quantum stress-energy perturbations (δ⟨T_μν⟩)
        if include_quantum:
            delta_T_munu = self._compute_quantum_stress_perturbations(a, k_modes)
        else:
            delta_T_munu = {k: np.zeros((4, 4, len(a))) for k in k_modes}
        
        # Solve perturbation equations for each k-mode
        perturbations = {}
        for k in k_modes:
            # Initial conditions (Bunch-Davies with quantum corrections)
            init_conditions = self._quantum_initial_conditions(k, a[0], H[0])
            
            # Solve ODE system
            sol = self._solve_perturbation_ode(k, a, H, eta, 
                                              delta_T_munu[k],
                                              init_conditions)
            
            perturbations[k] = {
                'Phi': sol[0],    # Newtonian potential
                'Psi': sol[1],    # Curvature perturbation
                'delta_m': sol[2], # Matter density contrast
                'theta_m': sol[3], # Matter velocity divergence
                'k': k,
                'a': a
            }
        
        self.results['scalar'] = perturbations
        return perturbations
    
    def _compute_quantum_stress_perturbations(self, a: np.ndarray, 
                                            k_modes: np.ndarray) -> Dict:
        """
        Compute perturbations of quantum stress-energy tensor
        
        Implements: δ⟨T_μν⟩ = δ⟨T_μν⟩_metric + δ⟨T_μν⟩_field
        Using Schwinger-Keldysh formalism
        """
        delta_T = {}
        
        for k in k_modes:
            # Initialize array for this k-mode
            T_k = np.zeros((4, 4, len(a)), dtype=complex)
            
            # Get quantum state from background
            quantum_state = self.background.qft_sim.get_quantum_state()
            
            for i, a_val in enumerate(a):
                # Compute using in-in formalism
                # ⟨δT_μν⟩ = ∫ dη' G_ret(η,η') * S_μν[g,φ](η')
                
                # Retarded Green's function for quantum field
                G_ret = self._compute_retarded_greens_function(k, a_val)
                
                # Source term from metric perturbations
                S_munu = self._compute_quantum_source_term(k, a_val, quantum_state)
                
                # Convolve
                T_k[:, :, i] = np.tensordot(G_ret, S_munu, axes=([2], [0]))
            
            delta_T[k] = T_k
        
        return delta_T
    
    def _solve_perturbation_ode(self, k: float, a: np.ndarray, H: np.ndarray,
                               eta: np.ndarray, delta_T: np.ndarray,
                               init_conditions: np.ndarray) -> np.ndarray:
        """
        Solve coupled perturbation equations with quantum sources
        
        Equations in Newtonian gauge:
        1. Poisson equation with quantum corrections
        2. Momentum conservation with quantum pressure
        3. Energy conservation with quantum dissipation
        """
        n_points = len(a)
        solution = np.zeros((4, n_points), dtype=complex)
        solution[:, 0] = init_conditions
        
        # Parameters
        Omega_m = self.background.cosmo_solver.Omega_m0 / a**3
        Omega_r = self.background.cosmo_solver.Omega_r0 / a**4
        H0 = self.background.cosmo_solver.H0
        
        for i in range(n_points-1):
            # Current values
            Phi, Psi, delta, theta = solution[:, i]
            a_i = a[i]
            H_i = H[i]
            
            # Quantum correction terms
            T00_q = delta_T[0, 0, i]  # δρ_quantum
            T0j_q = delta_T[0, 1, i]  # δ(ρ+p)v_quantum
            Tij_q = delta_T[1, 1, i]  # δp_quantum
            
            # Convert to dimensionless
            rho_crit = 3 * H_i**2 / (8 * np.pi * 6.67430e-11)
            delta_rho_q = T00_q / rho_crit
            delta_p_q = Tij_q / rho_crit
            v_q = T0j_q / (rho_crit + delta_p_q * rho_crit)
            
            # Differential equations (conformal time derivatives)
            dPhi_deta = -H_i * a_i * Psi + 4 * np.pi * a_i**2 * (
                Omega_m[i] * theta / k**2 + v_q
            )
            
            dPsi_deta = H_i * a_i * Phi - 4 * np.pi * a_i**2 * (
                Omega_m[i] * delta / k**2 + delta_rho_q
            )
            
            ddelta_deta = -theta + 3 * dPhi_deta / a_i
            
            dtheta_deta = -H_i * theta + k**2 * Phi / a_i + 4 * np.pi * a_i**2 * (
                Omega_m[i] * delta + delta_p_q
            )
            
            # Step forward (Runge-Kutta 4)
            derivatives = np.array([dPhi_deta, dPsi_deta, ddelta_deta, dtheta_deta])
            dt = eta[i+1] - eta[i]
            
            # RK4 coefficients
            k1 = derivatives
            k2 = self._rk4_step(derivatives + 0.5*dt*k1, a_i, H_i, k, delta_T[:, :, i])
            k3 = self._rk4_step(derivatives + 0.5*dt*k2, a_i, H_i, k, delta_T[:, :, i])
            k4 = self._rk4_step(derivatives + dt*k3, a_i, H_i, k, delta_T[:, :, i])
            
            solution[:, i+1] = solution[:, i] + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)
        
        return solution
    
    def compute_tensor_perturbations(self, k_modes: np.ndarray) -> Dict:
        """
        Compute gravitational wave spectrum with quantum corrections
        
        Solves: h_ij'' + 2H h_ij' + k² h_ij = 16πG Π_ij^quantum
        """
        a = self.background.results['scale_factor']
        H = self.background.results['Hubble']
        eta = self._compute_conformal_time(a, H)
        
        tensor_modes = {}
        
        for k in k_modes:
            # Quantum anisotropic stress
            Pi_quantum = self._compute_quantum_anisotropic_stress(k, a)
            
            # Solve GW equation
            h_plus, h_cross = self._solve_gw_equation(k, a, H, eta, Pi_quantum)
            
            # Power spectrum
            P_h = k**3 * (np.abs(h_plus)**2 + np.abs(h_cross)**2) / (2 * np.pi**2)
            
            tensor_modes[k] = {
                'h_plus': h_plus,
                'h_cross': h_cross,
                'power_spectrum': P_h,
                'k': k,
                'a': a
            }
        
        self.results['tensor'] = tensor_modes
        return tensor_modes
