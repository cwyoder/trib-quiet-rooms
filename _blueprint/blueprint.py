# -*- coding: utf-8 -*-

import sys
from os import path
sys.path.append( path.dirname( path.abspath(__file__) ) )
import archie
# To open the tarbell_config.py
import codecs 
import os

import locale
from flask import Blueprint

import jinja2 #for context-getting

from clint.textui import colored
from tarbell.hooks import register_hook
from tarbell.utils import puts

import xlrd             # for parsing excel dates
import datetime         # For parsing dates
import dateutil.parser  # For parsing dates

from PIL import Image   # For the image sizing
import urllib2          # For image sizing of rmeote/server-hosted images (like tribimg.com)
import re               # For dumb -> Smart quotes python filter

from tribune_viztools.tarbell.blueprint import TribuneTarbellBlueprint
from tribune_viztools.tarbell.hooks import (
    create_front_end_files,
    copy_front_end_build_script_templates,
    create_readme,
    create_unfuddle_project,
    newproject_add_excludes,
    newproject_add_default_omniture_config,
    merge_extra_context,
    update_facebook
)

from pprint import pprint # To do a php-like var_dump


NAME = "Tribune Off-Platform Tarbell Blueprint, version 2"

blueprint = TribuneTarbellBlueprint('blueprint', __name__)


try:
    locale.setlocale(locale.LC_ALL, 'en_US')
except locale.Error:
    puts(colored.red("Locale error"))



NEWPROJECT_HOOKS = (
    copy_front_end_build_script_templates,
    create_front_end_files,
    create_readme,
    create_unfuddle_project,
    newproject_add_excludes,
    newproject_add_default_omniture_config,
)

GENERATE_HOOKS = (
    archie.refresh_archie,
    merge_extra_context,
)

PREVIEW_HOOKS = (
    archie.refresh_archie,
)

PUBLISH_HOOKS = (
    update_facebook,
)

for f in NEWPROJECT_HOOKS:
    register_hook('newproject')(f)

for f in PREVIEW_HOOKS:
    register_hook('preview')(f)

for f in GENERATE_HOOKS:
    register_hook('generate')(f)

for f in PUBLISH_HOOKS:
    register_hook('publish')(f)

@blueprint.app_template_filter('get_thumbnail_info')
def get_thumbnail_info(image):
    """
        For SEO metadata, get and return image dimensions
    """
    print image
    try:
        # First, try to open the image from the local directory
        im = Image.open(image)
        width,height = im.size
        return {
            "width": width,
            "height": height
        }
    except IOError:
        # If the image is remote, i.e. you have an absolute URL to the image
        im = Image.open(urllib2.urlopen(image))
        print (im)
        width,height = im.size
        return {
            "width": width,
            "height": height
        }
    except:
        print ('>>>> Error getting thumbnail image')
        return False

@blueprint.app_template_filter('xldate_to_datetime')
def xldate_to_datetime(xldate):
    """
    Takes a date in excel format and returns it as a python datetime
    """

    try:

        if isinstance(xldate, unicode):
            retval = datetime.datetime.strptime(xldate, '%m/%d/%Y')
        else:
            retval = datetime.datetime(*xlrd.xldate_as_tuple(xldate,0))
    except:
        retval="???"    
    return retval

@blueprint.app_template_filter('format_date_with_strftime')
def format_date_with_strftime(date_to_format, format):
    """
    Formats a date in your preferred format using strftime.
    Includes a convenience format of "ISO" which will return 
    the date in standard ISO format, which should make schema 
    markup easier. You're welcome.
    """
    if format.upper() == "ISO":
        use_this_format = "%Y-%m-%dT%H:%M:%S-06:00"
    else:
        use_this_format = format

    return date_to_format.strftime(use_this_format) 

@blueprint.app_template_filter('get_ordinal_suffix')
def get_ordinal_suffix(n):
    
    """
    Takes a number (n) and adds the ordinal suffix. If the value cannot be converted
    to an integer, then the number (string?) is simply returned 

    1 => 1st
    303 => 303rd

    """
    suffixes = ["st", "nd", "rd"]
    suffix = "th"

    try:
        n = int(n)
        if n % 100//10 != 1:
            if n % 10 == 1:
                suffix = "st"
            elif n % 10 == 2:
                suffix = "nd"
            elif n % 10 == 3:
                suffix = "rd"
            else:
                suffix = "th"
        else:
            suffix = "th"

           
        return "{}{}".format(n, suffix)
    except ValueError:
        # There is a "Cook County" eventually coming through this function, so just return it
        return n

