

def remove_cropped_region(original_data, crop_coordinate):
    # Convert crop coordinate to array indices
    crop_position = tuple(int(coord) for coord in crop_coordinate)

    # Make a copy of the original data
    modified_data = original_data.copy()

    # Ensure that the cropped region fits within the original image
    original_shape = modified_data.shape

    # Set the values in the specified region to zeros
    modified_data[crop_position[0]:, crop_position[1]:] = 0

    return modified_data