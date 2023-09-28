# sfvqsamples
Tool for listening to speech samples from each used sfvq codebook index.


To run the program, type:

python playsamples.py YOUR_PATH_HERE

, where YOUR_PATH_HERE is the path from which you can access the TIMIT dataset folder. For example,

python playsamples.py /work/t405/T40571/sounds/


This will open a GUI where you can click on the canvas element which shows the codebook index as the x coordinate of the mouse. Clicking the canvas at that x coordinate plays the speech sample which was mapped to the corresponding codebook index in the sfvq, which was trained on the TIMIT dataset for both males and females.
