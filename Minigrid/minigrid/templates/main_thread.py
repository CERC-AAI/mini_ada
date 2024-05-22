import threading
import template_generator_thread
from pathlib import Path
import time
from minydra import MinyDict, resolved_args
from os.path import expanduser, expandvars
import os
import glob
import numpy as np
from sys import getsizeof


ROOT_PATH = Path(__file__).resolve().parent.parent.parent.parent


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


def array_to_hashable(arr):
    """Convert a 2D NumPy array to a hashable form."""
    return tuple(map(tuple, arr))


def main():
    shared_dict = {}
    shared_dict = {16: ""}
    thread1 = threading.Thread(target=add_numbers_to_dict, args=(1, 5, shared_dict))
    thread2 = threading.Thread(target=add_numbers_to_dict, args=(6, 10, shared_dict))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    print("Keys in the dictionary:", list(shared_dict.keys()))


def main2():
    print("hi")
    start_time = time.time()

    # done load the config args
    args = resolved_args()  # get command line args
    args = MinyDict.from_yaml(ROOT_PATH / "config" / "config.yaml").update(
        args
    )  # get config file args
    args.pretty_print()

    # done before the start of generation process,
    # from the output folder, we load existing files into a dict (with keys - npy maps, values - map paths)
    directory = (
        resolve(Path(args.map.output_folder)) / f"{args.map.height}x{args.map.height}"
    )
    os.makedirs(directory, exist_ok=True)
    # breakpoint()

    existing_maps = {}

    start = time.time()

    existing_map_paths = glob.glob(f"{directory}/*.npy")

    if existing_map_paths == []:
        highest_index = 0
        starting_index = 0
    else:
        highest_index = max(
            [
                int(filename.split("_")[-1].split(".")[0])
                for filename in existing_map_paths
            ]
        )
        starting_index = highest_index + 1

    print("hello time")
    end = time.time()
    print(end - start)
    print("existing .npy files count", len(existing_map_paths))

    start = time.time()
    for map_path in existing_map_paths:
        arr = np.load(map_path)
        arr_hash = array_to_hashable(arr)
        existing_maps[arr_hash] = map_path

    assert len(existing_map_paths) == len(existing_maps), "folder contains duplicates"

    print("hello time")
    end = time.time()
    print(end - start)
    print("existing unique maps count", len(existing_maps))

    common_map_pool = existing_maps.copy()  # todo check

    generated_maps = 0

    saturation = [0]  # Shared count variable wrapped in a list
    lock_dict = threading.Lock()  # Lock to synchronize access to count
    lock_saturation = threading.Lock()

    # the goal is for the threads to generate maps and fill the dict with unique maps from the generated ones.
    # after which we do a for loop through the dict and create maps that don't exist yet.
    saturation = [0]
    shared_dict = {}
    thread_count = args.thread.thread_count  # todo make an argument in config file
    batch_size = args.thread.batch_size

    # todo multithread in for loop
    # todo smartly add start and end index

    ####################
    start = time.time()
    threads = []
    print("starting_index", starting_index)

    start = 200
    end = 300
    template_generator_thread.main(
        start,
        end,
        common_map_pool,
        lock_dict,
        shared_dict,
        lock_saturation,
        saturation,
    )
    """
    for i in range(thread_count):
        start = batch_size * i + starting_index
        end = batch_size * (i + 1) + starting_index
        print(f"thread {i}", start, end)
        thread = threading.Thread(
            target=template_generator_thread.main,
            args=(
                start,
                end,
                common_map_pool,
                lock_dict,
                shared_dict,
                lock_saturation,
                saturation,
            ),
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    """
    end = time.time()
    print(f"time: for loop {thread_count} threads", end - start)
    ####################

    ####################
    """
    thread_count = 15
    start = time.time()
    threads = []
    print("starting_index", starting_index)
    for i in range(thread_count):
        start = batch_size * i + starting_index
        end = batch_size * (i + 1) + starting_index
        print(f"thread {i}", start, end)
        thread = threading.Thread(
            target=template_generator_thread.main,
            args=(
                start,
                end,
                common_map_pool,
                lock_dict,
                shared_dict,
                lock_saturation,
                saturation,
            ),
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end = time.time()
    print(f"time: for loop {thread_count} threads", end - start)
    """
    ####################
    """
    thread1 = threading.Thread(
        target=template_generator_thread.main,
        args=(
            batch_size * 0 + starting_index,
            batch_size + starting_index,
            common_map_pool,
            lock_dict,
            shared_dict,
            lock_saturation,
            saturation,
        ),
    )
    thread2 = threading.Thread(
        target=template_generator_thread.main,
        args=(
            batch_size + starting_index,
            batch_size * 2 + starting_index,
            common_map_pool,
            lock_dict,
            shared_dict,
            lock_saturation,
            saturation,
        ),
    )

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
    """

    """
    for i in range(n):
        start = i * range_size + 1
        end = start + range_size - 1 if i != n - 1 else 10  # Adjust end for the last thread
        thread = threading.Thread(target=add_numbers_to_dict, args=(start, end, shared_dict))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    """
    # print("Keys in the dictionary:", list(shared_dict.keys()))
    print(len(shared_dict))

    # todo remove this part and add it into threads' function, to do in parallel
    # done: for generated maps, do a for loop and save them
    """ # done (commented) 03/04/2024
    for map_npy, map_path in shared_dict.items():
        breakpoint()
        np.save(map_path, map_npy)
    """

    print("unique maps added to the folder: ", len(shared_dict))
    print("maps before generation", len(existing_maps))
    print("maps after generation", len(common_map_pool))
    print("maps in the folder after generation", len(glob.glob(f"{directory}/*.npy")))
    print("common_map_pool dict in bytes", getsizeof(common_map_pool))
    print("existing_maps dict in bytes", getsizeof(existing_maps))
    print("shared_dict dict in bytes", getsizeof(shared_dict))
    # breakpoint()


if __name__ == "__main__":
    main2()
