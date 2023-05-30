import sys

import pickle as pkl
import numpy as np

import harpspec

help_info = '''Usage: harpspec <command> <command-arguments>...
CLI interface to the harpspec python library.

Commands:

    collate (fits-file|directory) <dest-file>
        
        Formats either a single .fits file or all .fits files in a directory    x
        into a dataset with the names and spectra of the target(s) and
        serializes the resulting dataset to the file specified by dest-file.
        
        Examples: harpspec collate fits/ dataset.pkl
                  harpspec collate ADP.2014-09-16T11:03:59.140.fits spectrum.pkl
        
    match <unlabeled-dataset> <label-file> <dest-file>
        
        Assigns labels to the targets in unlabeled-dataset using the labels from
        label-file. Any remaining unlabeled targets are discarded. The resulting
        dataset is serialized and saved to dest-file.
        
        Example:  harpspec match dataset.pkl labels.csv labeled-dataset.pkl
        
    process <params-file> <dataset-file> <dest-file>
        
        Processes the spectra in dataset-file for use in training or inferring.
        The params-file stores information regarding how the spectra should be
        processed. The resultinf processed spectra are serialized as a dataset
        and saved to dest-file.
        
        Example:  harpspec process params.pkl labeled-dataset.pkl
                      training-data.pkl
        
    train <dataset-file> <model-file>
        
        Trains a harpspec model using the spectra in dataset-file and saves the 
        resulting model to model-file.
        
        Example:  harpspec train training-data.pkl model.pkl
        
    infer <dataset-file> <model-file> <dest-file>
        
        Assigns labels to the spectra in dataset-file using the model contained
        in model-file and saves the resulting labeled dataset to dest-file.
        
        Example:  harpspec infer dataset.pkl model.pkl inferred-dataset.pkl
        
    help
        
        Displays this help text.
        
        Example:  harpspec help
'''

def usage():
    print(help_info)

def main():
    
    args = sys.argv
    
    if len(args) < 2:
        usage()
        return
    
    if args[1] == 'collate':
        if not len(args) == 4:
            usage()
            return
        collate(*args[2:])
    elif args[1] == 'match':
        if not len(args) == 5:
            usage()
            return
        match(*args[2:])
    elif args[1] == 'process':
        if not len(args) == 5:
            usage()
            return
        process(*args[2:])
    elif args[1] == 'train':
        if not len(args) == 4:
            usage()
            return
        train(*args[2:])
    elif args[1] == 'infer':
        if not len(args) == 5:
            usage()
            return
        infer(*args[2:])
    elif args[1] == 'help':
        usage()
    else:
        print("Unknown command '%s', see 'harpspec help' for usage information" %args[1])
        
def collate(target, dest):

    dataset = harpspec.collate(target)
    
    with open(dest, 'wb') as f:
        pkl.dump(dataset, f)
        
def match(dataset_file, labels_file, dest):

    with open(dataset_file, 'rb') as f:
        dataset = pkl.load(f)
        
    labels, label_names = harpspec.load_labels(labels_file)
    dataset_labeled = harpspec.match(dataset, labels)
    dataset_labeled.label_names = label_names
    
    with open(dest, 'wb') as f:
        pkl.dump(dataset_labeled, f)

def process(plp_file, dataset_file, dest):
    
    with open(plp_file, 'rb') as f:
        plp = pkl.load(f)
        
    with open(dataset_file, 'rb') as f:
        dataset = pkl.load(f)
    
    dataset_processed = harpspec.process(dataset, plp)
    
    with open(dest, 'wb') as f:
        pkl.dump(dataset_processed, f)

def train(dataset_file, dest):
    
    with open(dataset_file, 'rb') as f:
        dataset = pkl.load(f)
    
    model = harpspec.train(dataset)
    
    with open(dest, 'wb') as f:
        pkl.dump(model, f)
        
def infer(dataset_file, model_file, dest):

    with open(dataset_file, 'rb') as f:
        dataset = pkl.load(f)
    
    with open(model_file, 'rb') as f:
        model = pkl.load(f)
        
    dataset_labeled = harpspec.infer(dataset, model)
    
    with open(dest, 'wb') as f:
        pkl.dump(dataset_labeled, f)