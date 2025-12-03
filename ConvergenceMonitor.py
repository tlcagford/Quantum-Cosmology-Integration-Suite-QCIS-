class ConvergenceMonitor:
    """Monitor and ensure convergence"""
    def __init__(self, max_iter=100, tol=1e-6):
        self.history = []
        self.max_iter = max_iter
        self.tol = tol
        
    def check_convergence(self, H_new, H_old):
        rel_change = np.max(np.abs(H_new - H_old) / H_old)
        self.history.append(rel_change)
        
        if rel_change < self.tol:
            return True, "Converged"
        elif len(self.history) > 10 and np.mean(self.history[-5:]) > np.mean(self.history[-10:-5]):
            return False, "Diverging"
        elif len(self.history) >= self.max_iter:
            return False, "Max iterations reached"
        return None, "Continue"
