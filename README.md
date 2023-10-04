# sfvqsamples
Tool for listening to speech samples from each used sfvq codebook index.


To run the program, type:

python playsamples.py YOUR_PATH_HERE

, where YOUR_PATH_HERE is the path from which you can access the TIMIT dataset folder. For example,

python playsamples.py /work/t405/T40571/sounds/


This will open a GUI where you can click on the canvas element which shows the codebook indices as the x and y coordinates of the mouse. Clicking the canvas with the left mouse button plays a random speech sample at that x coordinate which was mapped to the corresponding codebook index in the sfvq. Clicking the canvas with the right mouse button plays a random speech sample at the y coordinate. The background image represents the euclidean distances between the codebooks at indices x and y. 
