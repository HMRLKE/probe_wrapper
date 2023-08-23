# UD CoNLL-U morphology data processing



The goal of the project is to provide scripts that work with probing data.produce datasets for probings tasks,
The main script is called 'datagen_script.py' which utilizes different auxiliary functions from 'datagen_utils.py'.
These two scripts should be in the same folder.


## Functionality
    generate extended data
        a/ using conllu data
        b/ applying random indices
    run probing on the generated data
    get the statistics from the data-set

    TODO - extend if there is more

## Usage
It is recommended to utilize the functionality of the tmux command, since some operations may take a longer time.
With tmux the user can detach the session where the long processes are running.

Example commands:

    python main.py --generate --tags English,number_noun
    python main.py --generate --tags English,number_noun --random
    python main.py --probe_train --tags English,number_noun
    python main.py --probe_train --tags English,number_noun --random


Tag examples:
    English,number_noun
    English,number_noun|French,case_propn
    All,All

If tmux does not exist yet:

    tmux new -s probing_test

    tmux switch -t probing_test

If the scripts are not downloaded yet:

    git clone https://github.com/HMRLKE/UD_morph_data_processing.git

    cd UD_morph_data_processing

    conda create --name probing_data --file requirements.txt

    conda activate probing_data

    python datagen_script.py --language All --repo morphology_probes --pos_tag Noun --morph_tag Number

    cd probing
    pip install .
    cd ../

    python probing_all.py --pos_tag Noun --morph_tag Number


## Structure

The structure of the output files by rows:

    [sentence] [word] [id] [morph_tag] [relative_id~node distance] [child_word [child_idx] [syntactic_tag]

Since one sentence may have more relevant pairs, some sentences are in the output file multiple times.
One-sided syntactic relations 'root' are not included. In this case, the syntactic tag is root, but there is no parent node in the syntactic tree.

## Input datasets

The scripts find sentences from the specified git repositories, search for them in the CoNNLL-U files, and those, that are found, are extended with the selected tags:

More on the CoNNLL-U format: https://universaldependencies.org/format.html

The Git repositories used are: https://github.com/juditacs/probing or https://github.com/juditacs/morphology-probes
