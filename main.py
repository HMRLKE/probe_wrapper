from argparse import ArgumentParser

import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, 'src')

from datagen import download_data, generate_data
from probehandler import training, inference
from statistics import get_statistics

def parse_arguments():
    # Declaration of the argument parser
    parser = ArgumentParser()
    # Organizing the different functions into subparser
    subparsers = parser.add_subparsers(dest='command', help="Commands to access different functions in the probing wrapper project.")

    # Subparser for downloading the data
    subparsers.add_parser("download", help="Download the data needed for the dataset expansion.")

    # Subparser for generating the extended data
    gen_parser = subparsers.add_parser("generate", help="Generate the extended datasets.")
    gen_parser.add_argument("--tags", type=str, default="All,All")
    gen_parser.add_argument("--random", action="store_true")

    # Subparser for generating the extended data
    probe_parser = subparsers.add_parser("probe", help="Wrapper function for the probing.")
    probe_action_group = probe_parser.add_mutually_exclusive_group()
    probe_action_group.add_argument("--train", action='store_true', help="Train probing models.")
    probe_action_group.add_argument("--infer_test", action='store_true', help="Inference on trained models (statistics file is generated automatically).")
    probe_action_group.add_argument("--infer_posthoc", action='store_true', help="Make inference using a file called 'posthoc.tsv' instead of 'test.tsv'.")
    probe_parser.add_argument("--tags", type=str, default="all,all", help="Tags indicating the input used datasets. Not mandatory, default: all,all. Format: <Language,morphtag_postag>* [muliple tags allowed, separated by '|'] eg. English,number_noun")
    probe_parser.add_argument("--data_type", type=str, default="original", help="Select input data type from: {original, random, extended}")
    
    probe_parser.add_argument("--config_path", type=str, help="Set which configuration path should used at model training: {local, default}")

    # Subparser for the statistics retrieval action
    stats_parser = subparsers.add_parser("stats", help="Generate a statistics file from the model trainings (which models are saved in /home/workdir/...)")

    return parser.parse_args()

"""
Parser arguemnts:
help
download
generate
    --tags? [default: All,All]
    --random? [bool, false if not provided]
probe
    --train / --infer_test /  --infer_posthoc
    --tags? [default: All,All]
    --random? [bool, false if not provided]
stats
"""

def main():
    parser = parse_arguments()
    if parser.command == "download":
        download_data()
    elif parser.command == "generate":
        generate_data(parser.tags, parser.random)
    elif parser.command == "probe":
        if parser.train:
            training(parser.tags, parser.data_type, parser.config_path)
        elif parser.infer_test:
            inference(parser.tags, parser.data_type, parser.config_path)
        elif parser.infer_posthoc:
            inference(parser.tags, parser.data_type, parser.config_path, True)
    elif parser.command == "stats":
        #get_statistics(parser.infer)
        get_statistics()

if __name__ == '__main__':
    main()
