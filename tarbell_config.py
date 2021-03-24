# -*- coding: utf-8 -*-

"""
Tarbell project configuration
"""

# Google document key for the stories. If not specified, the Archie stuff is skipped
DOC_KEY = "11Oi28bskMXGDvOsrgV_zPGx-5uIoD-gghApA8OkK2RE"

# Google spreadsheet key
SPREADSHEET_KEY = "1ckG1QIsQWb232qD33jAm6mDtELsuO7edo_S2K-hv8Hs"

# Exclude these files from publication
EXCLUDES = ['*.md', 'requirements.txt', 'node_modules', 'sass', 'js/src', '*.ai', 'package.json', 'Gruntfile.js']

# Spreadsheet cache lifetime in seconds. (Default: 4)
# SPREADSHEET_CACHE_TTL = 4

# Create JSON data at ./data.json, disabled by default
# CREATE_JSON = True

# Get context from a local file or URL. This file can be a CSV or Excel
# spreadsheet file. Relative, absolute, and remote (http/https) paths can be 
# used.
# CONTEXT_SOURCE_FILE = ""

# EXPERIMENTAL: Path to a credentials file to authenticate with Google Drive.
# This is useful for for automated deployment. This option may be replaced by
# command line flag or environment variable. Take care not to commit or publish
# your credentials file.
# CREDENTIALS_PATH = ""

# S3 bucket configuration
S3_BUCKETS = {
    # Provide target -> s3 url pairs, such as:
    #     "mytarget": "mys3url.bucket.url/some/path"
    # then use tarbell publish mytarget to publish to it
    
    "production": "graphics.chicagotribune.com/illinois-seclusion",
    "staging": "apps.beta.tribapps.com/illinois-seclusion",
}

# Default template variables
DEFAULT_CONTEXT = {
   'OMNITURE': {   'domain': 'chicagotribune.com',
                    'section': 'news',
                    'sitename': 'Chicago Tribune',
                    'subsection': 'local',
                    'subsubsection': '',
                    'type': 'dataproject'},
    'name': 'illinois-seclusion',
    'title': 'Seclusion and isolation rooms misused in Illinois schools'
}