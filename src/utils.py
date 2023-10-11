import csv
import requests
import zipfile
import os
import tarfile
import re
import collections
import yaml
from unidecode import unidecode

from git import Repo
from pathlib import Path




def clean_string(str):
    """
    Remove non-alphabetic and non-numeric characters from the string, transformed into lowercase.

    Args:
        str (string): The input strign to simplify.

    Returns:
        The simplified version of the input string.
    """
    cleaned_string = re.sub('[^a-zA-Z0-9]', '', unidecode(str)) # Keep only alphabetic and numeric chars
    cleaned_string = cleaned_string.lower() # Convert to lowercase

    return cleaned_string


""" Functions for downloading data. """

def download_ud_treebank(base_url: str, ud_treebank_name: str):
    """
    Download the UD treebank to the current directory.

    Args:
        base_url (str): The url to download the file from.

        ud_treebank_name (str) The name of the UD treebank file.

    """
    filename = ud_treebank_name+".tgz"
    url = base_url + "/" + file_name
    print(f"Downloadng UD treebank from: {url}")
    response = requests.get(url)
    with open(file_name, "wb") as file:
        file.write(response.content)

    print("Download complete.")


def extract_ud_treebank(ud_treebank_name: str):
    """
    Extract the the UD treebank from the current directory.

    Parameters
    ----------
    ud_treebank_name (str): The name of the UD treebank file.
    """
    print(f"Extracting UD treebank: {ud_treebank_name}")
    try:
        with tarfile.open(ud_treebank_name+".tgz", "r:gz") as file:
            for member in file.getmembers():
                print(member.name)
                if member.name.startswith("ud-treebanks") and member.name.endswith(".conllu"):
                    file.extract(member)
        print("Extraction complete.")
    except tarfile.ReadError:
        print("Error: Invalid compressed file. Please ensure the downloaded file is a valid TAR archive.")
    except FileNotFoundError:
        print("Error: The downloaded file '" + ud_treebank_name + ".tgz' is missing.")


def download_github_repo(git_url, repo_dir):
    """
    Download a repository from github.
    The target directory has the same name as the repo on Github.

    Args:
        git_url (str): The url on Github without the repository name
        repo_dir (str): The name of the repository

    """
    Repo.clone_from(git_url+repo_dir, repo_dir)
    print(f"Downloaded data for probing from: {git_url}.")


def is_ud_treebank_downloaded(ud_treebank_name):
    return os.path.exists(ud_treebank_name)


def is_git_repo_downloaded(repo_name):
    return os.path.exists(repo_name)


# Download the latest UD treebank if it's not already downloaded for the requested language codes.
def download_ud_treebank_if_needed(base_url, ud_treebank_name):
    if not is_ud_treebank_downloaded(ud_treebank_name):
        download_ud_treebank(base_url, ud_treebank_name)
        extract_ud_treebank(ud_treebank_name)
    else:
        print(f"Treebank '{ud_treebank_name}' already downlaoded.")

# Download git repository if it's not already downloaded.
def download_git_repo_if_needed(git_url, repo_dir):
    if not is_git_repo_downloaded(repo_dir):
        download_github_repo(git_url, repo_dir)
    else:
        print(f"Git repo '{repo_dir}' already downlaoded.")


# For the AcsJudit data

def leaf_dirs(rootdir):
    """
    Return directory paths that contain no directories under the given path.
    Args:
        rootdir (str): directory path where the search starts.
    """
    dir_paths = []
    for subroot, dirs, files in os.walk(rootdir):
        if not dirs:
            dir_paths.append(subroot)
    return dir_paths

    

def filtered_path(directories, tags, back_offset):
    tags = tags.lower()
    lang_tag_pairs = [filter_elem.split(",") for filter_elem in list(tags.split("|"))]
    
    filtered_dir_list = []
    lang_allowed_tags = collections.defaultdict(set)
    lang_allowed_tags["all"] = set() #To prevent checking tag in non-existing 'language'
    for lang, morph_pos in lang_tag_pairs:
        lang_allowed_tags[lang].add(morph_pos)
    
    
    if not lang_allowed_tags["all"] is None and "all" in lang_allowed_tags["all"]:
        return directories

    for _dir in directories:
        #print(_dir)
        cur_lang = _dir.split(os.sep)[-back_offset].lower()
        cur_morph_pos = _dir.split(os.sep)[-(back_offset+1)].lower()
        
        #cur_morph_tag, cur_pos_tag =  cur_morph_pos.split('_')
        #print(lang)
        #print(cur_morph_tag)
        #print(cur_pos_tag)
        
        language_pass = bool('all' in lang_allowed_tags or cur_lang in lang_allowed_tags)
        tags_pass = bool('all' in lang_allowed_tags[cur_lang] or cur_morph_pos in lang_allowed_tags[cur_lang])
        
        #if cur_lang == "english":
        #    print(_dir)
        #print(cur_lang, language_pass, cur_morph_pos, tags_pass)
        
        if language_pass and tags_pass:
            filtered_dir_list.append(_dir)

        #if cur_morph_pos in lang_allowed_tags["all"]:
        #    filtered_dir_list.append(_dir)
        #elif (lang in lang_allowed_tags) and (morph_pos in lang_allowed_tags[lang] or "all" in lang_allowed_tags[lang]):
        #    filtered_dir_list.append(_dir)
    
    
    return filtered_dir_list


