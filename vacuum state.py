class QuantumState:
    """Quantum state specification for QFT"""
    def __init__(self, state_type='bunch_davies', alpha=1.0, beta=0.0):
        self.state_type = state_type  # bunch_davies, alpha, thermal, squeezed
        self.alpha = alpha  # For alpha-vacua
        self.beta = beta    # For squeezed states
        self.temperature = None  # For thermal states
