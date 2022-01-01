# HDReady
This is a HDR software fully written in Python. This is a project in development, your help will always be appreciated!

## What's the purpose of this project?

A DSLR camera has a limited dynamic range. When there are some dark and very bright things in the same scene some parts of your image will be over/underexposeded. This programs aims at merging a few **static** bracketed images to have a high dynamic range image.

## The program

I use Pillow to manipulate images.
The operation at the heard of the merging process is the following:   
optimal value = (sum of values * sum of weights) / (sum of weights)

If you want to know more about HDR and image merging, this is a gold mine: [NVIDIA_hdr_algorithms](https://research.nvidia.com/sites/default/files/publications/Gallo-Sen_StackBasedHDR_2016.pdf)
 
