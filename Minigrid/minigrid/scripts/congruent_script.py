import numpy as np
import pandas as pd

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
    return rectangles

def rotate_rectangle(rect):
    """
    Generate all four rotations of a rectangle.
    """
    rotations = [rect]
    for _ in range(3):
        rect = np.rot90(rect)
        rotations.append(rect)
    return rotations

def remove_duplicates(rectangles):
    """
    Remove duplicate rectangles including congruent ones under rotation.
    """
    unique_rectangles = []
    seen = set()
    
    for rect in rectangles:
        rotations = rotate_rectangle(rect)
        min_rotation = min(map(lambda x: x.tobytes(), rotations))
        if min_rotation not in seen:
            seen.add(min_rotation)
            unique_rectangles.append(rect)
            
    return unique_rectangles

def save_to_numpy_array(rectangles):
    """
    Convert the list of unique rectangles to a single NumPy array.
    """
    return np.array(rectangles)

def process_csv(file_path):
    """
    Process the CSV file to remove duplicates and save the unique rectangles to a NumPy array.
    """
    rectangles = load_csv(file_path)
    unique_rectangles = remove_duplicates(rectangles)
    return save_to_numpy_array(unique_rectangles)

# Example usage:
file_path = 'rectangles.csv'  # replace with your CSV file path
unique_rectangles_array = process_csv(file_path)
print(unique_rectangles_array)
