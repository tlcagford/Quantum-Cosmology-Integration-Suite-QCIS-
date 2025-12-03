class EfficientQCISBridge:
    """Efficient coupling of QFT to cosmology"""
    
    def __init__(self, qft_simulator):
        self.qft = qft_simulator
        
    def build_surrogate_model(self, training_points=100):
        """Learn Ω_ent(a) from sparse QFT evaluations"""
        # 1. Select strategic a values
        a_train = self._strategic_sampling()
        
        # 2. Compute full QFT at these points
        Omega_ent_train = []
        for a in a_train:
            metric = self._FLRW_metric(a)
            T_munu = self.qft.compute_RSET(metric)
            Omega_ent_train.append(self._T00_to_Omega(T_munu[0,0]))
        
        # 3. Train Gaussian Process
        from sklearn.gaussian_process import GaussianProcessRegressor
        self.gp = GaussianProcessRegressor()
        self.gp.fit(a_train.reshape(-1,1), Omega_ent_train)
        
    def Omega_ent(self, a):
        """Fast evaluation using surrogate model"""
        return self.gp.predict(np.array(a).reshape(-1,1))
