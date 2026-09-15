## Training

### Extracting

```
export PYTHONPATH=$(pwd)
export LD_LIBRARY_PATH=$HOME/miniconda3/envs/cjepa/lib/python3.10/site-packages/nvidia/cudnn/lib:${LD_LIBRARY_PATH:-}

python src/third_party/slotformer/base_slots/extract_videosaur.py \
    --weight "../pusht_videosaur_model.ckpt" \
    --data_root="/home/jichen/.stable_worldmodel" \
    --save_path="./pusht_videosaur_slots.pkl" \
    --dataset="pusht_expert" \
    --videosaur_config="src/third_party/videosaur/configs/videosaur/pusht_dinov2_hf.yml" \
    --params="src/third_party/slotformer/aloe_pusht_params.py"
```

### Download Databases

```
conda activate cjepa
cd /home/jichen/Downloads/cjepa

wget -nc https://huggingface.co/HazelNam/CJEPA/resolve/main/pusht_expert_action_meta.pkl
wget -nc https://huggingface.co/HazelNam/CJEPA/resolve/main/pusht_expert_proprio_meta.pkl
wget -nc https://huggingface.co/HazelNam/CJEPA/resolve/main/pusht_expert_state_meta.pkl
```

### Running the Script

```
cat << 'EOF' > run_train_pusht.sh
#!/usr/bin/env bash
set -e

source ~/miniconda3/etc/profile.d/conda.sh
conda activate cjepa

cd /home/jichen/Downloads/cjepa
export PYTHONPATH=$(pwd)
export LD_LIBRARY_PATH=$HOME/miniconda3/envs/cjepa/lib/python3.10/site-packages/nvidia/cudnn/lib:${LD_LIBRARY_PATH:-}

python src/train/train_causalwm_AP_node_pusht_slot.py \
    cache_dir="/home/jichen/.stable_worldmodel" \
    output_model_name="pusht_cjepa" \
    dataset_name="pusht_expert" \
    num_workers=8 \
    batch_size=256 \
    trainer.max_epochs=30 \
    num_masked_slots=1 \
    predictor_lr=5e-4 \
    proprio_encoder_lr=1e-4 \
    action_encoder_lr=5e-4 \
    dinowm.history_size=3 \
    dinowm.num_preds=1 \
    dinowm.proprio_embed_dim=128 \
    dinowm.action_embed_dim=128 \
    frameskip=5 \
    videosaur.NUM_SLOTS=4 \
    videosaur.SLOT_DIM=128 \
    predictor.heads=16 \
    embedding_dir="/home/jichen/Downloads/cjepa/pusht_videosaur_slots.pkl" \
    model.load_weights="/home/jichen/Downloads/pusht_videosaur_model.ckpt" \
    action_dir="/home/jichen/Downloads/cjepa/pusht_expert_action_meta.pkl" \
    proprio_dir="/home/jichen/Downloads/cjepa/pusht_expert_proprio_meta.pkl" \
    state_dir="/home/jichen/Downloads/cjepa/pusht_expert_state_meta.pkl" \
    use_hungarian_matching=false
EOF

chmod +x run_train_pusht.sh
nohup ./run_train_pusht.sh > train_pusht.log 2>&1 &
```


## Testing


## `pusht_videosaur`

```
cat > /tmp/cjepa_eval.sh <<'SH'
set -u
source ~/miniconda3/etc/profile.d/conda.sh
conda activate cjepa
cd /home/jichen/Downloads/cjepa
export PYTHONPATH=$(pwd)
export HYDRA_FULL_ERROR=1
export LD_LIBRARY_PATH=$HOME/miniconda3/envs/cjepa/lib/python3.10/site-packages/nvidia/cudnn/lib:${LD_LIBRARY_PATH:-}
POLICY="pusht_videosaur_1"
for SEED in 0 1 2; do
  echo "=== seed=${SEED} start $(date)"
  python src/plan/run.py \
    seed=${SEED} \
    policy=${POLICY} \
    cache_dir=/home/jichen/.stable_worldmodel \
    world.history_size=1 \
    world.frame_skip=1 \
    plan_config.horizon=5 \
    plan_config.receding_horizon=5 \
    plan_config.action_block=5 \
    eval.eval_budget=50 \
    output.filename=planning_${POLICY}_seed_${SEED}.txt \
    eval.dataset_name=pusht_expert_train \
    eval.goal_offset_steps=25 \
    wandb.use_wandb=false
  echo "=== seed=${SEED} done $(date)"
done
echo "ALL DONE $(date)"
SH

nohup bash /tmp/cjepa_eval.sh > /tmp/cjepa_eval.log 2>&1 &
```



| Seed | Episodes ($N$) | Successes | Success Rate (%) | Total CEM Time (s) | Wall Time (s) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 50 | 47 | 94.0 | 834.0 | 1253 |
| 1 | 50 | 44 | 88.0 | 824.2 | 1240 |
| 2 | 50 | 44 | 88.0 | 825.5 | 1239 |
| **Total / Mean** | **150** | **135** | **90.0 $\pm$ 3.46\*** | **827.9 (mean)** | **3732 (62.2 min)** |


### `pusht_videosaur_0`

| Seed | Episodes ($N$) | Successes | Success Rate (%) | Total CEM Time (s) | Wall Time (s) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 50 | 42 | 84.0 | 840.8 | 1258 |
| 1 | 50 | 32 | 64.0 | 835.5 | 1253 |
| 2 | 50 | 38 | 76.0 | 835.3 | 1244 |
| **Total / Mean** | **150** | **112** | **74.7 $\pm$ 10.1** | **837.2 (mean)** | **3755 (62.6 min)** |

