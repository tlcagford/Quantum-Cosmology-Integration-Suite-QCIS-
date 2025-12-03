# Add fluent interface
class FluentQCISSolver(UnifiedQCISSolver):
    def with_config(self, config_dict):
        self.config = QCISConfig(**config_dict)
        return self
        
    def with_qft_model(self, model_name):
        self.qft_sim.set_model(model_name)
        return self
        
    def solve(self):
        return self.solve_unified()

# Usage:
results = (FluentQCISSolver()
           .with_config({'H0': 67.4, 'Omega_m0': 0.315})
           .with_qft_model('scalar_field')
           .solve())
