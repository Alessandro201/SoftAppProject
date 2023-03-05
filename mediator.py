from functions import *
from settings import *
import pandas as pd
import os
import json

# Compute the path to the databases and the documentation
GENE_TABLE_PATH = os.path.join(os.getcwd(), GENE_TABLE_PATH)
DISEASE_TABLE_PATH = os.path.join(os.getcwd(), DISEASE_TABLE_PATH)
DOCS_PATH = os.path.join(os.getcwd(), DOCS_PATH)


# Instantiate the classes from functions.py
geneTable = GeneTable(GENE_TABLE_PATH)
diseaseTable = DiseaseTable(DISEASE_TABLE_PATH)
test = Testing(GENE_TABLE_PATH, DISEASE_TABLE_PATH)


def getInfoGenes():
    """Return a dictionary containing information of geneTable

    :return: Info about geneTable
    :rtype: dict"""

    gene_data = {'nrows': geneTable.get_dimensions()[0],
                 'ncols': geneTable.get_dimensions()[1],
                 'labels': geneTable.get_labels(),
                 'head': geneTable.get_head().values.tolist(),
                 'tail': geneTable.get_tail().values.tolist()}

    return gene_data


def getInfoDiseases():
    """Return a dictionary containing information of diseaseTable

    :return Info about diseaseTable
    :rtype dict"""

    disease_data = {'nrows': diseaseTable.get_dimensions()[0],
                    'ncols': diseaseTable.get_dimensions()[1],
                    'labels': diseaseTable.get_labels(),
                    'head': diseaseTable.get_head().values.tolist(),
                    'tail': diseaseTable.get_tail().values.tolist()}

    return disease_data


def getInfo():
    """
    Returns two dictionaries containing information on the two datasets

    :return two dictionaries
    :rtype tuple(dict, dict)
    """

    return getInfoGenes(), getInfoDiseases()


def getDiseaseTableList(start=0, end=None, step=1):
    """
    Return a list containing the rows of Disease Table from start index to end index. It works like as slicing.

    :rtype: list
    """
    return diseaseTable[start:end:step].values.tolist()


def getGeneTableList(start=0, end=None, step=1):
    """
    Return a list containing the rows of Gene Table from start index to end index. It works like as slicing.

    :rtype: list
    """
    return geneTable[start:end:step].values.tolist()


def getDistinctGenes():
    table = geneTable.distinct()

    data = {'labels': table.columns.values.tolist(),
            'rows': table.values.tolist(),
            'length': table.shape[0]}

    return data


def getDistinctDiseases():
    table = diseaseTable.distinct()

    data = {'labels': table.columns.values.tolist(),
            'rows': table.values.tolist(),
            'length': table.shape[0]}

    return data


def getGeneEvidences(gene):
    """Receives as input a geneid or a gene_symbol and returns a dictionary with the
    sentences that relates the COVID-19 with the gene.

    :param gene: the geneID or gene symbol input
    :type gene: str

    :returns: dictionary of sentences related with COVID-19 about the gene input
    :rtype: dict
    """
    try:
        gene = int(gene)
    except ValueError:
        gene = str(gene)

    table = geneTable.evidence(gene)

    data = {'labels': table.columns.values.tolist(),
            'rows': table.values.tolist(),
            'length': table.shape[0]}

    return data


def getDiseaseEvidences(disease):
    """Receives as input a geneid or a gene_symbol and returns a dictionary with the
    sentences that relates the COVID-19 with the gene.

    :param disease: the geneID or gene symbol input
    :type disease: str

    :returns: dictionary of sentences related with COVID-19 about the gene input
    :rtype: dict
    """
    table = diseaseTable.evidence(disease)

    data = {'labels': table.columns.values.tolist(),
            'rows': table.values.tolist(),
            'length': table.shape[0]}

    return data


def getCorrelation(num_rows, min_occurrences):
    """Returns a dict with the correlations between genes and diseases sorted by the highest number of occurrences.

    It allows to customize the number of correlations and the minimum occurrence.

    :return: A dictionary, the key for the rows is 'rows'
    :rtype: dict
    """

    # get the dataframe of the correlations
    corr = test.correlation_gene_disease()

    # create a dictionary containing the information and the rows of the dataframe
    data = {'labels': corr.columns.values.tolist(),
            'rows': corr.values.tolist(),
            'length': corr.shape[0],
            'min_occurrences': min_occurrences}

    # if min_occurrences is at its default value (0) it means that the user hasn't input any min_occurrences
    if min_occurrences == 0:
        # if num_rows == 0 it means the user wants to see all the correlations, thus returns all the data
        if num_rows == 0:
            return data

        # in case "rows" is higher than the number of correlations it will throw IndexError, and it will return all data
        try:
            # Select only the first [num_rows] rows from the dataframe
            data['rows'] = corr.iloc[:num_rows].values.tolist()
            data['length'] = len(data['rows'])
            return data

        except IndexError:
            return data

    else:
        # If min_occurrences is not zero the user wants only the correlations which occur more than min_occurrences.

        # Select only the rows with occurrences higher than min_occurrences
        corr = corr.loc[corr['occurrences'] >= min_occurrences]

        # if the user wants to see at most [num_rows] of rows, but we have more correlation, then are returned only
        # the num of correlations the user has selected. If num_rows == 0 it means the user has proactively chosen
        # that he wants to see all correlations
        if num_rows < len(corr) and num_rows != 0:
            data['rows'] = corr.iloc[:num_rows].values.tolist()
            data['length'] = len(data['rows'])
            return data
        else:
            data['rows'] = corr.values.tolist()
            data['length'] = len(data['rows'])
            return data


def getDiseasesRelatedToGene(gene):
    table = test.find_diseases_related_to_gene(gene)

    data = {'labels': table.columns.values.tolist(),
            'rows': table.values.tolist(),
            'length': table.shape[0]}

    return data


def getGenesRelatedToDisease(disease):
    table = test.find_genes_related_to_disease(disease)

    data = {'labels': table.columns.values.tolist(),
            'rows': table.values.tolist(),
            'length': table.shape[0]}

    return data


def getDocumentation(path, name_file=''):
    """Reads the documentation from .json files and return a dict.
    You can either input the whole path, or the folder and the name of the file.

    :param path: The path to the file or the path to the folder
    :type path: str
    :param name_file: The name of the file. It can be either with extension or without.
    It's optional if you input the path to the file in "path"
    :type name_file: str

    :return: The documentation
    :rtype: dict
    """

    if path.endswith('.json'):
        docs_path = path
    else:
        if name_file.endswith('.json'):
            docs_path = os.path.join(path, name_file)
        else:
            docs_path = os.path.join(path, name_file + '.json')

    with open(docs_path) as f:
        docs = json.load(f)

    return docs