---

### `pusht_videosaur_2`

| Seed | Episodes ($N$) | Successes | Success Rate (%) | Total CEM Time (s) | Wall Time (s) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 50 | 44 | 88.0 | 834.4 | 1255 |
| 1 | 50 | 39 | 78.0 | 845.9 | 1262 |
| 2 | 50 | 41 | 82.0 | 812.6 | 1234 |
| **Total / Mean** | **150** | **124** | **82.7 $\pm$ 5.0** | **831.0 (mean)** | **3751 (62.5 min)** |

```

export PYTHONPATH=$(pwd)
export HYDRA_FULL_ERROR=1
export LD_LIBRARY_PATH=$HOME/miniconda3/envs/cjepa/lib/python3.10/site-packages/nvidia/cudnn/lib:${LD_LIBRARY_PATH:-}

for POLICY in pusht_videosaur_0 pusht_videosaur_2; do
  for SEED in 0 1 2; do
    echo "=== [${POLICY}] seed=${SEED} start $(date)"
    python src/plan/run.py \
      seed=${SEED} \
      policy=${POLICY} \
      cache_dir=/home/jichen/.stable_worldmodel \
      world.history_size=1 \
      world.frame_skip=1 \
      plan_config.horizon=5 \
      plan_config.receding_horizon=5 \
      plan_config.action_block=5 \
      eval.eval_budget=50 \
      output.filename=planning_${POLICY}_seed_${SEED}.txt \
      eval.dataset_name=pusht_expert_train \
      eval.goal_offset_steps=25 \
      wandb.use_wandb=false
    echo "=== [${POLICY}] seed=${SEED} done $(date)"
  done
done

echo "ALL DONE $(date)"
SH

nohup /tmp/run_pusht_eval_0_2.sh > /tmp/pusht_eval_0_2.log 2>&1 &
```



## Environment

Here is the list of environment-tuning commands executed, grouped by action:

### 1. Fix Missing Intel MKL Symlinks
```bash
E=~/miniconda3/envs/cjepa/lib
cd $E
for f in libmkl_*.so.2; do
  base=${f%.2}
  [ -e "$base" ] || ln -s "$f" "$base"
done
```

### 2. Clean Conflicting PyTorch Installations & Reinstall
```bash
SP=~/miniconda3/envs/cjepa/lib/python3.10/site-packages

# Remove corrupt and conflicting PyTorch/Torchvision directories
rm -rf $SP/torch $SP/torchvision $SP/torch-2.4.0-py3.10.egg-info \
       $SP/torchvision-0.19.0-py3.10.egg-info $SP/torch-2.14.0.dist-info \
       $SP/torchvision-0.29.0.dist-info $SP/torchgen $SP/functorch

# Move leftover metadata out of the environment
mkdir -p ~/cjepa_env_backup
mv $SP/torch-2.4.0-py3.10.egg-info ~/cjepa_env_backup/

# Clean reinstall via pip
source ~/miniconda3/etc/profile.d/conda.sh
conda activate cjepa
pip install --force-reinstall --no-deps torch==2.14.0 torchvision==0.29.0
```

### 3. Upgrade Hugging Face `datasets`
```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate cjepa
pip install -q "datasets==4.8.5"
```

### 4. Align Submodule Dependencies
```bash
# Checkout pinned version of stable-worldmodel containing AutoCostModel
cd /home/jichen/Downloads/cjepa/src/third_party/stable-worldmodel
git stash push -m "local pusht env kwargs tweak (pre-pin)"
git checkout 221ac820a1adea75bed99df45ab592bb5f42306c

# Reinstall the package in editable mode
source ~/miniconda3/etc/profile.d/conda.sh
conda activate cjepa
pip install -e . --no-deps -q

# Revert outdated transform workaround in stable-pretraining
cd /home/jichen/Downloads/cjepa/src/third_party/stable-pretraining
git stash push -m "RGB transform workaround for old torchvision" stable_pretraining/data/transforms.py
```

### 5. Export Runtime Dynamic Library Paths
```bash
export LD_LIBRARY_PATH=$HOME/miniconda3/envs/cjepa/lib/python3.10/site-packages/nvidia/cudnn/lib:${LD_LIBRARY_PATH:-}
export PYTHONPATH=$(pwd)
export HYDRA_FULL_ERROR=1
```


## File Changes

### 1. Created File: `custom_models/__init__.py`
Created a new directory and Python module inside the repo root (`/home/jichen/Downloads/cjepa/custom_models/__init__.py`) containing:
* **Checkpoint unpickling aliases:** Added `sys.modules` mappings to redirect references from the legacy `custom_models` package to `src/` modules (`cjepa_predictor`, `dinowm_causal`, `dinowm_causal_AP_node`, `dinowm_causal_savi`).
* **Path injection:** Appended `src/third_party` to `sys.path`.
* **DINOv2 hidden states fix:** Added `_register_dinov2_output_capturing()` to register `Dinov2Model` and `Dinov2Encoder` into `transformers.utils.output_capturing._CAN_RECORD_REGISTRY`.

---

### 2. Modified Repository Submodules via Git
* **`src/third_party/stable-worldmodel/`**:
  * Stashed local uncommitted modifications using `git stash push -m "local pusht env kwargs tweak (pre-pin)"`.
  * Checked out commit `221ac820a1adea75bed99df45ab592bb5f42306c` (altering the working tree of this submodule).
* **`src/third_party/stable-pretraining/`**:
  * Stashed local modifications in `stable_pretraining/data/transforms.py` using `git stash push -m "RGB transform workaround for old torchvision"`.
