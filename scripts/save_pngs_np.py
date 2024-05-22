" to run this script, change the path to the folder with maps that you want to make images for"
" and change the path where you want to save the images to"

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path
from minydra import MinyDict, resolved_args

ROOT_PATH = Path(__file__).resolve().parent.parent.parent.parent


def load_npy_to_image(npy_file_path, color_map, magnification=20):
    # df = pd.read_csv(csv_file_path)
    # df = df.astype(str)
    image = np.load(npy_file_path)  # image is actually a numpy array, not an image yet
    image_2 = np.zeros((image.shape[0], image.shape[1], 3))

    # for i, row in df.iterrows():
    #    for j, value in enumerate(row):
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            # breakpoint()
            image_2[i, j] = color_map.get(image[i, j], (0, 0, 0))

    # If magnification is more than 1, upscale the image
    if magnification > 1:
        # image = np.repeat(image, magnification, axis=0)
        # image = np.repeat(image, magnification, axis=1)
        image_2 = np.repeat(image, magnification, axis=0)
        image_2 = np.repeat(image, magnification, axis=1)

    return image_2  # image


def process_directory(directory_path, color_map, output_path):
    """
    Process all CSV files in the given directory, converting each to an image.

    Args:
    - directory_path: Path to the directory containing CSV files.
    - color_map: A dictionary mapping cell contents (string) to colors (float3).
    """
    # breakpoint()
    output_directory = Path(directory_path)
    print("hello")
    total = 400
    i = 0
    # Iterate over all files in the directory
    for filename in os.listdir(directory_path):
        print(filename)
        if filename.endswith(".npy"):
            npy_file_path = os.path.join(directory_path, filename)
            # Convert the CSV to an image
            image = load_npy_to_image(npy_file_path, color_map)
            # Save the image
            base_name = os.path.splitext(filename)[0]
            # image_file_path = os.path.join(directory_path, "_pngs", base_name + ".png")
            image_file_path = os.path.join(output_path, base_name + ".png")
            os.makedirs(output_path, exist_ok=True)
            print(image_file_path)
            plt.imsave(image_file_path, image, cmap="Greys")
            print(f"Processed and saved: {image_file_path}")
            i = i + 1
            if i == total:
                break


# Example usage
if __name__ == "__main__":
    # Path to your directory containing CSV files
    # path = os.path.expanduser("$SCRATCH")

    args = resolved_args()  # get command line args
    args = MinyDict.from_yaml(ROOT_PATH / "config" / "config.yaml").update(
        args
    )  # get config file args
    args.pretty_print()

    # breakpoint()

    directory_path = "/home/mila/d/daria.yasafova/mini_ada/data/new_master_maps"
    directory_path = (
        "/home/mila/d/daria.yasafova/mini_ada/data/master_map_open_spaces_10x10"
    )
    directory_path = "/home/mila/d/daria.yasafova/scratch/Public/miniada/maps/10x10/"
    directory_path = "/home/mila/d/daria.yasafova/scratch/Public/miniada/maps/rooms_and_corridors_2/12x12"

    # Define a color map for mapping cell contents to colors
    # color_map = {
    #    "A": (1, 0, 0),  # Red
    #    "B": (0, 1, 0),  # Green
    #    # Add more mappings as needed
    # }

    # color_map = {
    #    "Wall": (0, 0, 0),  # Black
    #    "Space": (1, 1, 1),  # White
    #    "Exit": (1, 0, 0),  # Red
    #    # Add more mappings as needed
    # }

    color_map = {
        1: (0, 0, 0),  # Black
        0: (1, 1, 1),  # White
        # Add more mappings as needed
    }

    # output_path = "/home/mila/d/daria.yasafova/scratch/Public/miniada/images/ # todo

    # Process all CSV files in the directory
    process_directory(
        directory_path,
        color_map,
        # output_path="/home/mila/d/daria.yasafova/scratch/Public/miniada/map_images_10x10",
        output_path="/home/mila/d/daria.yasafova/scratch/Public/miniada/map_images_Rooms&Corr_12x12_2",
    )
    print()
