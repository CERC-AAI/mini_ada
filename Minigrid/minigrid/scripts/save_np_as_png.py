import numpy as np
import matplotlib.pyplot as plt
from minigrid.scripts.utils import convert_tiles

"""
def load_csv_to_image(csv_file_path, color_map):
    
    Load a CSV file and convert it to an image where each cell is a different pixel color.
    
    Args:
    - csv_file_path: Path to the CSV file.
    - color_map: A dictionary mapping cell contents (string) to a color (float3).
    
    Returns:
    - An image where each CSV cell is represented as a pixel with the corresponding color.
    
    # Load the CSV file
"""


def create_map_image(
    map: np.ndarray, map_generation_status, magnification=20
) -> np.ndarray:  # image is actually a 2d numpy array
    color_map = {  # todo add this to constants
        1: (0, 0, 0),  # Black
        0: (1, 1, 1),  # White
        -1: (1.0, 0.5, 0.25),  # orange
        2: (0.5, 0.5, 0.5),  # grey
        4: (0.5, 0, 1),  # violet
        3: (1, 0.5, 0.65),  # pink
        # Add more mappings as needed
        # nparr[nparr == "Space"] = 0  # constants, mappings, todo daria
        # nparr[nparr == "Wall"] = 1
        # nparr[nparr == "Undf(Wall)"] = 2
        # nparr[nparr == "Exit(Room)"] = 3
        # nparr[nparr == "Exit(Corridor)"] = 4
    }
    map = convert_tiles(map, map_generation_status)
    image = np.zeros((map.shape[0], map.shape[1], 3))

    for i in range(map.shape[0]):
        for j in range(map.shape[1]):
            image[i, j] = color_map.get(map[i, j], (0, 0, 0))

    # If magnification is more than 1, upscale the image
    #breakpoint()
    if magnification > 1:
        image = np.repeat(image, magnification, axis=0)
        image = np.repeat(image, magnification, axis=1)

    return image


def save_map_image(map: np.ndarray, map_generation_status: str, full_path: str) -> None:
    image = create_map_image(map, map_generation_status)
    plt.imsave(full_path, image)
    print(f"Processed and saved at: {full_path}")
