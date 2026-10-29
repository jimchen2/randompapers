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

Here are some other params to change

* **Slot Dimension ($D_{\text{slots}}$):** Controls the bottleneck size (Paper uses `128` for MOVi, `64` for YouTube-VIS).
* **Loss Softmax Temperature ($\tau$):** Controls the similarity loss sharpness (Paper uses `0.075` for MOVi, `0.25` for YouTube-VIS).
* **Feature reconstruction weight ($\alpha$):** Controls the balance between `loss_timesim` and `loss_featrec` (Paper uses `0.0` for MOVi, `0.1` for YouTube-VIS).
