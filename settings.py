# ---------- Settings ----------

# Base url for the publications on PubMed
BASE_PMID_URL = 'https://pubmed.ncbi.nlm.nih.gov/'


# ---------- Paths Settings ----------

# Location of the documentation json file. The default path is "static/docs".
# Use unix positioning '/' as it works everywhere
DOCS_PATH = r'static/docs'


# Locations of the two datasets. Use unix positioning '/' as it works everywhere
GENE_TABLE_PATH = './datasets/gene_evidences.tsv'
DISEASE_TABLE_PATH = './datasets/disease_evidences.tsv'

# ---------- Cache Settings ----------

# IF YOU DON'T KNOW WHAT YOU ARE DOING, DON'T MODIFY THIS SETTINGS

# cache settings
CACHE_CONFIG = {
    "CACHE_TYPE": "simple",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 3600
}
