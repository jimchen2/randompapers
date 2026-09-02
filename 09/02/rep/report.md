- *Towards Causal Representation Learning* ([arXiv:1911.10500](https://arxiv.org/pdf/1911.10500))
- *CausalVAE* ([arXiv:2004.08697](https://arxiv.org/pdf/2004.08697))
- *A Survey on Causal Generative Modeling* ([arXiv:2310.11011](https://arxiv.org/pdf/2310.11011))


---

## Towards Causal Representation Learning

https://arxiv.org/pdf/1911.10500

---

Current ML relies on IID data.

Physical Differential Equations - Causal modeling - Causal Models.

Common Cause Principle: X <- Z -> Y. You cannot extract causality from two variables without making extra assumptions, but adding more variables actually makes it easier.

Two variable limitation: Fisher's smoking theory: Smoking <- Gene -> Sickness

SCM (Structural causal models)

1. The Variables / Observables ($X_1, X_2, \dots, X_n$)
2. The Directed Acyclic Graph (The Flow of Causes)
3. The One-direction Functional Recipe ($X_i := f_i(\text{PA}_i, U_i)$)
4. Independent Noise ($U$)

Intervention replaces a specific function $X_i := f_i(\text{PA}_i, U_i)$ with a fixed value $\text{do}(X_i = c)$

Factorization:

$$p(X_1, \dots, X_n) = \prod_{i=1}^n p(X_i \mid \text{PA}_i)$$

Independence of Causality

- Changing one mechanism $p(X_i \mid \text{PA}_i)$ does not change the other mechanisms $p(X_j \mid \text{PA}_j)$ for $i \neq j$,
- Knowing $p(X_i \mid \text{PA}_i)$ does not give information about $p(X_j \mid \text{PA}_j)$.

Causality is about algorithms, not about distributions.

---

## CausalVAE

* **Kullback–Leibler (KL) Divergence:** Measures information lost when approximating distribution $P$ with $Q$. Asymmetric metric requiring $Q(x) > 0$ wherever $P(x) > 0$.
  $$D_{\mathrm{KL}}(P \parallel Q) = \sum_{x \in \mathcal{X}} P(x) \log \frac{P(x)}{Q(x)}$$

* **Gumbel Distribution:** Models the distribution of the maximum (or minimum) of a number of samples; used for extreme value analysis.

* **Importance Sampling:** Technique to estimate properties of target distribution $P$ using samples from proposal distribution $Q$.
  $$\mathbb{E}_{x \sim P}[f(x)] = \sum_{x} Q(x) \frac{P(x)}{Q(x)} f(x)$$

* **Variational Inference & ELBO:** Approximates intractable posterior $p(z|x)$ with $q(z|x)$ by maximizing the Evidence Lower Bound ($\text{ELBO}$):
  $$\log p(x) = D_{\text{KL}}(q(z|x) \parallel p(z|x)) + \text{ELBO}$$
  $$\text{ELBO} = \mathbb{E}_{q(z|x)}\left[\log \frac{p(x, z)}{q(z|x)}\right]$$

### Dataset (Simulation)

* **Physical Setup:** Water container containing a submerged ball, with fluid escaping through a side aperture.
* **Independent Variables:**
  * Ball diameter
  * Initial water level
  * Aperture height
  * Fluid outflow trajectory (causal variable)


Code Output

```
Epoch [000/101] | Loss: 3.0609 | KL: 8.9177 | Rec: 0.1894 | h(A): 0.012953 | Beta: 0.02
Epoch [020/101] | Loss: 8.9007 | KL: 3.8823 | Rec: 0.0899 | h(A): 0.002882 | Beta: 0.42
Epoch [040/101] | Loss: 15.3457 | KL: 2.9860 | Rec: 0.0897 | h(A): 0.016969 | Beta: 0.82
Epoch [060/101] | Loss: 17.6599 | KL: 1.9851 | Rec: 0.0901 | h(A): 0.017982 | Beta: 1.00
Epoch [080/101] | Loss: 17.1087 | KL: 1.4990 | Rec: 0.0897 | h(A): 0.013031 | Beta: 1.00
Epoch [100/101] | Loss: 16.7545 | KL: 1.2056 | Rec: 0.0893 | h(A): 0.010355 | Beta: 1.00
```

---

## A Survey on Causal Generative Modeling

* **L1: Association ($P(Y|X)$):** Passive observation of correlations.
* **L2: Intervention ($P(Y|\text{do}(X))$):** Active manipulation of variables.
* **L3: Counterfactuals ($P(Y_{X'}|X,Y)$):** Retrospective "what-if" reasoning given observed data.

* **Entangled:** Latents are unaligned mixtures of features.
* **Disentangled:** Latents represent isolated, independent factors.
* **Causal (CRL):** Latents model structured dependencies via:
  * *Independent Mechanisms (ICM):* Changing one causal module leaves others invariant.
  * *Sparse Shifts:* Interventions alter only a minimal subset of mechanisms.

CausalVAE

DEAR

SCM-VAE

ICM-VAE

TODO

---

## Further Reading

- 1803.01422 DAGs with NO TEARS
- 1804.03599 Understanding disentangling
- 1907.04809 Variational Autoencoders and Nonlinear ICA: A Unifying Framework
