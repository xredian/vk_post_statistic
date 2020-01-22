import csv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file
from gevent.pywsgi import WSGIServer
import graphics as gr
import matplotlib.pyplot as plt
import numpy as np
import parser_vk as vk
import random
import seaborn as sns


app = Flask(__name__)


@app.route('/', methods=['post', 'get'])
def data_input():
    message = ''
    if request.method == 'POST':
        global user_id, date
        user_id = request.form.get('user_id')
        date = request.form.get('date')
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            message = 'Please, input date in YYYY-MM-DD format'
            return render_template('input.html', message=message)
        if user_id != '' and date != '':
            global posts
            posts = vk.get_wall(user_id, date)
            if not posts:
                message = 'There is no posts for specified period'
                return render_template('input.html', message=message)
            return redirect(url_for('choose'))
        else:
            message = "Please enter user/community id and date"
    return render_template('input.html', message=message)


@app.route('/choose', methods=['post', 'get'])
def choose():
    if request.form.get('Download') == 'Download':
        return redirect(url_for('choose_values'))
    elif request.form.get('Graphic') == 'Graphic':
        return redirect(url_for('graphic'))
    return render_template('choose.html')


def wt_parse(name, post):
    """
    Selection of parametrs for patsing
    :param name: key name
    :param post: list of posts to parse
    :return: calls specific parser
    """
    if name == 'post_ids':
        return vk.ids_parse(post)
    elif name == 'text':
        return vk.text_parse(post)
    elif name == 'attachments':
        return vk.attachments_parse(post)
    elif name == 'num_attachments':
        return vk.num_attachments_parse(post)
    elif name == 'num_likes':
        return vk.likes_parse(post)
    elif name == 'num_reposts':
        return vk.reposts_parse(post)
    elif name == 'num_comments':
        return vk.comments_parse(post)


@app.route('/choose_values', methods=['post', 'get'])
def choose_values():
    global parsed_data
    parsed_data = {}
    names = ['post_ids', 'text', 'attachments', 'num_attachments', 'num_likes',
             'num_reposts', 'num_comments']
    for name in names:
        if request.form.get(name):
            parsed_data.update({name: wt_parse(name, posts)})
    if parsed_data:
        return redirect(url_for('download_csv', parsed_data=parsed_data))
    else:
        message = 'Please choose tha data you need'
        return render_template('choose_values.html', message=message)


@app.route('/download_csv', methods=['post', 'get'])
def download_csv():
    rnd = round(random.random() * 100)
    with open(f'{rnd}_{user_id}_statistics.csv', "w",
              encoding='utf-8-sig') as file:
        columns = [*parsed_data]
        writer = csv.writer(file)
        writer.writerow(columns)
        for elem in range(len(list(parsed_data.values())[0])):
            writer.writerow((parsed_data[key][elem] for key in columns))
    return send_file(f'{rnd}_{user_id}_statistics.csv',
                     mimetype='txt/csv',
                     as_attachment=True)


@app.route('/graphic', methods=['post', 'get'])
def graphic():
    message = ''
    plot = ''
    if request.method == 'POST':
        global period, value
        period = request.form.get('period')
        value = request.form.get('value')
        if value == 'posts':
            data = gr.post_stat(period, posts)
        else:
            data = gr.stat(period, value, posts)
        if type(data) == str:
            message = data
            return render_template('graphic.html', message=message)
        else:
            plot = plotting(data)
            if plot is None:
                message = 'There is no data for specified period'
                return render_template('graphic.html', message=message)
            else:
                message = 'Statistics:'
                if request.form.get('Download') == 'Download':
                    return redirect(url_for('download_png'))
    return render_template('graphic.html', message=message, plot=plot)


def plotting(values):
    global rn
    rn = round(random.random(), 2) * 100
    y = np.array(list(values.values()))
    x = np.array(list(values.keys()))
    if np.all(y == 0):
        return None
    sns.barplot(x, y, palette='bright')
    plt.title(f'Number of {value} by {period}')
    plt.ylabel(f'number of {value}')
    plt.xlabel(period)
    directory = f'{rn}_{user_id}_{value}_{period}.png'
    plt.savefig(f'static/{directory}')
    return directory


@app.route('/download_png', methods=['post', 'get'])
def download_png():
    return send_file(f'static/{rn}_{user_id}_{value}_{period}.png',
                     mimetype='png',
                     as_attachment=True)


if __name__ == "__main__":
    #app.run(debug=True)
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