def filter_dirs(directories, tags):
    return filtered_path(directories, tags, 1)

def filter_files(paths, tags):
    return filtered_path(paths, tags, 2)

"""
Functions to get paths used throughout the project.
They are collected here to avoid different pathing conflicts all over the project.
"""

def ud_treebank_source_url():
    return "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-5150"

def ud_treebank_name():
    return "ud-treebanks-v2.12"

def git_repo_url():
    return "https://github.com/juditacs/"

def git_repo_name_probe():
    return "probing"

def git_repo_name_probing_dataset():
    return "morphology_probes/data"

def rootdir_rnd_ext():
    return "datasets/random"
    #return "output_rnd"

def rootdir_dep_tree_ext():
    return "datasets/dep_tree"
    #return "output_ext"

def rootdir_orig():
    return "morphology_probes/data"


def inferece_accuracy_file_name():
    return "inference_accuracy.txt"

def home_workdir():
    home = str(Path.home())
    workdir = os.path.join(home, "workdir")
    return workdir

def data_rootdir(data_type: str):
    if data_type == "original":
        rootdir = rootdir_orig()
    elif data_type == "random":
        rootdir = rootdir_rnd_ext()
    elif data_type == "extended":
        rootdir = rootdir_dep_tree_ext()
    else:
        raise Exception(f"Unknown input data type provided: {data_type}")
    return rootdir


"""
If different models are going to be needed, this function could return paths to different
configuration files, each ponting to an other directory of files (trained on orginal / random ext. / dep. tree ext data).
"""
def model_config_path(config):
    
    DEFAULT_CONFIG_PATH = "probing/examples/config/transformer_probing.yaml"
    LOCAL_COONFIG_PATH = "custom_transformer_probing.yaml"
    
    if config == "default":
        config_path = DEFAULT_CONFIG_PATH
    elif config == "local":
        config_path = LOCAL_COONFIG_PATH
        create_dir_if_needed("models")
    return config_path


def tags_from_path(path):
    # path '/media/mzpx/HDD/Work/language_data_processing/output_ext/morphology_probes/data/number_noun/English/train.tsv'
    # return 'number_noun/English/train.tsv'
    tag_postfix = '/'.join(path.split('/')[-3:])
    return tag_postfix


def dataset_paths(rootdir, tags, absolute=False, posthoc=False):
    # Return triplets of dataset file paths matching tags.
    directories = leaf_dirs(rootdir)
    if tags:
        dir_paths = filter_dirs(directories, tags)
    datasets = []
    for _dir in dir_paths:
        train_path = os.path.join(_dir, "train.tsv")
        if not os.path.isfile(train_path):
            train_path = None
        dev_path = os.path.join(_dir, "dev.tsv")
        if not os.path.isfile(dev_path):
            dev_path = None
        test_file_name = "test.tsv" if not posthoc else "posthoc.tsv"
        test_path = os.path.join(_dir, test_file_name)
        if not os.path.isfile(test_path):
            test_path = None
        triplet = (train_path, dev_path, test_path)
        if absolute:
            triplet = tuple(map(os.path.abspath, triplet))
        datasets.append(triplet)
    return datasets


def extract_experiment_dir(config_path):
    """
    Get the experiemnt directory from the yaml configuration file.
    config_path - The path of the config file
    """
    with open(config_path, "r", encoding="utf-8") as conf_file:
        yaml_conf = yaml.safe_load(conf_file)
        experiment_dir = yaml_conf["experiment_dir"]
    return experiment_dir


def load_model_paths(rootdir, tags):
    """
    Load the paths of saved models, corresponding to the given tags
    Return dict: [train file path] -> model path
    """
    print(rootdir, tags) #OK
    path_dirs = {}
    for _dir in leaf_dirs(rootdir):

        res_path = os.path.join(_dir, "result.yaml")
        conf_path = os.path.join(_dir, "config.yaml")
        model_path = os.path.join(_dir, "model")

        if os.path.isfile(res_path) and \
           os.path.isfile(conf_path) and \
           os.path.isfile(model_path):

            creation_time = int(os.stat(model_path).st_ctime)
            with open(res_path, "r", encoding="utf-8") as result_file, open(conf_path, "r", encoding="utf-8") as conf_file:
                yaml_conf = yaml.safe_load(conf_file)
                train_path =  tags_from_path(yaml_conf["train_file"])

                #if output_dir in train_path:
                print(train_path)

                if not train_path in path_dirs:

                    path_dirs[train_path] = (_dir, creation_time)
                elif path_dirs[train_path][1] < creation_time:

                    path_dirs[train_path] = (_dir, creation_time)


    valid_train_paths = filter_files(list(path_dirs.keys()), tags)

    res = {p:path_dirs[p][0] for p in valid_train_paths}

    
    return res



