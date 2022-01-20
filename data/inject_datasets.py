from pathlib import Path
import numpy as np
import torch

def get_app_name(filename: str) -> str:
    idx1 = filename.find(":") + 4
    idx2 = filename.find("_fetched_")
    return filename[idx1:idx2]

def is_random(filename: str) -> bool:
    return "_rand" in filename

def get_parameter(filename: str, param: str) -> float:
    suffix_idx = filename.find(".pkl")
    if suffix_idx:
        filename = filename[:suffix_idx]
    idx = filename.split("_").index(param) + 1
    return float(filename.split("_")[idx])

def get_filename_pairs(high_load_dir: str, low_load_dir: str) -> dict:
    high_load_file_names = []
    low_load_file_names = []

    files = Path(high_load_dir).glob('*.pkl')
    for f in files:
        assert "_b_" in str(f)
        high_load_file_names.append(str(f))

    files = Path(low_load_dir).glob('*.pkl')
    for f in files:
        assert "_b_" not in str(f)
        low_load_file_names.append(str(f))

    assert len(high_load_file_names) > 0
    assert len(low_load_file_names) > 0
    assert len(high_load_file_names) == len(low_load_file_names)

    # Create 1:1 relationships between high load and low load files
    pairs = {}
    for hl_file in sorted(high_load_file_names):
        hl_app = get_app_name(hl_file)
        for ll_file in low_load_file_names:
            ll_app = get_app_name(ll_file)
            if hl_app == ll_app and is_random(hl_file) == is_random(ll_file):
                assert hl_file not in pairs
                pairs[hl_file] = ll_file

    assert len(high_load_file_names) == len(pairs)

    #for key, value in pairs.items():
    #    key = key[key.find(":")+4:]
    #    value = value[value.find(":")+4:]
    #    print(f"{key} ### {value}\n")
    
    return pairs

def match_marks(sequences: list, input_mapping: dict, output_mapping: dict) -> list:
    int_to_str_input_mapping = {value: key for key, value in input_mapping.items()}
    
    for seq in sequences:
        original_marks = seq["marks"]
        str_marks = list(map(lambda int_mark: int_to_str_input_mapping[int_mark], original_marks))
        seq["marks"] = list(map(lambda str_mark: output_mapping[str_mark], str_marks))
        
        assert type(seq["marks"]) == list
        assert len(original_marks) == len(seq["marks"])
        assert type(seq["marks"][0]) == int
        assert original_marks != seq["marks"]
    
    return sequences

def inject_high_in_low_load_datasets(filename_pairs, output_dir):

    def attribute_to_matrix(sequences, attribute):
        attribute_list = []
        for seq in sequences:
            attribute_list.append(seq[attribute])
        return np.array(attribute_list)
    
    def cold_start_ratio(init_times):
        num_activations = init_times.size
        num_cold_starts = np.sum(init_times > 0)
        return num_cold_starts / num_activations

    for count, (hl_file, ll_file) in enumerate(filename_pairs.items()):
        with open(hl_file, "rb") as f:
            hl_data = torch.load(f)
        hl_sequences = hl_data["sequences"]
        hl_mapping = hl_data["mapping"]
        with open(ll_file, "rb") as f:
            ll_data = torch.load(f)
        ll_sequences = ll_data["sequences"]
        ll_mapping = ll_data["mapping"]

        if hl_mapping != ll_mapping:
            # Match marks of high load datasets with marks of low load dataset.
            hl_sequences = match_marks(hl_sequences, hl_mapping, ll_mapping)
        
        assert len(hl_sequences) == get_parameter(hl_file, "fetched")
        assert len(ll_sequences) == get_parameter(ll_file, "fetched")

        # Inject high load traces until there are 30% cold starts in the final dataset.
        threshold = 0
        ratio = 0.0
        merged_sequences = []
        while ratio < 0.3 or len(merged_sequences) < 1000:
            
            assert threshold <= len(hl_sequences)
            assert threshold <= len(ll_sequences)
            
            merged_sequences = ll_sequences[:1000-threshold] + hl_sequences[:threshold]
            ratio = cold_start_ratio(attribute_to_matrix(merged_sequences, "init_times"))
            threshold += 1
         
        ll_data["sequences"] = merged_sequences
        
        assert len(merged_sequences) == 1000
        assert len(ll_data["sequences"]) == 1000

        save_name = f"/injected_{hl_file[hl_file.rfind('/')+1:]}"
        with open(output_dir + save_name, "wb") as f:
            torch.save(ll_data, f, pickle_protocol=4)
        print(f"Created {count + 1} of {len(filename_pairs)} datasets.")

if __name__=='__main__':
    high_load_dir = "./final_batched_high_load_n_400"
    low_load_dir = "./final_low_load_n_1000"
    output_dir = "./final_high_load_n_1000"
    pairs = get_filename_pairs(high_load_dir, low_load_dir)
    inject_high_in_low_load_datasets(pairs, output_dir)