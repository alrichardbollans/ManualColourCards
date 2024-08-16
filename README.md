Based on the image calibration methods of https://github.com/dazzafact/image_color_correction

This tool displays the source image and allows selection of the calibration card in the image. This is then used to calibrate the image using a reference
card image.

### Requirements

Tested with python 3.10 and package versions as in requirements.txt.

The reference card used to standardise images is found in `inputs/reference_card.png` -- this is currently just an example for use with
microscope slides and you can change this file to whatever you like. The colour card in the image to be standardised should be horizontally/vertically
aligned so it can be selected properly.

### Usage

Clone and unzip this repository. Set up a python 3.10 venv using requirements.txt.

In a command line navigate to the repository, then run `python card_finder_tool.py -i [INPUT_IMG_PATH] -o [OUTPUT_IMG_PATH]`

This should begin by displaying the source image. Click on the four corners of the colour card in this image. The standardised version will be
saved to OUTPUT_IMG_PATH. The extracted manual colour card will be saved to `inputs/_manual_detected_card.png` for you to inspect.

If you run with the `-c` flag you can specify a filepath where a colour card has been previously extracted. This can be helpful for running image
standardisation on batches of images with similar settings. If no file already exists there, you will have the opportunity to create one.

If you find any problems or have suggestions for improvements, please raise an issue or PR.