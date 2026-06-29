### Gaussian (gaussian.py) — finish off
- [ ] Test marginalise: 2×2 numerical check vs moment-form oracle
      (inv → slice mu[keep], Sigma[keep,keep] → convert back; np.allclose)
- [ ] Decide pseudo_inv param: precomputed matrix vs bool use_pinv flag
      (lean: bool flag, fall back to np.linalg.pinv on singular Lam_bb)
- [ ] Add return type hint -> "Gaussian" on marginalise (forward-ref string)
- [ ] Implement damp(): (1-beta)*new + beta*old on (eta, Lam)
- [ ] np.asarray on eta/Lam inputs in __init__ (lists -> ndarray)
- [ ] Confirm float64 dtype end-to-end (pin where inv() leaks floating[Any])

### Tests (set up tests/)
- [ ] test_gaussian.py: add/sub dim-mismatch raises, to_moment, marginalise oracle
- [ ] Wire pyright into project: uv add --dev pyright, uv run pyright gabp/

### Next class — Factor
- [ ] Re-confirm message state lives on Factor (Ortiz model: factor stores
      last outgoing msg per var; var->factor = belief - last msg)
- [ ] Factor holds (C, z, var_z); scatter to joint Gaussian
      (Lam = C^T var_z^-1 C, eta = C^T var_z^-1 z)
- [ ] factor->var message = scatter joint, then marginalise to target var

### Then
- [ ] VariableNode.update_belief (canonical sum via __add__)
- [ ] FactorGraph: hold nodes+factors, synchronous flooding loop + damping
- [ ] Validate against notebook oracle (beliefs match Lambda^-1 b ~1e-7)
