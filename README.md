Based on the image calibration methods of https://github.com/dazzafact/image_color_correction

This tool displays the source image and allows selection of the calibration card in the image. This is then used to calibrate the card to a reference
image.

## Requirements

Tested with python 3.10 and package versions as in requirements.txt.

## Usage

Clone and unzip this repository. Set up a python venv using requirements.txt.

In a command line navigate to the repository, then run `python card_finder_tool.py -i [INPUT_IMG_PATH] -o [OUTPUT_IMG_PATH]`

This should begin by displaying the source image. Click on the four corners of the colour card in this image. The standardised version should then be
saved to OUTPUT_IMG_PATH.

If you find any problems or have suggestions for improvements, please raise an issue.