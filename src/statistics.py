import os
import subprocess
#import shlex
import yaml

from utils import *
from datagen import *


def get_inference_stats():
    with open(inferece_accuracy_file_name(), "r") as accuracy_file:
        for l in accuracy_file.readlines():
            f"{dataset_type} {language} {morph} {pos} {model_name} {acc}"
            print(">>>", l)

def get_dev_stats():
    rootdir = home_workdir()
    output_file = open("diff_result_summary.txt", "w+", encoding="utf-8")

    orig_data = {}
    new_data = {}

    for dir in leaf_dirs(rootdir):
        res_path = os.path.join(dir, "result.yaml")
        conf_path = os.path.join(dir, "config.yaml")

        if os.path.isfile(res_path) and os.path.isfile(conf_path):
            creation_time = os.stat(dir).st_ctime
            with open(res_path, "r", encoding="utf-8") as result_file, open(conf_path, "r", encoding="utf-8") as conf_file:
                try:
                    yaml_res = yaml.safe_load(result_file)
                    yaml_conf = yaml.safe_load(conf_file)

                    data = {}
                    data["dev_file"] = yaml_conf["dev_file"]
                    data["train_file"] = yaml_conf["train_file"]

                    dev_path = yaml_conf["dev_file"]
                    path_parts = dev_path.split("/")
                    #print(yaml_res["dev_acc"])

                    if yaml_res["dev_acc"]:
                        try:

                            language = path_parts[-2]
                            pos, morph_tag = list(path_parts[-3].split("_"))
                            model_name = yaml_conf["model_name"]
                            accuracy  = yaml_res["dev_acc"][-1]

                            #res_line = f"{pos} {morph_tag} {language} {modell_name} {accuracy}"
                            #print(f"{language}\t{pos}\t{morph_tag}\t{accuracy}")
                            id_string = f"{language}\t{pos}\t{morph_tag}"
                            #print(id_string, creation_time, type(creation_time))
                            if "output/morphology_probes" in dev_path:
                                if not id_string in new_data or new_data[id_string][2] < creation_time:
                                    new_data[id_string] = [model_name, accuracy, creation_time]
                            else:
                                if not id_string in orig_data or orig_data[id_string][2] < creation_time:
                                    orig_data[id_string] = [model_name, accuracy, creation_time]
                            #print(res_line)

                            #output_file.write(res_line+'\n')
                        except Error as e:
                            print(e)



                except yaml.YAMLError as exc:
                    print(exc)

    # k ~ f"{language}\t{pos}\t{morph_tag}"
    # v ~ model_name, accuracy, creation_time
    for k,v in new_data.items():
        if k in orig_data.keys():
            cur_line = k+f"\t{v[0]}\t{v[1]}\t{orig_data[k][1]}"
            print(cur_line)
            output_file.write(cur_line+"\n")
    print("### only in new data:")
    for k,v in new_data.items():
        if k not in orig_data.keys():
            cur_line = k+f"\t{v[0]}\t{v[1]}\t"
            print(cur_line)
            output_file.write(cur_line+"\n")
    print("### only in orig data:")
    for k,v in orig_data.items():
        if k not in new_data.keys():
            cur_line = k+f"\t{v[0]}\t\t{v[1]}"
            print(cur_line)
            output_file.write(cur_line+"\n")

    output_file.close()


def get_statistics():
    #get_inference_stats()
    get_dev_stats()
    """
    if inference:
        get_inference_stats()
    else:
        get_dev_stats()
    """
