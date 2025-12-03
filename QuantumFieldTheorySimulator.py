# Key features I found:
class QuantumFieldTheorySimulator:
    def __init__(self, spacetime_metric, field_type='scalar'):
        self.metric = spacetime_metric
        self.field_type = field_type
        
    def solve_mode_functions(self, k_modes):
        """Solve mode equations in curved background"""
        # Implementation of:
        # u_k''(η) + [k² + m²a² - (1-6ξ)a''/a] u_k = 0
        
    def compute_bogoliubov_coefficients(self):
        """Compute α_k, β_k for particle production"""
        
    def renormalized_stress_energy_tensor(self):
        """Compute ⟨T_μν⟩ with adiabatic subtraction"""
        # Uses 4th order adiabatic regularization
        return self.adiabatic_subtraction(raw_T_munu, order=4)
