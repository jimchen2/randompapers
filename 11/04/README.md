## 1023

I trained the pendulum and CLEVRER again. CLEVRER converged. The previous problem was the learning rate.

However in Pendulum, the slot couldn't fit - like Bob and the shadow got into one slot, it recognized only 3 slots

See the tensorboard open the tensborboard on 
https://huggingface.co/jimchen2/jimchen2-clevrer-output
https://huggingface.co/jimchen2/jimchen2-pendulum-output

So I changed the shadow's color and size changed the shadow to blue

https://huggingface.co/jimchen2/jimchen2-blue-pendulum-output

## 1024

It seems that changing the shadow color to blue doesn't help.

## 1028

Videosaur won't converge - it would converge wrong, one slot would group all objects. 

See: https://huggingface.co/jimchen2/jimchen2-pendulum-output-1

Training in 1022 did the best - one slot captured the light, one slot grouped Bob and shadow. But how do you answer questions if you can't separate Bob and shadow?

The new trainings did worse. One run did not recognize anything. Two more runs grouped the light, Bob, and shadow all in one. And even worse, the loss (3 losses, including the Feature Reconstruction and Temporal Similarity loss) in all the trainings above are identical. You can't just tell if a training did good or bad by looking at the Tensorboard. 
 
Should I add more sample videos? Probably not.

## 1029

So I tried to read the Videosaur paper again.

Here are some other params to change

1. Decoder Type: switch from Mixer to MLP. It should have a stronger bias to separate objects.
2. Number of Slots: Increase to 5/6. The model is much more stable when given extra slots, while fewer slots causes the objects to merge.
3. Slot Dimension: Shrink it from 128 to 64 or 32 to prevent a single slot from having enough memory to hold all objects at the same time.
4. ViT Backbone: This network chops your image into a grid of squares (patches) and turns each square into a list of numbers. Model Size: ViT-Base vs. ViT-Small. Patch Size 16: Chops the image into 16x16 pixel squares. Patch Size 8: Chops the image into 8x8 pixel squares. 


Softmax temperature: Synthetic/simple data: 0.075, Real-world data: 0.25. This is synthetic data as well, so should be good.

Feature reconstruction weight: Synthetic/simple data: 0.0, Real-world data: 0.1. This is synthetic data, so should be good.

Time-shift: Default is 1. If your objects move slowly, increase to 2 or 3. I think 1 is ok here.


7. **ViT Backbone (`ViT-Base`):** Ensure you are using `ViT-Base` (not `Small`) and extracting **`Key`** features for the similarity loss, which the paper shows is required for stable training with the Mixer (Appendix B.4, Figure 6c).