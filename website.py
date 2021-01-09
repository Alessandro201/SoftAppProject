from flask import Flask, render_template, request, send_file, flash, make_response, redirect
from flask_paginate import Pagination, get_page_parameter
from flask_caching import Cache
from settings import *
from io import StringIO
import csv
from datetime import datetime
import mediator

app = Flask(__name__)

# Used by "flash" for flashing comments or errors
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# tell Flask to use the above defined config
app.config.from_mapping(config)
cache = Cache(app)


def run(**kwargs):
    """When called it starts the website"""
    app.run(**kwargs)


@app.route('/')
def homepage():
    """A webpage which explains briefly the project and allows you to download the datasets or to go through them"""

    return render_template('homepage.html')


@app.route('/download', methods=['POST'])
def download():
    """Allows to download the table computed as csv file.

    Steps:
    1) Get what_to_download to know the name by which the table is stored in the cache. It will also be
        the name of the file. If for some reason it can't find it, it flashes a popup and redirect to the previous page
    2) Get the table from the cache. If the data is None, it's likely that the cache has exceeded the timout
        defined in the config.py. You need to reload the page to compute again the table
    3) Extract from "data_to_save" which is a dictionary the rows and the labels of the table
    4) A csv.writer is instantiated. It needs StringIO
    5) Write as the first row the labels of the columns, then write all the rows
    6) Make a response which allows the .csv file to be downloaded
    7) Set some information of the file that will be downloaded like its name and filetype

    """

    # Step 1)
    NAME_FUNCTION = request.form.get('what_to_download')
    if NAME_FUNCTION is None:
        flash('Error in downloading the table, please try reloading the page.')
        return redirect(request.referrer)

    # Step 2)
    data_to_save = cache.get(NAME_FUNCTION)
    if data_to_save is None:
        flash('Timeout Error, please try reloading the page.')

    # Step 3)
    rows = data_to_save['rows']
    labels = [data_to_save['labels']]

    # Step 4)
    si = StringIO()
    cw = csv.writer(si)

    # Step 5)
    cw.writerows(labels)
    cw.writerows(rows)

    # Step 6)
    output = make_response(si.getvalue())

    # Step 7)
    output.headers["Content-Disposition"] = f"attachment; filename={NAME_FUNCTION}.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@app.route('/tableGenesEvidences/')
def genesTable():
    """A webpage which lets you go through gene data table.
    To do the pagination it uses Pagination() from flask-paginate"""

    # variables
    nRows = mediator.getInfo()[0][0]
    per_page = 30

    # Get the page from the form to let the user go to a specific page
    try:
        page = int(request.form['page'])
        if page < 1:
            page = 1

    except (KeyError, ValueError):
        page = request.args.get(get_page_parameter(), type=int, default=1)

    # start and end index of the table
    start = page * per_page
    end = (page + 1) * per_page

    # Returns a list of the rows from index start to index end
    df_list = mediator.getGeneTableList(start, end)

    # Prepares the pagination that allows you to click the number of the page and view it
    pagination = Pagination(page=page, total=nRows, record_name="gene entries",
                            css_framework='bootstrap4', per_page=per_page)

    return render_template('tableGenesEvidences.html',
                           rows=df_list,
                           labels=mediator.getInfo()[0][2],
                           pagination=pagination)


@app.route('/tableDiseasesEvidences/')
def diseasesTable():
    """A webpage which lets you go through gene data table.
    To do the pagination it uses Pagination() from flask-paginate"""

    # variables
    nRows = mediator.getInfo()[1][0]
    per_page = 30

    # Get the page from the form to let the user go to a specific page
    try:
        page = int(request.form['page'])
        if page < 1:
            page = 1

    except (KeyError, ValueError):
        page = request.args.get(get_page_parameter(), type=int, default=1)

    # start and end index of the table
    start = page * per_page
    end = (page + 1) * per_page

    # Returns a list of the rows from index start to index end
    df_list = mediator.getDiseaseTableList(start, end)

    # Prepares the pagination that allows you to click the number of the page and view it
    pagination = Pagination(page=page, total=nRows, record_name="diseases entries",
                            css_framework='bootstrap4', bs_version=4, per_page=per_page)

    return render_template('tableDiseasesEvidences.html',
                           labels=mediator.getInfo()[1][2],
                           rows=df_list,
                           pagination=pagination, )


@app.route('/downloadDiseases')
def diseasesTableDownload():
    """Let the user download the file"""
    from os import path

    # Compute the path to the databases
    disease_evidences_path = path.join(TABLES_LOCATION, DISEASE_TABLE_NAME)
    return send_file(disease_evidences_path, as_attachment=True)


@app.route('/downloadGenes')
def genesTableDownload():
    """Let the user download the file"""
    from os import path

    # Compute the path to the databases
    gene_evidences_path = path.join(TABLES_LOCATION, GENE_TABLE_NAME)

    return send_file(gene_evidences_path, as_attachment=True)


@app.route('/documentation')
def documentation():
    """A webpage with the documentation of the project"""

    return render_template('documentation.html')


@app.route('/about')
def about():
    """A webpage with the member of the group"""
    return render_template('about.html')


@app.route('/functions')
def functions():
    """A webpage which lets you select the operation you want to do with the datasets"""

    return render_template('functions.html')


# for a and b objective
@app.route('/info')
def info():
    """Returns a webpage with all the information about the data tables and a preview of heads and tails"""

    geneInfo, diseaseInfo = mediator.getInfo()
    gRows = geneInfo[0]
    gCols = geneInfo[1]
    gLabels = geneInfo[2]
    gHead = geneInfo[3]
    gTail = geneInfo[4]

    dRows = diseaseInfo[0]
    dCols = diseaseInfo[1]
    dLabels = diseaseInfo[2]
    dHead = diseaseInfo[3]
    dTail = diseaseInfo[4]

    return render_template('info.html',
                           geneRows=gRows, geneCols=gCols, geneLabels=gLabels, geneHead=gHead, geneTail=gTail,
                           disRows=dRows, disCols=dCols, disLabels=dLabels, disHead=dHead, disTail=dTail)


