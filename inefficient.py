# Current inefficient approach:
for each scale_factor a:                    # O(1000)
    compute_full_QFT_on_background(a)       # O(10⁶) operations each
    → Too slow for cosmological parameter estimation

# Need efficient approach:
learn_surrogate_model(sparse_QFT_samples)   # O(100) full calculations
use_GPR_to_predict_Ω_ent(a)                # O(1) evaluation
