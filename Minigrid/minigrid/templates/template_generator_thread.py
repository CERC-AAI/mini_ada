import sys

print(sys.path)


from minigrid.layout.map import MasterMap, SubMap
from minigrid.layout.constants import GENERATION_STATE

# from ..layout.map import (
#    MasterMap,
#    SubMap,
# )  # from mini_ada.Minigrid.minigrid.layout.constants import GENERATION_STATE
from pathlib import Path
from minydra import MinyDict, resolved_args
import os
import numpy as np
from minigrid.templates.mastermap_generator import generate_mastermap
import glob
from csv_diff import load_csv, compare
from os.path import expanduser, expandvars
import time
print(sys.path)

def resolve(path: Path) -> Path:
    """
    Resolves a path: expands user (~) and env variables ($X)
    then turns the path into an absolute one and turns it into
    a pathlib.Path instance

    Args:
        path (Union[str, pathlib.Path]): Path to resolve

    Returns:
        pathlib.Path: resolved path
    """
    return Path(expandvars(expanduser(str(path)))).resolve()


ROOT_PATH = Path(__file__).resolve().parent.parent.parent.parent


def user_intervention() -> bool:
    user_choice = input("Rewrite the map? Type y/n and press enter: ").strip().lower()
    if user_choice == "y" or user_choice == "yes":
        print(f"INFO: you typed '{user_choice}'. the map will be rewritten...")
        return True
    elif user_choice == "n" or user_choice == "no":
        print(f"INFO: you typed '{user_choice}'. the map will be not be rewritten.")
        # os.abort()
        return False
    else:
        print("INFO: unintelligable input, the program will now stop.")
        # os.abort()
        raise NotImplementedError


def isdublicate(folder_path, map) -> bool:
    if os.path.isdir(
        folder_path
    ):  # if path is a directory, we add each .csv file that starts with "layout" in its name
        if not folder_path.endswith("/"):
            folder_path = folder_path + "/"  # todo , temporary solution
        file_list = glob.glob(f"{folder_path}master_layout*.csv")
        breakpoint()

        # with open(map, "r") as file:
        #    new_csv = file.readlines()
        for master_layout in file_list:
            # with open(master_layout, "r") as master_file:
            #    old_csv = master_file.readlines()
            diff = compare(load_csv(open(map)), load_csv(open(file_list[2])))
            print(diff)
            # todo load each master_layout
            # compare it to map ()

    return 0


def array_to_hashable(arr):
    """Convert a 2D NumPy array to a hashable form."""
    return tuple(map(tuple, arr))


