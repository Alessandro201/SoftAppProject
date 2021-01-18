from abc import ABC, abstractmethod
import re
import pandas as pd
import os


class DataTables(ABC):
    @abstractmethod
    def get_table(self):
        pass

    @abstractmethod
    def get_dimensions(self):
        pass

    @abstractmethod
    def get_labels(self):
        pass

    @abstractmethod
    def get_head(self):
        pass

    @abstractmethod
    def get_tail(self):
        pass

    @abstractmethod
    def distinct(self):
        pass

    @abstractmethod
    def evidence(self, user_input):
        pass


class Analysis(ABC):
    @abstractmethod
    def correlation_gene_disease(self):
        pass

    @abstractmethod
    def find_diseases_related_to_gene(self, user_input):
        pass

    @abstractmethod
    def find_genes_related_to_disease(self, user_input):
        pass


class GeneTable(DataTables):

    def __init__(self, table, delimiter=None):
        """
        The function creates the GeneTable with the parameter table
        :param table: tha tsv file containing the table
        :type table: pandas.DataFrame
        """

        # Finds the delimiter based on the extension
        if delimiter is None:
            extension = os.path.splitext(table)[1]
            if extension == '.tsv':
                delimiter = '\t'
            else:
                delimiter = ','

        self.__geneTable = pd.read_csv(table, delimiter=delimiter)

    def __getitem__(self, item):
        """Allows the use of slicing on the instance of the class.

        :param item: the index of the row(s) to use for slicing
        :type item: slice

        :return: The data table sliced by index(es)
        :rtype: pandas.DataFrame"""
        return self.__geneTable.iloc[item]

    def get_table(self):
        """The function returns the table

        :return: The data table
        :rtype: pandas.DataFrame"""
        return self.__geneTable

    def get_dimensions(self):
        """
        The function records the number of rows and column of dataframe

        :return: tuple with rows and columns
        :rtype: tuple
        """
        return self.__geneTable.shape[0], self.__geneTable.shape[1]

    def get_labels(self):
        """
        The function records the labels of each columns of a dataframe

        :return: list with all the column labels
        :rtype: list
        """
        return list(self.__geneTable.columns)

    def get_head(self):
        """
        The function returns the first ten rows of the dataframe

        :return: dataframe with the first 10 rows of dataframe
        :rtype: panda.DataFrame
        """
        return self.__geneTable.head()

    def get_tail(self):
        """
        The function returns the last ten rows of the dataframe

        :return: dataframe with the last 10 rows of dataframe
        :rtype: panda.DataFrame
        """
        return self.__geneTable.tail()

    def distinct(self):
        """
        It returns a dataframe of unique genes (gene_symbol, geneid) present in the dataframe

        :return: dataframe of unique genes
        :rtype: pandas.DataFrame
        """
        genes = self.__geneTable[['gene_symbol', 'geneid']]
        return genes.drop_duplicates(subset='gene_symbol').sort_values('gene_symbol')

    def evidence(self, gene):
        """Receives as input a geneID or a gene symbol and returns a dataframe with the
        sentences that relates the COVID-19 with the gene.

        :param gene: the geneID or gene symbol input
        :type gene: str
        :returns: dataframe of evidences of the gene relation to COVID-19
        :rtype: pandas.DataFrame
        """
        if type(gene) is int:
            evid = self.__geneTable[self.__geneTable['geneid'] == gene]
        else:
            evid = self.__geneTable[self.__geneTable['gene_symbol'] == gene]
        evid = evid[evid['sentence'].str.contains('>COVID-19<')]

        # keeping only these columns
        return evid[['sentence', 'nsentence', 'pmid']]


