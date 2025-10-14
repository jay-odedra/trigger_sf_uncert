import json
import numpy as np
import ROOT

from concurrent.futures import ProcessPoolExecutor, as_completed
import time

# Example function to simulate a job
def job(job_id):
    print(f"Starting Job {job_id}")
    
    matrix_input_dir = "/eos/user/j/jodedra/AnalysisWork_2024/systematics/TriggerScaleFactors/MakingScaleFactorTuples/ScaleFactors_04_03_25/Step_1_Make_Matrix/MatrixSampleSF_1000/"
    
    jsonfileinput = "/eos/user/j/jodedra/AnalysisWork_2024/systematics/TriggerScaleFactors/MakingScaleFactorTuples/ScaleFactors_04_03_25/TriggerJsons/trigger_sfs_ptbinned.json"
   
    with open(jsonfileinput, 'r') as file:
    # Step 3: Load the JSON data into a dictionary
        triggerjson = json.load(file)
    
    jsondata = triggerjson["trigger_OR"]["sfs"]




    file_paths = {
        #"measurement_data" :  "measurement_data.root",
        #"measurement_same_sign_electrons" :  "measurement_same_sign_electrons.root",
        "measurement_rare" :  "measurement_rare.root",
        "measurement_jpsi" :  "measurement_jpsi.root",
        "measurement_psi2s" :  "measurement_psi2s.root",
        "measurement_kstar_jpsi_kaon" :  "measurement_kstar_jpsi_kaon.root",
        "measurement_kstar_jpsi_pion" :  "measurement_kstar_jpsi_pion.root",
        "measurement_k0star_jpsi_kaon" :  "measurement_k0star_jpsi_kaon.root",
        "measurement_k0star_jpsi_pion" :  "measurement_k0star_jpsi_pion.root",
        "measurement_chic1_jpsi_kaon" :  "measurement_chic1_jpsi_kaon.root",
        "measurement_jpsipi_jpsi_pion" :  "measurement_jpsipi_jpsi_pion.root",
        "measurement_kstar_psi2s_pion" :  "measurement_kstar_psi2s_pion.root",
        "measurement_k0star_psi2s_kaon" :  "measurement_k0star_psi2s_kaon.root",
        "measurement_k0star_psi2s_pion" :  "measurement_k0star_psi2s_pion.root",
        "measurement_kstar_pion" :  "measurement_kstar_pion.root",
        "measurement_k0star_kaon" :  "measurement_k0star_kaon.root",
        "measurement_k0star_pion" :  "measurement_k0star_pion.root",
    }
    
    

    

    
    
    
    values_mean = []
    values_stat_err = []
    #values_syst_err = []
    for i in range(len(jsondata)):
        values_mean.append(str(jsondata[i][0]))
        values_stat_err.append(str(jsondata[i][1]))
    #    values_syst_err.append(str(jsondata[i][2]))

    mean_vector_name_def = f"myv_{job_id:03d}"
    stat_err_vector_name_def = f"myv_stat_err_{job_id:03d}"
    #syst_err_vector_name_def = f"myv_syst_err_{job_id:03d}"

    ROOT.gInterpreter.Declare(f"std::vector<float> {mean_vector_name_def} = {{" + ",".join(values_mean) + "};")
    ROOT.gInterpreter.Declare(f"std::vector<float> {stat_err_vector_name_def} = {{" + ",".join(values_stat_err) + "};")
    #ROOT.gInterpreter.Declare(f"std::vector<float> {syst_err_vector_name_def} = {{" + ",".join(values_syst_err) + "};")
    
    # Load the matrix from the text file
    loaded_matrix = np.loadtxt(f"{matrix_input_dir}Gauss_sampled_matrix_{job_id:03d}.txt", delimiter=" ")
    # Convert the loaded matrix to a format that can be passed to C++
    matrix_as_list = loaded_matrix.tolist()

    # Convert the matrix to a string representation that can be used in C++
    matrix_as_string = "{" + ",".join("{" + ",".join(map(str, row)) + "}" for row in matrix_as_list) + "}"
    
    unique_matrix_name = f"matrix_{job_id}"
    unique_load_function = f"load_matrix_{job_id}"
    unique_scale_factor_function = f"scale_factor_matrix_{job_id}"
    unique_scale_factor_sampled_withtrig_function = f"scale_factor_sampled_withtrig_{job_id}"

    ROOT.gInterpreter.Declare(f"""
    #include <vector>
    #include <iostream>

    std::vector<std::vector<float>> {unique_matrix_name};

    void {unique_load_function}() {{
        {unique_matrix_name}.clear();
        std::vector<std::vector<float>> temp_matrix = {matrix_as_string};
        for (const auto& row : temp_matrix) {{
            {unique_matrix_name}.push_back(row);
        }}
    }}

        
    std::vector<float> {unique_scale_factor_function}(float L2pt) {{
        std::vector<float> result;
        for (const auto& row : {unique_matrix_name}) {{
            if (L2pt < 5.0) {{
                result.push_back(row[0]);
            }}
            else if (L2pt >= 5.0 && L2pt < 7.0) {{
                result.push_back(row[0]);
            }}
            else if (L2pt >= 7.0 && L2pt < 9.0) {{
                result.push_back(row[1]);
            }}
            else if (L2pt >= 9.0 && L2pt < 10.0) {{
                result.push_back(row[2]);
            }}
            else if (L2pt >= 10.0 && L2pt < 11.0) {{
                result.push_back(row[3]);
            }}
            else if (L2pt >= 11.0 && L2pt < 12.0) {{
                result.push_back(row[4]);
            }}
            else if (L2pt >= 12.0 && L2pt < 13.0) {{
                result.push_back(row[5]);
            }}
            else if (L2pt >= 13.0) {{
                result.push_back(row[6]);
            }}
        }}
        return result;
    }}
    std::vector<float> {unique_scale_factor_sampled_withtrig_function}(std::vector<float> samples, float trig_wgt) {{
        std::vector<float> result_withtrig;
        for (int i = 0; i < samples.size(); i++) {{
            result_withtrig.push_back(samples[i] * trig_wgt);
        }}
        return result_withtrig;
    }}
    """)
    
    scale_factor_function_name = f"scale_factor_{job_id}"
    scale_factor_stat_err_function_name = f"scale_factor_stat_err_{job_id}"
    #scale_factor_syst_err_function_name = f"scale_factor_syst_err_{job_id}"
    
    ROOT.gInterpreter.Declare(f"""
        double scale_factor_{job_id}(float pt) {{
            if (pt < 5.0) {{ return {mean_vector_name_def}[0]; }}
            else if (pt >= 5.0 && pt < 7.0) {{ return {mean_vector_name_def}[0]; }}
            else if (pt >= 7 && pt < 9.0) {{ return {mean_vector_name_def}[1]; }}
            else if (pt >= 9.0 && pt < 10.0) {{ return {mean_vector_name_def}[2]; }}
            else if (pt >= 10.0 && pt < 11.0) {{ return {mean_vector_name_def}[3]; }}
            else if (pt >= 11.0 && pt < 12.0) {{ return {mean_vector_name_def}[4]; }}
            else if (pt >= 12.0 && pt < 13.0) {{ return {mean_vector_name_def}[5]; }}
            else if (pt >= 13.0) {{ return {mean_vector_name_def}[6]; }}
            else {{ return -1000.0; }}
        }}

        double scale_factor_stat_err_{job_id}(float pt) {{
            if (pt < 5.0) {{ return {stat_err_vector_name_def}[0]; }}
            else if (pt >= 5.0 && pt < 7.0) {{ return {stat_err_vector_name_def}[0]; }}
            else if (pt >= 7 && pt < 9.0) {{ return {stat_err_vector_name_def}[1]; }}
            else if (pt >= 9.0 && pt < 10.0) {{ return {stat_err_vector_name_def}[2]; }}
            else if (pt >= 10.0 && pt < 11.0) {{ return {stat_err_vector_name_def}[3]; }}
            else if (pt >= 11.0 && pt < 12.0) {{ return {stat_err_vector_name_def}[4]; }}
            else if (pt >= 12.0 && pt < 13.0) {{ return {stat_err_vector_name_def}[5]; }}
            else if (pt >= 13.0) {{ return {stat_err_vector_name_def}[6]; }}
            else {{ return -1000.0; }}
        }}
        """)
    
    '''
        double scale_factor_syst_err_{job_id}(float pt) {{
            if (pt < 5.0) {{ return {syst_err_vector_name_def}[0]; }}
            else if (pt >= 5.0 && pt < 7.0) {{ return {syst_err_vector_name_def}[0]; }}
            else if (pt >= 7 && pt < 9.0) {{ return {syst_err_vector_name_def}[1]; }}
            else if (pt >= 9.0 && pt < 10.0) {{ return {syst_err_vector_name_def}[2]; }}
            else if (pt >= 10.0 && pt < 11.0) {{ return {syst_err_vector_name_def}[3]; }}
            else if (pt >= 11.0 && pt < 12.0) {{ return {syst_err_vector_name_def}[4]; }}
            else if (pt >= 12.0 && pt < 13.0) {{ return {syst_err_vector_name_def}[5]; }}
            else if (pt >= 13.0) {{ return {syst_err_vector_name_def}[6]; }}
            else {{ return -1000.0; }}
        }}
        """)
    '''
    getattr(ROOT, unique_load_function)()
    
    for key, value in file_paths.items():
        input_file = "/eos/user/j/jodedra/AnalysisWork_2024/systematics/TriggerScaleFactors/MakingScaleFactorTuples/ScaleFactors_04_03_25/data_and_mc_files_with_all_Vars_with_npvs/"+value
        tree_name = "mytree"
        print("Processing file: ", input_file)
        if "sampled" in key:
            weight_branch = "trig_wgt_reweighted"
        else:
            weight_branch = "trig_wgt"

        output_file = "/eos/user/j/jodedra/AnalysisWork_2024/systematics/TriggerScaleFactors/MakingScaleFactorTuples/ScaleFactors_04_03_25/data_and_mc_files_with_all_Vars_with_npvs_with_trig_sfs/" + key + "_" + str(job_id) + "_TrigSfs.root"
        df = ROOT.RDataFrame(tree_name, input_file)














        df = df.Define("sf_combined_mean", f"scale_factor_{job_id}(L2pt)")
        #df = df.Define("sf_combined_syst_err", f"scale_factor_syst_err_{job_id}(L2pt)")
        df = df.Define("sf_combined_stat_err", f"scale_factor_stat_err_{job_id}(L2pt)")
        df = df.Define("sf_combined_mean_trig_wgt","sf_combined_mean*"+weight_branch)
        #df = df.Define("sf_combined_syst_err_trig_wgt","sf_combined_syst_err*"+weight_branch)
        df = df.Define("sf_combined_stat_err_trig_wgt","sf_combined_stat_err*"+weight_branch)
        #df = df.Define("sf_combined_stat_samples",f"{unique_scale_factor_function}(L2pt)")
        #df = df.Define("sf_combined_stat_samples_trig_wgt", f"{unique_scale_factor_sampled_withtrig_function}(sf_combined_stat_samples, "+weight_branch+")")
        
        df.Snapshot(tree_name, output_file)

    
    print(f"Finished Job {job_id}")
    return f"Result of Job {job_id}"









if __name__ == "__main__":
    # List of jobs to execute
    jobs = list(range(0, 1))  # Adjust the range as needed
    
    # Maximum number of parallel jobs
    max_parallel_jobs = 1
    
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