# for c objective
@app.route('/distinctGenes')
def distinctGenes():
    """A webpage with all the unique distinct genes in the gene table"""

    distinctGenes = mediator.getDistinctGenes()

    return render_template('distinctGenes.html', distinctGenes=distinctGenes, numDistinctGenes=len(distinctGenes))


# for e objective
@app.route('/distinctDiseases')
def distinctDiseases():
    """A webpage with all the unique distinct disease in the disease table"""

    NAME_FUNCTION = 'distinct_diseases'

    labels, rows = mediator.getDistinctDiseases()

    diseases = {'labels': labels,
                'rows': rows}

    cache.set(NAME_FUNCTION, diseases)

    return render_template('distinctDiseases.html', diseases=diseases,
                           numDistinctDiseases=len(diseases['rows']), NAME_FUNCTION=NAME_FUNCTION)


# for d objective
@app.route('/geneEvidences', methods=["POST", "GET"])
def geneEvidences():
    """The first time the user access "geneEvidences" it is requested with 'GET' method.
    Then it returns a webpage which lets the user input a geneSymbol or a geneID.
    It is then submitted back to "geneEvidences" but with 'POST' method.
    Now it returns a webpage which lists all the evidences in literature of the gene"""

    if request.method == "GET":
        return render_template('inputGeneEvidences.html')
    else:
        gene = request.form['gene']
        evidences = mediator.getGeneEvidences(gene)
        return render_template("geneEvidences.html", gene=gene, evidences=evidences, numEvidences=len(evidences),
                               base_pmid_url=BASE_PMID_URL)


# for f objective
@app.route('/diseaseEvidences', methods=["POST", "GET"])
def diseaseEvidences():
    """The first time the user access "diseaseEvidences" it is requested with 'GET' method.
    Then it returns a webpage which lets the user input a diseaseID or a diseaseName.
    It is then submitted back to "diseaseEvidences" but with 'POST' method.
    Now it returns a webpage which lists all the evidences in literature of the disease"""

    if request.method == "GET":
        return render_template('inputDiseaseEvidences.html')
    else:
        disease = request.form['disease']
        evidences = mediator.getDiseaseEvidences(disease)
        return render_template('diseaseEvidences.html', disease=disease, evidences=evidences,
                               numEvidences=len(evidences), base_pmid_url=BASE_PMID_URL)


# for g objective
@app.route('/correlation', methods=["POST", "GET"])
def correlation():
    """The webpage lists the correlations between genes and diseases.

    It allows th user to customize the results, he can decide the number of correlations to show ("rows")
    and the minimum number of occurrences a correlation need to have to be shown ("occurrences").

    Occurrences ha priority over rows. In fact, if "occurrence" is given and the user hasn't written
    anything in "rows" then it sets "rows" to 0 which means that all rows will be returned.
    Also, if the user wants 50 rows, but the rows which meet the occurrence requirement are 30,
    only 30 rows will be returned.
    """

    # This is for the first time the user visits the page
    if request.method == "GET":
        rows = 10
        occurrences = 0

    else:
        try:
            occurrences = request.form['occurrence']
            occurrences = int(occurrences)
        except (ValueError, TypeError, KeyError):
            occurrences = 0

        try:
            rows = request.form['rows']
            rows = int(rows)
        except (ValueError, TypeError):
            if occurrences != 0:
                rows = 0
            else:
                rows = 10

    correlations = mediator.getCorrelation(rows, occurrences)

    return render_template('correlation.html', correlations=correlations, occurrences=occurrences,
                           numCorrelations=len(correlations))


# for h objective
@app.route('/diseasesRelatedToGene', methods=["POST", "GET"])
def diseasesRelatedToGene():
    """The first time the user access "diseasesRelatedToGene" it is requested with 'GET' method.
    Then it returns a webpage which lets the user input a geneSymbol or a geneID.
    It is then submitted back to "diseasesRelatedToGene" but with 'POST' method.
    Now it returns a webpage which lists all the diseases related to the gene found in literature"""

    if request.method == "GET":
        return render_template('inputDiseasesRelatedToGene.html')
    else:
        gene = request.form['gene']
        diseaseRelToGene = mediator.getDiseasesRelatedToGene(gene)
        return render_template("diseasesRelatedToGene.html", gene=gene, diseases=diseaseRelToGene,
                               numDiseases=len(diseaseRelToGene))


# for i objective
@app.route('/genesRelatedToDisease', methods=["POST", "GET"])
def genesRelatedToDisease():
    """The first time the user access "genesRelatedToDisease" it is requested with 'GET' method.
    Then it returns a webpage which lets the user input a diseaseName or a diseaseID.
    It is then submitted back to "genesRelatedToDisease" but with 'POST' method.
    Now it returns a webpage which lists all the genes related to the disease found in literature"""

    if request.method == "GET":
        return render_template('inputGenesRelatedToDisease.html')
    else:
        disease = request.form['disease']
        genesRelToDisease = mediator.getGenesRelatedToDisease(disease)
        return render_template("genesRelatedToDisease.html", disease=disease, genes=genesRelToDisease,
                               numGenes=len(genesRelToDisease))


if __name__ == '__main__':
    import mediator

    BASE_PMID_URL = 'https://pubmed.ncbi.nlm.nih.gov/'
    app.run(debug=True)