def main(
    start,
    end,
    common_map_pool,
    lock_dict,
    shared_dict,
    lock_saturation,
    saturation,
):
    start_time = time.time()
    print(f"thread starts at {start}, ends at {end - 1}")
    args = resolved_args()  # get command line args
    args = MinyDict.from_yaml(ROOT_PATH / "config" / "config.yaml").update(
        args
    )  # get config file args
    args.pretty_print()

    #######
    # when using n_maps and not start_index/end_index strategy
    """
    file_list = glob.glob(f"{ROOT_PATH / args.map.output_folder}/master_layout*.csv")
    # extracting the highest index among existing master maps in the output folder
    if file_list == []:
        highest_index = 0
    else:
        highest_index = max(
            [int(filename.split("_")[-1].split(".")[0]) for filename in file_list]
        )
    """
    # make directory
    directory = (
        resolve(Path(args.map.output_folder)) / f"{args.map.height}x{args.map.height}"
    )
    os.makedirs(directory, exist_ok=True)

    generated_maps = 0

    for current_index in range(start, end):

        #######
        # when using n_maps and not start_index/end_index strategy
        """
        for i in range(args.map.n_maps):
            current_index = highest_index + i + 1
            print("CURRENT INDEX", current_index)
            print(f"{current_index =}")
            full_output_path = (
                f"{ROOT_PATH / args.map.output_folder}/master_layout_{current_index}.csv"
            )
        """

        # full_output_path = (
        #    f"{ROOT_PATH / args.map.output_folder}/master_layout_{current_index}.csv"
        # )
        """
        # make directory
        directory = (
            resolve(Path(args.map.output_folder))
            / f"{args.map.height}x{args.map.height}"
        )
        os.makedirs(directory, exist_ok=True)
        """
        full_output_path = f"{directory}/master_layout_{current_index}.npy"

        # full_output_path = f"{args.map.output_folder}/master_layout_{current_index}.csv"

        #######
        """
        if os.path.exists(full_output_path):
            print(
                f"WARNING: the map at {full_output_path} already exists. Choose what to do."
            )
            # print(args.map.rewrite)
            # breakpoint()
            if args.map.rewrite == "user_defined":
                user_choice = user_intervention()
                if user_choice is True:
                    pass
                elif user_choice is False:
                    continue
            elif args.map.rewrite is False:
                print("INFO: rewrite=False was chosen. The map won't be rewritten.")
                continue
            elif args.map.rewrite is True:
                print("INFO: rewrite=True was chosen. The map will be rewritten.")
                pass
            else:
                raise NotImplementedError
        """
        if os.path.exists(full_output_path):
            continue
        else:
            mmap, coverage_ratio = generate_mastermap(args)
            # breakpoint()
            if (
                coverage_ratio > args.map.coverage_ratio * 0.69
            ):  # daria done update from 27/03/24 15:51

                # breakpoint()
                # todo add a check for a duplicate comparing this mapp to all the maps in the output folder
                # folder_path = f"{ROOT_PATH / args.map.output_folder}"
                # dublicate = isdublicate(folder_path, mmap)
                # mmap.to_csv(full_output_path) # daria todo removed , replaced with numpy array
                """
                # previous approach, before duplicates
                mmap.saveas_numpy_arr(full_output_path)
                print(f"INFO: a master map is generated at {full_output_path}")
                """
                map_npy = mmap.to_npy()
                map_hash = array_to_hashable(map_npy)
                # new approach 28/03/2024, with threads
                if map_hash in common_map_pool:
                    with lock_saturation:
                        saturation[0] += 1
                        print("saturation:", saturation)
                else:
                    with lock_saturation:
                        saturation[0] = 0
                    with lock_dict:
                        common_map_pool[map_hash] = full_output_path
                        shared_dict[map_hash] = full_output_path
                        np.save(
                            full_output_path, map_npy
                        )  # done 03/04/2024 undone 05/04/2024
                    # if os.path.exists(full_output_path):
                    #    continue
                    # else:
                    #    np.save(full_output_path, map_npy)
                    #    print(f"INFO: a master map is generated at {full_output_path}")
                    #    generated_maps = generated_maps + 1
                    # np.save(full_output_path, map_npy)

                    # print(f"INFO: a master map is generated at {full_output_path}") # todo print
                    generated_maps = generated_maps + 1
                if (
                    saturation[0] == 1
                ):  # args.map.timeout_duplicates: todo daria check then go back
                    # print("INFO: saturation point has been reached.")
                    # break
                    raise Exception(
                        f"INFO: saturation point has been reached. Stopping further processing. The saturation point is reached at {len(common_map_pool)} maps for size {args.map.height}x{args.map.height}"
                    )
                # folder_path = f"{ROOT_PATH / args.map.output_folder}"
                # dublicate = isdublicate(folder_path, full_output_path)
            else:
                # breakpoint()
                # np.save(full_output_path, map_npy)  # ??? # todo decide what's this
                continue

    # save only unique maps across the batch
    # for map_hash, map_path in unique_maps.items():
    #    print(map_path, "map path!")
    #    np.save(map_path, map_hash)
    #    print(f"INFO: a master map is generated at {map_path}")

    end_time = time.time()
    elapsed = end_time - start_time
    print(
        time.strftime(
            f"elapsed time of this thread: %Hh%Mm%Ss ({generated_maps} maps generated)",
            time.gmtime(elapsed),
        )
    )  # '04h13m06s'


if __name__ == "__main__":
    main()
