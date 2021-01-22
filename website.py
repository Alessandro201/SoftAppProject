from flask import Flask, render_template, request, send_file, flash, make_response, redirect
from flask_paginate import Pagination, get_page_parameter
from flask_caching import Cache
from settings import *
from io import StringIO
from os import path
import csv
import mediator
from mediator import DISEASE_TABLE_PATH, GENE_TABLE_PATH, DOCS_PATH

app = Flask(__name__)

# Used by "flash" for flashing comments or errors as popup
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# tell Flask to use the config (defined in settings.py)
app.config.from_mapping(CACHE_CONFIG)
cache = Cache(app)


def run(**kwargs):
    """When called it starts the website"""
    app.run(**kwargs)


@app.route('/')
def homepage():
    """A webpage which explains briefly the project and allows you to download the datasets or to go through them"""

    return render_template('homepage.html', diseaseTablePath=DISEASE_TABLE_PATH,
                           geneTablePath=GENE_TABLE_PATH)


@app.route('/about')
def about():
    """A webpage with the member of the group"""
    return render_template('about.html')


@app.route('/documentation', defaults={'file': 'projectOverview'})
@app.route('/documentation/<file>')
def documentation(file):
    """Return the webpages with the documentation of the project.

    Every webpage of the docs has it's name added after "/documentation/"
    This means that you can add all the webpages that you want and you won't need to write a single line of code,
    just add the html files to "templates/documentation/" and the .json files with the documentation to the
    folder containing all the .json written in "settings.py".

    Any eventual exception is purposefully caught here and not in mediator.py to show the error
    as a popup with flash()"""

    try:
        docs = mediator.getDocumentation(DOCS_PATH, file)
    except OSError as err:
        flash({
            'type': 'error',
            'header': 'Something went wrong!',
            'message': 'There was an error in loading the documentation. You are redirected to the Project Overview',
            'details': err,
        })
        docs = mediator.getDocumentation(DOCS_PATH, 'projectOverview')
        return render_template('documentation/projectOverview.html', docs=docs)

    return render_template('documentation/%s.html' % file, docs=docs)


@app.route('/functions')
def functions():
    """A webpage which lets you select the operation you want to do with the datasets"""

    return render_template('functions.html')


@app.route('/download', methods=['POST'])
def download():
    """Allows to download the table computed as tsv file.

    Steps:
    Step 1) Get "name_file" from the page that requested the download.
    Step 2) Check if "name_file" is None. If it is it means that the previous page did not return any value,
        or does not have any button named "name_file".
    Step 3) If "name_file" is not None, it computes the complete path by joining the current path of execution
        of the program, thus the main directory of the program, and "name_file". Then it checks if it's a file
        and if it's exists. It if does it means the previous page requested a file to download, and it downloads it,
        Otherwise it means "name_file" is the name of the name that will have the table once it'll be converted to .tsv.
    Step 3.1) In the latter case, it requests the table from the cache by using the global variable "TABLE_CACHE_NAME"
        define in "settings.py". If the data retrieved is None it means that there was not any table in the cache, thus
        it redirect to the previous page and tells the user through a notification that he needs to reload the page as
        the table probably expired from the cache.
    Step 4) Extract from the dictionary "data_to_save" the rows and the labels of the table.
    Step 5) A csv.writer is instantiated. It needs StringIO to instantiate a file-object.
    Step 6) Write as the first row the labels of the columns, then write all the rows
    Step 7) Make a response which allows the .tsv file to be downloaded
    Step 8) Set some information of the file that will be downloaded like its name and filetype

    """

    # Step 1)
    name_file = request.form.get('name_file')

    # Step 2)
    if name_file is None:
        flash({'type': 'warning',
               'header': 'Something went wrong!',
               'message': 'Error in downloading the table, please try reloading the page!',
               'details': f"\"name_file\" not found in the forms. It means that the page that "
                          f"requested the download did not send any value."})
        return redirect(request.referrer)
    else:
        complete_path = os.path.join(os.getcwd(), name_file)

        # Step 3)
        if os.path.isfile(complete_path) is True:
            return send_file(complete_path, as_attachment=True)
        else:
            # Step 3.1)
            data_to_save = cache.get(TABLE_CACHE_NAME)
            if data_to_save is None:
                flash({'type': 'warning',
                       'header': 'Something went wrong!',
                       'message': 'I could not get the table to let you download it, please try reloading the page!',
                       'details': f"\"{name_file}\" was not found or the data was not in the cache!"})
                return redirect(request.referrer)

    # Step 4)
    rows = data_to_save['rows']
    labels = [data_to_save['labels']]

    # Step 5)
    si = StringIO()
    cw = csv.writer(si, delimiter='\t')

    # Step 6)
    cw.writerows(labels)
    cw.writerows(rows)

    # Step 7)
    output = make_response(si.getvalue())

    # Step 8)
    output.headers["Content-Disposition"] = f"attachment; filename={name_file}.tsv"
    output.headers["Content-type"] = "text/tsv"
    return output


