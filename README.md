# Morphing App - Fourier Transform Mixer

## Overview

This desktop application is designed to demonstrate the relative importance of the magnitude and phase components in a 2D signal (Image) using Fourier Transform Mixer. The software allows users to open and view four grayscale images simultaneously, control image sizes, customize Fourier Transform components, adjust brightness/contrast, and perform real-time mixing with customizable weights and region selections.

## Features

### Image Viewers

1. **Open and View Images:**
   - Open and view four grayscale images, with automatic conversion to grayscale for colored images.
   - Ensure unified sizes for all images based on the smallest size.

2. **FT Components Display:**
   - Each image has two displays: one for the image itself and the other for Fourier Transform components.
   - Fourier Transform (FT) components include Magnitude, Phase, Real, and Imaginary.
   - Easily switch between components using a combo-box/drop-menu selection.

3. **Easy Browse:**
   - Change any image by double-clicking on its viewer.


 https://github.com/shehab400/Face_Morphing/assets/115353206/76d56a14-b3c9-46ee-a665-912e4a55ae4e
### Output Ports

1. **Two Output Viewports:**
   - The mixer result can be shown in one of two output viewports, each similar to the input image viewport.
   - Users can control where the mixer result is displayed.

### Brightness/Contrast

1. **Adjustable Brightness/Contrast:**
   - Change the brightness/contrast of any image viewport via mouse dragging (up/down and left/right).
   - Apply adjustments to any of the four FT components as well.

### Components Mixer

1. **Customizable Weights:**
   - Output image is the inverse Fourier transform (ifft) of a weighted average of the FT of the input four images.
   - Customize weights for each image FT using sliders.

### Regions Mixer

1. **Region Selection:**
   - Allow users to pick regions for each FT component (inner or outer) using a rectangle drawn on each FT.
   - Provide an option to include the inner or outer region, with the selected region highlighted (semi-transparent coloring or hashing).
   - Customize the size (or percentage) of the region rectangle via a slider or resize handles.

### Real-time Mixing

1. **Progress Bar:**
   - Display a progress bar during the mixing process, indicating the update of the operation.
   - Cancel the previous operation if the user requests a new update while the previous one is still running (check threads).

https://github.com/shehab400/Face_Morphing/assets/115353206/2ab61801-b46e-4633-b42d-7ac0a49b0ca6
## Usage

1. **Open Images:**
   - Use the file menu or drag-and-drop images onto the respective viewports.

2. **Adjust Components:**
   - Select FT components and adjust brightness/contrast as needed.

3. **Customize Weights:**
   - Use sliders to customize weights for each image.

4. **Region Selection:**
   - Draw rectangles on FT components to select regions.

5. **Real-time Mixing:**
   - Initiate mixing and monitor progress with the displayed progress bar.

## Contributors

- Shehap Elhadary
- AbdelRahman Hesham
- Mohamed Ibrahim





