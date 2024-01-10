#!/usr/bin/python3
#
# AgileCards:
#
# Show images from a directory of images in random
# order with a browser via a webapplication until
# all images are shown and start over.
# Optionally a startbanner and a logo can be shown.
#
# Version 1.0: initial release
# Version 1.1: linted with Pylama
# Version 1.2: state is saved when card is OKed
# Version 1.3: added baseLink for app & templates
# Version 1.4: the logo is now optional
# Version 1.5: optional banner at startup
# Version 1.6: banner with expiring cookie
# Version 1.7: added reload-function
# Version 1.8: dynamic fileextensions for imagesfiles
#
# last updated by P.Schweizer on 31.12.2023 13:19
#

# import modules
import os
import sys
import random
import pickle
from flask import Flask, render_template, redirect, make_response, request
app = Flask(__name__)


# start of config:
servLink = '/agilecards'
testLink = 'http://127.0.0.1:8080'
imgFormats = ('.png', '.jpg', '.jpeg', '.gif')
# end of config.


# init vars
stateFile = os.path.join(app.root_path, 'agilecards.state')
imgDir = os.path.join(app.root_path, 'static')
testPort = testLink.split(':')[-1]
testIP = testLink.split(':')[-2]
testIP = ''.join(chr for chr in testIP if chr.isdigit() or chr == '.')
cardAmount = 0
cardFiles = []
cardUndo = []


# show version
print(" agilecards v.1.8 started")


# check and set baseLink
if sys.argv[0] == os.path.basename(__file__):
    # when first param of executed programm equals name
    # of current script, its running local for testing
    baseLink = testLink
else:
    baseLink = servLink


# load state if exist
if os.path.isfile(stateFile):
    print(" state-file found, loading - " + stateFile)
    with open(stateFile, 'rb') as file:
        cardFiles, cardAmount, cardUndo = pickle.load(file)
else:
    print(" no state-file found.")


# save state when card changes
def write_status_file():
    print(" card(s) changed, saving status - " + stateFile)
    with open(stateFile, 'wb') as file:
        pickle.dump([cardFiles, cardAmount, cardUndo], file)


# check and get image (first match)
def get_image_file(query):
    result = None
    for file in os.listdir(imgDir):
        if file.startswith(query) and file.endswith(imgFormats):
            result = file
            break
    if result is None:
        print(" no " + query + "-file found.")
    return (result)


# check and get card files
def get_card_files():
    results = []
    allFiles = os.listdir(imgDir)
    imgFiles = [file for file in allFiles if file.endswith(imgFormats)]
    results = [file for file in imgFiles if not file.startswith(('logo', 'banner'))]
    print(" cards found - " + str(results))
    return (results)


# default/index page
@app.route("/")
def index():
    # include banner if exist
    if get_image_file('banner') is not None:
        bannerImg = '<img src="' + baseLink + '/static/' + get_image_file('banner') + '">'
        templateData = {
            'Banner': bannerImg,
            'Link': baseLink,
        }
        # pass index page to browser and set expiring cookie
        response = make_response(render_template('index.html', **templateData))
        response.set_cookie('AgileCards', 'ShowBannerAgain', max_age=43200)
        return response
    else:
        # otherwise pass select page to browser
        return redirect(baseLink + "/select")


# select page
@app.route("/select")
def select():
    # make some vars global
    global cardUndo
    global cardFiles
    global cardAmount
    global statusMsg
    # load images if list is empty and shuffle them
    if len(cardFiles) <= 0:
        del cardUndo[:]
        cardFiles = get_card_files()
        cardAmount = len(cardFiles)
        random.shuffle(cardFiles)
        if len(cardFiles) <= 0:
            statusMsg = "no cards found!"
        else:
            statusMsg = "loaded & randomized cards:"
            write_status_file()
    else:
        statusMsg = "deck of cards:"
    # include logo if exist
    if get_image_file('logo') is not None:
        logoImg = '<img src="' + baseLink + '/static/' + get_image_file('logo') + '">'
    else:
        logoImg = ''
    # get data for the select page
    templateData = {
        'Message': statusMsg,
        'Cards': cardAmount,
        'Left': len(cardFiles),
        'Logo': logoImg,
        'Link': baseLink,
    }
    # check if cookie for banner expired and if a banner exist
    if (request.cookies.get('AgileCards') is None
       and get_image_file('banner') is not None):
        # jump to index page
        return redirect(baseLink)
    else:
        # pass select page to browser
        return render_template('select.html', **templateData)


# cards page
@app.route("/card")
def card():
    # get data for image or jump to select page
    if len(cardFiles) <= 0:
        return redirect(baseLink + "/select")
    else:
        templateData = {
            'Image': cardFiles[0],
            'Link': baseLink,
        }
        # pass card page to browser
        return render_template('card.html', **templateData)


# next operation
@app.route("/next")
def next():
    # set data for next image or jump to select page
    if len(cardFiles) <= 0:
        return redirect(baseLink + "/select")
    else:
        # add image to undo-buffer
        cardUndo.append(cardFiles[0])
        # remove image from list
        del (cardFiles[0])
        # save state
        write_status_file()
        # jump to select page
        return redirect(baseLink + "/select")


# undo operation
@app.route("/undo")
def undo():
    # restore image from undo or jump to select page
    if len(cardUndo) <= 0:
        return redirect(baseLink + "/select")
    else:
        # restore image from undo
        cardFiles.insert(0, cardUndo[-1])
        # remove image from undo
        del (cardUndo[-1])
        # save state
        write_status_file()
        # jump to select page
        return redirect(baseLink + "/select")


# reload operation
@app.route("/reload")
def reload():
    # empty the image list and jump to select page
    del cardFiles[:]
    return redirect(baseLink + "/select")


# start local flask server for testing
if __name__ == "__main__":
    app.run(host=testIP, port=testPort, debug=False)
