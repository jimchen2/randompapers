https://arxiv.org/pdf/2310.11011

Encoder-Text: Looks back and ahead -> Vectors/probability (BERT masked words)
Decoder-Text: No look-ahead -> Probability (decoder-only LLM transformers)
Encoder + Decoder (text summary)

Encoder-Image: Image -> Vectors (ResNet, GAN Discriminator)
Variational Encoder-Image: Image -> Gaussian distributions params
Decoder-Image: Vectors -> Image  (GAN Generator)
Variational Decoder-Image: Gaussian distributions sample -> Image (Diffusion models)
Variational Autoencoder: Variational Encoder-Image + Variational Decoder-Image
GAN: GAN Generator and GAN Discriminator in opposition


Pearl's Hierarchy:

L1: height (5'10), city (Moscow), parental net worth (3M dollars), major (CS), activity (scrolling), dating success (0)
L2: hard intervention: do(increase parental net worth now) -> dating success? realistic soft intervention: do(read Pushkin for 2 hours) -> dating success?
L3: (backwards in time) if Dima's city was Piter instead of Moscow? if Dima had majored in literature (took the EGE differently)? -> dating success?
