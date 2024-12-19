from flask import Flask, render_template

app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello():
    return render_template('index.html')

@app.route('/python-2', methods=['POST'])
def python2():
    return render_template('python2.html')

@app.route('/python-3', methods=['POST'])
def python3():
    return render_template('python3.html')

if __name__ == '__main__':
    app.run(debug=True)
