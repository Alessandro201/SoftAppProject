from abc import ABC, abstractmethod

import pandas as pd


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

    def __init__(self, table):
        """
        The function creates the GeneTable with the parameter table
        :param table: tha tsv file containing the table
        :type table: pandas.DataFrame
        """
        self.__geneTable = pd.read_csv(table, delimiter='\t')

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
    def __init__(self, table):
        """
        The function creates the GeneTable with the parameter table
        :param table: tha tsv file containing the table
        :type table: pandas.DataFrame
        """
        self.__diseaseTable = pd.read_csv(table, delimiter='\t')

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

        if disease.startswith('C') and len(disease) == 8:
            evid = self.__diseaseTable[self.__diseaseTable['diseaseid'] == disease]
        else:
            evid = self.__diseaseTable[self.__diseaseTable['disease_name'] == disease]
        evid = evid[evid['sentence'].str.contains('>COVID-19<')]

        # keeping only these columns
        return evid[['sentence', 'nsentence', 'pmid']]


class Testing(Analysis):
    def __init__(self, table, table2):
        """
        The function find the correlations and the relation between genes and diseases of  the two dataframes

        :param table: dataframe
        :type: dataframe
        :param table2: dataframe
        :type: dataframe
        """
        self.__diseaseTable = pd.read_csv(table, delimiter='\t')
        self.__geneTable = pd.read_csv(table2, delimiter='\t')

    def correlation_gene_disease(self):
        # todo: finish comment

        """

        :returns: a DataFrame containing the correlations between genes and diseases and their count
        :rtype: pandas.DataFrame
        """

        # obtain the union with all possible sentences of the two dataframes without duplicates like the professor asked
        # same as your file

        # The merge occurs on pmid and nsentence (instead of sentence) because in the same publication the
        # nth sentence ("nsentence") will always be "sentence", but in this way the program runs faster
        # because it has to check only some numbers instead of whole strings.
        # The same goes for drop duplicates. When the function drop_duplicates search for duplicates
        # of the subset, with nsentence it avoids checking for whole strings as it would instead do with sentences.
        df = pd.DataFrame.merge(self.__diseaseTable, self.__geneTable, how='inner', on=['pmid', 'nsentence'])
        df.drop_duplicates(subset=['pmid', 'gene_symbol', 'disease_name', 'nsentence'], inplace=True)

        # Once all cleaning operations are done it keeps only the two columns needed for the analysis
        df = df[['gene_symbol', 'disease_name']]

        # Returns a DataFrame containing the couple gene-disease and the num of correlations
        return df.value_counts().to_frame('occurrences').reset_index()


        #todo: check it, if I'm not wrong we should add an else to the if
    def find_diseases_related_to_gene(self, user_input):
        """The function receive as input a geneID or a gene symbol and then returns a dataframe with the
        disesase related to the gene.

        :param user_input: the geneID or gene symbol input
        :type user_input: str
        :returns: a dataframe with the diseases related to the gene given in the input
        :rtype: pandas.DataFrame
        """
        rel = pd.DataFrame.merge(self.__diseaseTable, self.__geneTable, how='inner')

        if type(user_input) is int:
            user_input = self.__geneTable[self.__geneTable['geneid'] == user_input]
            user_input = user_input.loc[user_input.index[0], 'gene_symbol']

        # keeping only the rows which contain the user_input
        rel = rel[rel['sentence'].str.contains('>' + user_input + '<', regex=False)]

        # keeping only 'disease_name' and 'diseaseid' columns
        rel = rel[['disease_name', 'diseaseid']]

        # Using title() on all entries of 'disease_name' to avoid the sorting
        # of uppercase diseases first and lowercase diseases last
        rel['disease_name'] = rel['disease_name'].str.title()
        return rel.drop_duplicates(subset='disease_name').sort_values('disease_name')

    #todo: check it, if I'm not wrong we should add an else to the if
    def find_genes_related_to_disease(self, user_input):
        """The function receive as input a diseaseID or a disease name and then returns a dataframe with the
        genes related to the disease.

        :param user_input: the diseaseID or disease name input
        :type user_input: str
        :returns: a dataframe with the genes related to the disease given in the input
        :rtype: pandas.DataFrame
        """

        rel = pd.DataFrame.merge(self.__diseaseTable, self.__geneTable, how='inner')

        if user_input.startswith('C') and len(user_input) == 8:
            user_input = self.__diseaseTable[self.__diseaseTable['diseaseid'] == user_input]
            user_input = user_input.loc[user_input.index[0], 'disease_name']

        rel = rel[rel['sentence'].str.contains('>' + user_input + '<', regex=False)]

        # keeping only 'gene_symbol' and 'geneid' columns
        rel = rel[['gene_symbol', 'geneid']]

        return rel.drop_duplicates(subset='gene_symbol').sort_values('gene_symbol')


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

    # testing
    # print(test.correlation_gene_disease())
    # print(test.find_diseases_related_to_gene(59272))
    # print(test.find_diseases_related_to_gene('ACE2'))
    # (test.find_genes_related_to_disease('C0009450'))
    # print(test.find_genes_related_to_disease('Communicable Diseases'))

    test.correlation_gene_disease()
