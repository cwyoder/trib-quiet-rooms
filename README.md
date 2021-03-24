NOTE: ALL MEDIA HAS BEEN REMOVED FROM REPOSITORY TO MAKE IT PUBLIC

# Illinois school seclusion

A [Tarbell](http://tarbell.io) project.

Assumptions
-----------

* Python 2.7
* Tarbell 1.0.\*
* Node.js
* grunt-cli (See http://gruntjs.com/getting-started#installing-the-cli)
* Sass

Custom configuration
--------------------

## DEFAULT_CONTEXT['OMNITURE']

This project uses [python-tribune-omniture](https://github.com/newsapps/python-tribune-omniture) to render the Omniture `<script>` tags for the Tribune's analytics.  You'll need to configure the dictionary named `OMNITURE` in the `DEFAULT_CONTEXT` dictionary in your `tarbell_config.py`:


    DEFAULT_CONTEXT = {
        'name': 'lead',
        'title': 'Lead',
        'analytics_path': '',
        'OMNITURE': {
            'domain': 'chicagotribune.com',
            'sitename': 'Chicago Tribune',
            'section': 'news',
            'subsection': 'watchdog',
            'subsubsection': '',
            'type': 'dataproject',
        },
    }

Building front-end assets
-------------------------

This project uses [npm scripts](https://css-tricks.com/why-npm-scripts/) with a little help from [Grunt](http://gruntjs.com/) to build front-end assets.

To compile CSS and JavaScript for this project, first install the build tool depenencies:

    npm install

When you run:

    npm run build    

npm will compile `sass/styles.scss` into `css/styles.css` and bundle/minify `js/src/app.js` into `js/app.min.js`.

If you want to recompile as you develop, run:

    npm run build && npm run watch


The blueprint simply sets up the the build tools to generate `styles.css` and `js/app.min.js`, you'll have to explicitly update your templates to point to these generated files.  The reason for this is to make you think about whether you're actually going to use an external CSS or JavaScript file and avoid a request for an empty file if you don't end up putting anything in your custom stylesheet or JavaScript file.

To add `styles.css`, add this to your template file (likely, `index.html`):

    
    <link rel="stylesheet" href="css/styles.css">
    

To add `app.min.js` to your template file:

    
    <script src="js/app.min.js"></script>
    
