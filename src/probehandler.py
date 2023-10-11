import os
import subprocess
import shlex
import yaml

from argparse import ArgumentParser

from utils import *



def get_paths(orig = False):
    if orig:
        rootdir = 'morphology_probes/data/'
    else:
        rootdir = 'output/morphology_probes/data/'
    print(f"Geting data paths from: {rootdir}")
    path_pairs = []
    for subroot, dirs, files in [x for x in os.walk(rootdir)]:
        if not dirs:
            train_name = "train.tsv"
            dev_name = "dev.tsv"
            if train_name in files and dev_name in files:
                train_path = os.path.join(subroot, train_name)
                dev_path = os.path.join(subroot, dev_name)
                path_pairs.append((train_path, dev_path))

    return path_pairs


def compare_results(result_path, test_path):
    #TODO open the files and compute the accuracy of the inference
    result_file = open(result_path, "r")
    test_file = open(test_path, "r")

    resultdata = result_file.readlines()
    testdata = test_file.readlines()
    correct_counter = 0
    for i, line in enumerate(resultdata):
        res_line = resultdata[i]
        test_line = testdata[i]
        res_parts = res_line.split("\t")
        test_parts = test_line.split("\t")
        #print(i)
        if res_parts[3].strip() == test_parts[3].strip():
            correct_counter+=1
    if len(resultdata) > 0:
        return correct_counter/len(resultdata)*100
    else:
        None


def inference(tags: str, data_type: str, config = "default", posthoc: bool = False):
    # example /home/<username>/workdir/exps/morph/
    #model_accuracies = {}
    #print(tags, data_type, config)
    rootdir = data_rootdir(data_type)
    config_path = model_config_path(config)
    experiment_dir = extract_experiment_dir(config_path)

    train_exp_path_pairs = load_model_paths(experiment_dir, tags)
    
    path_triplets = dataset_paths(rootdir, tags, True, posthoc)
    tmp_result_filename = "tmp_results.txt"
    acc_results = []

    for idx, triplet in enumerate(path_triplets):
        train_path, dev_path, test_path = triplet

        train_path_tags = tags_from_path(train_path)
        
        if train_path_tags in train_exp_path_pairs:
            try:
                exp_dir_path = train_exp_path_pairs[train_path_tags]
                inference_command = f"python probing/src/probing/inference.py --experiment-dir {exp_dir_path} --test-file {test_path} > {tmp_result_filename}"
                print(f"{idx+1}/{len(path_triplets)} Inference. Running command:\n    {inference_command}")
                
                subprocess.run(inference_command, shell=True)

            except Exception as err:
                print(f"Unexpected {err=}, {type(err)=}")
                pass

            language = test_path.split("/")[-2]
            morph, pos = test_path.split("/")[-3].split("_")

            conf_file = open(os.path.join(exp_dir_path, "config.yaml"), "r", encoding="utf-8")
            yaml_conf = yaml.safe_load(conf_file)
            model_name = yaml_conf["model_name"]

            # extended/random | TEST_DATA/POSTHOC | English | number_noun | bert-base-multilingual-cased | 98.7485779294653
            test_type = "posthoc" if posthoc else "test_data"
            acc = compare_results(tmp_result_filename, test_path)
            #print(f"{data_type} {test_type} {language} {morph} {pos} {model_name} {acc}")
            
            #This block is for saving the data into a text file after every inference
            meta_data_key = "\t".join([language, morph, pos, model_name])

            saved_data = read_statistics_from_file(inferece_accuracy_file_name())
            #print(saved_data)
            acc_pair = ["","",""]
            #print(f"<{meta_data_key}>")
            if meta_data_key in saved_data:
                acc_pair = saved_data[meta_data_key]
                #print(f"found: <{acc_pair}>")
                
            if data_type == "original":
                acc_pair[0] = acc
            elif data_type == "extended":
                acc_pair[1] = acc
            elif data_type == "random":
                acc_pair[2] = acc
            else:
                raise Exception(f"Unknown input data type provided: {data_type}")

            saved_data[meta_data_key] = acc_pair

            write_statistics_to_file(inferece_accuracy_file_name(), saved_data)
        


def training(tags: str, data_type: str, config = "default"):
    
    rootdir = data_rootdir(data_type)
    config_path = model_config_path(config)
        
    path_triplets = dataset_paths(rootdir, tags)
    folder_num = len(path_triplets)
    folder_counter = 1

    for triplet in path_triplets:

        train_path, dev_path, test_path = tuple(map(os.path.abspath, triplet))
        
        try:
            train_command = f"python probing/src/probing/train.py --config {config_path}"
            train_command += f"  --train-file {train_path}  --dev-file {dev_path}"
            print(f"{folder_counter}/{folder_num} Training. Running command:")
            print(f"    {train_command}")
            subprocess.run(train_command, shell=True)
            print("Train scripts executed.")
            folder_counter+=1

        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}\nFailed to run command: {train_command}")
