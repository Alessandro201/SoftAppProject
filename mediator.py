from functions import *
from settings import *
import pandas as pd
import os

# Compute the path to the databases
gene_evidences_path = os.path.join(TABLES_LOCATION, GENE_TABLE_NAME)
disease_evidences_path = os.path.join(TABLES_LOCATION, DISEASE_TABLE_NAME)

# Instantiate the classes from functions.py
geneTable = GeneTable(gene_evidences_path, DELIMITER)
diseaseTable = DiseaseTable(disease_evidences_path, DELIMITER)
test = Testing(gene_evidences_path, disease_evidences_path, DELIMITER)


def getInfo():
    """
    Returns two dictionaries containing informations on the two datasets

    :return two dictionaries
    :rtype dict
    """

    gene_data = {'nrows': geneTable.get_dimensions()[0],
                 'ncols': geneTable.get_dimensions()[1],
                 'labels': geneTable.get_labels(),
                 'head': geneTable.get_head().values.tolist(),
                 'tail': geneTable.get_tail().values.tolist()}

    disease_data = {'nrows': diseaseTable.get_dimensions()[0],
                    'ncols': diseaseTable.get_dimensions()[1],
                    'labels': diseaseTable.get_labels(),
                    'head': diseaseTable.get_head().values.tolist(),
                    'tail': diseaseTable.get_tail().values.tolist()}

    return gene_data, disease_data


def getDiseaseTableList(start=0, end=None, step=1):
    return diseaseTable[start:end:step].values.tolist()


def getGeneTableList(start=0, end=None, step=1):
    return geneTable[start:end:step].values.tolist()


def getDistinctGenes():
    table = geneTable.distinct()

    data = {'labels': table.columns.values.tolist(),
            'rows': table.values.tolist(),
            'lenght': table.shape[0]}

    return data


def getDistinctDiseases():
    table = diseaseTable.distinct()

    data = {'labels': table.columns.values.tolist(),
            'rows': table.values.tolist(),
            'lenght': table.shape[0]}

    return data


def getGeneEvidences(gene):
    """Receives as input a geneid or a gene_symbol and returns a list with the
    sentences that relates the COVID-19 with the gene.

    :param gene: the geneID or gene symbol input
    :type gene: str
    :returns: list of sentences related with COVID-19 about the gene input
    :rtype: list
    """
    try:
        gene = int(gene)
    except ValueError:
        gene = str(gene)

    table = geneTable.evidence(gene)

    data = {'labels': table.columns.values.tolist(),
            'rows': table.values.tolist(),
            'lenght': table.shape[0]}

    return data


def getDiseaseEvidences(disease):
    table = diseaseTable.evidence(disease)

    data = {'labels': table.columns.values.tolist(),
            'rows': table.values.tolist(),
            'lenght': table.shape[0]}

    return data


def getCorrelation(num_rows, min_occurrence):
    """Returns a list of the correlations between genes and diseases sorted by the highest number of occurrences.

    It allows to customize the number of correlations and the minimum occurrence.

    Occurrence has priority over the number of rows.
    """

    corr = test.correlation_gene_disease()

    data = {'labels': corr.columns.values.tolist(),
            'rows': corr.values.tolist(),
            'lenght': corr.shape[0],
            'min_occurrences': min_occurrence}

    if min_occurrence == 0:
        if num_rows == 0:
            return data

        # in case "rows" is higher than the number of correlations it returns all of them
        try:
            data['rows'] = corr.iloc[:num_rows].values.tolist()
            data['lenght'] = len(data['rows'])
            return data
        except IndexError:
            return data

    else:
        # if a row has an occurrence higher than the minimum the user wants then it gets added to new_corr, which
        # at the end is returned
        corr = corr.loc[corr['occurrences'] >= min_occurrence]

        if num_rows < len(corr) and num_rows != 0:
            data['rows'] = corr.iloc[:num_rows].values.tolist()
            data['lenght'] = len(data['rows'])
            return data
        else:
            data['rows'] = corr.values.tolist()
            data['lenght'] = len(data['rows'])
            return data


def getDiseasesRelatedToGene(gene):
    table = test.find_diseases_related_to_gene(gene)

    data = {'labels': table.columns.values.tolist(),
            'rows': table.values.tolist(),
            'lenght': table.shape[0]}

    return data


def getGenesRelatedToDisease(disease):
    table = test.find_genes_related_to_disease(disease)

    data = {'labels': table.columns.values.tolist(),
            'rows': table.values.tolist(),
            'lenght': table.shape[0]}

    return data
