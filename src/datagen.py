import csv
import requests
import zipfile
import os
import tarfile
import re

from argparse import ArgumentParser
from unidecode import unidecode
from random import randrange
from git import Repo
from utils import *



def process_ud_sentence(sentence_data):
    """
    Extract data from the lines conaining the UD data of sentences.
    More on UD (universal dependencies) CONLLU file format:
    https://universaldependencies.org/format.html
    Example for the sentence 'A mentésben nem állhat be technikai szünet':
    1	A	a	DET	_	Definite=Def|PronType=Art	2	det	_	_
    2	mentésben	mentés	NOUN	_	Case=Ine|Number=Sing	4	obl	_	_
    3	nem	nem	ADV	_	PronType=Neg	4	advmod	_	_
    4	állhat	áll	VERB	_	Definite=Ind|Mood=Pot|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act	0	root	_	_
    5	be	be	ADV	_	Degree=Pos	4	compound:preverb	_	_
    6	technikai	technikai	ADJ	_	Case=Nom|Degree=Pos|Number=Sing	7	amod:att	_	_
    7	szünet	szünet	NOUN	_	Case=Nom|Number=Sing	4	nsubj	_	SpaceAfter=No
    8	.	.	PUNCT	_	_	4	punct	_	_
    Args:
        lines (list of strings): The lines of the sentence data. See example above.

    Returns:
        pair:
            -the sentence
            -sentence data [word, w. index, morph. tag(s), parent word (in dependency tree), parent word, p. word index, relationship in the tree]
    """
    #lines = list(filter(None, list(sentence_data.split("\n"))))
    lines = list(sentence_data.split("\n"))

    comment_lines = [l for l in lines if l[0] == "#"]
    data_lines = [l for l in lines if not l[0] == "#"]
    separated_lines = [l.split("\t") for l in data_lines]


    #starts with # text =
    orig_sentnece_text = list([l for l in lines if l.startswith("# text =")][0].split("# text = "))[1]
    sentence_parts = []

    data_lists = []
    for line_elems in separated_lines:
        if line_elems[0].isdigit():
            w2_idx = int(line_elems[0])-1
            sentence_parts.append(line_elems[1])
        else:
            continue
        #word_idx, line_elems = [l.split("\t") for l in data_lines]
        try:
            if line_elems[6] == "_" or line_elems[7] == "root":
                continue
        except e:
            print(line_elems)
            print(e)
            exit()
        w1_idx = int(line_elems[6])-1 #
        w1 = separated_lines[w1_idx][1]


        w2 = line_elems[1]
        morph_tags = line_elems[5]
        rela = line_elems[7]
        pos_tag = line_elems[3]

        data_lists.append([w2, w2_idx, pos_tag, morph_tags, w1, w1_idx, rela])

    joined_sentence_tokens = " ".join(sentence_parts)
    #print(orig_sentnece_text, data_lists, "\n\n")
    return joined_sentence_tokens, orig_sentnece_text, data_lists


def process_morpho_file(file_path):
    """
    The format of the data for the morpholoical probes:
        Tolles ( Fisch - ) Restaurant direkt am Luitjensee gelegen .	Tolles	0	Neut

    The keys to the dict are the simplifed sentences, the values are the data from the rows in a list
    """
    sentence_dict = {}

    with open(file_path, "r", encoding="utf-8") as sentence_data_file:
        for line in sentence_data_file:
            sentence_data = [s.strip() for s in line.split("\t")]
            raw_sentence = clean_string(sentence_data[0])
            sentence_dict[raw_sentence] = sentence_data

    return sentence_dict



def extract_UD_sentences_from_all_files(file_paths):
    """
    Args:
        file_paths (list of strings): the paths to the .conllu files containing the data
    Returns:
        dict:   containing the inforamtion for the processed data.
                The dict key is the given character-simplified sentence (see the 'clean_string' function).

    This function reads all the files and processes the sentences in them.
    The processed data is saved in files in the same folder structure as they are read from,
    with one difference: the root fodler is called 'UD_processed'

    The sentences are in the following format in the UD treebank files, being separated with empty lines:

        # sent_id = train-5
        # text = A verseny több szinten folyik.
        1	A	a	DET	_	Definite=Def|PronType=Art	2	det	_	_
        2	verseny	verseny	NOUN	_	Case=Nom|Number=Sing	5	nsubj	_	_
        3	több	több	DET	_	Definite=Ind|PronType=Ind	4	det	_	_
        4	szinten	szint	NOUN	_	Case=Sup|Number=Sing	5	obl	_	_
        5	folyik	folyik	VERB	_	Definite=Ind|Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act	0	root	_	SpaceAfter=No
        6	.	.	PUNCT	_	_	5	punct	_	_
    """
    sentence_data_dict = {}
    for cur_path in file_paths:
        #if not os.path.isfile(cur_path):
        #    print(f"UD treebank data file not found at: {cur_path}")
        #print(f"    Collecting sentence data from UD treebank dataset at: {cur_path}")
        #with open(cur_path, "r", encoding="unicode_escape") as conllu_file:
        with open(cur_path, "r") as conllu_file:
            content = conllu_file.read()
            senence_data_paragraphs = list(filter(None, content.split("\n\n")))

            for sentence_paragrpah in senence_data_paragraphs:
                """
                sentence, data_lists = process_ud_sentence(sentence_paragrpah)
                raw_sentence = clean_string(sentence)
                sentence_data_dict[raw_sentence] = [sentence, data_lists]
                """
                try:
                    # joined_sentence_tokens, orig_sentnece_text, data_lists
                    token_sentnece, orig_sentnece, data_lists = process_ud_sentence(sentence_paragrpah)
                    raw_sentence = clean_string(orig_sentnece)
                    #toekn_sentnece ~ sentence rejoined from the conllu tokens
                    sentence_data_dict[raw_sentence] = [token_sentnece, orig_sentnece, data_lists]
                except Exception as e:
                    print(sentence_paragrpah)    # the exception type
                    print(e.args)     # arguments stored in .args
                    print(e)          # __str__ allows args to be printed directly,

    return sentence_data_dict


