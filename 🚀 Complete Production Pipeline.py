def main():
    """Main production pipeline"""
    import yaml
    
    # Load configuration
    with open("config/validation_config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    # Create validation pipeline
    pipeline = QuantumCosmologyValidation(config)
    
    # Run validation
    results = pipeline.run_validation()
    
    # Save results
    output_dir = config.get('output_dir', './results')
    os.makedirs(output_dir, exist_ok=True)
    
    # Save to HDF5
    with h5py.File(f"{output_dir}/validation_results.h5", 'w') as f:
        # Save quantum results
        quantum_grp = f.create_group('quantum')
        quantum_grp.create_dataset('k_modes', data=results['quantum']['perturbations']['k_modes'])
        quantum_grp.create_dataset('P_zeta', data=results['quantum']['perturbations']['scalar']['power_spectrum']['P_zeta'])
        
        # Save CMB spectra
        cmb_grp = f.create_group('cmb_spectra')
        cmb_grp.create_dataset('ell', data=results['quantum']['cmb_spectra']['ell'])
        cmb_grp.create_dataset('TT_quantum', data=results['quantum']['cmb_spectra']['TT'])
        cmb_grp.create_dataset('TT_lcdm', data=results['lcdm']['TT'])
        
        # Save Planck comparison
        comp_grp = f.create_group('planck_comparison')
        comp_grp.attrs['delta_chi2'] = results['planck_comparison']['delta_chi2']
        comp_grp.attrs['delta_logZ'] = results['planck_comparison']['delta_logZ']
        comp_grp.attrs['preferred_model'] = results['planck_comparison']['preferred_model']
    
    # Generate report
    report = f"""
    QUANTUM COSMOLOGY VALIDATION REPORT
    ====================================
    
    Configuration:
    - H0: {config.get('H0', 67.4)}
    - Ω_cdm: {config.get('Omega_cdm', 0.264)}
    - Quantum corrections: {config.get('quantum_corrections', True)}
    
    Results:
    - Quantum model χ²/dof: {results['planck_comparison']['quantum_chi2']['chi2_per_dof']:.2f}
    - ΛCDM χ²/dof: {results['planck_comparison']['lcdm_chi2']['chi2_per_dof']:.2f}
    - Δχ²: {results['planck_comparison']['delta_chi2']:.2f}
    - ΔlogZ (Bayesian evidence): {results['planck_comparison']['delta_logZ']:.2f}
    - Preferred model: {results['planck_comparison']['preferred_model']}
    - Significance: {results['planck_comparison']['sigma_significance']:.1f}σ
    
    Conclusion:
    {results['planck_comparison']['evidence_strength']}
    """
    
    with open(f"{output_dir}/validation_report.txt", 'w') as f:
        f.write(report)
    
    print(report)
    print(f"\nResults saved to: {output_dir}/")
    print("Validation complete!")

if __name__ == "__main__":
    main()
