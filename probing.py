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


def inference(tags: str, random: bool, posthoc: bool = False):
    # example /home/<username>/workdir/exps/morph/
    #model_accuracies = {}
    train_exp_path_pairs = train_experiment_pairs(home_workdir(), tags, random)
    rootdir = rootdir_rnd() if random else rootdir_ext()
    path_triplets = dataset_paths(rootdir, tags, True, posthoc)
    tmp_result_filename = "tmp_results.txt"
    acc_results = []
    for train_path, dev_path, test_path in path_triplets:

        exp_dir_path = train_exp_path_pairs[train_path]
        inference_command = f"python probing/src/probing/inference.py --experiment-dir {exp_dir_path} --test-file {test_path} > {tmp_result_filename}"
        print(f"Running command:\n    {inference_command}")

        try:
            subprocess.run(inference_command, shell=True)
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")

        language = test_path.split("/")[-2]
        morph, pos = test_path.split("/")[-3].split("_")
        dataset_type = "random" if random else "extended"



        conf_file = open(os.path.join(exp_dir_path, "config.yaml"), "r", encoding="utf-8")
        yaml_conf = yaml.safe_load(conf_file)
        model_name = yaml_conf["model_name"]


        # extended/random | TEST_DATA/POSTHOC | English | number_noun | bert-base-multilingual-cased | 98.7485779294653
        train_type = "random" if random else "extended"
        test_type = "posthoc" if posthoc else "test_data"
        acc = compare_results(tmp_result_filename, test_path)
        print(f"{train_type} {test_type} {language} {morph} {pos} {model_name} {acc}")

        """
        This block is for saving the data into a text file after every inference"
        meta_data_key = f"{language} {morph} {pos} {model_name}"


        #model_accuracies[]

        saved_data = read_statistics_from_file(inferece_accuracy_file_name())

        acc_pair = ("","")
        if meta_data_key in saved_data:
            acc_pair = saved_data[meta_data_key]

        if random:
            acc_pair[1] = acc
        else:
            acc_pair[0] = acc

        saved_data[meta_data_key] = acc_pair

        write_statistics_to_file(inferece_accuracy_file_name(), saved_data)
        """


def training(tags: str, random: bool):


    rootdir = rootdir_rnd() if random else rootdir_ext()
    path_triplets = dataset_paths(rootdir, tags)
    folder_num = len(path_triplets)
    folder_counter = 0

    for train_path, dev_path, test_path in path_triplets:

        try:
            train_script = "python probing/src/probing/train.py --config probing/examples/config/transformer_probing.yaml"
            train_script += f"  --train-file {train_path}  --dev-file {dev_path}"
            folder_counter+=1
            print(f"Folder num: ({folder_counter}/{folder_num})")
            print(f"Script to run:\n{train_script}")
            subprocess.run(train_script, shell=True)

            print("Train scripts executed.")

        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}\nFailed to run command: {train_script}")
