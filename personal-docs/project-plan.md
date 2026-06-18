# Project Plan — Bayesian State Estimation for Sensor Drift in Pipeline Networks

_Working document for supervisor review. Tracks current status, the work remaining to
finalise the GaBP implementation, the reproduction of Demirel et al., comparison methods,
and the network hand-off for proprietary ground-truth generation._

Last updated: 2026-06-16

---

## 1. Status summary

All current code lives in [`notebooks/01-explore-gmrf.ipynb`](../notebooks/01-explore-gmrf.ipynb)
(`src/pipenet/graph.py` is still empty). The work so far targets a **7-node example from the
study brief** — this is a *separate* case from the Demirel benchmark (see §2).

| Component | State | Notes |
| --------- | ----- | ----- |
| Graph builder (`build_graph`) | Working | Builds pygsp graph + Laplacian + Fourier basis from an edge table |
| Estimator 1: Laplacian-regularised LS | Working | `A = I + γL`, `x̂ = A⁻¹y`. This is effectively the **RWLS baseline** (§5) |
| Estimator 2: Bayesian GMRF (exact) | Working | `Λ_post = Q + R⁻¹`, `x̂ = Λ_post⁻¹ R⁻¹ y` |
| Spectral anomaly check | Working, needs interpretation | High-frequency energy ratio = 0.33 (see §4 caveat) |
| **GaBP** | **Defined but never run or validated** | This is the blocker — see §3, WS0 |
| Newton–Raphson | Not started | Core comparison for the dissertation |
| Demirel et al. reproduction | Not started | 14-node benchmark — see §6 |
| Evaluation harness / figures | Not started | Nothing plotted yet |
| Package + tests | Not started | Memory note: refactor notebook → tested `pipenet` |

---

## 2. Scope: two distinct case studies

Keep these separate in code and in the write-up — they use different networks and (importantly)
different GaBP formulations.

- **Case A — 7-node brief network.** Direct pressure measurements at every node (H = I).
  Posterior precision is `Λ_post = Q + R⁻¹`. Pairwise precision-matrix GaBP applies directly.
  _Most of this is already built; it just needs finalising and validating._
- **Case B — 14-node Demirel benchmark.** Heterogeneous measurements (pressure, edge flow,
  nodal injection), nonlinear measurement functions, factor-graph GaBP. _New build._

> ⚠️ The numeric targets in the study brief are unreliable (known issue) — recompute everything
> from the equations rather than chasing the brief's worked numbers.

---

## 3. Work packages (checklist)

### WS0 — Finalise & validate the GaBP (Case A) — _highest priority_

- [X] **Fix return bug:** `gabp` currently returns `(mu, P_i)` where `P_i` is the leaked
      loop variable — only the *last* node's precision. Return all N posterior precisions.
- [X] **Run it.** It is never called. Add the acceptance test that defines "finalised":
  - `mu_GaBP` must equal `x_bay` from `bayesian_gmrf()`'s exact inverse (to `tol`).
  - `1/P_i_GaBP` must equal `np.diag(inv_lambda_post)` (to `tol`).
- [X] **State & check the convergence condition.** Gaussian BP converges to the exact posterior
      iff `Λ_post` is walk-summable (diagonal dominance is the easy sufficient check). Cite
      Weiss & Freeman (2001) [15] — the same result the Demirel paper relies on.
- [X] **Convergence diagnostic.** Record per-iteration message residual and plot it. The current
      `break` watches only `P_msg`, not `m_msg` — the means can still be moving when it stops.
- [X] **Document the schedule.** Messages are updated in place (Gauss–Seidel-style), not
      synchronous flooding. Note this — it changes iteration count, not the fixed point.

### WS1 — Comparison methods ("other methods")

- [ ] **Newton–Raphson** — the deterministic state estimator; spine of the dissertation comparison.
- [ ] **WLS** — the paper's primary baseline (eq. 3). For Case A with H = I this collapses to
      the GMRF solve you already have.
- [ ] **RWLS** — regularised WLS. Your Laplacian-regularised LS estimator already *is* this in
      spirit; formalise it as the named baseline.
- [ ] Align priors so comparisons are apples-to-apples: estimator 1 uses `A = I + γL` while
      estimator 2 uses `Q = γL + 1e-4·I` **plus** a noise model. Reconcile or justify.