@blueprint.app_template_filter('check_if_is_okay_to_publish')
# @jinja2.contextfilter
def check_if_is_okay_to_publish(photo, BUCKET_NAME):
    """
    Takes a p2p data dict and determines if it is okay to publish this content item. It will return true
    in all cases except when the content is not set to Live and the publish url is the production bucket
    """
    # TODO: Make this work!

    if BUCKET_NAME and BUCKET_NAME.upper() == "PRODUCTION":
        #  If we're publishing live
        working_state = photo['content_item_state_code'].upper()
        if (working_state == "LIVE"):
            # Photo must be set to live when publishing to prod
            return True
        # If it is not set to live, do not output
        print (puts(colored.red("This photo is NOT set live: {}".format(photo['slug']))))
        return False
    # Since we're either publishing local or staging, go ahead and allow it.
    # IMPORTANT NOTE: This just tests the s3 bucket. If a new bucket is identified
    # and it is named something else, such as "project_prod", then our check 
    # will not catch it. The assumption here is that the only live-to-the-public 
    # bucket is "production" 

    return True

@blueprint.app_template_filter('strip_whitespace')
def strip_whitespace(text):
    """
    Removes leading and trailing whitespace 
    """
    return text.strip()

@blueprint.app_template_filter('dumb_to_smart_quotes')
def dumb_to_smart_quotes(string):
    """
    Takes a string and returns it with dumb quotes, single and double,
    replaced by smart quotes. Accounts for the possibility of HTML tags
    within the string.

    https://gist.github.com/davidtheclark/5521432
    """

    # Find dumb double quotes coming directly after letters or punctuation,
    # and replace them with right double quotes.
    string = re.sub(r'([a-zA-Z0-9.,?!;:\'\"])"', r'\1&#8221;', string)
    # Find any remaining dumb double quotes and replace them with
    # left double quotes.
    string = string.replace('"', '&#8220;')
    # Reverse: Find any SMART quotes that have been (mistakenly) placed around HTML
    # attributes (following =) and replace them with dumb quotes.
    string = re.sub(r'=&#8220;(.*?)&#8221;', r'="\1"', string)
    # Follow the same process with dumb/smart single quotes
    string = re.sub(r"([a-zA-Z0-9.,?!;:\"\'])'", r'\1&#8217;', string)
    string = string.replace("'", '&#8216;')
    string = re.sub(r'=&#8216;(.*?)&#8217;', r"='\1'", string)
    return string


@blueprint.app_template_filter('get_photo_limit')
def get_photo_limit(design):
    """
    The numerous photo designs breakdown with too many photos. This filter will
    return a limit on the number of photos allowed. The returned value is used as a limiter
    on the for loop which outputs the individual images.
    """
    
    design = int(design)

    if design == 0:
        # option 0 is a gallery, so it doesn't realy need any limits. We'll use 100 as an analogue for "unlimited"
        return 100
    elif design == 1:
        # Option 1 is just plain ol' stacked photos, one after another. Again, no limit needed.
        return 100
    elif design == 2:
        # Side by side.
        return 2
    elif design == 3:
        # Side by side with a fullwidth photo on top.
        return 3
    elif design == 4:
        # 2x2 grid
        return 4
    elif design == 5:
        # Not sure what this one is, yet. 
        return 2
    # If the user has selected a design that's not yet defined, return our "unlimited"
    return 100


@blueprint.app_template_filter('find_inline_link')
@jinja2.contextfilter
def find_inline_link(ctx, words):
    """
    Looks for '{{ ROOT URL }}' and return the actual root url
    """
    return words.replace('{{ ROOT_URL }}', ctx['ROOT_URL'])


# ##############################
# # THIS IS THE ARCHIEML STUFF #
# ##############################

@blueprint.app_template_filter()
def add_ptags(text):
    p_text = '<p>'+text; # opening p
    p_text = p_text.replace('\n', '</p><p>') + '</p>' # closing p
    return Markup(p_text)

@blueprint.app_template_filter()
def format(title):
  return title.replace('-', ' ').capitalize()

@blueprint.app_template_filter()
def lower(filename):
  return filename.lower()




@register_hook('newproject')
def newproject_add_doc_key(site, git):
    """
    With all the caveats referenced in `newproject_add_excludes in viz_tools`, 
    add a variable, DOC_KEY, to tarbell_config.py to allow easy access to the 
    ArchieML downloading/parsing. We'll do this with string.replace() because 
    we can't make a config template. We need to open and edit it in place.

    This is an old issue: https://github.com/tarbell-project/tarbell/issues/308 
    
    # Google spreadsheet key
    SPREADSHEET_KEY = "1lZHJ_xisqmVYOxtgGgKao4kwUUbgoPJWqd9HrO5qeNY"


    """
    
    tarbell_config_path = os.path.join(site.path, 'tarbell_config.py')
    
    with codecs.open(tarbell_config_path, 'r') as f:
        tarbell_config = f.read()

    
    doc_key_strings = "# Google document key for the stories. If not specified, the Archie stuff is skipped\n# DOC_KEY = \"None\"\n\n# Google spreadsheet key"
    tarbell_config = tarbell_config.replace("# Google spreadsheet key", doc_key_strings)

    with codecs.open(tarbell_config_path, 'w') as f:
        f.write(tarbell_config)

    git.commit('tarbell_config.py', '-m', "Add option for ArchieML/DOC_KEY")

