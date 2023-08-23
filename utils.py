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
    for subroot, dirs, files in [x for x in os.walk(rootdir)]:
        if not dirs:
            dir_paths.append(subroot)
    return dir_paths


def filtered_path(directories, tags, back_offset):
    lang_tag_pairs = [filter_elem.split(",") for filter_elem in list(tags.split("|"))]
    tags = tags.lower()
    filtered_dirs = []
    lang_allowed_tags = collections.defaultdict(set)
    lang_allowed_tags["all"] = set() #To prevent checking tag in non-existing 'language'
    for lang, morph_pos in lang_tag_pairs:
        lang_allowed_tags[lang].add(morph_pos)

    for k, v in lang_allowed_tags.items():
        print(f"{k} > {v}")

    if lang_allowed_tags["all"] and "all" in lang_allowed_tags["all"]:
        return directories

    for dir in directories:

        lang = dir.split(os.sep)[-back_offset]
        morph_pos = dir.split(os.sep)[-(back_offset+1)]

        if morph_pos in lang_allowed_tags["all"]:
            filtered_dirs.append(dir)
        elif lang in lang_allowed_tags and (morph_pos in lang_allowed_tags[lang] or "all" in lang_allowed_tags[lang]):
            filtered_dirs.append(dir)

    return filtered_dirs

def filtered_dirs(directories, tags):
    return filtered_path(directories, tags, 1)

def filtered_files(paths, tags):
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

def rootdir_rnd():
    return "output_rnd"

def rootdir_ext():
    return "output_ext"

def inferece_accuracy_file_name():
    return "inference_accuracy.txt"

def home_workdir():
    home = str(Path.home())
    workdir = os.path.join(home, "workdir")
    return workdir


def dataset_paths(rootdir, tags, absolute=False, posthoc=False):
    # Return triplets of dataset file paths matcing tags.
    directories = leaf_dirs(rootdir)
    if tags:
        dir_paths = filtered_dirs(directories, tags)
    datasets = []
    for dir in dir_paths:
        train_path = os.path.join(dir, "train.tsv")
        if not os.path.isfile(train_path):
            train_path = None
        dev_path = os.path.join(dir, "dev.tsv")
        if not os.path.isfile(dev_path):
            dev_path = None
        test_file_name = "test.tsv" if not posthoc else "posthoc.tsv"
        test_path = os.path.join(dir, test_file_name)
        if not os.path.isfile(test_path):
            test_path = None
        triplet = (train_path, dev_path, test_path)
        if absolute:
            triplet = tuple(map(os.path.abspath, triplet))
        datasets.append(triplet)
    return datasets


def train_experiment_pairs(rootdir, tags, random):
    # rootdir ~ /home/<username>/workdir/exps/morph/
    path_dirs = {}
    output_dir = rootdir_rnd() if random else rootdir_ext()
    for dir in leaf_dirs(rootdir):

        res_path = os.path.join(dir, "result.yaml")
        conf_path = os.path.join(dir, "config.yaml")
        model_path = os.path.join(dir, "model")

        if os.path.isfile(res_path) and \
           os.path.isfile(conf_path) and \
           os.path.isfile(model_path):

            creation_time = os.stat(model_path).st_ctime
            with open(res_path, "r", encoding="utf-8") as result_file, open(conf_path, "r", encoding="utf-8") as conf_file:
                yaml_conf = yaml.safe_load(conf_file)
                train_path =  yaml_conf["train_file"]
                #Paths of experiemnts created on the type of data: extended/random
                if output_dir in train_path:
                    if not train_path in path_dirs:
                        path_dirs[train_path] = (dir, creation_time)
                    elif path_dirs[train_path][0] < creation_time:
                        path_dirs[train_path] = (dir, creation_time)

    for k, v in path_dirs.items():
        print(f"{k}: {v}")
    valid_train_paths = filtered_files(path_dirs.keys(), tags)
    print("#####",path_dirs.keys())

    return {p:path_dirs[p][0] for p in valid_train_paths}



