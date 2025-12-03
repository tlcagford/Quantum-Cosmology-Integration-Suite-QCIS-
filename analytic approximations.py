# Use known results for conformally coupled fields
def omega_ent_conformal(a):
    # For m=0, ξ=1/6: ⟨T_μν⟩ ~ H⁴ terms
    return alpha * (H(a)/H0)**4

# Use DeWitt-Schwinger expansion for massive fields
def omega_ent_dewitt_schwinger(a, m):
    # Expansion in curvature/mass²
    # ⟨T_μν⟩ ~ R²/m² + R³/m⁴ + ...
    return sum(coefficients * curvature_terms)
