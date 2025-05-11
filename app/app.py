import os
import sqlite3
from db import init_db
from flask import (Flask, url_for,
                   render_template, request, g, redirect)
from models.primers import Primers

current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
init_db()


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(os.path.join(os.path.dirname(__file__),
                                            "../data/primers_db.db"))
    return g.db


@app.route("/")
@app.route('/index')
def index():
    primers = Primers.all(get_db())
    return render_template("index.html", primers=primers)


@app.route('/pair/<gene_id>')
def pair(gene_id):
    primer_pair = Primers.get(gene_id, get_db())
    return render_template('pair.html', pair=primer_pair)


@app.route('/add', methods=['GET', 'POST', 'PUT'])
def add():
    if request.method == 'POST':
        primers = Primers(request.form['gene_id'], request.form['forward_primer'], request.form['reverse_primer'])
        primers.save(get_db())
        return redirect(url_for('pair', gene_id=primers.gene_id))
    else:
        return render_template('add.html')


@app.route('/edit/<gene_id>')
def edit(gene_id):
    primers = Primers.get(gene_id, get_db())
    return render_template('add.html', primers=primers)


@app.route('/delete/<gene_id>')
def delete(gene_id):
    primers = Primers.get(gene_id, get_db())
    primers.delete(get_db())
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
