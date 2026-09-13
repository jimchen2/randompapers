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
