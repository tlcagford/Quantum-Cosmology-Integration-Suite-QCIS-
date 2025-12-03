# Current (wrong):
rho_ent = T_munu[0, 0]
p_ent = np.mean(T_munu[1:4, 1:4])

# Reality in FLRW:
# T^μ_ν = diag(-ρ, p, p, p) by isotropy
# But RSET has OFF-DIAGONAL terms in general
# And time derivatives of curvature terms
