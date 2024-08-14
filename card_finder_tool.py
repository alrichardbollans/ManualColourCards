import argparse
import os

import numpy as np

_inputs_path = 'inputs'
if not os.path.isdir(_inputs_path):
    os.mkdir(_inputs_path)

_manual_detected_card_img_file = os.path.join(_inputs_path, "cropped_image.jpg")


def manual_find_colour_card(image_path):
    # Remove any previous versions
    try:
        os.remove(_manual_detected_card_img_file)
        print(f'Removed old detected image: {_manual_detected_card_img_file}')
    except OSError:
        pass

    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg

    # Load the image
    img = mpimg.imread(image_path)

    # Global list to store the coordinates
    coords = []

    # Function to capture click events
    def onclick(event):
        ix, iy = event.xdata, event.ydata
        coords.append((ix, iy))

        # Plot a point where the user clicked
        plt.plot(ix, iy, 'ro')
        plt.draw()

        # Stop after 4 clicks
        if len(coords) == 4:
            plt.close()

    # Display the image
    fig, ax = plt.subplots()
    ax.imshow(img)

    # Connect the click event to the onclick function
    cid = fig.canvas.mpl_connect('button_press_event', onclick)

    # Start the event loop
    plt.show()

    # After the loop ends, coords will contain the four corners
    # Requires the card to be aligned
    if len(coords) == 4:
        # Extract the x and y coordinates
        x_coords = [coord[0] for coord in coords]
        y_coords = [coord[1] for coord in coords]

        # Calculate the bounding box
        min_x, max_x = int(min(x_coords)), int(max(x_coords))
        min_y, max_y = int(min(y_coords)), int(max(y_coords))

        # Crop the image using numpy slicing
        card = img[min_y:max_y, min_x:max_x]

        # Display the cropped image
        # plt.imshow(card)
        # plt.show()

        # Save the cropped image to load later
        mpimg.imsave(_manual_detected_card_img_file, card)

    else:
        raise ValueError("Error: Less than 4 corners were selected.")


def _match_cumulative_cdf_mod(source, template, full):
    """
    Return modified full image array so that the cumulative density function of
    source array matches the cumulative density function of the template.
    """
    src_values, src_unique_indices, src_counts = np.unique(source.ravel(),
                                                           return_inverse=True,
                                                           return_counts=True)
    tmpl_values, tmpl_counts = np.unique(template.ravel(), return_counts=True)

    # calculate normalized quantiles for each array
    src_quantiles = np.cumsum(src_counts) / source.size
    tmpl_quantiles = np.cumsum(tmpl_counts) / template.size

    interp_a_values = np.interp(src_quantiles, tmpl_quantiles, tmpl_values)

    # Here we compute values which the channel RGB value of full image will be modified to.
    interpb = []
    for i in range(0, 256):
        interpb.append(-1)

    # first compute which values in src image transform to and mark those values.

    for i in range(0, len(interp_a_values)):
        frm = src_values[i]
        to = interp_a_values[i]
        interpb[frm] = to

    # some of the pixel values might not be there in interp_a_values, interpolate those values using their
    # previous and next neighbours
    prev_value = -1
    prev_index = -1
    for i in range(0, 256):
        if interpb[i] == -1:
            next_index = -1
            next_value = -1
            for j in range(i + 1, 256):
                if interpb[j] >= 0:
                    next_value = interpb[j]
                    next_index = j
            if prev_index < 0:
                interpb[i] = (i + 1) * next_value / (next_index + 1)
            elif next_index < 0:
                interpb[i] = prev_value + ((255 - prev_value) * (i - prev_index) / (255 - prev_index))
            else:
                interpb[i] = prev_value + (i - prev_index) * (next_value - prev_value) / (next_index - prev_index)
        else:
            prev_value = interpb[i]
            prev_index = i

    # finally transform pixel values in full image using interpb interpolation values.
    wid = full.shape[1]
    hei = full.shape[0]
    ret2 = np.zeros((hei, wid))
    for i in range(0, hei):
        for j in range(0, wid):
            ret2[i][j] = interpb[full[i][j]]
    return ret2


def match_histograms_mod(inputCard, referenceCard, fullImage):
    """
        Return modified full image, by using histogram equalizatin on input and
         reference cards and applying that transformation on fullImage.
    """
    if inputCard.ndim != referenceCard.ndim:
        raise ValueError('Image and reference must have the same number '
                         'of channels.')
    matched = np.empty(fullImage.shape, dtype=fullImage.dtype)
    for channel in range(inputCard.shape[-1]):
        matched_channel = _match_cumulative_cdf_mod(inputCard[..., channel], referenceCard[..., channel],
                                                    fullImage[..., channel])
        matched[..., channel] = matched_channel
    return matched


def match_images():
    # Methods from: https://github.com/dazzafact/image_color_correction/tree/main
    # write image of card in source image
    manual_find_colour_card(args["input"])
    # importing one of these breaks the manual colour card finder
    import cv2

    print("[INFO] loading images...")
    ref_colour_card = cv2.imread(os.path.join(_inputs_path, "reference_card.png"))
    image = cv2.imread(args["input"])
    image_colour_card = cv2.imread(_manual_detected_card_img_file)

    # apply histogram matching from the color matching card in the
    # reference image to the color matching card in the input image
    print("[INFO] matching images...")
    out = match_histograms_mod(image_colour_card, ref_colour_card, image)
    # show our input color matching card after histogram matching
    print("[INFO] writing images...")
    cv2.imwrite(args["output"], out)
    print("[INFO] exiting...")


def main():
    match_images()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()

    ap.add_argument("-i", "--input", required=True,
                    help="path to the input image to apply color correction to")
    ap.add_argument("-o", "--output", required=True,
                    help="path to save the corrected output image to")
    args = vars(ap.parse_args())
    main()
