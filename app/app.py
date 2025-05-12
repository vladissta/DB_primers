import os
import sqlite3
from db import init_db
from flask import (Flask, url_for,
                   render_template, request, g, redirect)
from models.primers import Gene, Primers

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


@app.route('/pair/<primers_id>')
def pair(primers_id):
    primer_pair = Primers.get(primers_id, get_db())
    return render_template('pair.html', pair=primer_pair)


# @app.route('/genes/<gene_id>')
# def gene(gene_id):
#     gene = Gene.get(gene_id, get_db())
#     return render_template('gene.html', gene=gene)


@app.route('/add', methods=['GET', 'POST', 'PUT'])
def add():
    if request.method == 'POST':
        gene = Gene(gene_id=request.form['gene_id'], seq="")

        primers = Primers(
            primers_id=None,
            gene=gene,
            fwd_seq=request.form['forward_primer'],
            rev_seq=request.form['reverse_primer']
        )
        
        primers.save(get_db())
        
        return redirect(url_for('pair', primers_id=primers.primers_id))
    else:
        return render_template('add.html')


# @app.route('/edit/<primers_id>')
# def edit(primers_id):
#     primers = Primers.get(primers_id, get_db())
#     return render_template('add.html', primers=primers)

@app.route('/edit/<primers_id>', methods=['GET', 'POST'])
def edit(primers_id):
    primers = Primers.get(primers_id, get_db())
    if request.method == 'POST':
        primers.fwd_seq = request.form['forward_primer']
        primers.rev_seq = request.form['reverse_primer']
        primers.save(get_db())
        return redirect(url_for('pair', primers_id=primers_id))
    else:
        return render_template('add.html', primers=primers)


@app.route('/delete/<primers_id>')
def delete(primers_id):
    primers = Primers.get(primers_id, get_db())
    primers.delete(get_db())
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
