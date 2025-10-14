import json
import numpy as np
import ROOT

def sample_from_gaussian(mean, stddev, n_samples=1000):
    """
    Samples multiple numbers from a Gaussian distribution.

    Parameters:
    mean (float): The mean of the Gaussian distribution.
    stddev (float): The standard deviation of the Gaussian distribution.
    n_samples (int): The number of samples to generate.

    Returns:
    np.ndarray: An array of samples from the Gaussian distribution.
    """
    return np.random.normal(mean, stddev, n_samples)

jsonfileinput = "/eos/user/j/jodedra/AnalysisWork_2024/systematics/TriggerScaleFactors/MakingScaleFactorTuples/ScaleFactors_04_03_25/TriggerJsons/trigger_sfs_ptbinned.json"

with open(jsonfileinput, 'r') as file:
    # Step 3: Load the JSON data into a dictionary
    triggerjson = json.load(file)
    
jsondata = triggerjson["trigger_OR"]["sfs"]

outputdir = "/eos/user/j/jodedra/AnalysisWork_2024/systematics/TriggerScaleFactors/MakingScaleFactorTuples/ScaleFactors_04_03_25/Step_1_Make_Matrix/MatrixSampleSF_1000/"

values_mean = []
values_stat_err = []
#values_syst_err = []
for i in range(len(jsondata)):
    values_mean.append(str(jsondata[i][0]))
    values_stat_err.append(str(jsondata[i][1]))
    #values_syst_err.append(str(jsondata[i][2]))

# Generate 1000 samples for each mean and standard error value
for i in range(1000):
    samples_matrix = []
    for mean, stat_err in zip(values_mean, values_stat_err):
        samples = sample_from_gaussian(float(mean), float(stat_err), 100)
        samples_matrix.append(samples)

    # Convert the list of samples to a numpy array and transpose it to store samples vertically
    samples_matrix = np.array(samples_matrix).T
    print(samples_matrix)
    
    # Save the matrix to a text file with a three-digit number
    filename = outputdir + f"Gauss_sampled_matrix_{i:03d}.txt"
    np.savetxt(filename, samples_matrix, delimiter=" ")

print("Matrices saved to files with three-digit numbers.")