from www import app
from flask import render_template, url_for, request
import copy
import re


def to_utf8(i):
    try:
        c = chr(i).encode('utf8')
        return chr(i)
    except UnicodeEncodeError as e:
        return ''

@app.before_first_request
def init():
    app.uinfo.load()
    
@app.route('/')
def welcome():
    blocks = app.uinfo.get_block_infos()
    b1 = blocks[:int(len(blocks)/2)]
    b2 = blocks[int(len(blocks)/2):] 
    data = { 
        "chars": app.uinfo.get_random_char_infos(32),
        "blocks1": b1,
        "blocks2": b2
    }
    return render_template("welcome.html", data=data)

@app.route('/c/<code>')
def show_code(code):
    app.logger.info('get /c/{}'.format(code))
    if not re.match('^[0-9A-Fa-f]{1,6}$', code):
        return render_template("404.html")
    
    code = int(code.lower(), 16)
    info = copy.deepcopy(app.uinfo.get_char(code))
    
    related = []
    for r in info['related']:
        related.append(app.uinfo.get_char_info(r))
    info["related"] = related
    
    confusables = []
    for r in info["confusables"]:
        confusables.append(app.uinfo.get_char_info(r))
    info["confusables"] = confusables
    
    info["case"] = app.uinfo.get_char_info(info["case"])
    info["prev"] = app.uinfo.get_char_info(info["prev"])
    info["next"] = app.uinfo.get_char_info(info["next"])
    
    info["block"] = app.uinfo.get_block_info(info["block"])
    info["subblock"] = app.uinfo.get_subblock_info(info["subblock"])
    
    return render_template("code.html", data=info)

@app.route('/b/<code>')
def show_block(code):
    app.logger.info('get /b/{}'.format(code))
    if not re.match('^[0-9A-Fa-f]{1,6}$', code):
        return render_template("404.html")
    
    code = int(code.lower(), 16)
    info = copy.deepcopy(app.uinfo.get_block(code))
    if not info:
        return render_template("404.html")
    
    chars = []
    for c in range(info["range_from"], info["range_to"]+1):
        chars.append(app.uinfo.get_char_info(c))
    info["chars"] = chars
    
    info["prev"] = app.uinfo.get_block_info(info["prev"])
    info["next"] = app.uinfo.get_block_info(info["next"])
    
    return render_template("block.html", data=info)


@app.route('/search', methods=['POST'])
def search():
    query = request.form['q']
    app.logger.info('get /search/{}'.format(query))
    matches, msg = app.uinfo.search_by_name(query, 100)
    return render_template("search_results.html", msg=msg, matches=matches)
