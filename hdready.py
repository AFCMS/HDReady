from math import exp
import os

import pickle
import fire
from PIL import Image
from os import listdir
from os.path import isfile, join, dirname
from multiprocessing import Pool

coeff = None
width = None
height = None


# Functions
def generate_dictionnary(stdDeviation: int)->'coefficient dictionnary':
    """This function generates a dictionnary that associates the weight 
    of a pixel channel and it's weight
    Arg:
        stdDeviation: parameter of the Gaussian function
    Return:
        (dict): dictonnary of weigths"""
    return {value: round((exp(-((value-127)**2)/(2*stdDeviation**2))), 6) 
           for value in range(0, 256)}


def open_images(imagesFolderPath:str)->'list containing images':
    """This function open and store the images to merge into a list
    Args:
        imagesFolderPath (str): path of the folder containing the images
        e.g. 'C:/Users/John/myImage/bracketed_images_bridge/'
    """
    images = []
    imagesPath = [
        f for f in listdir(imagesFolderPath)
        if isfile(join(imagesFolderPath, f))]
    images = [Image.open(os.path.join(imagesFolderPath, name)) 
             for name in imagesPath]
    return images


def exposition_measure(channels:tuple)->'weight':
    """This function measures the exposition of a given pixel
    and apply a Gauss curve to compute the weight
    Arg:
        channels (tuple): tuple that contains red, green and blue channel
    Return:
        coeff (int): exposure weight of the pixel"""
    global coeff
    weight = 1
    for x in range(3):
        weight *= coeff[channels[x]]
    return weight


def generate_new_image(imagesToMerge: list):
    """This function merges the images into a new one
    Arg:
        imagesToMerge (list): list containing the input images
    Return:
        finalImage (image object): a part of the final image
    """
    global width
    global height
    finalImage = Image.new(mode="RGB", size=(width, height))
    for y in range(height):
        for x in range(width):
            newPixel = [0, 0, 0]
            # Compute coefficients
            pixels = [image.getpixel((x, y)) for image in imagesToMerge]
            coefficient = [exposition_measure(rgb) for rgb in pixels]
            sum_coeff = sum(coefficient)
            # Normalization of coefficient values
            coefficient = [c / sum_coeff if sum_coeff != 0 
                          else c for c in coefficient]
            # Merging
            for i in range(len(coefficient)):
                for n in range(3):
                    newPixel[n] += pixels[i][n] * coefficient[i]
            # Rounding values
            newPixel = tuple([round(a) for a in newPixel])
            # Write new rgb values into the final image
            finalImage.putpixel((x, y), newPixel)
    return finalImage

def images_crop(imagesToMerge:list, processes:int):
    """This function cuts the images in processes parts WIP
    Args:
        imagesToMerge (list): list containing images objects
        processes (int): number of cores used by the fusion process and number
            of parts of the images.
    """
    global width
    global height
    # Generation of the coordinates of the part of the images
    parts = [(int(x*(1/processes)*width), 0, int((x+1)*(1/processes)), height)
            for x in range(processes)]
    if processes == 1:
        return imagesToMerge
    return [[img.crop(parts[x]) for img in imagesToMerge] 
           for x in range(processes)]
        

def images_reassemble(imagesToStick:list):
    """This function reassembles the parts of the final image
    Arg:
        imagesToStick (list): contains the pieces of the final image
    Return:
        (image object): final image
    WIP
    """
    global width
    global height
    finalImage = Image.new(mode="RGB", size=(width, height))
    finalImage.paste(imagesToStick[0])
    finalImage.paste(imagesToStick[1], (int(width/2), 0, width, height))
    return finalImage


def start(imagesFolderPath: str, finalPath: str,
         stdDeviation: int = 100, processes: int = 1):
    """This function launches the merging process. stdDeviation parameter is
    used to compute the weight of a given pixel. The smaller the value, the
    greater the dynamic range.

    Args:
        imagesFolderPath (str): path of the folder that contains the images
        to merge
        finalPath (str): complete path of the output merged image
            (e.g. 'C:\\Users\\Tim\\Images\\hdr_bridge.png')
        stdDeviation (int): standart deviation of the gaussian curve used
            a weight generator. This parameter can be from 10 to 150
            with a step of 10
        processes (int): number of processes to decrease the time of execution,
            i.e. number of cores used by the merging algorithm
    
    Raises:
        FileNotFoundError: if the specified path of the folder is incorrect
        Exception: if there is no image to compute in the folder

    """
    global coeff
    global width
    global height
    # Check if the folder containing the images exists or not
    if os.path.isdir(imagesFolderPath):
        # Generating the coeff dictionnary and opening the images to merge
        coeff = generate_dictionnary(stdDeviation)
        images = open_images(imagesFolderPath)
    else:
        raise FileNotFoundError
    # Check if the folder contains images:
    if len(os.listdir(imagesFolderPath)) == 0:
        raise Exception("There is no image in the folder!")
    # Check if the final directory exists and create it if it doesn't
    if not os.path.exists(os.path.dirname(finalPath)):
        os.makedirs(os.path.dirname(finalPath))
    # Declaring the size of the images
    width, height = images[0].width, images[0].height
    # Division of the images
    divided_images = images_crop(images)
    # Multiprocessing
    if __name__ == '__main__':
        with Pool(2) as p:
            pieces_of_final_images = p.map(generate_new_image, divided_images)
    # Reassemble the pieces of the final image
    finalImage = images_reassemble(pieces_of_final_images)
    # Saving the final image
    finalImage.save(finalPath)
    # End message
    print('HDR merging completed')


fire.Fire(start)