def group_paths_on_language(dataset_triplets):
    #Returns dict with the lanugage as the key , and a list of morph_pos tags with the dataset path triplets
    extended_data = collections.defaultdict(list)
    for path_triplet in dataset_triplets:
        train_path, dev_path, test_path = path_triplet
        _dir = None
        if train_path:
            _dir = os.path.dirname(train_path)
        elif dev_path:
            _dir = os.path.dirname(dev_path)
        elif test_path:
            _dir = os.path.dirname(test_path)

        lang = _dir.split(os.sep)[-1]
        morph_pos = _dir.split(os.sep)[-2]
        extended_data[lang].append((morph_pos, path_triplet))

    return extended_data


def conllu_file_path_loader(language):
    treebank_name = ud_treebank_name()
    if not os.path.isdir(treebank_name):
        raise Exception(f"UD treebank directory not found at: {treebank_name}")
    print(f"Start reading the UD treebank from: {treebank_name}")

    langname = language.lower()
    # Fix the syntax difference of the names of swedish datasets.
    langname = langname.replace("bokmal", "bokmaal")
    for root, dirs, files in os.walk(treebank_name):
        for dirname in dirs:

            if clean_string(langname) in clean_string(dirname):
                cur_dir  = os.path.join(root, dirname)
                for lang_root, lang_dirs, lang_files in os.walk(cur_dir):
                    for cur_lang_file in lang_files:
                        file_path = os.path.join(lang_root, cur_lang_file)
                        yield file_path


"""
File manipualtion functions.
"""
def create_dir_if_needed(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Directory created: '{output_dir}'")


def find_all_languages():
    # Should work only for morphology_probing atm
    # TODO finsih
    found_languages = set()

    for root, dirs, files in os.walk("morphology_probes/data"):
        for dirname in dirs:
            cur_dir  = os.path.join(root, dirname)
            for lang_root, lang_dirs, lang_files in os.walk(cur_dir):
                for lang_dir_name in lang_dirs:
                    found_languages.add(lang_dir_name)

    return list(found_languages)

def find_all_tag_pairs():
    base_path = f"morphology_probes/data"
    tag_pairs = [ tuple(os.path.basename(f.path).split("_")) for f in os.scandir(base_path) if f.is_dir() ]

    return tag_pairs

def read_statistics_from_file(path):
    """
    Read the data from a TSV file (with 'tab' separators) of this format:
    language	morph_tag	pos_tag	model_name	tacc_original	tacc_extendedt	acc_extended
    Args:
        path (str): The path of the tsv file with the statistics
    Returns:
        A dictionary with the statistics:
            key (str) ~ language morph_tag pos_tag model_name
            value (tuple/pair) ~ (random_data_accuracy, extended_data_accuracy)
    """
    stats_dict = {}
    if not os.path.exists(path):
        return stats_dict
    with open(path) as stats_file:
        csv_reader = csv.reader(stats_file, delimiter='\t')
        for idx, row in enumerate(csv_reader):
            if idx == 0:
                pass
            else:
                key = "\t".join(row[:4])
                val = list(row[4:])
                stats_dict[key] = val
    return stats_dict


def write_statistics_to_file(path, stats_dict):
        """
        Write the statistics data from 'stats_dict' dictionary to a file:
        language	morph_tag	pos_tag	model_name	tacc_original	tacc_extendedt	acc_extended
        Args:
            path (str): The path of the target tsv file with the statistics
            stats_dict (dict): The statistics data in this format ((with 'tab' separators)):
                key (str) ~ language morph_tag pos_tag model_name
                value (tuple/pair) ~ (random_data_accuracy, extended_data_accuracy)
        """
        with open(path, 'w', newline='') as stats_file:
            tsv_writer = csv.writer(stats_file, delimiter='\t')

            # Write the header row
            header = ["language", "morph_tag", "pos_tag", "model_name", "acc_original", "acc_extended", "acc_random"]
            tsv_writer.writerow(header)

            # Write the data rows
            for key, (acc_orig, acc_ext, acc_rnd) in stats_dict.items():
                language, morph_tag, pos_tag, model_name = key.split()  # Unpack key parts
                row = [language, morph_tag, pos_tag, model_name, acc_orig, acc_ext, acc_rnd]
                tsv_writer.writerow(row)