### WS2 — Demirel et al. reproduction (Case B)

See the full spec in §6. Headline tasks:

- [ ] Reconstruct the 14-node meshed topology from Fig. 1 + input data (ref [11]).
- [ ] Implement pipe-resistance / Darcy–Weisbach measurement model (eqs. 17–22).
- [ ] Implement **factor-graph** GaBP (eqs. 6–15) in two stages: (a) **linear subset first** —
      pressure-only factors (`C=1`) + virtual-measurement priors — validated against the exact
      `Λ⁻¹` solve; (b) add the nonlinear edge-flow / injection factors and the Jacobian/linearisation
      layer (eq. 23). Staging isolates message-passing bugs from linearisation bugs.
- [ ] Decide single-shot vs re-linearised: follow arXiv:1702.05781 and run GaBP inside a
      Gauss–Newton outer loop (re-linearise each step). This _is_ the NR-vs-GaBP comparison —
      don't leave it ambiguous in the write-up.
- [ ] Note the engine is **moment-form** (messages carry mean + variance, two directions
      var↔factor), distinct from Case A's information-form pairwise messages — it's a new core,
      not an extension of the notebook `gabp`.
- [ ] Reproduce the three measurement configurations (Table I) and the per-node relative error
      metric (eq. 25); compare GaBP vs WLS vs RWLS (reproduce Fig. 2).

### WS3 — Network hand-off for proprietary ground truth

See §5. Build a plausible physical network now, confirm format/parameters with supervisor.

### WS4 — Evaluation harness

- [ ] Per-estimator RMSE/MAE (Case A) and mean relative error per node (Case B, eq. 25), one table.
- [ ] Figures: network graph; true vs measured vs estimated overlay; posterior-variance bands;
      GaBP convergence curve; reproduction of Demirel Fig. 2.
- [ ] Sanity-check the spectral anomaly result (§4).

### WS5 — Refactor to a tested package

- [ ] Move `build_graph` + estimators into `src/pipenet/`; the GaBP-vs-exact check (WS0) becomes
      your first `pytest`.
- [ ] Minor cleanups: `bayesian_gmrf` hardcodes `7`/`identity(7)` → use `N`; the array named
      `sigma` actually holds **variances** (0.25, 225) → rename.

### WS6 — Supervisor report

- [ ] Structure: problem & networks → methods (GMRF, pairwise GaBP, factor-graph GaBP, NR, WLS,
      RWLS) → results + figures → discussion (convergence guarantee, the two GaBP formulations,
      spectral finding) → limitations → next steps.
- [ ] Lead with the validated result: "GaBP reproduces the exact posterior to 1e-4 in N iterations."

---

## 4. Open technical caveats

- **Spectral anomaly direction.** The ratio `‖U_highᵀ y‖² / ‖U_highᵀ x_true‖² = 0.33` means the
  *measurement* has **less** high-frequency energy than the truth. That's because the faulty node
  (true value 100, neighbours ~108/110) is a genuine high-frequency dip that the bad reading
  (108.47) *smooths over*. So the detector as framed would not flag this fault — decide what it is
  actually for before presenting it.
- **0- vs 1-indexing.** Brief says σ₄ = 15; code inflates index 3. Be consistent in the write-up.

---

## 5. Network hand-off plan (Decision item)

**Goal:** give the supervisor a network specification so the company's proprietary hydraulic
solver can generate a ground-truth pressure field to model against.

**Key gap:** the current graph is an *abstract weighted Laplacian* (weights 1.5, 2.0, …). A
hydraulic solver needs *physical* inputs: node coordinates, pipe length/diameter/roughness,
nodal demands, and a reference (slack) pressure.

**Plan (per decisions taken 2026-06-16):**