def group_paths_on_language(dataset_triplets):
    #Returns dict with the lanugage as the key , and a list of morph_pos tags with the dataset path triplets
    extended_data = collections.defaultdict(list)
    for path_triplet in dataset_triplets:
        train_path, dev_path, test_path = path_triplet
        dir = None
        if train_path:
            dir = os.path.dirname(train_path)
        elif dev_path:
            dir = os.path.dirname(dev_path)
        elif test_path:
            dir = os.path.dirname(test_path)

        lang = dir.split(os.sep)[-1]
        morph_pos = dir.split(os.sep)[-2]
        extended_data[lang].append((morph_pos, path_triplet))

    return extended_data

"""
def probing_path_loader(tags=None, orig=False):
    dataset_triplets = morpho_dataset_paths(tags, orig)
    prefix = "output_rnd/" if orig else "output/"

    probing_paths = list((prefix+t[0],prefix+t[1],prefix+t[2]) for t in dataset_triplets)
    return probing_paths
"""

"""
def morpho_file_path_loader(repo_name, pos_tag=None, morph_tag=None, language=None):
    result_paths = []
    if repo_name == "probing":
        if not language == None:
            raise Exception("A language should not be specified for extraction from 'probing'.")
        if not pos_tag == None:
            raise Exception("A pos-tag should not be specified for extraction from 'probing'.")
        if not morph_tag == None:
            raise Exception("A morphological-tag should not be specified for extraction from 'probing'.")
        data_dir_path = "probing/examples/data/morphology_probing_with_sample_level_masking/english_verb_tense"
        for cur_root, cur_dirs, cur_files in os.walk(data_dir_path):
            for filename in cur_files:
                cur_file_path  = os.path.join(cur_root, filename)
                result_paths.append(cur_file_path)
    elif repo_name == "morphology_probes":
        if language == None:
            raise Exception("No language was specified for extraction from 'morphology-probes'.")
        for root, dirs, files in os.walk("morphology_probes/data"):
            for dir_name in dirs:
        #for dir_name in [d for d in os.listdir("morphology_probes/data")]:
                if not (pos_tag.lower() in dir_name):
                    continue
                if not (morph_tag.lower() in dir_name):
                    continue
                language_dir = os.path.join(root, dir_name)

                for lang_root, lang_dirs, _ in os.walk(language_dir):
                    for cur_lang_dir in lang_dirs:

                        if cur_lang_dir.lower() == language.lower():
                            lang_dir_path  = os.path.join(lang_root, cur_lang_dir)

                            for data_root, _, data_files in os.walk(lang_dir_path):
                                for file_name in data_files:
                                    datafile_path  = os.path.join(data_root, file_name)
                                    result_paths.append(datafile_path)
                                break
                    break
            break

    return result_paths
"""

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
    Read the data format (with 'tab' separators) of ths format:
    language	morph_tag	pos_tag	model_name	acc_new	acc_orig
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
    with open(path, "r") as stat_file:
        for l in stat_files.readlines():
            elems = l.split("\t")
            key = "\t".join(elems[:4])
            val = tuple(elems[4:])
            stats_dict[key] = val
    return stats_dict

def write_statistics_to_file(path, stats_dict):
        """
        Write the statistics data from 'stats_dict' dictionary to a file:
        language	morph_tag	pos_tag	model_name	acc_new	acc_orig
        Args:
            path (str): The path of the target tsv file with the statistics
            stats_dict (dict): The statistics data in this format ((with 'tab' separators)):
                key (str) ~ language morph_tag pos_tag model_name
                value (tuple/pair) ~ (random_data_accuracy, extended_data_accuracy)
        """
        with open(path, 'w') as file:
            # Write the header row
            header = "language\tmorph_tag\tpos_tag\tmodel_name\tacc_extended\tacc_random\n"
            file.write(header)

            # Write the data rows
            for key, (acc_ext, acc_rnd) in stats_dict.items():
                language, morph_tag, pos_tag, model_name = key.split()  # Unpack key parts
                row = f"{language}\t{morph_tag}\t{pos_tag}\t{model_name}\t{acc_ext}\t{acc_rnd}\n"
                file.write(row)