@app.route('/browseGenesDataset')
def browseGenesDataset():
    """A webpage which lets you go through gene dataset.
    To do the pagination it uses Pagination() from flask-paginate"""

    # variables
    data = mediator.getInfoGenes()
    rows_per_page = 30

    # Get the page from the form to let the user go to a specific page
    # The value of "page" is taken with functions from flask-paginate otherwise it raises errors
    page = int(request.args.get(get_page_parameter(), type=int, default=1))
    if page < 1:
        flash({'type': 'warning',
               'header': 'Warning!',
               'message': 'You need to insert a positive number!'})

    # start and end indexes of the table
    start = (page - 1) * rows_per_page
    end = page * rows_per_page

    # Returns a list of the rows from index start to index end
    data['rows'] = mediator.getGeneTableList(start, end)

    # Prepares the pagination that allows you to click the number of the page and view it in the webpage
    pagination = Pagination(page=page, total=data['nrows'], record_name="gene entries",
                            css_framework='bulma', per_page=rows_per_page)

    return render_template('browseGenesDataset.html',
                           base_pmid_url=BASE_PMID_URL,
                           data=data,
                           pagination=pagination)


@app.route('/browseDiseasesDataset')
def browseDiseasesDataset():
    """A webpage which lets you go through disease dataset.
    To do the pagination it uses Pagination() from flask-paginate"""

    # variables
    data = mediator.getInfoDiseases()
    rows_per_page = 30

    # Get the page from the form to let the user go to a specific page
    # The value of "page" is taken with functions from flask-paginate otherwise it raises errors

    page = int(request.args.get(get_page_parameter(), type=int, default=1))
    if page < 1:
        flash({'type': 'warning',
               'header': 'Warning!',
               'message': 'You need to insert a positive number!'})

    # start and end index of the table
    start = (page - 1) * rows_per_page
    end = page * rows_per_page

    # Returns a list of the rows from index start to index end
    data['rows'] = mediator.getDiseaseTableList(start, end)

    # Prepares the pagination that allows you to click the number of the page and view it
    pagination = Pagination(page=page, total=data['nrows'], record_name="diseases entries",
                            css_framework='bulma', per_page=rows_per_page)

    return render_template('browseDiseasesDataset.html',
                           base_pmid_url=BASE_PMID_URL,
                           data=data,
                           pagination=pagination)


# for a and b objective
@app.route('/info')
def info():
    """Returns a webpage with all the information about the data tables and a preview of heads and tails"""

    gene_data, disease_data = mediator.getInfo()

    return render_template('operations/info.html', gene_data=gene_data, disease_data=disease_data)


# for c objective
@app.route('/distinctGenes')
def distinctGenes():
    """A webpage with all the unique distinct genes in the gene dataset"""

    NAME_FUNCTION = 'distinct_genes'

    data = mediator.getDistinctGenes()

    cache.set(TABLE_CACHE_NAME, data)

    return render_template('operations/distinctGenes.html', data=data, NAME_FUNCTION=NAME_FUNCTION)


# for e objective
@app.route('/distinctDiseases')
def distinctDiseases():
    """A webpage with all the unique distinct disease in the disease table"""

    NAME_FUNCTION = 'distinct_diseases'

    data = mediator.getDistinctDiseases()

    cache.set(TABLE_CACHE_NAME, data)

    return render_template('operations/distinctDiseases.html', data=data, NAME_FUNCTION=NAME_FUNCTION)


# for d objective
@app.route('/geneEvidences', methods=["POST", "GET"])
def geneEvidences():
    """The first time the user access "geneEvidences" it is requested with 'GET' method.
    Then it returns a webpage which lets the user input a geneSymbol or a geneID.
    It is then submitted back to "geneEvidences" but with 'POST' method.
    Now it returns a webpage which lists all the evidences in literature of the relation between
    the gene and COVID-19"""

    NAME_FUNCTION = '_evidences'

    if request.method == "GET":
        return render_template('operations/inputGeneEvidences.html')
    else:
        gene = request.form['gene']
        data = mediator.getGeneEvidences(gene)

        cache.set(TABLE_CACHE_NAME, data)

        return render_template("operations/geneEvidences.html", gene=gene, data=data, NAME_FUNCTION=NAME_FUNCTION,
                               base_pmid_url=BASE_PMID_URL)