- [ ] Build a **plausible physical network now** (don't wait on the supervisor). Use the Demirel
      14-node topology as the basis — work on a **network-to-network** basis, i.e. one physical
      spec maps to one abstract graph.
- [ ] Generate provisional ground truth with **pandapipes** (open-source, ref [14]) — this is
      exactly what the paper does, so it doubles as a faithful reproduction of their method *and*
      a stand-in until the proprietary truth arrives.
- [ ] **Confirm with supervisor:**
  - Export format the proprietary tool ingests (EPANET-style `.inp`? CSV node/edge tables? bespoke?).
  - Realistic pipe parameters (diameter, roughness, demands) and operating pressure.
  - Whether the company network differs from the Demirel benchmark.

---

## 6. Demirel et al. — implementation spec

> Demirel, de Jongh, Mueller, Leibfried, _"Data Fusion and State Estimation Using Belief
> Propagation in Gas Distribution Networks"_, KIT. (Attached PDF.)

**Implementation reference (the main source).** Demirel's GaBP is a direct application of the
Ćosović–Vukobratović factor-graph BP framework — their message equations are derived (and
correct) there, so implement against these, not Demirel's print:

- Ćosović & Vukobratović (2017), _Fast Real-Time DC State Estimation … BP_, arXiv:1705.01376 —
  the **linear-Gaussian** message equations (8)/(13)/(15); the validated source for §6.2.
- Ćosović & Vukobratović (2019), _Distributed Gauss–Newton Method for AC SE Using BP_,
  arXiv:1702.05781 — the **nonlinear** case: GaBP runs _inside_ a Gauss–Newton outer loop that
  re-linearises each iteration. This is the direct analogue of the Newton–Raphson comparison.
- Reference code (Julia, read the logic — don't port): `mcosovic/GBP_noisy_linear_systems`
  (closest to the linear milestone), `mcosovic/Belief_Propagation_DC_State_Estimation`, `GaussBP.jl`.

### 6.1 The crucial distinction from Case A

| | Case A (your current GaBP) | Case B (Demirel GaBP) |
|---|---|---|
| Graph | Pairwise MRF on `Λ_post` | Bipartite **factor graph** (variable + factor nodes) |
| Factors | — (work on precision matrix directly) | One factor per **measurement** |
| Messages | node→node on `Λ` | variable→factor (eqs. 6–8) and factor→variable (eqs. 9–12) |
| Measurements | direct pressure only, H = I | pressure, edge flow, nodal injection — **nonlinear** |
| Linearity | linear-Gaussian throughout | linearise `h(x)` around operating point (eq. 23), iterate |

**Unifying view (worth stating in the report):** both solve the same MAP / WLS problem in
information form, `Λ = Q + Hᵀ R⁻¹ H`. In Case A, H = I (direct pressure at every node), so
`Λ = Q + R⁻¹` — exactly your notebook. In Case B, H contains flow/injection rows from the
linearised measurement functions, so H ≠ I. The factor-graph GaBP is the distributed way to
solve that same system, and because `h` is nonlinear it sits inside a Gauss–Newton-style outer
loop — which connects directly to your Newton–Raphson comparison.

### 6.2 Factor-graph message passing (linear-Gaussian; to implement against)

Variable → factor (eqs. 7–8):

```
1/σ²_{xs→fi} = Σ_{fa ∈ Fs\fi} 1/σ²_{fa→xs}
   z_{xs→fi} = σ²_{xs→fi} · Σ_{fa ∈ Fs\fi} ( z_{fa→xs} / σ²_{fa→xs} )
```

Factor → variable (eqs. 10–12), with Jacobian coefficients `C_xs = ∂h_i/∂x_s` (eq. 13):

```
z_{fi→xs}  = (1/C_xs) · ( z_i − Σ_{xb ∈ Vi\xs} C_xb · z_{xb→fi} )
σ²_{fi→xs} = (1/C²_xs) · ( σ²_zi  +  Σ_{xb ∈ Vi\xs} C²_xb · σ²_{xb→fi} )
```

> ✅ **Sign resolved — it is a `+` (sum).** Demirel's eq. (12b) prints a **minus**; this is a typo.
> Cross-checked against the source these equations come from — Ćosović & Vukobratović (2017),
> eq. (13b) (arXiv:1705.01376) — which has the **plus**, as a variance propagated through a linear
> map must (independent uncertainties can only add, then scale by 1/C²). Use the `+`.
> Demirel's (8)/(12a)/(15) match Ćosović's (8)/(13a)/(15) one-for-one; (12b) is the _sole_
> discrepancy. Unit check: a pressure factor (`h=p_i`, `C=1`, no other variables) collapses to
> `z_{f→x}=z_i`, `σ²_{f→x}=σ²_i` — i.e. a direct measurement just injects its reading.

Marginals (eqs. 14–15):

```
1/σ̂²_xs = Σ_{fc ∈ Fs} 1/σ²_{fc→xs}
   x̂_s  = σ̂²_xs · Σ_{fc ∈ Fs} ( z_{fc→xs} / σ²_{fc→xs} )
```

### 6.3 Gas measurement model (eqs. 17–22)

- Pipe resistance: `R_ij = 16·λ·p_n·ρ_n·Z_m·T_m / (π²·d⁵·T_n)` (eq. 18); `λ` from Colebrook–White
  (implicit, solve iteratively).
- Pressure at node i: `h_pi = p_i` → Jacobian `C = 1` (linear).
- Edge flow i→j: `h_V̇ij = sgn(p_i−p_j)·√(|p_i−p_j|/R_ij)` (eq. 21) → nonlinear, linearise.
- Nodal injection (Kirchhoff): `h_V̇i = −Σ_{k∈Nb(i)} sgn(p_i−p_k)·√(|p_i−p_k|/R_ik)` (eq. 22).

### 6.4 Benchmark, configurations, metric

- **Network:** 14-node meshed gas distribution network (Fig. 1), input data from ref [11]
  (Cerbe & Lend — German textbook; may need reconstructing from the figure). Slack/external node
  modelled with a controlled pressure. Operating pressure `p_N = 3000 Pa`.
- **Measurement configs (Table I):** (1) 14 direct + 14 indirect = 28; (2) 7 direct + 21 indirect
  = 28; (3) 1 direct + 16 indirect = 17 (ill-conditioned).
- **Noise:** four standard deviations `σ = [σ1, σ2, σ3, σ4]` — small (~0.01 p.u.) for real
  pressure/flow/slack sensors, very large (~10⁶) for "virtual" no-information measurements.
  _Read exact values off the paper; the PDF text is partly garbled._
- **Metric (eq. 25):** mean relative error per node, `(1/n) Σ |x_se,i − x_true,i| / x_true,i`.
- **Comparison:** GaBP vs WLS vs RWLS. Expected result: GaBP ≈ WLS when well-observed; RWLS needed
  for the ill-conditioned config 3. Reproduce Fig. 2.

---

## 7. Decisions needed from supervisor

1. Export format the proprietary hydraulic solver ingests.
2. Realistic pipe parameters + operating pressure (or confirm the Demirel/textbook values are fine
   as a stand-in).
3. Whether the company's target network differs from the 14-node benchmark.
4. Whether a faithful factor-graph GaBP reproduction is required, or whether the information-form
   equivalence (§6.1) is acceptable for the comparison.

---

## 8. References

- Demirel et al., _Data Fusion and State Estimation Using Belief Propagation in Gas Distribution
  Networks_, KIT (attached).
- Weiss & Freeman (2001), _Correctness of Belief Propagation in Gaussian Graphical Models of
  Arbitrary Topology_, Neural Computation 13(10) — convergence guarantee [15].
- Lohmeier et al. (2020), _pandapipes_, Sustainability 12(23):9899 — ground-truth generator [14].
- Ćosović & Vukobratović (2017), _Fast Real-Time DC State Estimation in Electric Power Systems
  Using Belief Propagation_, arXiv:1705.01376 — **validated linear factor-graph GaBP equations**
  (the source Demirel's eqs. 6–15 derive from; has the correct `+` in 13b).
- Ćosović & Vukobratović (2019), _Distributed Gauss–Newton Method for (AC) State Estimation Using
  Belief Propagation_, IEEE Trans. Power Syst. 34(1):648–658 / arXiv:1702.05781 — nonlinear case,
  GaBP inside a Gauss–Newton outer loop (ties to the NR comparison).
- Bickson (2008), _Gaussian Belief Propagation: Theory and Application_, arXiv:0811.2518 — general
  GaBP theory reference.
- Reference implementations (Julia): `github.com/mcosovic/GBP_noisy_linear_systems`,
  `github.com/mcosovic/Belief_Propagation_DC_State_Estimation`, `GaussBP.jl`.
