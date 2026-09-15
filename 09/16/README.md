Independence



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

---

### 3. Temporary & Runner Scripts Created
* **`/tmp/cjepa_eval.sh`**: Bash script created to run evaluation sequentially across seeds `0`, `1`, and `2`.
* **`/tmp/cjepa_eval.log`**: Log file capturing stdout and stderr from the background evaluation run.

---

### 4. Generated Evaluation Output Files
The evaluation runs produced the following result files in `src/plan/`:
* `src/plan/planning_pusht_videosaur_1_seed_0.txt`
* `src/plan/planning_pusht_videosaur_1_seed_1.txt`
* `src/plan/planning_pusht_videosaur_1_seed_2.txt`
* `src/plan/smoke.txt` (from initial verification runs)

## Commands 

Here are all the evaluation commands executed, in chronological order:

### 1. Initial Evaluation Smoke Tests (Debugging Phase)

**First smoke test attempt (Command 42):**
```bash
cd /home/jichen/Downloads/cjepa
source ~/miniconda3/etc/profile.d/conda.sh
conda activate cjepa
export PYTHONPATH=$(pwd)
export HYDRA_FULL_ERROR=1

timeout 900 python src/plan/run.py \
  seed=0 \
  policy=pusht_videosaur_1 \
  world.history_size=1 \
  world.frame_skip=1 \
  plan_config.horizon=5 \
  plan_config.receding_horizon=5 \
  plan_config.action_block=5 \
  eval.eval_budget=25 \
  eval.num_eval=2 \
  output.filename=smoke.txt \
  eval.dataset_name=pusht_expert_train \
  eval.goal_offset_steps=25 \
  wandb.use_wandb=false
```

**Smoke test re-run after updating `datasets` (Command 51):**
```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate cjepa
export PYTHONPATH=$(pwd)
export HYDRA_FULL_ERROR=1

timeout 1200 python src/plan/run.py \
  seed=0 \
  policy=pusht_videosaur_1 \
  world.history_size=1 \
  world.frame_skip=1 \
  plan_config.horizon=5 \
  plan_config.receding_horizon=5 \
  plan_config.action_block=5 \
  eval.eval_budget=25 \
  eval.num_eval=2 \
  output.filename=smoke.txt \
  eval.dataset_name=pusht_expert_train \
  eval.goal_offset_steps=25 \
  wandb.use_wandb=false
```

**Smoke test with explicit `cache_dir` (Command 53):**
```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate cjepa
export PYTHONPATH=$(pwd)
export HYDRA_FULL_ERROR=1

timeout 1800 python src/plan/run.py \
  seed=0 \
  policy=pusht_videosaur_1 \
  cache_dir=/home/jichen/.stable_worldmodel \
  world.history_size=1 \
  world.frame_skip=1 \
  plan_config.horizon=5 \
  plan_config.receding_horizon=5 \
  plan_config.action_block=5 \
  eval.eval_budget=25 \
  eval.num_eval=2 \
  output.filename=smoke.txt \
  eval.dataset_name=pusht_expert_train \
  eval.goal_offset_steps=25 \
  wandb.use_wandb=false
```

**Smoke test after creating `custom_models` shim (Command 59):**
```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate cjepa
export PYTHONPATH=$(pwd)
export HYDRA_FULL_ERROR=1

timeout 1800 python src/plan/run.py \
  seed=0 \
  policy=pusht_videosaur_1 \
  cache_dir=/home/jichen/.stable_worldmodel \
  world.history_size=1 \
  world.frame_skip=1 \
  plan_config.horizon=5 \
  plan_config.receding_horizon=5 \
  plan_config.action_block=5 \
  eval.eval_budget=25 \
  eval.num_eval=2 \
  output.filename=smoke.txt \
  eval.dataset_name=pusht_expert_train \
  eval.goal_offset_steps=25 \
  wandb.use_wandb=false
```

**Smoke test with `LD_LIBRARY_PATH` cuDNN fix (Command 63):**
```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate cjepa
export PYTHONPATH=$(pwd)
export HYDRA_FULL_ERROR=1
export LD_LIBRARY_PATH=$HOME/miniconda3/envs/cjepa/lib/python3.10/site-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH

timeout 1800 python src/plan/run.py \
  seed=0 \
  policy=pusht_videosaur_1 \
  cache_dir=/home/jichen/.stable_worldmodel \
  world.history_size=1 \
  world.frame_skip=1 \
  plan_config.horizon=5 \
  plan_config.receding_horizon=5 \
  plan_config.action_block=5 \
  eval.eval_budget=25 \
  eval.num_eval=2 \
  output.filename=smoke.txt \
  eval.dataset_name=pusht_expert_train \
  eval.goal_offset_steps=25 \
  wandb.use_wandb=false
```

**Final smoke test verification after transformers hook patch (Command 85):**
```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate cjepa
export PYTHONPATH=$(pwd)
export HYDRA_FULL_ERROR=1
export LD_LIBRARY_PATH=$HOME/miniconda3/envs/cjepa/lib/python3.10/site-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH

timeout 2400 python src/plan/run.py \
  seed=0 \
  policy=pusht_videosaur_1 \
  cache_dir=/home/jichen/.stable_worldmodel \
  world.history_size=1 \
  world.frame_skip=1 \
  plan_config.horizon=5 \
  plan_config.receding_horizon=5 \
  plan_config.action_block=5 \
  eval.eval_budget=25 \
  eval.num_eval=2 \
  output.filename=smoke.txt \
  eval.dataset_name=pusht_expert_train \
  eval.goal_offset_steps=25 \
  wandb.use_wandb=false
```

---

### 2. Full Multi-Seed Evaluation Run (Command 86)

**Creation of script `/tmp/cjepa_eval.sh`:**
```bash
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
```

**Background execution:**
```bash
nohup bash /tmp/cjepa_eval.sh > /tmp/cjepa_eval.log 2>&1 &
```
