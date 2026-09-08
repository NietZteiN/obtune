
**CodeLlama-7b · Python — the live panel**

| approach | representative row | mean single | L0 | L1b | L1r | L2 | S1 | S2 | X1 | H1 | C_L1b_S1 | C_L1r_S1 | C_S1_L1r | C_L2_S4 | C_L1r_S3 | C_S4_S3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Objectives — consistency / alignment | `cons_lam3_s42` | **0.405** | 0.423 | 0.403 | 0.396 | 0.399 | 0.402 | 0.423 | 0.280 | — | — | — | — | — | — | — |
| Objectives — curriculum | `currmono_kl` | **0.401** | 0.417 | 0.404 | 0.398 | 0.396 | 0.396 | 0.413 | 0.254 | — | — | — | — | — | — | — |
| Routing / MoLE mixtures | `mole_router` | **0.393** | 0.429 | 0.381 | 0.383 | 0.386 | 0.395 | 0.421 | — | — | — | — | — | — | — | — |
| Leave-one-transform-out | `loto_holdL0` | **0.392** | 0.418 | 0.391 | 0.391 | 0.383 | 0.386 | 0.407 | — | — | — | — | — | — | — | — |
| Monolithic breadth | `mono_all` | **0.389** | 0.411 | 0.386 | 0.387 | 0.380 | 0.385 | 0.404 | 0.231 | 0.232 | 0.345 | 0.350 | 0.326 | 0.385 | 0.380 | 0.403 |
| Objectives — negatives / unlikelihood | `neg_data` | **0.388** | 0.403 | 0.394 | 0.389 | 0.399 | 0.364 | 0.396 | 0.199 | — | — | — | — | — | — | — |
| Task-vector merges | `sweep_dare_ties_d0p3` | **0.387** | 0.429 | 0.372 | 0.388 | 0.388 | 0.393 | 0.394 | — | — | — | — | — | — | — | — |
| Other | `s2fam` | **0.385** | 0.420 | 0.356 | 0.371 | 0.384 | 0.398 | 0.416 | — | — | — | — | — | — | — | — |
| Per-condition specialists | `tuned_S2` | **0.383** | 0.430 | 0.351 | 0.379 | 0.375 | 0.392 | 0.419 | 0.286 | 0.283 | 0.286 | 0.303 | 0.301 | 0.370 | 0.377 | 0.420 |
| Execution-trace SFT | `trace_mono` | **0.378** | 0.392 | 0.382 | 0.384 | 0.377 | 0.356 | 0.389 | — | — | — | — | — | — | — | — |
| Reference — clean-code control | `tuned_L0` | **0.377** | 0.428 | 0.357 | 0.377 | 0.380 | 0.383 | 0.388 | 0.269 | 0.273 | 0.279 | 0.294 | 0.285 | 0.355 | 0.360 | 0.392 |
| Rank / capacity controls | `ctl_r64` | **0.377** | 0.426 | 0.358 | 0.381 | 0.382 | 0.377 | 0.386 | — | — | — | — | — | — | — | — |
| Clean-code control variants | `tuned_L0_half` | **0.367** | 0.413 | 0.358 | 0.368 | 0.365 | 0.369 | 0.379 | 0.259 | — | — | — | — | — | — | — |
| Family-exposure specialists (X1 and siblings) | `tuned_X1` | **0.361** | 0.411 | 0.341 | 0.362 | 0.351 | 0.368 | 0.383 | 0.315 | 0.318 | — | — | — | — | — | — |
| Family-exposure variants | `x1_resample` | **0.352** | 0.401 | 0.334 | 0.349 | 0.347 | 0.354 | 0.378 | 0.324 | — | — | — | — | — | — | — |
| Zero-training — ICL and oracle prompting | `icl_k4_cross` | **0.277** | 0.329 | 0.271 | 0.295 | 0.287 | 0.254 | 0.281 | — | — | — | — | — | — | — | — |
| Reference — format floor | `formatonly` | **0.210** | 0.281 | 0.221 | 0.230 | 0.231 | 0.172 | 0.196 | 0.125 | 0.133 | — | — | — | — | — | — |
| Zero-training — symbolic normalization | `norm_structural` | **0.200** | 0.255 | 0.200 | 0.207 | 0.202 | 0.168 | 0.221 | — | — | — | — | — | — | — | — |
| Reference — untuned | `base` | **0.194** | 0.257 | 0.197 | 0.207 | 0.202 | 0.168 | 0.193 | 0.119 | 0.129 | 0.141 | 0.131 | 0.135 | 0.176 | 0.172 | 0.186 |

**CodeLlama-13b · Python**

