Setup

```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda3
rm miniconda.sh

source $HOME/miniconda3/bin/activate
conda init bash
conda create -n cjepa python=3.12 -y
conda activate cjepa
conda install -y ffmpeg
pip install --upgrade pip uv
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
uv pip install seaborn webdataset swig einops torchcodec av accelerate tensorboard tensorboardX hickle pycocotools wget hydra-core omegaconf "pytorch-lightning>=2.0,<2.7"
```



# --- Patching Third-Party Compatibility ---
mkdir -p ./src/third_party/nerv/nerv/utils/
cp ./src/custom_codes/misc.py ./src/third_party/nerv/nerv/utils/misc.py

# --- Download & Configure Push-T Checkpoint ---
cd ..
wget https://huggingface.co/HazelNam/CJEPA/resolve/main/cjepa-ckpts/pusht_videosaur_1_epoch_30_object.ckpt

mkdir -p ~/.stable_worldmodel/checkpoints/
mv pusht_videosaur_1_epoch_30_object.ckpt ~/.stable_worldmodel/checkpoints/pusht_videosaur_1_object.ckpt

# --- Evaluation Execution ---
cd cjepa
bash scripts/pusht/test_planning.sh
