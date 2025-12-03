# Step 1: Implement mode equation solver
def solve_mode_equation(k, a_array, m, xi):
    # Solve: f''_k + ω_k²(τ) f_k = 0
    # where ω_k² = k² + m²a² - (1-6ξ)a''/a
    # using numerical ODE solver
    
# Step 2: Implement adiabatic regularization
def adiabatic_subtraction(raw_rho, a, order=4):
    # Compute WKB expansion to 4th order
    # Subtract divergent terms
    
# Step 3: Implement conservation check
def check_conservation(T_munu, a):
    # Verify ∇_μ T^μν = 0
