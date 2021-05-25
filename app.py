import datetime
import json
import os
import secrets
import requests
from functools import wraps
from flask import Flask, session, request, send_from_directory, redirect, render_template
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton

app = Flask(__name__)
with open('settings.json', 'r') as f:
    s = str(f.read())
    s = json.loads(s)
ur = f'{s["protocol"]}://{s["host"]}:{s["port"]}'
bot = Bot(s['token'])
app.secret_key = secrets.token_urlsafe(30)
app.config['UPLOAD_FOLDER'] = s['upload_folder']
app.config['PAGES_FOLDER'] = s['pages_folder']
app.config["url"] = ur
urls = []
admins = ['1023708694']


def is_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'login' in session and session['login']:
            return func(*args, **kwargs)
        return render_template('login.html')

    return wrapper


@app.route('/lo/<token>', methods=['GET'])
def login(token):
    with open('links.json', 'r') as f:
        s = str(f.read())
        js = json.loads(s)
    if token in js['links']:
        js['links'].remove(token)
        with open('links.json', 'w') as f:
            json.dump(js, f)
        session['login'] = True
    return redirect('/')


@app.route('/login', methods=['POST'])
def login_():
    id = request.form.get('id')
    if id in admins:
        with open('links.json', 'r') as f:
            s = str(f.read())
            js = json.loads(s)
        with open('links.json', 'w') as f:
            s = secrets.token_urlsafe(30)
            js['links'].append(s)
            json.dump(js, f)
        try:
            k = [[InlineKeyboardButton('Клик!', url=f'{ur}/lo/{s}')]]
            k = InlineKeyboardMarkup(k)
            bot.send_message(chat_id=id, text=f'Ссылка для входа:', reply_markup=k)
        except:
            pass
    return redirect('/')


@app.route('/')
@is_login
def home():
    return render_template('home.html')


@app.route('/urls')
@is_login
def urls_tools():
    return render_template('urls.html', last='', host=app.config["url"])


@app.route('/create_url', methods=['POST'])
@is_login
def create_url():
    if request.form.get('url2') != '' and request.form.get('url1') != '':
        with open('package.json', 'r') as f:
            s = str(f.read())
            js = json.loads(s)
            js[request.form.get('url2')] = request.form.get('url1')
        with open('package.json', 'w') as f:
            json.dump(js, f)
    return render_template('urls.html',
                           last=f'Ссылка: {app.config["url"]}/links/{request.form.get("url2")}',
                           href=f'/links/{request.form.get("url2")}', host=app.config["url"])


@app.route('/links/<l>')
def red(l):
    with open('package.json', 'r') as f:
        s = str(f.read())
        js = json.loads(s)
    try:
        return redirect(js[l])
    except:
        return 'ERROR'


@app.route('/delete/<l>')
@is_login
def dele(l):
    with open('package.json', 'r') as f:
        s = str(f.read())
        js = json.loads(s)
        js.pop(l, None)
    with open('package.json', 'w') as f:
        json.dump(js, f)
    return redirect('/worklinks')


@app.route('/worklinks')
@is_login
def ret():
    html = '''
  <table border="1" width="100%" cellpadding="5">
   <tr>
    <th>Сокращённая ссылка</th>
    <th>Старая ссылка</th>
    <th><a href="/">Главная</a></th>
   </tr>
   '''
    with open('package.json', 'r') as f:
        s = str(f.read())
        js = json.loads(s)
    for i in js.keys():
        html += f'<tr><td><a href="{app.config["url"]}/links/{i}">{app.config["url"]}/links/{i}</a></td>' \
                f'<td><a href="{js[i]}">{js[i]}</a></td>' \
                f'<td><a href="delete/{i}"><button>Удалить</button></a></td></tr>'
    html += '</table>'
    return html


@app.route('/files')
@is_login
def fi():
    return render_template('files.html')


@app.route('/save', methods=['POST'])
@is_login
def sa():
    file = request.files['file']
    if file:
        filename = file.filename
        file.save(f'{app.config["UPLOAD_FOLDER"]}/{filename}')
        return render_template('files.html', href=f'{app.config["url"]}/download/{filename}')
    return 'ERROR'


@app.route('/download/<f>')
def download(f):
    return send_from_directory(app.config["UPLOAD_FOLDER"], f)


@app.route('/allfiles')
@is_login
def allfiles():
    html = '''
  <table border="1" width="100%" cellpadding="5">
   <tr>
    <th>Файл</th>
    <th>Ссылка</th>
    <th><a href="/">Главная</a></th>
   </tr>
   '''
    for i in os.listdir(app.config['UPLOAD_FOLDER']):
        html += f'<tr><td><a href="{app.config["url"]}/download/{i}">{i}</a></td>' \
                f'<td><a href="{app.config["url"]}/download/{i}">{app.config["url"]}/download/{i}</a></td>' \
                f'<td><a href="deletef/{i}"><button>Удалить</button></a></td></tr>'
    html += '</table>'
    return html


@app.route('/deletef/<f>')
@is_login
def deletef(f):
    if f in os.listdir(app.config["UPLOAD_FOLDER"]):
        os.remove(f'{app.config["UPLOAD_FOLDER"]}/{f}')
    return redirect('/allfiles')


