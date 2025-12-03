
# Quantum-Corrected Cosmological Perturbation Solver

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: GPLv3 for non-commercial](https://img.shields.io/badge/License-GPLv3%20for%20non--commercial-green.svg)](LICENSE-GPL)
[![arXiv](https://img.shields.io/badge/arXiv-2407.xxxxx-b31b1b.svg)](https://arxiv.org/abs/2407.xxxxx)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.xxxxxxx.svg)](https://doi.org/10.5281/zenodo.xxxxxxx)
[![Build Status](https://github.com/tlcagford/quantum-cosmology/workflows/CI/badge.svg)](https://github.com/tlcagford/quantum-cosmology/actions)

## 🔬 Overview

A complete computational framework for cosmological perturbation theory with first-principles quantum corrections. This package implements:

- **Quantum-corrected Mukhanov-Sasaki equations** with backreaction from quantum fields
- **Full Boltzmann integration** with quantum scattering terms
- **Tensor perturbations** (gravitational waves) with quantum sources
- **Integration with CLASS/CAMB** for validation
- **Planck 2018 data validation** with Bayesian evidence computation
- **Production-ready pipeline** for cosmological parameter constraints

## 🚀 Features

### Core Physics
- **Quantum stress-energy perturbations** using Schwinger-Keldysh formalism
- **Bunch-Davies & α-vacuum initial conditions** with quantum corrections
- **Renormalization schemes**: adiabatic (4th order), point-splitting, dimensional
- **Self-consistent backreaction** between metric and quantum fields
- **Entanglement entropy** calculations for cosmological horizons

### Numerical Methods
- Adaptive Runge-Kutta integration for perturbation equations
- Line-of-sight integration for CMB spectra
- Sparse matrix methods for large k-mode computations
- GPU acceleration support (via CuPy/Numba)
- Parallel computation over k-modes

### Data & Validation
- **Planck 2018 likelihood integration**
- **CMB power spectra** (TT, TE, EE, BB, ϕϕ) with quantum effects
- **Matter power spectrum** with quantum corrections
- **Bayesian evidence** calculation for model comparison
- **Hubble tension** and **S₈ tension** analysis tools

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- C/C++ compiler (for CLASS integration)
- HDF5 library (for data storage)

### Quick Install
```bash
# Clone repository
git clone https://github.com/tlcagford/quantum-cosmology.git
cd quantum-cosmology

# Install with pip
pip install -e .

# Or with conda
conda env create -f environment.yml
conda activate quantum-cosmo
📜 License
Dual License Structure

This software is available under two distinct licenses:
1. Academic/Non-Commercial License (FREE)

    For: Academic researchers, students, non-profit organizations

    Permissions:

        Free use, modification, and distribution

        Use in academic research and publications

        Classroom and educational use

    Requirements:

        Cite the original work in publications

        No commercial use allowed

2. Personal Commercial License (REQUIRED)

    For: Companies, commercial organizations, for-profit use

    Requirements:

        License required for any commercial use

        Contact: Tony E. Ford - 📧 tlcagford@gmail.com

        Commercial licensing terms negotiated individually

Usage Rights Summary
Use Case	License Required	Cost
Academic Research	No	FREE
University Teaching	No	FREE
Personal Projects	No	FREE
Commercial Product	YES	Negotiable
Corporate R&D	YES	Negotiable
SaaS Integration	YES	Negotiable
