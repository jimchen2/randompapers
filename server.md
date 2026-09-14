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






already:git clone https://github.com/galilai-group/stable-pretraining.gitMove into the directory:cd stable-pretrainingInstall the package locally:pip install -e . [1] (https://github.com/galilai-group/stable-pretraining)



  161  git clone https://github.com/galilai-group/stable-pretraining.git
  162  ls
  163  cd stable-pretraining/
  164  pip install -e . [1] (https://github.com/galilai-group/stable-pretraining)
  165  pip install -e .
  166  clear
  167  cd ..
  168  ls
  169  cd cjepa/
  170  clear
  171  ls
  172  bash scripts/pusht/test_planning.sh
  173  ls
  174  ModuleNotFoundError: No module named 'stable_worldmodel'
  175  pip install stable-worldmodel
  176  clera
  177  clear
  178  bash scripts/pusht/test_planning.sh
  179  pip install imageio
  180  clear
  181  bash scripts/pusht/test_planning.sh
  182  pip install ale-py
  183  clear
  184  bash scripts/pusht/test_planning.sh
  185  clear
  186  history
(cjepa) jichen@uark.edu@eecs-s-sail2025:~/Downloads/cjepa$ 
