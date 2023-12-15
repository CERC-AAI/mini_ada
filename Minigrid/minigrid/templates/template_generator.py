from minigrid.layout.map import MasterMap, SubMap
from minigrid.layout.constants import GENERATION_STATE
from pathlib import Path
from util import now
from minydra import MinyDict, resolved_args
import os
from pathlib import Path
from numpy.random import choice
import pandas as pd
import numpy as np
from minigrid.templates.mastermap_generator import generate_mastermap


ROOT_PATH = Path(__file__).resolve().parent.parent.parent.parent


def user_intervention() -> None:
    user_choice = input("continue? type y/n and press enter: ").strip().lower()
    if user_choice == "y" or user_choice == "yes":
        print(f"you typed '{user_choice}'. program will now continue running...")
    elif user_choice == "n" or user_choice == "no":
        print(f"you typed '{user_choice}'. program will now stop.")
        os.abort()
    else:
        print("unintelligable input, program will now stop.")
        os.abort()


if __name__ == '__main__':

    args = resolved_args() # get command line args
    args = MinyDict.from_yaml(ROOT_PATH / "config" / "config.yaml").update(args) # get config file args
    args.pretty_print()

    for i in range(args.map.n_maps):
        full_output_path = f"{ROOT_PATH / args.map.output_folder}/master_layout_{i}.csv"
        if os.path.exists(full_output_path):
            print(f"WARNING: the map at {full_output_path} already exists. it will be rewritten")
            user_intervention()
        mmap = generate_mastermap(args)
        mmap.to_csv(full_output_path)
        print(f"INFO: a master map is generated at {full_output_path}")
                    