| approach | representative row | mean single | L0 | L1b | L1r | L2 | S1 | S2 | X1 | C_L1b_S1 | C_L1r_S1 | C_S1_L1r | C_L2_S4 | C_L1r_S3 | C_S4_S3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Objectives — consistency / alignment | `cons_lam3` | **0.441** | 0.463 | 0.437 | 0.437 | 0.430 | 0.435 | 0.469 | 0.293 | 0.377 | 0.376 | 0.367 | 0.432 | 0.433 | 0.461 |
| Monolithic breadth | `mono_all` | **0.423** | 0.446 | 0.423 | 0.419 | 0.419 | 0.412 | 0.444 | 0.254 | 0.367 | 0.370 | 0.359 | 0.422 | 0.411 | 0.439 |
| Reference — clean-code control | `tuned_L0` | **0.409** | 0.469 | 0.396 | 0.416 | 0.408 | 0.404 | 0.424 | 0.297 | 0.322 | 0.320 | 0.318 | 0.389 | 0.408 | 0.424 |
| Reference — untuned | `base` | **0.215** | 0.252 | 0.222 | 0.225 | 0.228 | 0.213 | 0.184 | — | — | — | — | — | — | — |

**CodeLlama-34b · Python**

| approach | representative row | mean single | L0 | L1b | L1r | L2 | S1 | S2 | X1 | H1 | C_L1b_S1 | C_L1r_S1 | C_S1_L1r | C_L2_S4 | C_L1r_S3 | C_S4_S3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Objectives — consistency / alignment | `cons_lam3` | **0.496** | 0.526 | 0.493 | 0.486 | 0.481 | 0.493 | 0.525 | 0.334 | — | 0.423 | 0.425 | 0.425 | 0.476 | 0.483 | 0.520 |
| Monolithic breadth | `mono_all` | **0.468** | 0.496 | 0.470 | 0.458 | 0.463 | 0.467 | 0.483 | 0.300 | 0.297 | 0.398 | 0.397 | 0.403 | 0.454 | 0.457 | 0.489 |
| Reference — clean-code control | `tuned_L0` | **0.462** | 0.522 | 0.419 | 0.468 | 0.465 | 0.472 | 0.484 | 0.326 | 0.321 | 0.322 | 0.349 | 0.364 | 0.431 | 0.451 | 0.480 |
| Reference — untuned | `base` | **0.214** | 0.254 | 0.205 | 0.220 | 0.231 | 0.222 | 0.191 | — | 0.143 | — | — | — | — | — | — |

**Llama-3.1-8B · Python — the cross-family replicate**

| approach | representative row | mean single | L0 | L1b | L1r | L2 | S1 | S2 | X1 |
|---|---|---|---|---|---|---|---|---|---|
| Objectives — consistency / alignment | `cons_lam3` | **0.415** | 0.447 | 0.407 | 0.403 | 0.408 | 0.412 | 0.445 | 0.255 |
| Monolithic breadth | `mono_all` | **0.393** | 0.425 | 0.390 | 0.386 | 0.388 | 0.393 | 0.409 | 0.220 |
| Reference — clean-code control | `tuned_L0` | **0.390** | 0.447 | 0.364 | 0.388 | 0.391 | 0.397 | 0.411 | 0.249 |
| Reference — untuned | `base` | **0.220** | 0.257 | 0.222 | 0.243 | 0.215 | 0.213 | 0.205 | 0.132 |

**CodeLlama-7b · JavaScript — the cross-language grid (E13)**

| approach | representative row | mean single | L0 | L1b | L1r | L2 | S1 | S2 | C_L1b_S1 | C_L1r_S1 | C_S1_L1r | C_L2_S4 | C_L1r_S3 | C_S4_S3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Objectives — consistency / alignment | `cons_lam3` | **0.552** | 0.565 | 0.556 | 0.556 | 0.544 | 0.549 | 0.558 | 0.519 | 0.523 | 0.539 | 0.550 | 0.536 | 0.556 |
| Monolithic breadth | `mono_all` | **0.501** | 0.500 | 0.500 | 0.496 | 0.494 | 0.509 | 0.508 | 0.481 | 0.475 | 0.479 | 0.510 | 0.480 | 0.502 |
| Reference — clean-code control | `tuned_L0` | **0.479** | 0.532 | 0.474 | 0.518 | 0.530 | 0.519 | 0.353 | 0.441 | 0.491 | 0.495 | 0.474 | 0.512 | 0.361 |
| Reference — untuned | `base` | **0.291** | 0.359 | 0.264 | 0.331 | 0.319 | 0.321 | 0.220 | 0.267 | 0.283 | 0.285 | 0.280 | 0.300 | 0.230 |