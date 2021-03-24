
######### Specifically for the ArchieML

import htmlmin # to minify html

import codecs, archieml
from subprocess import call
# from collections import OrderedDict
# from jinja2 import Markup
# from jinja2.exceptions import TemplateNotFound
# from pprint import pprint
from apiclient import errors

# imports bc copied blueprint functions #
from clint.textui import colored
# import p2p
from tarbell.utils import puts
from tarbell.oauth import get_drive_api
from tarbell.hooks import register_hook




##############################
# THIS IS THE ARCHIEML STUFF #
##############################

def get_drive_api_stuff(site, DOC_KEY):
    
    service = get_drive_api()
    try:
        docfile = service.files().get(fileId=DOC_KEY).execute()
        downloadurl = docfile['exportLinks']['text/html'] # export as 'text/html' instead of 'text/plain' if we want to parse links and styles
        resp, content = service._http.request(downloadurl)
        print ">>>>> WRITING TO OUT_DRIVE.HTML"
        # write to file
        with open('out_drive.html', 'w+') as f:
            text = content.decode("utf-8-sig", errors='ignore') # get rid of BOM
            f.write(text.encode('utf8', 'replace')) # lol
        return text
    except errors.HttpError, error:
        print 'An error occurred: %s' % error

def get_extra_context():
    print ">>>>> PARSING NEW STORY"
    call(["node", "_blueprint/scripts/js_parser.js", "out_drive.html"]) # parse the html before loading it into archieML
    with open('./out_parsed.txt') as f:
        data = archieml.load(f)
    data = dict(data)
    return data



# @blueprint.app_template_filter()
# def add_ptags(text):
#     p_text = '<p>'+text; # opening p
#     p_text = p_text.replace('\n', '</p><p>') + '</p>' # closing p
#     return Markup(p_text)

# @blueprint.app_template_filter()
# def format(title):
#   return title.replace('-', ' ').capitalize()

# @blueprint.app_template_filter()
# def lower(filename):
#   return filename.lower()

def _get_published_content(site, s3, **extra_context):
    template = site.app.jinja_env.get_template('_content.html')
    context = site.get_context(publish=True)
    context.update(extra_context)
    rendered = template.render(**context)

    return rendered

def p2p_publish_archiemlstory(site, s3):
    if not is_production_bucket(s3.bucket, site.project.S3_BUCKETS):
        puts(colored.red(
            "\nNot publishing to production bucket. Skipping P2P publiction."))
        return

    context = site.get_context(publish=True)

    # Handle old-style configuration for publishing HTML story from values
    # worksheet. This is deprecated, but still support it in case someone
    # accidentally upgrades their blueprint in an old project
    try:
        content_item = get_deprecated_htmlstory_config(context)
        msg = ("\nYou've configured your HTML story in the 'values' worksheet. "
                "Don't do this. It will work for now, but may stop working "
                "soon. Instead, configure it in the 'p2p_content_items' "
                "worksheet.")
        puts(colored.red(msg))
        p2p_publish_htmlstory(content_item, site, s3)

    except KeyError:
        # This is fine. Actually preferred. There shouldn't be anything
        # P2P-related
        pass

    try:
        content_items = context[CONTENT_ITEMS_WORKSHEET]
    except KeyError:
        # No worksheet with the P2P content item configuration.  Fail!
        msg = ("\nYou need a worksheet named {0} in your Tarbell spreadsheet "
               "to publish P2P content items").format(CONTENT_ITEMS_WORKSHEET)
        puts(colored.red(msg))
        return

    for i, content_item in enumerate(content_items):
        try:
            content_type = content_item['content_type']
        except KeyError:
            msg = ("\nYou need to specify a content type for P2P content "
                    "item {0}").format(i)
            continue

        try:
            if content_type == 'blurb':
                p2p_publish_blurb(content_item, site, s3)

            elif content_type == 'htmlstory':
                p2p_publish_htmlstory(content_item, site, s3)

            else:
                msg = ("\nUnknown content type '{0}' for P2P content "
                       "item {1}. Skipping publication.").format(content_type, i)
                puts(colored.yellow(msg))
                continue

        except MissingP2PContentItemFieldError as e:
            # The spreadsheet is missing a field needed to publish. Fail
            # gracefully.
            msg = ("\nYou need to specify field '{0}' for P2P content "
                    "item {1}. Skipping publication.").format(e.field_name, i)
            puts(colored.yellow(msg))
            continue

        except TemplateNotFound:
            msg = ("\nCould not find template '{0}' for P2P content "
                   "item {1}. Skipping publication").format(
                       content_item['template'], i)
            puts(colored.yellow(msg))
            continue


def refresh_archie(site, temp_dir=False, pub_details=False):
    """
    This function only exists to call the update() method from within the hooks
    """

    try:
        """
        If a DOC_KEY is defined, then updating the ArchieML will work.
        """        
        get_drive_api_stuff(site, site.project.DOC_KEY)
        site.project.DEFAULT_CONTEXT.update(**get_extra_context())
        print("\n>>>>> Refreshing ArchieML content")
        
        # Clean up the temporary files
        call(["rm", "-rf", "out_drive.html"]) 
        call(["rm", "-rf", "out_parsed.txt"]) 


    except:
        """
        If a DOC_KEY is not defined, then keep moving
        """
        print("\n>>>>> No Google Doc key provided, thus no ArchieML to update")