class DiseaseTable(DataTables):
    def __init__(self, table, delimiter=None):
        """
        The function creates the GeneTable with the parameter table
        :param table: tha tsv file containing the table
        :type table: pandas.DataFrame
        """

        # Finds the delimiter based on the extension
        if delimiter is None:
            extension = os.path.splitext(table)[1]
            if extension == '.tsv':
                delimiter = '\t'
            else:
                delimiter = ','

        self.__diseaseTable = pd.read_csv(table, delimiter=delimiter)

    def __getitem__(self, item):
        """
        Allows the use of slicing on the instance of the class.

        :param item: the index of the row(s) to use for slicing
        :type item: slice

        :return: The data table sliced by index(es)
        :rtype: pandas.DataFrame
        """
        return self.__diseaseTable.iloc[item]

    def get_table(self):
        """
        The function returns the table
        
        :return: The data table
        :rtype: pandas.DataFrame
        """
        return self.__diseaseTable

    def get_dimensions(self):
        """
        The function records the number of rows and column of dataframe

        :return: tuple with rows and columns
        :rtype: tuple
        """
        return self.__diseaseTable.shape[0], self.__diseaseTable.shape[1]

    def get_labels(self):
        """
        The function records the labels of each columns of a dataframe

        :return: list with all the column labels
        :rtype: list
        """
        return list(self.__diseaseTable.columns)

    def get_head(self):
        """
        The function returns the first ten rows of the dataframe

        :return: dataframe with the first 10 rows of dataframe
        :rtype: panda.DataFrame
        """
        return self.__diseaseTable.head()

    def get_tail(self):
        """
        The function returns the last ten rows of the dataframe

        :return: dataframe with the last 10 rows of dataframe
        :rtype: panda.DataFrame
        """
        return self.__diseaseTable.tail()

    def distinct(self):
        """
        It returns a dataframe of unique diseases (disease_name, diseaseid) present in the dataframe.
        Every word of the diseases is capitalized to allow the sorting algorithm to sort them correctly
        instead of putting the lowercase at the end.

        :return: dataframe with unique diseases
        :rtype: pandas.DataFrame
        """

        disease = self.__diseaseTable[['disease_name', 'diseaseid']]
        disease['disease_name'] = disease['disease_name'].str.title()
        return disease.drop_duplicates(subset='disease_name').sort_values('disease_name')

    def evidence(self, disease):
        """Receives as input a diseaseID or a disease name and returns a dataframe with the
        sentences that relates the COVID-19 with the disease.

        :param disease: the diseaseID or disease name input
        :type disease: str
        :returns: dataframe of evidences of the disease relation to COVID-19
        :rtype: pandas.DataFrame
        """

        if re.match("C\d{7,}",disease):
            evid = self.__diseaseTable[self.__diseaseTable['diseaseid'] == disease]
        else:
            evid = self.__diseaseTable[self.__diseaseTable['disease_name'] == disease]
        evid = evid[evid['sentence'].str.contains('>COVID-19<')]

        # keeping only these columns
        evid = evid[['sentence', 'nsentence', 'pmid']]

        return evid


