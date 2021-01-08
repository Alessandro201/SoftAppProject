import pandas as pd
import re
from timebudget import timebudget
import timeit

genetable = pd.read_csv('gene_evidences.tsv', sep='\t')
diseasetable = pd.read_csv('disease_evidences.tsv', sep='\t')


# function 7
# timebudget just returns the time it took to execute the function
@timebudget
def correlation():
    """The function returns the correlation between a gene and the diseases mentioned in the sentence column
    of the table. To do it iterates through the table, search in the sentence if there is a disease and then
    it links it to the gene written in the gene_symbol column. If such a link between the disease and the gene
    already happened then it increase the number of times such correlation happened.

    The correlations are saved in this format:
    correlations = {gene1: {disease1: 1, disease2:4, disease3: 2},
                    gene2: {disease2: 3, disease4:1, disease5: 4}}
    """
    df = pd.read_csv('gene_evidences.tsv', sep='\t')

    corr = {}

    # every for cycle, .iterrows() returns a tuple with the index and the row.
    # to access the value in a column of the row you need to do row[name of the column]
    for index, row in df.iterrows():
        # Split the sentence every time it finds "class='disease ...' and returns a list of all the items
        sentenceDivided = re.split("class='disease.*?'", row['sentence'])
        try:
            # print("divided: ", sentenceDivided)

            # the first index of the list is the first piece of the sentence which precede "class='disease...'"
            # if it's present, otherwise it's just the sentence without any diseases mentioned.
            # Thus within the try except statement I keep only the piece of the sentence starting from the index 1.
            # If no index 1 is present, thus if no diseased is mentioned it throws a IndexError which is caught by
            # the except statement.

            for stringWithDisease in sentenceDivided[1:]:

                # Every "class='disease...' is followed by ">[disease name]</span>" due to HTML code syntax.
                # re.search() finds the first piece of the string which matches the pattern given
                disease = re.search('>.*?<', stringWithDisease)

                # .group() returns the string. It also does other things but we only need this one.
                # remove ">" from the start and "<" from the end.
                disease = disease.group()[1:-1]

                # print("disease: ", disease)

                # check if the gene (in the column gene_symbol of the row) already exist in the dictionary
                # by trying to assign its value to a dummy variable.
                # If it's not present it raises a KeyError which is caught by the except statement.
                # In this case it is then defined.
                try:
                    _ = corr[row['gene_symbol']]

                    # check if the disease already exist in the dictionary which is the value of the gene
                    # by trying to increase the number of times there was a correlation
                    try:
                        corr[row['gene_symbol']][disease] += 1
                    except KeyError:
                        corr[row['gene_symbol']][disease] = 1

                except KeyError:
                    corr[row['gene_symbol']] = {disease: 1}

        except IndexError:
            pass

    return corr


def correlation_find(gene):
    """The function returns the correlation between a gene and the diseases mentioned in the sentence column
    of the table. To do it iterates through the table, search in the sentence if there is a disease and then
    it links it to the gene written in the gene_symbol column. If such a link between the disease and the gene
    already happened then it increase the number of times such correlation happened.

    The correlations are saved in this format:
    correlations = {gene1: {disease1: 1, disease2:4, disease3: 2},
                    gene2: {disease2: 3, disease4:1, disease5: 4}}
    """
    df = pd.read_csv('gene_evidences.tsv', sep='\t')

    corr = {}

    # every for cycle, .iterrows() returns a tuple with the index and the row.
    # to access the value in a column of the row you need to do row[name of the column]
    for index, row in df.iterrows():
        # Split the sentence every time it finds "class='disease ...' and returns a list of all the items
        sentenceDivided = re.split("class='disease.*?'", row['sentence'])
        try:
            # print("divided: ", sentenceDivided)

            # the first index of the list is the first piece of the sentence which precede "class='disease...'"
            # if it's present, otherwise it's just the sentence without any diseases mentioned.
            # Thus within the try except statement I keep only the piece of the sentence starting from the index 1.
            # If no index 1 is present, thus if no diseased is mentioned it throws a IndexError which is caught by
            # the except statement.

            for stringWithDisease in sentenceDivided[1:]:

                # Every "class='disease...' is followed by ">[disease name]</span>" due to HTML code syntax.
                # re.search() finds the first piece of the string which matches the pattern given
                disease = re.search('>.*?<', stringWithDisease)

                # .group() returns the string. It also does other things but we only need this one.
                # remove ">" from the start and "<" from the end.
                disease = disease.group()[1:-1]

                # print("disease: ", disease)

                # check if the gene (in the column gene_symbol of the row) already exist in the dictionary
                # by trying to assign its value to a dummy variable.
                # If it's not present it raises a KeyError which is caught by the except statement.
                # In this case it is then defined.
                gene_in_rows = row['gene_symbol'].upper()
                try:
                    _ = corr[gene_in_rows]

                    # check if the disease already exist in the dictionary which is the value of the gene
                    # by trying to increase the number of times there was a correlation
                    try:
                        corr[gene_in_rows][disease] += 1
                    except KeyError:
                        corr[gene_in_rows][disease] = 1

                except KeyError:
                    corr[gene_in_rows] = {disease: 1}

        except IndexError:
            pass

    return corr[gene]


