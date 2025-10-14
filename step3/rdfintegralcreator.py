import json
import numpy as np
import ROOT

from concurrent.futures import ProcessPoolExecutor, as_completed
import time
ROOT.ROOT.EnableImplicitMT()

def job(job_id):
    print(f"Starting Job {job_id}")

    file_input_dir = "/eos/cms/store/group/phys_bphys/DiElectronX/jodedra/1000_output_data_noD0cut/"
    mode = "jpsi"
    file_name = f"measurement_{mode}_{job_id}_TrigSfs.root"
    file_input = file_input_dir + file_name
    root_file = ROOT.TFile.Open(file_input)
    df = ROOT.RDataFrame("mytree", root_file)
    if mode == "rare":
        selection = "(bdt_score > 3.95) && (Bmass > 4.75) && (Bmass < 5.7) && (Mll > 1.05) && (Mll < 2.45) && (KLmassD0>2.0)"
    else:
        selection = "(bdt_score > 3.95) && (Bmass > 4.75) && (Bmass < 5.7) && (Mll > 2.9) && (Mll < 3.2) && (KLmassD0>2.0)"
    final_mc_values = []
    output_dir ="/eos/user/j/jodedra/AnalysisWork_2024/systematics/TriggerScaleFactors/MakingScaleFactorTuples/ScaleFactors_04_03_25/Step_3_integral_calc/integral_1000_jpsi/"
    output_file = open(f"{output_dir}integrals_{mode}_100_part_{job_id}_.txt", "a")
    for sampleval in range(100):
        weight = f"sf_combined_stat_samples_trig_wgt[{sampleval}]"
        df_filtered = df.Filter(selection).Define("weight", weight)
        hist = df_filtered.Histo1D(("hist", "Histogram of sf_combined_samples_trig_wgt", 50, 0, 10), "Bmass", "weight")
        integral = hist.Integral()
        #print(integral)
        
        # Append the integral to the final_mc_values list
        final_mc_values.append(integral)
        output_file.write(f"{integral}\n")
        output_file.flush()
    
# Optionally, plot the final_mc_values list using matplotlib
    output_file.close()
    print(f"Finished Job {job_id}")
    return f"Result of Job {job_id}"





if __name__ == "__main__":
    # List of jobs to execute
    jobs = list(range(0, 1000))  # Adjust the range as needed
    
    # Maximum number of parallel jobs
    max_parallel_jobs = 20
    
    # Use ProcessPoolExecutor for parallel processing
    with ProcessPoolExecutor(max_workers=max_parallel_jobs) as executor:
        # Submit jobs to the executor
        future_to_job = {executor.submit(job, job_id): job_id for job_id in jobs}
        
        # As jobs complete, handle results
        for future in as_completed(future_to_job):
            job_id = future_to_job[future]
            try:
                result = future.result()  # Get the result of the job
                print(result)
            except Exception as e:
                print(f"Job {job_id} generated an exception: {e}")