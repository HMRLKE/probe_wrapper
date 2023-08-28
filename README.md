# An extended wrapper for @juditacs's probing repo

The aim of this repo is to easify the usage of the probing repository via:

- Data generating scripts with automatical download options
- Task-specific data generation for a higher-resolution analysis (and debugging)
- Tailoring the probing repository to support *indirect* probing
- Delivering quick statistics after both probing & inference sessions


# Indirect deptree probing

The ultimate goal is to perform indirect probing. Indirect in a sense that one is probing Morphological features but interprets the probes' behaviour via deptree relations when triggered with perturbations. We use both *random* and *deptree perturbations*. Random perturbations mean randomly `<MASK>`-ed input tokens, Deptree perturbations mean `<MASK>`-ed deptree neighbours relative to the *target* token

# Install

clone the repo 

    git clone https://github.com/HMRLKE/probe_wrapper/

    cd probe_wrapper
    
A dedicated virtual environment is recommended, which meets the *requirements.txt*

    conda create --name probing_data --file requirements.txt

    conda activate probing_data

Install @juditacs's probing repo: 

    cd probing
    pip install .
    cd ../

    python probing_all.py --pos_tag Noun --morph_tag Number


## Usage

Example commands:

To generate dataset for English number_noun morphological tag, with *deptree perturbations*:

    python main.py --generate --tags English,number_noun
To generate dataset for English number_noun morphological tag, with *random perturbations*:

    python main.py --generate --tags English,number_noun --random
Train the probes (diagnostic classifiers) on data with *deptree perturbations*
    python main.py --probe_train --tags English,number_noun


Tag examples:
    English,number_noun
    English,number_noun|French,case_propn
    All,All

## Structure

The structure of the output files by rows:

    [sentence] [word] [id] [morph_tag] [relative_id~node distance] [child_word [child_idx] [syntactic_tag]

Since one sentence may have more relevant pairs, some sentences are in the output file multiple times.
One-sided syntactic relations 'root' are not included. In this case, the syntactic tag is root, but there is no parent node in the syntactic tree.

## Input datasets

Currently the scripts are seeking sentences from the specified git repositorie (https://github.com/juditacs/morphology-probes) in the UD treebank (https://universaldependencies.org/), and those, that are found, are extended with the deptree relations.

More on the CoNNLL-U format: https://universaldependencies.org/format.html

# Citation
- The Git repositories to be cited https://github.com/juditacs/probing or https://github.com/juditacs/morphology-probes
- NLE paper
- UD 2.10

# TODO

- [ ] Enumerate the deptree relations by their label in the derived dataset and UD. Calculate the KL between them.
- [ ] Collect and share the relevant literature with SZTAKI HLT
- [ ] Prepare a new inference script to compare the two sets of probes in *various settings*
- [ ] Discuss the *various settings* (Target masking, Random perturbation, Deptree perturbation {All, by all labels, etc})
