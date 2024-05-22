import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path
from minydra import MinyDict, resolved_args

ROOT_PATH = Path(__file__).resolve().parent.parent.parent.parent


def load_csv_to_image(csv_file_path, color_map, magnification=20):
    df = pd.read_csv(csv_file_path)
    df = df.astype(str)
    image = np.zeros((df.shape[0], df.shape[1], 3))
    for i, row in df.iterrows():
        for j, value in enumerate(row):
            image[i, j] = color_map.get(value, (0, 0, 0))

    # If magnification is more than 1, upscale the image
    if magnification > 1:
        image = np.repeat(image, magnification, axis=0)
        image = np.repeat(image, magnification, axis=1)

    return image


def process_directory(directory_path, color_map, output_path):
    """
    Process all CSV files in the given directory, converting each to an image.

    Args:
    - directory_path: Path to the directory containing CSV files.
    - color_map: A dictionary mapping cell contents (string) to colors (float3).
    """
    breakpoint()
    output_directory = Path(directory_path)

    # Iterate over all files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".csv"):
            csv_file_path = os.path.join(directory_path, filename)
            # Convert the CSV to an image
            image = load_csv_to_image(csv_file_path, color_map)
            # Save the image
            base_name = os.path.splitext(filename)[0]
            # image_file_path = os.path.join(directory_path, "_pngs", base_name + ".png")
            image_file_path = os.path.join(output_path, base_name + ".png")
            os.makedirs(output_path, exist_ok=True)
            plt.imsave(image_file_path, image)
            print(f"Processed and saved: {image_file_path}")


# Example usage
if __name__ == "__main__":
    # Path to your directory containing CSV files
    # path = os.path.expanduser("$SCRATCH")

    args = resolved_args()  # get command line args
    args = MinyDict.from_yaml(ROOT_PATH / "config" / "config.yaml").update(
        args
    )  # get config file args
    args.pretty_print()

    breakpoint()

    directory_path = "/home/mila/d/daria.yasafova/mini_ada/data/new_master_maps"
    directory_path = (
        "/home/mila/d/daria.yasafova/mini_ada/data/master_map_open_spaces_10x10"
    )
    directory_path

    # Define a color map for mapping cell contents to colors
    # color_map = {
    #    "A": (1, 0, 0),  # Red
    #    "B": (0, 1, 0),  # Green
    #    # Add more mappings as needed
    # }

    color_map = {
        "Wall": (0, 0, 0),  # Black
        "Space": (1, 1, 1),  # White
        "Exit": (1, 0, 0),  # Red
        # Add more mappings as needed
    }

    # Process all CSV files in the directory
    process_directory(
        directory_path,
        color_map,
        output_path="/home/mila/d/daria.yasafova/scratch/ada/map_pngs_new",
    )
