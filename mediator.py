from functions import *
from settings import *
import pandas as pd
import os

# Compute the path to the databases
gene_evidences_path = os.path.join(TABLES_LOCATION, GENE_TABLE_NAME)
disease_evidences_path = os.path.join(TABLES_LOCATION, DISEASE_TABLE_NAME)

# Instantiate the classes from functions.py
geneTable = GeneTable(gene_evidences_path)
diseaseTable = DiseaseTable(disease_evidences_path)
test = Testing(gene_evidences_path, disease_evidences_path)


def getInfo():
    geneRows, geneCols = geneTable.get_dimensions()
    geneLabels = geneTable.get_labels()
    geneHead = geneTable.get_head().values.tolist()
    geneTail = geneTable.get_tail().values.tolist()

    diseaseRows, diseaseCols = diseaseTable.get_dimensions()
    diseaseLabels = diseaseTable.get_labels()
    diseaseHead = diseaseTable.get_head().values.tolist()
    diseaseTail = diseaseTable.get_tail().values.tolist()

    return ((geneRows, geneCols, geneLabels, geneHead, geneTail),
            (diseaseRows, diseaseCols, diseaseLabels, diseaseHead, diseaseTail))


def getDiseaseTableList(start=0, end=None, step=1):
    return diseaseTable[start:end:step].values.tolist()


def getGeneTableList(start=0, end=None, step=1):
    return geneTable[start:end:step].values.tolist()


def getDistinctGenes():
    return geneTable.distinct().values.tolist()


def getDistinctDiseases():
    table = diseaseTable.distinct()
    return table.columns.values.tolist(), table.values.tolist()


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

    return geneTable.evidence(gene).values.tolist()


def getDiseaseEvidences(disease):
    return diseaseTable.evidence(disease).values.tolist()


def getCorrelation(num_rows, min_occurrence):
    """Returns a list of the correlations between genes and diseases sorted by the highest number of occurrences.

    It allows to customize the number of correlations and the minimum occurrence.

    Occurrence has priority over the number of rows.
    """

    corr = test.correlation_gene_disease()

    if min_occurrence == 0:
        if num_rows == 0:
            return corr.values.tolist()

        # in case "rows" is higher than the number of correlations it returns all of them
        try:
            return corr.iloc[:num_rows].values.tolist()
        except IndexError:
            return corr.values.tolist()

    else:
        # if a row has an occurrence higher than the minimum the user wants then it gets added to new_corr, which
        # at the end is returned
        corr = corr.loc[corr['occurrences'] >= min_occurrence]

        if num_rows < len(corr) and num_rows != 0:
            return corr.iloc[:num_rows].values.tolist()
        else:
            return corr.values.tolist()


def getDiseasesRelatedToGene(gene):
    return test.find_diseases_related_to_gene(gene).values.tolist()


def getGenesRelatedToDisease(disease):
    return test.find_genes_related_to_disease(disease).values.tolist()
