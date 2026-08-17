# Scale-corrected merge_dare_linear

PEFT's `dare_linear` combination applies `sqrt(|w*scaling|)` to lora_A and lora_B
SEPARATELY (peft/tuners/lora/model.py:893-897), so the reconstruction B_new @ A_new
contains 36 terms `B_i A_j` where only the 6 diagonal ones are wanted; DARE's
1/(1-density) = 2x rescale is then applied to each factor, multiplying the product by 4.

Measured against the EXACT uniform mixture sum_i (1/6) dW_i over 196 modules:

| merge | ||dW||/exact | cosine to exact |
|---|---|---|
| merge_ties | 0.243 | 0.843 |
| merge_dare_ties | 0.802 | 0.871 |
| merge_dare_linear | **7.175** | 0.832 |

All three point the SAME way. dare_linear is not a bad merging method here - it is the
right direction at ~7x the right magnitude, which pushes the model far off-distribution
(accuracy 0.02-0.06, below the untouched base's 0.15-0.22).

This adapter is merge_dare_linear with lora_B scaled by 1/7.175 = 0.139373, which makes its
||dW|| match the exact mixture while leaving its direction untouched. If it now scores near
merge_dare_ties, the collapse was purely a scale artifact and dare_linear should be reported
as an implementation artifact rather than a method result.
