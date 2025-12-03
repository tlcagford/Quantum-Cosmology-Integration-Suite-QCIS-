def run_production_analysis(config_file: str, output_dir: str):
    """
    Production-level analysis for publication
    
    Parameters
    ----------
    config_file : str
        YAML configuration file
    output_dir : str
        Directory for results and plots
    
    Returns
    -------
    dict
        Complete results suitable for publication
    """
    import yaml
    import matplotlib.pyplot as plt
    from datetime import datetime
    
    # Load configuration
    with open(config_file, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    config = PipelineConfig(**config_dict)
    
    # Create pipeline
    pipeline = QuantumCosmologyPipeline(config)
    
    # Run analysis
    start_time = datetime.now()
    results = pipeline.run_full_pipeline()
    end_time = datetime.now()
    
    # Save results
    output_file = f"{output_dir}/results_{start_time.strftime('%Y%m%d_%H%M%S')}.h5"
    pipeline.save_results(results, output_file)
    
    # Generate publication-quality figures
    figures = pipeline.generate_publication_figures(results, output_dir)
    
    # Generate LaTeX tables
    tables = pipeline.generate_latex_tables(results, output_dir)
    
    # Write summary report
    report = pipeline.write_summary_report(results, output_dir)
    
    # Compute statistics for paper
    statistics = {
        'run_time': str(end_time - start_time),
        'memory_usage': pipeline.get_memory_usage(),
        'chi2_per_dof': results['data_comparison']['chi2_total'] / 
                       (config.n_data_points - config.n_parameters),
        'bayesian_evidence_difference': (
            results['data_comparison']['bayesian_evidence'] - 
            config.lcdm_evidence
        ),
        'hubble_tension_resolution': pipeline.compute_tension_resolution(),
        's8_tension_resolution': pipeline.compute_s8_resolution()
    }
    
    # Package for publication
    publication_package = {
        'results': results,
        'figures': figures,
        'tables': tables,
        'report': report,
        'statistics': statistics,
        'config': config_dict,
        'code_version': pipeline.get_version(),
        'dependencies': pipeline.get_dependencies(),
        'reproducibility_info': pipeline.get_reproducibility_info()
    }
    
    print(f"\n📊 Analysis complete!")
    print(f"   Results saved to: {output_file}")
    print(f"   Figures saved to: {output_dir}")
    print(f"   χ²/dof = {statistics['chi2_per_dof']:.2f}")
    print(f"   ΔlnZ vs ΛCDM = {statistics['bayesian_evidence_difference']:.2f}")
    
    return publication_package


# Example usage
if __name__ == "__main__":
    # Production run
    results = run_production_analysis(
        config_file="config/production_run.yaml",
        output_dir="results/production_run_2024"
    )
    
    # Quick test run
    test_config = PipelineConfig(
        H0=67.4,
        Omega_m0=0.315,
        compute_dynamical_spacetime=False,
        compute_holographic=False,
        n_k_modes=50,
        l_max=1000
    )
    
    test_pipeline = QuantumCosmologyPipeline(test_config)
    test_results = test_pipeline.run_full_pipeline()
