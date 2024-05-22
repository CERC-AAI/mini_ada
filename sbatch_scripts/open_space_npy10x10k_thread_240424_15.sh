#!/bin/bash
#SBATCH --job-name=OpSp_npy10x10k
#SBATCH --cpus-per-task=20
#SBATCH --gres=gpu:0
#SBATCH --mem=100G   
#SBATCH --error=/home/mila/d/daria.yasafova/scratch/miniada/scratch/%j_OpSp_npy10x10_10k_error.out
#SBATCH --output=/home/mila/d/daria.yasafova/scratch/miniada/scratch/%j_OpSp_npy10x10_10k.out


module load anaconda/3
module load cuda/11
conda activate miniada

echo "running script at /home/mila/d/daria.yasafova/mini_ada/sbatch_scripts/open_space_npy10x10k_thread.sh"
cd /home/mila/d/daria.yasafova/mini_ada/Minigrid/minigrid/templates/
python main_thread.py map.height=15 map.coverage_ratio=0.9 map.rewrite=False map.start_index=100 map.end_index=10000 map.output_folder=$SCRATCH/Public/miniada/maps thread.thread_count=20 thread.batch_size=100000 map.timeout_duplicates=50