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
    # db = get_db()
    # grab each gene_id only once
    # cur = db.execute(
    #     'SELECT DISTINCT gene_id FROM primers ORDER BY gene_id;'
    # )

    gene_ids = [gene.gene_id for gene in Gene.all(get_db())]
    return render_template("index.html", gene_ids=gene_ids)


# @app.route('/pair/<primers_id>')
# def pair(primers_id):
#     primer_pair = Primers.get(primers_id, get_db())
#     return render_template('pair.html', pair=primer_pair)


@app.route('/pairs/<gene_id>')
def pairs(gene_id):
    db = get_db()
    # fetch every primers_id for this gene
    cur = db.execute(
        'SELECT primers_id FROM primers WHERE gene_id = ? ORDER BY primers_id;',
        (gene_id,)
    )
    primer_ids = [r[0] for r in cur.fetchall()]
    # load each full Primers object
    primers = [Primers.get(pid, db) for pid in primer_ids]
    return render_template('pairs.html', gene_id=gene_id, primers=primers)



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
        
        return redirect(url_for('pairs', primers_id=primers.primers_id,
                                gene_id=primers.gene.gene_id))
    else:
        return render_template('add.html')

@app.route('/edit/<primers_id>', methods=['GET', 'POST'])
def edit(primers_id):
    primers = Primers.get(primers_id, get_db())
    if request.method == 'POST':
        primers.fwd_seq = request.form['forward_primer']
        primers.rev_seq = request.form['reverse_primer']
        primers.save(get_db())
        return redirect(url_for('pairs', primers_id=primers_id, gene_id=primers.gene.gene_id))
    else:
        return render_template('add.html', primers=primers, gene_id=primers.gene.gene_id)


@app.route('/delete/<primers_id>')
def delete(primers_id):
    primers = Primers.get(primers_id, get_db())
    primers.delete(get_db())
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
