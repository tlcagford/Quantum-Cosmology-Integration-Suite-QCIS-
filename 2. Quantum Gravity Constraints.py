from qcis import constrain_quantum_parameters

posteriors = constrain_quantum_parameters(
    datasets=['planck2018', 'pantheon_plus', 'boss_dr12'],
    parameters=['field_mass', 'coupling', 'cutoff_scale']
)