# @timebudget
def correlation_alby():
    """The function returns the correlation between a gene and the diseases mentioned in the sentence column
    of the two tables. To do it iterates through the table, search in the sentence if there is a disease and then
    it links it to the gene written in the gene_symbol column. If such a link between the disease and the gene
    already happened then it increase the number of times such correlation happened.

    The correlations are saved in this format:
    correlations = {gene1: {disease1: 1, disease2:4, disease3: 2},
                    gene2: {disease2: 3, disease4:1, disease5: 4}}

    :returns: a dictionary of dictionaries representing each key a gene and each value a dictionary with the number
    of occurance of a disease for that gene
    :rtype: dictionary
    """

    corr = {}

    # obtain the union with all possible sentences of the two dataframes without duplicates like the professor asked
    # same as your file
    df = pd.DataFrame.merge(diseasetable, genetable, how='inner')
    df.sort_values('gene_symbol', inplace=True)
    df.drop_duplicates(subset=['sentence', 'gene_symbol'], inplace=True)

    for index, row in df.iterrows():
        # Split the sentence every time it finds "class='disease ...' and returns a list of all the items
        sentenceDivided = re.split("class='disease.*?'", row['sentence'])
        try:
            # print("divided: ", sentenceDivided)

            # the first index of the list is the first piece of the sentence which precede "class='disease...'"
            # if it's present, otherwise it's just the sentence without any diseases mentioned.
            # Thus within the try except statement I keep only the piece of the sentence starting from the index 1.
            # If no index 1 is present, thus if no diseased is mentioned it throws a IndexError which is caught by
            # the except statement.

            for stringWithDisease in sentenceDivided[1:]:

                # Every "class='disease...' is followed by ">[disease name]</span>" due to HTML code syntax.
                # re.search() finds the first piece of the string which matches the pattern given
                Disease = re.search('>.*?<', stringWithDisease)

                # .group() returns the string. It also does other things but we only need this one.
                # remove ">" from the start and "<" from the end.
                Disease = Disease.group()[1:-1]

                # print("disease: ", disease)

                # check if the gene (in the column gene_symbol of the row) already exist in the dictionary
                # by trying to assign its value to a dummy variable.
                # If it's not present it raises a KeyError which is caught by the except statement.
                # In this case it is then defined.
                try:
                    _ = corr[row['gene_symbol']]

                    # check if the disease already exist in the dictionary which is the value of the gene
                    # by trying to increase the number of times there was a correlation
                    try:
                        corr[row['gene_symbol']][Disease] += 1
                    except KeyError:
                        corr[row['gene_symbol']][Disease] = 1

                except KeyError:
                    corr[row['gene_symbol']] = {Disease: 1}

        except IndexError:
            pass

    # create a list of tuples of each correspondence and then sort them based on the correspondence
    # corr_list =  [(gene1, disease1, correspondence),
    #               (gene1, disease2, correspondence),
    #               (gene2, disease1, correspondence),..]
    corr_list = [(gene, disease, corr[gene][disease]) for gene in corr.keys() for disease in corr[gene].keys()]
    corr_list_sorted = sorted(corr_list, key=lambda y: y[2], reverse=True)

    return corr_list_sorted



@timebudget
def new_correlation():
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
    df = pd.DataFrame.merge(diseasetable, genetable, how='inner', on=['pmid', 'nsentence'])
    df.drop_duplicates(subset=['pmid', 'gene_symbol', 'disease_name', 'nsentence'], inplace=True)

    # Once all cleaning operations are done it keeps only the two columns needed for the analysis
    df = df[['gene_symbol', 'disease_name']]

    # Returns a DataFrame containing the couple gene-disease and the num of correlations
    return df.value_counts().to_frame('occurrences').reset_index()



def getDiseasesRelatedToGene(gene):
    """The function returns the correlation between a gene and the diseases mentioned in the sentence column
    of the table. To do it iterates through the table, search in the sentence if there is a disease and then
    it links it to the gene written in the gene_symbol column. If such a link between the disease and the gene
    already happened then it increase the number of times such correlation happened.

    The correlations are saved in this format:
    correlations = {gene1: {disease1: 1, disease2:4, disease3: 2},
                    gene2: {disease2: 3, disease4:1, disease5: 4}}
    """

    global df

    print(gene)

    diseases = {}
    # every for cycle, .iterrows() returns a tuple with the index and the row.
    # to access the value in a column of the row you need to do row[name of the column]
    for index, row in df.iterrows():
        # Split the sentence every time it finds "class='disease ...' and returns a list of all the items

        if row['gene_symbol'] == gene or row['geneid'] == gene:
            sentenceDivided = re.split("class='disease.*?'", row['sentence'])
            try:
                # print("divided: ", sentenceDivided)

                # the first index of the list is the first piece of the sentence which precede "class='disease...'"
                # if it's present, otherwise it's just the sentence without any diseases mentioned.
                # Thus within the try except statement I keep only the piece of the sentence starting from the index 1.
                # If no index 1 is present, thus if no diseased is mentioned it throws a IndexError which is caught by
                # the except statement.

                for stringWithDisease in sentenceDivided[1:]:

                    # Every "class='disease...' is followed by ">[disease name]</span>" due to HTML code syntax.
                    # re.search() finds the first piece of the string which matches the pattern given
                    disease = re.search('>.*?<', stringWithDisease)

                    # .group() returns the string. It also does other things but we only need this one.
                    # remove ">" from the start and "<" from the end.
                    disease = disease.group()[1:-1]

                    try:
                        _ = diseases[disease]
                    except KeyError:
                        diseases[disease] = ''

                    # print("disease: ", disease)

            except IndexError:
                pass

        return diseases.keys()


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)


    # print(genetable.sort_values('pmid').head())

    print(timeit.timeit(correlation_alby, number=10) / 10)
    print(timeit.timeit(new_correlation, number=50) / 50)
