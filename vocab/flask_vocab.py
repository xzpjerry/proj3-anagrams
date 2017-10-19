"""
Flask web site with vocabulary matching game
(identify vocabulary words that can be made 
from a scrambled string)
"""

import flask
import logging

# Our own modules
from letterbag import LetterBag
from vocab import Vocab
from jumble import jumbled
import config

###
# Globals
###
app = flask.Flask(__name__)

CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY  # Should allow using session variables

#
# One shared 'Vocab' object, read-only after initialization,
# shared by all threads and instances.  Otherwise we would have to
# store it in the browser and transmit it on each request/response cycle,
# or else read it from the file on each request/responce cycle,
# neither of which would be suitable for responding keystroke by keystroke.

WORDS = Vocab(CONFIG.VOCAB)

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    """The main page of the application"""
    flask.g.vocab = WORDS.as_list()
    flask.session["target_count"] = min(
        len(flask.g.vocab), CONFIG.SUCCESS_AT_COUNT)
    flask.session["jumble"] = jumbled(
        flask.g.vocab, flask.session["target_count"])
    flask.session["matches"] = []
    app.logger.debug("Session variables have been set")
    assert flask.session["matches"] == []
    assert flask.session["target_count"] > 0
    app.logger.debug("At least one seems to be set correctly")
    return flask.render_template('vocab.html')


#######################
# Form handler.
# CIS 322 note:
#   You'll need to change this to a
#   a JSON request handler

# Done!
#######################

# Add parameters just for the test purpose
def repeated(text, matches):
    return (text in matches)

def in_jumble(text, jumble):
    return LetterBag(jumble).contains(text)

def matched(text, WORDS = WORDS):
    return WORDS.has(text)

def find_new_word(text, jumble, WORDS, matches):
    return matched(text, WORDS) and in_jumble(text, jumble) and not repeated(text, matches)

@app.route("/_check")
def check():
    """
    () -> {"text":string, "matches":[], "target_count": int, "jumble": []}

    User has submitted the form with a word ('attempt')
    that should be formed from the jumble and on the
    vocabulary list.  We respond depending on whether
    the word is on the vocab list (therefore correctly spelled),
    made only from the jumble letters, and not a word they
    already found.
    """
    app.logger.debug("Entering check")

    # The data we need, from form and from cookie
    jumble = flask.session["jumble"]
    matches = flask.session.get("matches", [])  # Default to empty list

    # Get data from request.args
    text = flask.request.args.get("text", type=str)
    rslt = {"text": text, 'matches': matches,
            'target_count': flask.session["target_count"], "jumble": jumble}

    def matcher():
        '''
        (bool, bool) -> int

        A func for examining user's performance 
        '''
        if find_new_word(text, jumble, WORDS, matches):
            # Cool, they found a new word
            rslt['matches'].append(text)
            flask.session["matches"] = rslt['matches']
            return 0

        # input a repeated word
        elif repeated(text, matches):
            return 1

        # input a word that isn't in the list
        elif not matched(text):
            return 2

        # input a word that is in the list but cannot be made
        elif not in_jumble(text, jumble):
            return 3
        else:
            app.logger.debug("This case shouldn't happen!")
            assert False  # Rm.aises AssertionError

    rslt['status_num'] = matcher()

    return flask.jsonify(result=rslt)


###############
# AJAX request handlers
#   These return JSON, rather than rendering pages.
###############


@app.route("/_example")
def example():
    """
    Example ajax request handler
    """
    app.logger.debug("Got a JSON request")
    rslt = {"key": "value"}
    return flask.jsonify(result=rslt)


#################
# Functions used within the templates
#################

@app.template_filter('filt')
def format_filt(something):
    """
    Example of a filter that can be used within
    the Jinja2 code
    """
    return "Not what you asked for"

###################
#   Error handlers
###################


@app.errorhandler(404)
def error_404(e):
    app.logger.warning("++ 404 error: {}".format(e))
    return flask.render_template('404.html'), 404


@app.errorhandler(500)
def error_500(e):
    app.logger.warning("++ 500 error: {}".format(e))
    assert not True  # I want to invoke the debugger
    return flask.render_template('500.html'), 500


@app.errorhandler(403)
def error_403(e):
    app.logger.warning("++ 403 error: {}".format(e))
    return flask.render_template('403.html'), 403


####

if __name__ == "__main__":
    if CONFIG.DEBUG:
        app.debug = True
        app.logger.setLevel(logging.DEBUG)
        app.logger.info(
            "Opening for global access on port {}".format(CONFIG.PORT))
        app.run(port=CONFIG.PORT, host="0.0.0.0")
