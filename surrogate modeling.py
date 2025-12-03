# Use surrogate modeling
from sklearn.gaussian_process import GaussianProcessRegressor

class SurrogateModel:
    """Learn Ω_ent(a) from sparse QFT evaluations"""
    def __init__(self):
        self.gp = GaussianProcessRegressor()
        self.training_points = []
        
    def train(self, a_sample, Omega_ent_sample):
        self.gp.fit(a_sample.reshape(-1, 1), Omega_ent_sample)
        
    def predict(self, a):
        return self.gp.predict(a.reshape(-1, 1))
