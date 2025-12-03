from qcis import solve_hubble_tension

results = solve_hubble_tension(
    H0_low=67.4,     # Planck CMB
    H0_high=73.04,   # SH0ES
    dataset='combined'
)
