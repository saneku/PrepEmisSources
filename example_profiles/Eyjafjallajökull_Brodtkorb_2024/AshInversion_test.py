import json
import numpy as np

def expandVariable(emission_times, level_heights, ordering_index, variable):
    #Make JSON-data into 2d matrix
    x = np.ma.masked_all(ordering_index.shape)
    for t in range(len(emission_times)):
        for a in range(len(level_heights)):
            emis_index = ordering_index[a, t]
            if (emis_index >= 0):
                x[a, t] = variable[emis_index]
    return x

def readJson(json_filename, 
        **kwargs):
    #Read data
    with open(json_filename, 'r') as infile:
        json_string = infile.read()

    #Parse data
    json_data = json.loads(json_string)

    #Add metadata to json_data
    #json_data["filename"] = os.path.abspath(json_filename)
    #json_data["meta"] = json.dumps(json_data)

    #Parse data we care about
    json_data["emission_times"] = np.array(json_data["emission_times"], dtype='datetime64[ns]')
    json_data["level_heights"] = np.array(json_data["level_heights"], dtype=np.float64)
    volcano_altitude = json_data["volcano_altitude"]

    json_data["ordering_index"] = np.array(json_data["ordering_index"], dtype=np.int64)
    #json_data["a_priori"] = np.array(json_data["a_priori_2d"], dtype=np.float64)
    json_data["a_posteriori"] = np.array(json_data["a_posteriori_2d"], dtype=np.float64)

    #json_data["residual"] = np.array(json_data["residual"], dtype=np.float64)
    #json_data["convergence"] = np.array(json_data["convergence"], dtype=np.float64)

    #json_data["run_date"] = np.array(json_data["run_date"], dtype='datetime64[ns]')

    #Make JSON-data into 2d matrix
    json_data["a_posteriori"] = expandVariable(json_data["emission_times"], json_data["level_heights"], json_data["ordering_index"], json_data["a_posteriori"])
    #json_data["a_priori"] = expandVariable(json_data["emission_times"], json_data["level_heights"], json_data["ordering_index"], json_data["a_priori"])

    #Prune any unused a priori elevations and timesteps
    #if (prune):
    #    valid_elevations = max(np.flatnonzero((json_data['a_priori'].max(axis=1) + json_data['a_posteriori'].max(axis=1)) > prune_zero)) + 1
    #    valid_times = np.flatnonzero((json_data['a_priori'].max(axis=0) + json_data['a_posteriori'].max(axis=0)) > prune_zero)
    #    if valid_times_min is None:
    #        valid_times_min = min(valid_times)
    #    if valid_times_max is None:
    #        valid_times_max = max(valid_times) + 1

        #json_data['a_priori'] = json_data['a_priori'][:valid_elevations,valid_times_min:valid_times_max]
    #    json_data['a_posteriori'] = json_data['a_posteriori'][:valid_elevations,valid_times_min:valid_times_max]
    #    json_data["ordering_index"] = json_data["ordering_index"][:valid_elevations,valid_times_min:valid_times_max]
    #    json_data["emission_times"] = json_data["emission_times"][valid_times_min:valid_times_max]
    #    json_data["level_heights"] = json_data['level_heights'][:valid_elevations]

    return json_data


if __name__ == "__main__":
    json_filename='/Users/ukhova/Downloads/PrepEmisSources/example_profiles/Eyjafjallajökull_Brodtkorb_2024/inversion_000_1.00000000_a_posteriori_reference.json'
    json_data = readJson(json_filename)
    
    print(json_data)
    times = json_data['emission_times']
    y_labels = [a for a in np.cumsum(np.concatenate(([json_data['volcano_altitude']], json_data['level_heights'])))]