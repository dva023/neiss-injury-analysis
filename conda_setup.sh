#!/bin/bash

conda create -n svm_env python=3.11
conda activate svm_env

# Install RAPIDS (includes cuML)
conda install -c rapidsai -c nvidia -c conda-forge \
	cuml=24.10 \
	cuda-version=12.4

# Install other packages
conda install -c conda-forge scikit-learn pandas numpy matplotlib seaborn

# For ThunderSVM
# pip install thundersvm-cuda12

# Save environment
conda env export >environment.yml