class Testing(Analysis):
    def __init__(self, geneTable, diseaseTable, geneDelimiter=None, diseaseDelimiter=None):

        # Finds the delimiter of the gene dataset based on the extension
        if geneDelimiter is None:
            extension = os.path.splitext(geneTable)[1]
            if extension == '.tsv':
                geneDelimiter = '\t'
            else:
                geneDelimiter = ','

        # Finds the delimiter of the disease dataset based on the extension
        if diseaseDelimiter is None:
            extension = os.path.splitext(diseaseTable)[1]
            if extension == '.tsv':
                diseaseDelimiter = '\t'
            else:
                diseaseDelimiter = ','

        self.__diseaseTable = pd.read_csv(diseaseTable, delimiter=geneDelimiter)
        self.__geneTable = pd.read_csv(geneTable, delimiter=diseaseDelimiter)

    def correlation_gene_disease(self):
        """
        The function returns a database with the correlation between genes and diseases sorted by the most frequent.

        Steps:
        1) Merging of the two dataframes:
            The merge occurs on pmid and nsentence (instead of sentence) because they are interchangeable as
            in the same publication the nth sentence ("nsentence") will always be "sentence".
            But in this way the program runs faster because it has to check only some numbers instead of whole strings
            to know which rows to merge.
        2) Dropping duplicates:
            The same concept goes for "drop_duplicates". When the function drop_duplicates() search for duplicates
            of the subset, with "nsentence" it avoids checking for whole strings as it would instead do with sentences.
            "geneid" and "diseaseid" follow the same concept and are used instead of "gene_symbol" and "disease_name".
        3) Keeping only the columns needed, thus one for gene and one for disease
        4) Count occurrences of the couple gene-disease and create a new dataframe with a couple as row and their
            occurrences in a new column; labels: ['gene_symbol', 'disease_name', 'occurrences'].


        :returns: a DataFrame containing the correlations between genes and diseases and their count
        :rtype: pandas.DataFrame
        """

        # Step 1)
        df = pd.DataFrame.merge(self.__diseaseTable, self.__geneTable, how='inner', on=['pmid', 'nsentence'])

        # Step 2)
        df.drop_duplicates(subset=['pmid', 'geneid', 'diseaseid', 'nsentence'], inplace=True)

        # Step 3)
        df = df[['gene_symbol', 'disease_name']]

        # Step 4)
        df = df.value_counts().to_frame('occurrences').reset_index()
        return df

    def find_diseases_related_to_gene(self, gene):

        """
        The function receive as input a geneID or a gene symbol and then returns a dataframe with the
        diseases related to the gene.
        
        Steps:
        1) Merging of the two dataframes:
            The merge occurs on pmid and nsentence (instead of sentence) because they are interchangeable as
            in the same publication the nth sentence ("nsentence") will always be "sentence". 
            But in this way the program runs faster because it has to check only some numbers instead of whole strings
            to know which rows to merge.
        2) Dropping duplicates:
            The same concept goes for "drop_duplicates". When the function drop_duplicates() search for duplicates 
            of the subset, with "nsentence" it avoids checking for whole strings as it would instead do with sentences.
            "geneid" and "diseaseid" follow the same concept and are used instead of "gene_symbol" and "disease_name".
        3) Performing search: 
            It first tries to convert gene (string) given as input to an int. If it can, then it means it's a genid and only
            only the rows whose value in the columns 'geneid' will be "gene" will be kept. Otherwise it means "gene"
            given as input is a "gene_symbol" and only the rows whose value in the columns 'gene_symbol' will be 
            "gene" given as input will be kept.  
        4) Keeping only the columns needed
        5) Using title() on all diseases:
            Some diseases are all lowercase and when sorted will be placed at the end of the table as the majority 
            have the first letter uppercase. With title() all words of the diseases are now capitalized, 
            and sort_values() will do what we want.
        6) Dropping duplicates and sorting
            
            
        :param gene: the geneid or gene_symbol input
        :type gene: str or int
        :returns: a dataframe with the diseases related to gene
        :rtype: pandas.DataFrame
        """

        # step 1)
        df = pd.DataFrame.merge(self.__diseaseTable, self.__geneTable, how='inner', on=['pmid', 'nsentence'])

        # step 2)
        df.drop_duplicates(subset=['pmid', 'geneid', 'diseaseid', 'nsentence'], inplace=True)

        # step 3)
        try:
            gene = int(gene)
            df = df[df['geneid'] == gene]
        except ValueError:
            df = df[df['gene_symbol'] == gene]

        # step 4)
        df = df[['disease_name', 'diseaseid']]

        # step 5)
        df['disease_name'] = df['disease_name'].str.title()

        # step 6)
        df = df.drop_duplicates(subset='diseaseid').sort_values('disease_name')

        return df

    def find_genes_related_to_disease(self, disease):
        """
        The function receive as input a diseaseid or a disease_name and then returns a dataframe with the
        diseases related to the gene.

        Steps:
        1) Merging of the two dataframes:
            The merge occurs on pmid and nsentence (instead of sentence) because they are interchangeable as
            in the same publication the nth sentence ("nsentence") will always be "sentence".
            But in this way the program runs faster because it has to check only some numbers instead of whole strings
            to know which rows to merge.
        2) Dropping duplicates:
            The same concept goes for "drop_duplicates". When the function drop_duplicates() search for duplicates
            of the subset, with "nsentence" it avoids checking for whole strings as it would instead do with sentences.
            "geneid" and "diseaseid" follow the same concept and are used instead of "gene_symbol" and "disease_name".
        3) Performing search:
            Check if the disease matches a pattern which consist of the first element as a 'C' and then at least
            7 numbers until the end of the string. If it matches, then it means it's a "diseaseid" and only
            the rows whose value in the columns "diseaseid" are "disease" will be kept. Otherwise it means "disease"
            given as input is a "disease_name" and only the rows whose value in the columns 'disease_name' are the
            "gene" given as input will be kept.
        4) Keeping only the columns needed.
        6) Dropping duplicates and sorting


        :param disease: the geneid or gene_symbol input
        :type disease: str
        :returns: a dataframe with the diseases related to gene
        :rtype: pandas.DataFrame
        """

        # Step 1)
        df = pd.DataFrame.merge(self.__diseaseTable, self.__geneTable, how='inner',
                                on=['pmid', 'nsentence'])

        # Step 2)
        df.drop_duplicates(subset=['pmid', 'geneid', 'diseaseid', 'nsentence'], inplace=True)

        # Step 3)
        if re.match('^C\d{7,}$', disease) is not None:
            # First select all rows which match the diseaseid, then take its disease_name from the first row
            df = df[df['diseaseid'] == disease]
        else:
            df = df[df['disease_name'] == disease]

        # Step 4)
        df = df[['gene_symbol', 'geneid']]

        # Step 5)
        df = df.drop_duplicates(subset='geneid').sort_values('gene_symbol')

        return df


if __name__ == '__main__':
    # test
    gene = GeneTable('gene_evidences.tsv')
    disease = DiseaseTable('disease_evidences.tsv')
    test = Testing('disease_evidences.tsv', 'gene_evidences.tsv')

    # GeneTable
    # print(gene.get_dimensions())
    # print(gene.get_labels())
    # print(gene.get_heads())
    # print(gene.get_tails())
    # print(gene.distinct())
    # print(gene.evidence(183))
    # print(gene.evidence('AGT'))

    # diseaseTable
    # print(disease.get_dimensions())
    # print(disease.get_labels())
    # print(disease.get_heads())
    # print(disease.get_tails())
    # print(disease.distinct())
    # print(disease.evidence('C0000727'))
    # print(disease.evidence('Abdomen, Acute'))
    # print(disease.evidence('C000656484'))
    # print(disease.evidence('SARS-CoV-2'))

    # testing
    # print(test.correlation_gene_disease())
    # print(test.find_diseases_related_to_gene(59272))
    # print(test.find_diseases_related_to_gene('ACE2'))
    # (test.find_genes_related_to_disease('C0009450'))
    # print(test.find_genes_related_to_disease('Communicable Diseases'))

    test.correlation_gene_disease()
