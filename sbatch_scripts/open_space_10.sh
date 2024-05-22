#!/bin/bash
#SBATCH --job-name=open_space_10x10
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:0
#SBATCH --mem=12G          
#SBATCH --partition=unkillable
#SBATCH --error=/home/mila/d/daria.yasafova/scratch/miniada/scratch/%j_open_space_10x10_error.out
#SBATCH --output=/home/mila/d/daria.yasafova/scratch/miniada/scratch/%j_open_space_10x10.out


module load anaconda/3
module load cuda/11
conda activate miniada


cd /home/mila/d/daria.yasafova//mini_ada/Minigrid/minigrid/templates/
python template_generator.py map.height=10 map.coverage_ratio=1 map.rewrite=False map.start_index=10 map.end_index=1000