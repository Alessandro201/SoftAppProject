import os

# --------- Settings -------------

# Base url for the publications on PubMed
BASE_PMID_URL = 'https://pubmed.ncbi.nlm.nih.gov/'

# Locations of the two datasets. By default the \datasets is selected
TABLES_LOCATION = r'datasets'
TABLES_LOCATION = os.path.join(os.getcwd(), TABLES_LOCATION)

# Datasets name
GENE_TABLE_NAME = 'gene_evidences.tsv'
DISEASE_TABLE_NAME = 'disease_evidences.tsv'

# cache settings. If You don't know what you are doing, don't do it
CACHE_CONFIG = {
    "DEBUG": True,  # some Flask specific configs
    "CACHE_TYPE": "simple",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 3600
}
# name of the cache containing the table
TABLE_CACHE_NAME = 'table_cache'

DELIMITER = '\t'
