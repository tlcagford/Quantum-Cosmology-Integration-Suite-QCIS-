"""
planck_validation.py

Validation against Planck 2018 data with statistical analysis
"""

import numpy as np
import h5py
import requests
import tarfile
import io
from typing import Dict, Tuple, Optional
from scipy import stats, integrate
import matplotlib.pyplot as plt

class PlanckValidator:
    """
    Validate quantum perturbation results against Planck data
    
    Downloads Planck 2018 likelihoods and performs statistical comparison
    """
    
    def __init__(self, data_dir: str = "./planck_data"):
        """
        Initialize Planck validator
        
        Parameters
        ----------
        data_dir : str
            Directory to store Planck data
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Planck 2018 data URLs
        self.data_urls = {
            'plik_lite': 'http://pla.esac.esa.int/pla/aio/product-action?COSMOLOGY.FILE_ID=COM_PowerSpect_CMB-base-plikHM-TTTEEE-lowl-lowE-lensing-minimum-theory_R3.01.zip',
            'cam_spec': 'http://pla.esac.esa.int/pla/aio/product-action?COSMOLOGY.FILE_ID=COM_PowerSpect_CMB-base-camspecHM-TTTEEE-lowl-lowE-lensing-minimum-theory_R3.01.zip',
            'lensing': 'http://pla.esac.esa.int/pla/aio/product-action?COSMOLOGY.FILE_ID=COM_PowerSpect_CMB-lensing-minimum-theory_R3.01.zip',
            'lowl': 'http://pla.esac.esa.int/pla/aio/product-action?COSMOLOGY.FILE_ID=COM_PowerSpect_CMB-lowL-mask95_R3.01.zip'
        }
        
        # Download data if not already present
        self._download_planck_data()
        
        # Load data
        self.planck_data = self._load_planck_data()
    
    def _download_planck_data(self):
        """Download Planck 2018 likelihood data"""
        for name, url in self.data_urls.items():
            filename = os.path.join(self.data_dir, f"{name}.tar.gz")
            
            if not os.path.exists(filename):
                print(f"Downloading {name} Planck data...")
                try:
                    response = requests.get(url, stream=True)
                    response.raise_for_status()
                    
                    with open(filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # Extract
                    with tarfile.open(filename, 'r:gz') as tar:
                        tar.extractall(self.data_dir)
                    
                    print(f"  Downloaded and extracted {name}")
                except Exception as e:
                    warnings.warn(f"Failed to download {name}: {e}")
    
    def _load_planck_data(self) -> Dict:
        """Load Planck CMB power spectra and covariance matrices"""
        data = {}
        
        # Load TT, TE, EE spectra
        try:
            # TT spectrum
            tt_file = os.path.join(self.data_dir, "COM_PowerSpect_CMB-TT-full_R3.01.txt")
            if os.path.exists(tt_file):
                tt_data = np.loadtxt(tt_file)
                data['TT'] = {
                    'ell': tt_data[:, 0],
                    'Cl': tt_data[:, 1],
                    'error': tt_data[:, 2]
                }
            
            # TE spectrum
            te_file = os.path.join(self.data_dir, "COM_PowerSpect_CMB-TE-full_R3.01.txt")
            if os.path.exists(te_file):
                te_data = np.loadtxt(te_file)
                data['TE'] = {
                    'ell': te_data[:, 0],
                    'Cl': te_data[:, 1],
                    'error': te_data[:, 2]
                }
            
            # EE spectrum
            ee_file = os.path.join(self.data_dir, "COM_PowerSpect_CMB-EE-full_R3.01.txt")
            if os.path.exists(ee_file):
                ee_data = np.loadtxt(ee_file)
                data['EE'] = {
                    'ell': ee_data[:, 0],
                    'Cl': ee_data[:, 1],
                    'error': ee_data[:, 2]
                }
            
            # Lensing potential
            pp_file = os.path.join(self.data_dir, "COM_PowerSpect_CMB-lensing-potential_R3.01.txt")
            if os.path.exists(pp_file):
                pp_data = np.loadtxt(pp_file)
                data['PP'] = {
                    'ell': pp_data[:, 0],
                    'Cl': pp_data[:, 1],
                    'error': pp_data[:, 2]
                }
            
            # Covariance matrices
            cov_file = os.path.join(self.data_dir, "COM_PowerSpect_CMB-covariance_R3.01.txt")
            if os.path.exists(cov_file):
                cov_data = np.loadtxt(cov_file)
                # Parse covariance matrix
                n_ell = len(data['TT']['ell'])
                data['covariance'] = cov_data.reshape(n_ell, n_ell)
            
        except FileNotFoundError as e:
            warnings.warn(f"Planck data file not found: {e}")
        
        return data
    
    def compute_chi2(self, theory_spectra: Dict, 
                    use_covariance: bool = True) -> Dict:
        """
        Compute χ² between theory and Planck data
        
        Parameters
        ----------
        theory_spectra : dict
            Theory CMB spectra with keys 'TT', 'TE', 'EE', 'PP'
        use_covariance : bool
            Whether to use full covariance matrix
            
        Returns
        -------
        dict
            χ² values and goodness-of-fit metrics
        """
        chi2_results = {}
        
        for spectrum in ['TT', 'TE', 'EE', 'PP']:
            if spectrum in self.planck_data and spectrum in theory_spectra:
                data = self.planck_data[spectrum]
                theory = theory_spectra[spectrum]
                
                # Interpolate theory to data ell values
                ell_data = data['ell']
                Cl_data = data['Cl']
                error_data = data['error']
                
                # Theory spectrum (must have 'ell' and 'Cl' keys)
                ell_theory = theory['ell']
                Cl_theory = theory['Cl']
                
                # Interpolate
                Cl_theory_interp = np.interp(ell_data, ell_theory, Cl_theory)
                
                # Compute χ²
                if use_covariance and spectrum == 'TT' and 'covariance' in self.planck_data:
                    # Full covariance matrix
                    diff = Cl_theory_interp - Cl_data
                    cov_inv = np.linalg.pinv(self.planck_data['covariance'])
                    chi2 = diff.T @ cov_inv @ diff
                    dof = len(diff) - 6  # Approximate degrees of freedom
                else:
                    # Diagonal errors
                    diff = Cl_theory_interp - Cl_data
                    chi2 = np.sum((diff / error_data)**2)
                    dof = len(diff) - 2  # Less parameters for individual spectra
                
                # Goodness of fit
                p_value = 1 - stats.chi2.cdf(chi2, dof)
                
                chi2_results[spectrum] = {
                    'chi2': chi2,
                    'chi2_per_dof': chi2 / dof,
                    'dof': dof,
                    'p_value': p_value,
                    'goodness_of_fit': 'excellent' if p_value > 0.05 else
                                      'good' if p_value > 0.01 else
                                      'moderate' if p_value > 0.001 else 'poor'
                }
        
        # Combined χ²
        if chi2_results:
            total_chi2 = sum(r['chi2'] for r in chi2_results.values())
            total_dof = sum(r['dof'] for r in chi2_results.values())
            
            chi2_results['combined'] = {
                'chi2': total_chi2,
                'chi2_per_dof': total_chi2 / total_dof,
                'dof': total_dof,
                'p_value': 1 - stats.chi2.cdf(total_chi2, total_dof)
            }
        
        return chi2_results
    
    def compute_bayesian_evidence(self, theory_spectra: Dict, 
                                 prior_width: float = 0.1) -> float:
        """
        Approximate Bayesian evidence for theory model
        
        Uses Laplace approximation: logZ ≈ logL_max + ½k log(2π) - ½log|F|
        where F is Fisher information matrix
        """
        # Maximum likelihood (minimum χ²/2)
        chi2_results = self.compute_chi2(theory_spectra)
        logL_max = -0.5 * chi2_results['combined']['chi2']
        
        # Number of parameters (approximate)
        k = 6  # Cosmological parameters
        
        # Fisher matrix approximation
        # For Gaussian likelihood, F ≈ 1/σ²
        # Approximate as identity matrix times average precision
        avg_precision = 1/np.mean([d['error']**2 for d in self.planck_data.values() 
                                  if 'error' in d])
        
        log_det_F = k * np.log(avg_precision)
        
        # Evidence
        logZ = (logL_max + 0.5*k*np.log(2*np.pi) - 0.5*log_det_F 
                - k*np.log(prior_width))
        
        return logZ
    
    def compare_with_lcdm(self, quantum_spectra: Dict, 
                         lcdm_spectra: Dict) -> Dict:
        """
        Compare quantum model with ΛCDM
        
        Parameters
        ----------
        quantum_spectra : dict
            CMB spectra from quantum model
        lcdm_spectra : dict
            CMB spectra from ΛCDM
            
        Returns
        -------
        dict
            Comparison metrics including Δχ² and ΔlogZ
        """
        # Compute χ² for both models
        chi2_quantum = self.compute_chi2(quantum_spectra)
        chi2_lcdm = self.compute_chi2(lcdm_spectra)
        
        # Compute Bayesian evidence
        logZ_quantum = self.compute_bayesian_evidence(quantum_spectra)
        logZ_lcdm = self.compute_bayesian_evidence(lcdm_spectra)
        
        # Statistical significance
        delta_chi2 = chi2_lcdm['combined']['chi2'] - chi2_quantum['combined']['chi2']
        delta_logZ = logZ_quantum - logZ_lcdm
        
        # Significance from Δχ² (assuming χ² distribution)
        if delta_chi2 > 0:
            p_value = stats.chi2.sf(delta_chi2, df=1)  # 1 parameter difference
            sigma = stats.norm.ppf(1 - p_value/2)
        else:
            p_value = 1.0
            sigma = 0.0
        
        # Jeffreys' scale for Bayesian evidence
        if delta_logZ > 5:
            evidence_strength = "Very strong for quantum"
        elif delta_logZ > 2.5:
            evidence_strength = "Strong for quantum"
        elif delta_logZ > 1:
            evidence_strength = "Substantial for quantum"
        elif delta_logZ > -1:
            evidence_strength = "Inconclusive"
        elif delta_logZ > -2.5:
            evidence_strength = "Substantial for ΛCDM"
        else:
            evidence_strength = "Strong for ΛCDM"
        
        return {
            'delta_chi2': delta_chi2,
            'delta_logZ': delta_logZ,
            'p_value': p_value,
            'sigma_significance': sigma,
            'evidence_strength': evidence_strength,
            'quantum_chi2': chi2_quantum['combined'],
            'lcdm_chi2': chi2_lcdm['combined'],
            'preferred_model': 'quantum' if delta_logZ > 0 else 'ΛCDM'
        }
    
    def plot_comparison(self, theory_spectra: Dict, 
                       output_file: Optional[str] = None):
        """
        Generate publication-quality comparison plots
        
        Parameters
        ----------
        theory_spectra : dict
            Theory CMB spectra to plot
        output_file : str, optional
            Path to save figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()
        
        spectra = ['TT', 'TE', 'EE', 'PP']
        titles = ['Temperature (TT)', 'Temperature-Polarization (TE)', 
                 'E-mode (EE)', 'Lensing Potential (PP)']
        
        for i, (spec, title) in enumerate(zip(spectra, titles)):
            ax = axes[i]
            
            if spec in self.planck_data and spec in theory_spectra:
                data = self.planck_data[spec]
                theory = theory_spectra[spec]
                
                # Plot Planck data
                ax.errorbar(data['ell'], data['Cl'], 
                          yerr=data['error'],
                          fmt='o', markersize=2, alpha=0.5,
                          label='Planck 2018', color='gray')
                
                # Plot theory
                ax.plot(theory['ell'], theory['Cl'], 
                       'r-', linewidth=2, label='Quantum Model')
                
                # Residuals
                # Interpolate theory to data points
                Cl_interp = np.interp(data['ell'], theory['ell'], theory['Cl'])
                residuals = (Cl_interp - data['Cl']) / data['error']
                
                # Add residuals in inset or second axis
                ax_inset = ax.inset_axes([0.6, 0.6, 0.35, 0.35])
                ax_inset.plot(data['ell'], residuals, 'k.', markersize=1)
                ax_inset.axhline(0, color='red', linestyle='--', alpha=0.5)
                ax_inset.set_ylabel('Residuals/σ')
                ax_inset.set_xlabel('ℓ')
                
                ax.set_xlabel('Multipole ℓ')
                ax.set_ylabel('$D_ℓ$ [μK²]' if spec != 'PP' else '$C_ℓ^{ϕϕ}$')
                ax.set_title(title)
                ax.legend()
                ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
        
        return fig
