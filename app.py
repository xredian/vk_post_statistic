import csv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file
import parser_vk as vk
import random

app = Flask(__name__)


@app.route('/', methods=['post', 'get'])
def data_input():
    message = ''
    if request.method == 'POST':
        global user_id
        user_id = request.form.get('user_id')
        date = request.form.get('date')
        if user_id != '' and datetime.strptime(date, '%Y-%m-%d'):
            global posts
            posts = vk.get_posts(user_id, date)
            return redirect(url_for('choose'))
        else:
            message = "Please enter user/community id and date"
    return render_template('input.html', message=message)


def func(name, value):
    if name == 'post_ids':
        return vk.ids_parse(value)
    elif name == 'text':
        return vk.text_parse(value)
    elif name == 'attachments':
        return vk.attachments_parse(value)
    elif name == 'num_attachments':
        return vk.num_attachments_parse(value)
    elif name == 'num_likes':
        return vk.likes_parse(value)
    elif name == 'num_reposts':
        return vk.reposts_parse(value)
    elif name == 'num_comments':
        return vk.comments_parse(value)


@app.route('/choose', methods=['post', 'get'])
def choose():
    global parsed_data
    parsed_data = {}
    names = ['post_ids', 'text', 'attachments', 'num_attachments', 'num_likes',
             'num_reposts', 'num_comments']
    for name in names:
        if request.form.get(name):
            parsed_data.update({name: func(name, posts)})
    if parsed_data:
        return redirect(url_for('download_csv', parsed_data=parsed_data))
    else:
        message = 'Please choose tha data you need'
        return render_template('choose.html', message=message)


@app.route('/download_csv', methods=['post', 'get'])
def download_csv():
    rnd = round(random.random()*100)
    with open(f'{rnd}_{user_id}_statistics.csv', "w", encoding='utf-8-sig') as file:
        columns = [*parsed_data]
        writer = csv.writer(file)
        writer.writerow(columns)
        for elem in range(len(list(parsed_data.values())[0])):
            writer.writerow((parsed_data[key][elem] for key in columns))
    return send_file(f'{rnd}_{user_id}_statistics.csv',
                     mimetype='txt/csv',
                     as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