def get_morph_tag(selected_morph_tag, morph_tags):

    tags = morph_tags.split("|")
    for tag_pair in tags:
        #print(tag_pair)
        if not "=" in tag_pair:
            continue
        tag_type, tag_value = tag_pair.split("=")
        if tag_type.lower() ==selected_morph_tag.lower():
            return tag_value
    return None


def process_sentence_data(ud_data_dict: dict, morph_path: str, allowed_tags: set, pos_tag: str, morph_tag: str):
    """
    Args:
        ud_data_dict:
        morph_path:
        allowed_tags: the tags that are present in the training data (if they aren't, the model won't recognize them in the test data)
        pos_tag:
        morph_tag:
    Returns:
        collected_sentence_data
        collected_tags
        match_rate
    """
    morph_data_dict = process_morpho_file(morph_path)

    match_count = 0 # Counter for the sentences that were found in the UD CoNLL-U dataset
    collected_sentence_data = []
    collected_tags = set()


    #Uncomment for testing the search of same sentences in the CoNLLU and morphology datasets!
    """
    search_key = "goodafternoonsara"

    ud_conllu_matches  = [(key, value) for key, value in ud_data_dict.items() if search_key in key]
    morphology_matches  = [(key, value) for key, value in morph_data_dict.items() if search_key in key]
    print(ud_conllu_matches)
    print(morphology_matches)
    if ud_conllu_matches and morphology_matches:
        print("   ### UD data dict")
        ud_str = ud_conllu_matches[0][1][0]
        print(f"<{ud_str}>")
        print("   ### Morphology data dict")
        mor_str = morphology_matches[0][1][0]
        print(f"<{mor_str}>")
        print(morphology_matches[0][0] in ud_data_dict)
        print(ud_conllu_matches[0][0] in morph_data_dict)
    """


    for raw_sentence, morph_sentence_data in morph_data_dict.items():

        if raw_sentence in ud_data_dict:

            valid_match = 0 # Add only if was inlcuded in the result data at least once
            sentence, orig_ud_sentence, ud_sentence_data_lists = ud_data_dict[raw_sentence]

            for data_list in ud_sentence_data_lists:
                orig_sentence = morph_sentence_data[0]
                w_parent, w_parent_idx, found_pos_tag, found_morph_tags, w_child, w_child_idx, rela = data_list

                result_tag = get_morph_tag(morph_tag, found_morph_tags)
                # Only the relevant pos and morpg elements incuded
                if  (not result_tag ==  None and
                    (not allowed_tags or (result_tag in allowed_tags)) and
                    (pos_tag.lower() == found_pos_tag.lower())):


                    # Put the relevenat data in the correct order

                    cur_data_row = [sentence, w_parent, w_parent_idx, result_tag, w_child_idx-w_parent_idx, w_child, w_child_idx, rela]
                    collected_tags.add(result_tag)
                    #cur_data_row = [sentence, w_parent, w_parent_idx, result_tag, w_child_idx-w_parent_idx]
                    valid_match = 1
                    collected_sentence_data.append(cur_data_row)

            #if valid_match == 0:
            #    print(f"<{raw_sentence}> {morph_sentence_data} {result_tag}")
            match_count += valid_match

    match_rate = 0
    if not collected_sentence_data:
        print(f"    --No matching sentence found.")
    else:
        sentence_count = len(morph_data_dict)
        match_rate = match_count/sentence_count*100
        print(f"    --Expanded {match_count}/{sentence_count} sentneces (Match rate: {match_rate:.2f}%) from: {morph_path}")
    return collected_sentence_data, collected_tags, match_rate


def write_sentence_data(output_file: str, processed_data):
    with open(output_file, "w") as f:
        for row_data in processed_data:
            csv_row = '\t'.join(map(str, row_data))
            f.write(csv_row+'\n')




