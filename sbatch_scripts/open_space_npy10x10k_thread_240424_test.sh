#!/bin/bash
#SBATCH --job-name=OpSp_npy10x10k
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:0
#SBATCH --mem=1G   
#SBATCH --error=/home/mila/d/daria.yasafova/scratch/miniada/scratch/%j_OpSp_npy10x10_10k_error.out
#SBATCH --output=/home/mila/d/daria.yasafova/scratch/miniada/scratch/%j_OpSp_npy10x10_10k.out


module load anaconda/3
module load cuda/11
conda activate miniada

echo "running script at /home/mila/d/daria.yasafova/mini_ada/sbatch_scripts/open_space_npy10x10k_thread.sh"
cd /home/mila/d/daria.yasafova/mini_ada/sbatch_scripts
python -u test.py 