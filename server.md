Setup

```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda3
rm miniconda.sh

source $HOME/miniconda3/bin/activate
conda init bash
conda create -n cjepa python=3.10 -y
conda activate cjepa
conda install -y ffmpeg
pip install --upgrade pip uv
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
uv pip install seaborn webdataset swig einops torchcodec av accelerate tensorboard tensorboardX hickle pycocotools wget hydra-core omegaconf "pytorch-lightning>=2.0,<2.7"
```



# --- Download & Configure Push-T Checkpoint ---
cd ..
wget https://huggingface.co/HazelNam/CJEPA/resolve/main/cjepa-ckpts/pusht_videosaur_1_epoch_30_object.ckpt

mkdir -p ~/.stable_worldmodel/checkpoints/
mv pusht_videosaur_1_epoch_30_object.ckpt ~/.stable_worldmodel/checkpoints/pusht_videosaur_1_object.ckpt


pip install 'stable-worldmodel[env]'
WANDB_MODE=disabled bash scripts/pusht/test_planning.sh









# 1. Install stable-pretraining
git clone https://github.com/galilai-group/stable-pretraining.git
cd stable-pretraining
git checkout 92b5841
pip install -e .

# 2. Install stable-worldmodel
cd ..
git clone https://github.com/galilai-group/stable-worldmodel.git
cd stable-worldmodel
git checkout 221ac82
pip install -e .

# 3. Install nerv
cd ..
git clone https://github.com/Wuziyi616/nerv.git
cd nerv
git checkout v0.1.0
pip install -e .
