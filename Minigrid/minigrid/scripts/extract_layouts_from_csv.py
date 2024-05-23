import numpy as np
import pandas as pd
import os
import argparse
from save_np_as_png import save_map_image


"""
This script extracts layouts of an arbitrary size N x M from a source csv
containing an arbitriry number of layouts
and saves each layout into a separate csv file.
This script only works with layouts of rectangular shape.
In order to avoid unexpected and wrong outputs,
make sure to only have rectangular layouts in the source csv file.
"""


def find_next_rectangle(data):
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if not pd.isna(data[i, j]):
                # Find the top-left corner of the next rectangle
                top_left = (i, j)

                # Find the bottom-right corner
                bottom_right = find_bottom_right(data, top_left)

                return top_left, bottom_right
    return None, None


def find_bottom_right(data, top_left):
    i, j = top_left
    max_i, max_j = i, j

    # Find the right boundary
    while max_j + 1 < data.shape[1] and not pd.isna(data[i, max_j + 1]):
        max_j += 1

    # Find the bottom boundary
    while max_i + 1 < data.shape[0] and not pd.isna(data[max_i + 1, j]):
        max_i += 1

    return (max_i, max_j)


def extract_rectangle(data, top_left, bottom_right):
    i1, j1 = top_left
    i2, j2 = bottom_right

    # Extract the rectangle
    rectangle = np.array(
        data[i1 : i2 + 1, j1 : j2 + 1], copy=True
    )  # using a copy otherways rectangle gets deleted
    # when we remove the rectangle from the original data

    # Mark the rectangle cells as NaN
    data[i1 : i2 + 1, j1 : j2 + 1] = np.nan

    return rectangle


def save_rectangles(data, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    rectangle_count = 0
    while True:
        top_left, bottom_right = find_next_rectangle(data)
        if top_left is None:
            break

        rectangle = extract_rectangle(data, top_left, bottom_right)
        # Save the rectangle to a CSV file
        rectangle_df = pd.DataFrame(rectangle)
        rectangle_df.to_csv(
            f"{output_dir}/rectangle_{rectangle_count}.csv", index=False, header=False
        )
        # Save the layout as an image as well
        breakpoint()
        save_map_image(
            rectangle,
            map_generation_status="in_progress",
            full_path=f"{output_dir}/rectangle_{rectangle_count}.png",
        )
        rectangle_count += 1

def get_rectangles(data: np.ndarray) -> list[np.ndarray]:
    rectangles = []
    #for i in data:
    #    print(i)
    while True:
        top_left, bottom_right = find_next_rectangle(data)
        if top_left is None:
            break

        rectangle = extract_rectangle(data, top_left, bottom_right) # todo check if it modifies data (removes it)
        #rectangles = np.append(rectangles, rectangle) # this is wrong, it appends it into one large numpy array, instead of a list of numpy arrays
        rectangles.append(rectangle)

    #breakpoint()

    return rectangles
        

def main(input_file, output_dir):
    # Read the CSV file into a NumPy array
    data = pd.read_csv(input_file, header=None).to_numpy()
    print(data)
    for i in data:
        print(i)
    #breakpoint()
    #get_rectangles(data) # todo remove this later, just testing why it's not working
    print(data)
    for i in data:
        print(i)
    save_rectangles(data, output_dir)
    #print(data)
    #for i in data:
    #    print(i)
    #breakpoint()
    # Save the modified original array back to a CSV file
    modified_df = pd.DataFrame(data)
    modified_df.to_csv(
        "modified_" + os.path.basename(input_file), index=False, header=False
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract layouts from a CSV file.")
    parser.add_argument("--input_file", help="Path to the input CSV file")
    parser.add_argument(
        "--output_dir", help="Directory to save the extracted layouts as csv files"
    )

    args = parser.parse_args()

    main(args.input_file, args.output_dir)

# python extract_layouts_from_csv.py --input_file="/home/mila/d/daria.yasafova/mini_ada/data/source_csv/layouts_minigrid - WIP_layout_rooms_10052024.csv" --output_dir="/home/mila/d/daria.yasafova/mini_ada/data/templates/extracted_rooms"
# python extract_layouts_from_csv.py --input_file="/home/mila/d/daria.yasafova/mini_ada/data/source_csv/layouts_minigrid - HERE_layout_rooms_10052024.csv" --output_dir="/home/mila/d/daria.yasafova/mini_ada/data/templates/extracted_rooms"
#python extract_layouts_from_csv.py --input_file="/home/mila/d/daria.yasafova/mini_ada/data/source_csv/layouts_minigrid - HERE_layout_rooms_10052024.csv" --output_dir="/home/mila/d/daria.yasafova/scratch/miniada/images"