@app.route('/savepage', methods=['POST'])
@is_login
def savepage():
    file = request.files['file']
    if file:
        filename = file.filename
        file.save(f'{app.config["PAGES_FOLDER"]}/{filename}')
        return render_template('savehtml.html', href=f'{app.config["url"]}/{app.config["PAGES_FOLDER"]}/{filename}')
    return 'ERROR'


@app.route('/html')
@is_login
def htm():
    return render_template('savehtml.html')


@app.route('/pages/<f>')
def pages(f):
    if f in os.listdir(app.config["PAGES_FOLDER"]):
        return send_from_directory(app.config["PAGES_FOLDER"], f)
    return 'ERROR'


@app.route('/deletep/<f>')
@is_login
def deletep(f):
    if f in os.listdir(app.config["PAGES_FOLDER"]):
        os.remove(f'{app.config["PAGES_FOLDER"]}/{f}')
    return redirect('/allpages')


@app.route('/allpages')
@is_login
def allpages():
    html = '''
  <table border="1" width="100%" cellpadding="5">
   <tr>
    <th>HTML</th>
    <th>Ссылка</th>
    <th><a href="/">Главная</a></th>
   </tr>
   '''
    for i in os.listdir(app.config["PAGES_FOLDER"]):
        html += f'<tr><td><a href="{app.config["url"]}/pages/{i}">{i}</a></td>' \
                f'<td><a href="{app.config["url"]}/pages/{i}">{app.config["url"]}/pages/{i}</a></td>' \
                f'<td><a href="deletep/{i}"><button>Удалить</button></a></td></tr>'
    html += '</table>'
    return html


@app.route('/r/<link>')
def redir(link):
    with open('lin.json', 'r') as f:
        s = str(f.read())
        js = json.loads(s)
    if link in js.keys():
        d = requests.get(f'http://ipinfo.io/{request.remote_addr}/json').json()
        j = dict()
        j['time'] = str(datetime.datetime.now())
        j['ip'] = request.remote_addr
        if 'city' in d.keys():
            j['city'] = d['city']
        else:
            j['city'] = '-'
        if 'country' in d.keys():
            j['country'] = d['country']
        else:
            j['country'] = '-'
        if 'timezone' in d.keys():
            j['timezone'] = d['timezone']
        else:
            j['timezone'] = '-'
        js[link]['pereh'].append(j)
        with open('lin.json', 'w') as f:
            json.dump(js, f)
        return redirect(js[link]['redirect'])
    else:
        return 'ERROR'


@app.route('/make_r')
@is_login
def make_r():
    return render_template('r.html', last='', host=app.config["url"])


@app.route('/create_r', methods=['POST'])
@is_login
def create_r():
    if request.form.get('url2') != '' and request.form.get('url1') != '':
        with open('lin.json', 'r') as f:
            s = str(f.read())
            js = json.loads(s)
            js[request.form.get('url2')] = {"redirect": request.form.get('url1'), "pereh": []}
        with open('lin.json', 'w') as f:
            json.dump(js, f)
    return render_template('r.html',
                           last=f'Ссылка: {app.config["url"]}/r/{request.form.get("url2")}',
                           href=f'/r/{request.form.get("url2")}', host=app.config["url"])


@app.route('/info/<name>')
@is_login
def info_name(name):
    with open('lin.json', 'r') as f:
        s = str(f.read())
        js = json.loads(s)
    html = f'''
    <table border="1" width="100%" cellpadding="5">
   <tr>
    <th>ip</th>
    <th>Город</th>
    <th>Страна</th>
    <th>Временная зона</th>
    <th>Время</th>
   </tr>
   '''
    for i in js[name]["pereh"]:
        html += f'<tr><td>{i["ip"]}</td>' \
                f'<td>{i["city"]}</td>' \
                f'<td>{i["country"]}</td>' \
                f'<td>{i["timezone"]}</td>' \
                f'<td>{i["time"]}</td></tr>'
    html += '</table>'
    return html


@app.route('/allr')
@is_login
def allr():
    html = '''
  <table border="1" width="100%" cellpadding="5">
   <tr>
    <th>Ссылка</th>
    <th>Подробная инфармация</th>
    <th><a href="/">Главная</a></th>
   </tr>
   '''
    with open('lin.json', 'r') as f:
        s = str(f.read())
        js = json.loads(s)
    for i in js.keys():
        html += f'<tr><td><a href="{app.config["url"]}/r/{i}">{app.config["url"]}/r/{i}</a></td>' \
                f'<td><a href="{ur}/info/{i}">Подробнее</a></td>' \
                f'<td><a href="deleter/{i}"><button>Удалить</button></a></td></tr>'
    html += '</table>'
    return html


@app.route('/deleter/<l>')
@is_login
def deler(l):
    with open('lin.json', 'r') as f:
        s = str(f.read())
        js = json.loads(s)
        js.pop(l, None)
    with open('lin.json', 'w') as f:
        json.dump(js, f)
    return redirect('/allr')


if __name__ == '__main__':
    app.run(host=s['host'], port=s['port'])
