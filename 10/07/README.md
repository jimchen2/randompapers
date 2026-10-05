Stage 1 is Videosaur

https://huggingface.co/datasets/jimchen2/pendulum-cjepa-dataset

```
export PYTHONPATH=$(pwd)

python src/train/train_causalwm_from_clevrer_slot.py \
    cache_dir="~/.stable_worldmodel" \
    output_model_name="pendulum_cjepa" \
    dataset_name="pendulum" \
    num_workers=4 \
    batch_size=64 \
    trainer.max_epochs=30 \
    num_masked_slots=1 \
    predictor_lr=5e-4 \
    dinowm.history_size=6 \
    dinowm.num_preds=10 \
    frameskip=1 \
    videosaur.NUM_SLOTS=4 \
    videosaur.SLOT_DIM=128 \
    predictor.heads=16 \
    embedding_dir="../pendulum_videosaur_4slots.pkl"
```
