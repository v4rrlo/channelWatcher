#!flask/bin/python
from flask import Flask, render_template, jsonify, request
from dbmanager import *

app = Flask(__name__)
manager = DBManager('src/database.db')


@app.route('/')
@app.route('/index')
def index():
    streamers = manager.get_streamers()
    return render_template("index.html", streamers=streamers)


@app.route('/user/<username>')
def show_user_profile(username):
    data = manager.get_streamer_data(username)
    return render_template("user.html", data=data, streamer=username)


@app.route('/user/request', methods=['GET', 'POST'])
def found():
    if request.method == 'GET':
        return render_template("request.html",
                               data={})
    else:
        username = request.form['streamer']
        start_date = request.form['startdate']
        end_date = request.form['enddate']
        data = manager.get_streamer_data_specific_date(username, start_date,
                                                       end_date)
        return render_template("request.html",
                               streamer=username,
                               startdate=start_date,
                               enddate=end_date,
                               data=data)


if __name__ == '__main__':
    app.run(debug=True)
