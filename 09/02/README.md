## [2004.08697 CausalVAE, Yang](https://arxiv.org/pdf/2004.08697)

- [Kullback–Leibler divergence](https://en.wikipedia.org/wiki/Kullback–Leibler_divergence): Measures which Q1, Q2... is a better representation of P where any Q covers P (Q(x)>0 wherever P(x)∣f(x)∣ >0)

$$D_{\mathrm{KL}}(P \parallel Q) = \sum_{x \in \mathcal{X}} P(x) \log \frac{P(x)}{Q(x)}.
$$

> Asymmetric, is not a distance (you pack clothes for Moscow, you might still do well in California, you pack for California, the cold weather in Moscow is out of distribution, so you freeze/infinite penalty)

> Is the yearly weather (in terms of colder days) in Leningrad or Anchorage is a better approximation for the yearly weather in Moscow?

- [Gumbel distribution](https://en.wikipedia.org/wiki/Gumbel_distribution): To represent an extreme event

> The highest rainfall in Leningrad over 10 years. Or the highest total time a gambler plays among 1 million gamblers in a 51% rigged casino.

- [Importance sampling](https://en.wikipedia.org/wiki/Importance_sampling): Use distribution Q to estimate the expectation of distribution P where Q covers P (Q(x)>0 wherever P(x) ∣f(x)∣ >0)

$$\mathbb{E}_{x \sim P}[f(x)] = \sum P(x)f(x) = \sum Q(x) \frac{P(x)}{Q(x)} f(x) $$

> Dima doesn't know the lottery payout price, but Dima knows the probability of winning. Dima controls the machine to artificially win a few times and calculates with different weights. Crude Monte Carlo (random sampling and taking the average) fails because it relies on too many samples.

- [Variational Bayesian methods
](https://en.wikipedia.org/wiki/Variational_Bayesian_methods), ELBO

KL Divergence: $$D_{\text{KL}}(p_{\text{approx}}(z|x) \parallel p(z|x)) = \int p_{\text{approx}}(z|x) \log \left( \frac{p_{\text{approx}}(z|x)}{p(z|x)} \right) dz$$

$$D_{\text{KL}}(p_{\text{approx}}(z|x) \parallel p(z|x)) +  \int p_{\text{approx}}(z|x) \log \left( \frac{p(x, z)}{p_{\text{approx}}(z|x)} \right) dz = \log p(x)$$


ELBO is:
$$\text{ELBO} = \int p_{\text{approx}}(z|x) \log \left( \frac{p(x, z)}{p_{\text{approx}}(z|x)} \right) dz$$


---

- Dataset (generated): a fixed water container with water, ball inside, and a hole on the right side. Water is spilling out. 
- Independent Variables: ball size, water height, hole height (predetermined), water spilling trajectory (causal factor)

TODO

## [1911.19599 Causality for Machine Learning, Schölkopf](https://arxiv.org/pdf/1911.10500)

---

Current ML relies on IID data.

Physical Differential Equations - Causal modeling - Causal Models.

Common Cause Principle: X <- Z -> Y. You cannot extract causality from two variables without making extra assumptions, but adding more variables actually makes it easier. Two variable limitation: Fisher's smoking theory: Smoking <- Gene -> Sickness

Additive Noise Model: $Y = f(X) + \text{Noise}$, and test both directions

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

Causality is about algorithms, not about distributions. Random Variables can be dependent - even if the causal mechanisms are independent.

## [2310.11011 Survey on Causal Generative Modeling](https://arxiv.org/pdf/2310.11011)

- Encoder-Text: Looks back and ahead -> Vectors/probability (BERT masked words) 
- Decoder-Text: No look-ahead -> Probability (decoder-only LLM transformers) 
- Encoder + Decoder (text summary)

---

- Encoder-Image: Image -> Vectors (ResNet, GAN Discriminator) 
- Variational Encoder-Image: Image -> Gaussian distributions params 
- Decoder-Image: Vectors -> Image (GAN Generator) 
- Variational Decoder-Image: Gaussian distributions sample -> Image (Diffusion models) 
- Variational Autoencoder: Variational Encoder-Image + Variational Decoder-Image 
- GAN: GAN Generator and GAN Discriminator in opposition

---

Pearl's Hierarchy:

- L1: height (5'10), city (Moscow), age (20), parental net worth (3M dollars), major (CS), activity (scrolling), dating success (0) 
- L2: hard intervention: do(increase parental net worth now) -> dating success? realistic soft intervention: do(read Pushkin for 2 hours) -> dating success? 
- L3: (backwards in time) if Dima's city was Piter instead of Moscow, how does other factors change? if Dima had majored in literature (took the EGE differently)? -> dating success?

---

- Entangled Learning: Everything mixed, you don't know which dimension of the vector corresponds to age or major 
- Disentangled Learning: Isolated variables map to age, height, city, parental net worth, etc (but if Dima is 30, shouldn't you also change his salary?) 
- Causal Representation Learning: Variables influence each other: age -> salary, major -> activity
  - Independent Causal Mechanisms: Reading Pushkin does not change Dima's height.
  - Sparse Mechanism Shift: If Dima moves to Piter, a few variables (activity, university) might change, and most variables (age, height) don't change

---

CausalVAE
DEAR
SCM-VAE
ICM-VAE

TODO
