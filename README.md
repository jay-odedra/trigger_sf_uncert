# Project Workflow

## Step 1: 
- This creates multiple trigger scale factors (a matrix) which is randomley distrubuted from the original scale factor file and the associated uncertainties

## Step 2: 
- This takes in the matrix from step 1 and applies these scale factors to files. It creates multiple files each with a different sampled scale factor

## Step 3: 
- This calculated the integral value for the files with the scale factor applied and prints it to a txt file

## Step 4: 
- using the text files of all the values for different sampled scale factors we fit using a gaussian to get the error which is then used to calcualte uncertainty for trigger scale factors
