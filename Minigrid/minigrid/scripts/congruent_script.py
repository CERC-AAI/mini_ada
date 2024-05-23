import numpy as np
import pandas as pd
from extract_layouts_from_csv import get_rectangles
from save_np_as_png import save_map_image
import os

def load_csv(file_path):
    """
    Load the CSV file and parse the data into a list of rectangles (numpy arrays).
    """
    df = pd.read_csv(file_path, header=None)
    rectangles = []
    current_rectangle = []
    for index, row in df.iterrows():
        if pd.isna(row[0]):  # assuming blank line separates rectangles
            if current_rectangle:
                rectangles.append(np.array(current_rectangle))
                current_rectangle = []
        else:
            current_rectangle.append(row.tolist())
    if current_rectangle:
        rectangles.append(np.array(current_rectangle))

    breakpoint()
    return rectangles

def rotate_rectangle(rect, i, output_dir, visualize):
    """
    Generate all four rotations of a rectangle.
    """
    rotations = [rect]
    output_dir = output_dir + f"/rect_{i}/"
    #output_dir = output_dir = "/home/mila/d/daria.yasafova/mini_ada/data/source_csv/rect/"
    

    # save image of the orinal extracted rectangle
    os.makedirs(output_dir, exist_ok=True)
    if visualize is True:
        save_map_image(rect,
                map_generation_status="in_progress",
                full_path=f"{output_dir}/rect.png",
            )
    for _ in range(3):
        rect = np.rot90(rect)
        # save image of its rotations
        if visualize is True:
            save_map_image(rect,
                map_generation_status="in_progress",           
                full_path=f"{output_dir}/rect_rotation_{_}.png",
            )
        rotations.append(rect)

    return rotations

def remove_duplicates(rectangles, output_dir):
    """
    Remove duplicate rectangles including congruent ones under rotation.
    """
    unique_rectangles = []
    seen = set()
    
    i = 0
    for rect in rectangles:
        rotations = rotate_rectangle(rect, i, output_dir, visualize=False)
        min_rotation = min(map(lambda x: tuple(map(tuple, x)), rotations))
        #breakpoint() # todo check later
        if min_rotation not in seen:
            seen.add(min_rotation)
            unique_rectangles.append(rect)
        i = i + 1
            
    #breakpoint()
    return unique_rectangles

def save_to_numpy_array(rectangles):
    """
    Convert the list of unique rectangles to a single NumPy array.
    """
    return np.array(rectangles)

# todo use it later
def process_csv(input_file, output_dir):
    data = pd.read_csv(input_file, header=None).to_numpy()
    rectangles = get_rectangles(data)
    unique_rectangles = remove_duplicates(rectangles, output_dir)
    #breakpoint() # todo check that i is int and not a numpy array
    i = 0
    for rectangle in unique_rectangles:
        # Save the rectangle to a CSV file
        rectangle_df = pd.DataFrame(rectangle)
        rectangle_df.to_csv(
            f"{output_dir}/rectangle_{i}.csv", index=False, header=False
        )
        breakpoint()
        # Save the layout as an image as well
        save_map_image( # todo daria check why images are empty
            rectangle,
            map_generation_status="in_progress",
            full_path=f"{output_dir}/rectangle_{i}.png",
        )
        i = i + 1



    #rectangles = load_csv(file_path) this doesn't work
    #unique_rectangles = remove_duplicates(rectangles)
    #return save_to_numpy_array(unique_rectangles)

# Example usage:
input_file = '/home/mila/d/daria.yasafova/mini_ada/data/source_csv/layouts_minigrid - HERE_layout_rooms_10052024.csv'  # replace with your CSV file path
output_dir = "/home/mila/d/daria.yasafova/mini_ada/data/source_csv/big_test"
#input_file = "/home/mila/d/daria.yasafova/mini_ada/data/source_csv/layouts_minigrid - small_test_HERE_layout_rooms_10052024.csv"
#output_dir = "/home/mila/d/daria.yasafova/mini_ada/data/source_csv/small_test"

# TODO daria fix this mess

#breakpoint()
#data = pd.read_csv(input_file, header=None).to_numpy()
#rectangles = get_rectangles(data)
#unique_rectangles = remove_duplicates(rectangles, output_dir)
#breakpoint()
process_csv(input_file, output_dir)

# todo save the unique layouts as csv files