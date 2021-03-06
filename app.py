import csv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file
from gevent.pywsgi import WSGIServer
import statistics as gr
import matplotlib.pyplot as plt
import numpy as np
import parser_vk as vk
import random
import seaborn as sns


app = Flask(__name__, static_folder='static', template_folder='templates')


@app.route('/', methods=['post', 'get'])
def data_input():
    message = ''
    if request.method == 'POST':
        global user_id, date
        user_id = request.form.get('user_id')
        date = request.form.get('date')
        if user_id != '':
            try:
                # in browsers other than google chrome, the date should be
                # entered in YYYY-MM-DD format
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


def what_to_parse(name, post):
    """
    Selection of parameters for parsing
    :param name: key name
    :param post: list of posts to parse
    :return: calls specific parser
    """
    names = ['likes', 'comments', 'reposts']
    for one in names:
        if one == name:
            return vk.parse(post, one)
    if name == 'id':
        return vk.ids_parse(post)
    elif name == 'text':
        return vk.text_parse(post)
    elif name == 'attachments':
        return vk.attachments_parse(post)
    elif name == 'num_attachments':
        return vk.num_attachments_parse(post)


@app.route('/choose_values', methods=['post', 'get'])
def choose_values():
    global parsed_data
    parsed_data = {}
    names = ['id', 'text', 'attachments', 'num_attachments', 'likes',
             'reposts', 'comments']
    for name in names:
        if request.form.get(name):
            parsed_data.update({name: what_to_parse(name, posts)})
    if parsed_data:
        return redirect(url_for('download_csv'))
    else:
        message = 'Please choose tha data you need'
        return render_template('choose_values.html', message=message)


@app.route('/download_csv', methods=['get'])
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
                     mimetype='text/csv',
                     as_attachment=True)


@app.route('/graphic', methods=['post', 'get'])
def graphic():
    msg = ''
    plot = ''
    if request.method == 'POST':
        global period, value
        period = request.form.get('period')
        value = request.form.get('value')
        if value == 'posts':
            data = gr.post_statistics(period, posts)
        else:
            data = gr.average_statistics(period, value, posts)
        if type(data) == str:
            msg = data
            return render_template('graphic.html', msg=msg)
        else:
            plot = plotting(data)
            msg = 'Statistics:'
            return render_template('graphic.html', msg=msg, plot=plot)
    return render_template('graphic.html', msg=msg, plot=plot)


def plotting(values):
    y = np.array(list(values.values()))
    x = np.array(list(values.keys()))
    sns.barplot(x, y, palette='bright')
    plt.title(f'Number of {value} by {period}')
    plt.ylabel(f'number of {value}')
    plt.xlabel(period)
    file_name = f'{value}_{period}_{user_id}.png'
    plt.savefig(f'static/{file_name}')
    plt.close('all')
    return file_name


if __name__ == "__main__":
    # app.run(debug=True)
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
