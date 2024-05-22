from sys import getsizeof
import numpy as np
import os
import time
from sys import getsizeof


def array_to_bytes(arr):
    """Convert a NumPy array to bytes."""
    return arr.tobytes()


def array_to_hashable(arr):
    """Convert a 2D NumPy array to a hashable form."""
    return tuple(map(tuple, arr))


def find_duplicates(dataset_path):
    """Find duplicates in a dataset of NumPy arrays."""
    array_hashes = {}
    duplicate_arrays = []
    duplicate_paths = []

    dataset_path = "/network/scratch/d/daria.yasafova/miniada/numpy/10x10/"

    unique_maps = {}
    duplicates = {}
    unq_maps = set()
    start_time = time.time()
    for filename in os.listdir(dataset_path):

        if filename.endswith(".npy"):
            file_path = os.path.join(dataset_path, filename)
            arr = np.load(file_path)
            arr_hash = array_to_hashable(arr)

            unique_maps[arr_hash] = file_path
            unq_maps.add(arr_hash)
            """
            if arr_hash in unique_maps:
                # breakpoint()
                if arr_hash in duplicates:
                    # breakpoint()
                    duplicates[arr_hash].append(file_path)

                else:
                    duplicates[arr_hash] = [file_path]
            else:
                unique_maps[arr_hash] = file_path
            """

    print(len(os.listdir(dataset_path)))
    print("len dict", len(unique_maps))
    print("len set", len(unq_maps))
    print("dict in bytes", getsizeof(unique_maps))
    print("set in bytes", getsizeof(unq_maps))

    end_time = time.time()
    elapsed = end_time - start_time
    print(
        time.strftime(f"elapsed time: %Hh%Mm%Ss", time.gmtime(elapsed))
    )  # '04h13m06s'
    breakpoint()
    return duplicate_arrays, duplicate_paths


def delete_duplicates(paths):
    """Delete duplicate files at given paths."""
    for path in paths:
        os.remove(path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Find and delete duplicates in a dataset of NumPy arrays."
    )
    parser.add_argument(
        "dataset_path",
        type=str,
        help="Path to the dataset directory containing NumPy arrays.",
    )
    args = parser.parse_args()

    dataset_path = args.dataset_path

    # Find duplicate arrays and their paths
    duplicate_arrays, duplicate_paths = find_duplicates(dataset_path)

    if duplicate_arrays:
        print("Duplicates found:")
        for duplicate in duplicate_arrays:
            print(duplicate)

        # Optionally delete duplicates
        confirm_delete = input("Do you want to delete these duplicates? (yes/no): ")
        if confirm_delete.lower() == "yes":
            delete_duplicates(duplicate_paths)
            print("Duplicates deleted.")
        else:
            print("Duplicates not deleted.")
    else:
        print("No duplicates found.")
