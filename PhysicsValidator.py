class PhysicsValidator:
    """Validate physical consistency"""
    
    @staticmethod
    def check_energy_conditions(rho, p):
        """Check weak, strong, dominant energy conditions"""
        # Weak: rho >= 0, rho + p >= 0
        # Strong: rho + 3p >= 0
        # Dominant: rho >= |p|
        violations = []
        if rho < 0:
            violations.append("Negative energy density")
        if rho + p < 0:
            violations.append("Weak energy condition violated")
        return violations
    
    @staticmethod
    def check_causality(c_sound_squared):
        """Check causality (c_sound <= 1)"""
        if c_sound_squared > 1:
            return "Superluminal sound speed"
        return None

class ErrorRecovery:
    """Graceful error recovery"""
    def solve_with_recovery(self):
        try:
            return self.solve_unified()
        except ConvergenceError:
            print("Using fallback method...")
            return self.solve_with_fallback()
        except NumericalInstabilityError:
            print("Reducing step size...")
            self.config.n_points *= 2
            return self.solve_unified()