def generate_dataset(ud_data_dict, morph_data_path_triplet, pos_tag, morph_tag, random=False):
    """
    Args:
        morph_langname:     the language name (it is needed, since in the morph. data they are in folders named according the language). Example: 'English'
        selected_morph_tag: example: 'Tense'
        morph_data_paths:   the paths of the files that conatain the morphological probe data.
        ud_data_paths:      the paths of the files that conatain the UD conllu data.
    Returns:
        dict:   containing the inforamtion for the processed data.
                The dict key is the given character-simplified sentence (see the 'clean_string' function).
    Create the desired datasets in a folder called 'processed_output' writing the data into relevant .tsv files.
    Example output file names:
    """


    #morph_data_dict = extract_morph_sentences_for_language(morph_dir_path, morph_langname)
    #dict of dicts: 'dev', 'train', 'test' dicts

    #morph_data_dicts = extract_morph_sentences_keep_datasets(morph_data_paths)

    #TODO ket keys from train!!!
    #use only training keys from conllu
    traindata_tags = None
    for morph_path in morph_data_path_triplet:
        #extended data
        ext_output_file = os.path.join(rootdir_dep_tree_ext(), morph_path)
        rnd_output_file = os.path.join(rootdir_rnd_ext(), morph_path)
    
        
        #print(morph_data_path_triplet)
        #print(ext_output_dir)
        #print(rnd_output_dir)
        # process sentences in files
        # ud_data_dict: dict, morph_path: string, pos_tag:string, morph_tag: string
        #print(f"    Collecting data from: {morph_path}")

        data_to_write, collected_tags, match_rate = process_sentence_data(ud_data_dict, morph_path, traindata_tags, pos_tag, morph_tag)
        #The training path should be the first one among the path triplet.
        if morph_path.split(os.sep)[-1] == "train.tsv":
            traindata_tags = collected_tags
        if data_to_write and match_rate > 5:
            #print(f"    Writing data to: {output_file}")
            
            if random:
                target_file = rnd_output_file
                
                data_to_write = [sentence_data[:4]+[randrange(len(sentence_data[0].split())),'_','_','_'] for sentence_data in data_to_write]
            else:
                target_file = ext_output_file
            
            target_dir = os.path.dirname(target_file)
            create_dir_if_needed(target_dir)
            # Create output directory if does not exist
            print(f"        Writing data to file: {target_file}")
            write_sentence_data(target_file, data_to_write)
        else:
            print("    WARNING! No data retrieved.")


#TODO return only existing combinations?
def find_tag_combinations(morph_pos_tag, language):
    if morph_pos_tag == "All":
        base_path = f"morphology_probes/data"
        morph_pos_list = [ tuple(os.path.basename(f.path).split("_")) for f in os.scandir(base_path) if f.is_dir() ]
    else:
        morph_pos_list = [tuple(morph_pos_tag.split("_"))]

    if language == "All":
        found_languages = set()
        for root, dirs, files in os.walk("morphology_probes/data"):
            for dirname in dirs:
                cur_dir  = os.path.join(root, dirname)
                for lang_root, lang_dirs, lang_files in os.walk(cur_dir):
                    for lang_dir_name in lang_dirs:
                        found_languages.add(lang_dir_name)
        language_list = list(found_languages)
    else:
        language_list = [language]

    return [([(mt,pt) for mt,pt in morph_pos_list], lang) for lang in language_list]


def download_data():
    # Download the source datasets and the probing project. No further action taken.
    base_url = ud_treebank_source_url()
    treebank_name = ud_treebank_name()
    download_ud_treebank_if_needed(base_url, treebank_name)
    git_url = git_repo_url()
    download_git_repo_if_needed(git_url, git_repo_name_probe())
    download_git_repo_if_needed(git_url, git_repo_name_probing_dataset())


def generate_data(tags: str, random = False):
    # Deafault behaviour: download only on explicit command, see:
    #download_data()

    dataset_path_triplets = dataset_paths(git_repo_name_probing_dataset(), tags)
    dataset_dict  = group_paths_on_language(dataset_path_triplets)
    counter = 1
    dataset_count = sum(map(len, dataset_dict.values()))

    for lang, datalist in dataset_dict.items():
        

        ud_data_paths = list(conllu_file_path_loader(lang))
        ud_data_dict  = extract_UD_sentences_from_all_files(ud_data_paths)

        for morph_pos, morph_data_paths in datalist:
            morph_tag, pos_tag = list(morph_pos.split("_"))
            print(f"\n {counter}/{dataset_count}. Language: {lang}; Morph: {morph_tag}; PoS: {pos_tag}")
            counter+=1

            #morph_data_paths = morpho_file_path_loader(morph_repo_name, pos_tag, morph_tag, lang)

            generate_dataset(ud_data_dict, morph_data_paths, pos_tag, morph_tag, random)