# for f objective
@app.route('/diseaseEvidences', methods=["POST", "GET"])
def diseaseEvidences():
    """The first time the user access "diseaseEvidences" it is requested with 'GET' method.
    Then it returns a webpage which lets the user input a diseaseID or a diseaseName.
    It is then submitted back to "diseaseEvidences" but with 'POST' method.
    Now it returns a webpage which lists all the evidences in literature of the disease"""

    NAME_FUNCTION = '_evidences'

    if request.method == "GET":
        return render_template('operations/inputDiseaseEvidences.html')
    else:
        disease = request.form['disease']
        data = mediator.getDiseaseEvidences(disease)

        cache.set(TABLE_CACHE_NAME, data)

        return render_template('operations/diseaseEvidences.html', disease=disease, data=data,
                               base_pmid_url=BASE_PMID_URL, NAME_FUNCTION=NAME_FUNCTION)


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
        nrows = 10
        min_occurrences = 0

    # if it's not the first time the user visit the page, it tries to get any eventual value inserted in the form
    else:
        try:
            min_occurrences = request.form['occurrence']
            min_occurrences = int(min_occurrences)

            # The minimum occurrences is 1, so if the user has selected a negative number occurrences will be changed
            # to 0 which is the default and shows every correlation, at least if the user has chosen 0 as "nrows"
            if min_occurrences < 0:
                min_occurrences = 0

        except ValueError:
            # If it raise ValueError it means "occurrences" it's a string which cannot be converted to a number.
            # It's either an empty string or a word. If it's a word it notifies the user of the error and
            # it sets "occurrences" to the default value
            if min_occurrences != '':
                flash({'type': 'warning',
                       'header': 'Warning!',
                       'message': 'You need to insert a number not a word!'})
            min_occurrences = 0

        try:
            nrows = request.form['rows']
            nrows = int(nrows)

            # if the user has inserted a negative number it converts it to 0 (show all correlation) if the user
            # has inserted a minimum occurrences [min_occurrences], otherwise it will show the top 10. A notification
            # will be shown to explain what has been done
            if nrows < 0:
                if min_occurrences != 0:
                    nrows = 0
                    flash({'type': 'warning',
                           'header': 'Wrong number!',
                           'message': 'You need to insert a positive number! '
                                      'Here are all the correlations '
                                      'that matches the minimum occurrences.'})
                else:
                    nrows = 10
                    flash({'type': 'warning',
                           'header': 'Wrong number!',
                           'message': 'You need to insert a positive number! '
                                      'Here are the first top 10 correlations.'})

        except ValueError:
            # If it raise ValueError it means "nrows" is a string which cannot be converted to a number.
            # It's either an empty string or a word. If it's a word it notifies the user of the error
            # and it set "nrows" to the default value
            if nrows != '':
                flash({'type': 'warning',
                       'header': 'Warning!',
                       'message': 'You need to insert a number not a word!'})
            if min_occurrences == 0:
                nrows = 10
            else:
                nrows = 0

    data = mediator.getCorrelation(nrows, min_occurrences)

    NAME_FUNCTION = 'correlation'

    cache.set(TABLE_CACHE_NAME, data)

    return render_template('operations/correlation.html', data=data, NAME_FUNCTION=NAME_FUNCTION)


# for h objective
@app.route('/diseasesRelatedToGene', methods=["POST", "GET"])
def diseasesRelatedToGene():
    """The first time the user access "diseasesRelatedToGene" it is requested with 'GET' method.
    Then it returns a webpage which lets the user input a geneSymbol or a geneID.
    It is then submitted back to "diseasesRelatedToGene" but with 'POST' method.
    Now it returns a webpage which lists all the diseases related to the gene found in literature"""

    NAME_FUNCTION = 'diseases_rel_to_'

    if request.method == "GET":
        return render_template('operations/inputDiseasesRelatedToGene.html')
    else:
        gene = request.form['gene']
        data = mediator.getDiseasesRelatedToGene(gene)

        cache.set(TABLE_CACHE_NAME, data)

        return render_template("operations/diseasesRelatedToGene.html", gene=gene, data=data,
                               NAME_FUNCTION=NAME_FUNCTION)


# for i objective
@app.route('/genesRelatedToDisease', methods=["POST", "GET"])
def genesRelatedToDisease():
    """The first time the user access "genesRelatedToDisease" it is requested with 'GET' method.
    Then it returns a webpage which lets the user input a diseaseName or a diseaseID.
    It is then submitted back to "genesRelatedToDisease" but with 'POST' method.
    Now it returns a webpage which lists all the genes related to the disease found in literature"""

    NAME_FUNCTION = 'genes_rel_to_'

    if request.method == "GET":
        return render_template('operations/inputGenesRelatedToDisease.html')
    else:
        disease = request.form['disease']
        data = mediator.getGenesRelatedToDisease(disease)

        cache.set(TABLE_CACHE_NAME, data)
        return render_template("operations/genesRelatedToDisease.html", data=data, disease=disease,
                               NAME_FUNCTION=NAME_FUNCTION)


if __name__ == '__main__':
    import mediator

    app.run(debug=True)
