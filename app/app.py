import os
import sqlite3
from db import init_db
from flask import Flask, url_for, render_template, request, g, redirect
from models.models import Gene, Primers

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
    gene_ids = [gene.gene_id for gene in Gene.all(get_db())]
    return render_template("index.html", gene_ids=gene_ids)


@app.route('/pairs/<gene_id>')
def pairs(gene_id):
    primers = Primers.get_by_gene(gene_id, get_db())
    return render_template('pairs.html', gene_id=gene_id, primers=primers)


@app.route('/gene/<gene_id>')
def gene(gene_id):
    gene = Gene.get(gene_id, get_db())
    return render_template('gene.html', gene=gene)

@app.route('/gene_edit/<gene_id>', methods=['GET', 'POST'])
def gene_edit(gene_id, seq=None):
    gene = Gene.get(gene_id, get_db())
    if request.method == 'POST':
        gene.seq = seq if seq else request.form['sequence']
        gene.save(get_db())
        return redirect(url_for('gene', gene_id=gene.gene_id))
    else:
        return render_template('gene_edit.html', gene=gene)


@app.route('/add', methods=['GET', 'POST'])
@app.route('/add/<gene_id>', methods=['GET', 'POST'])
def add(gene_id=None):
    if request.method == 'POST':
        gene = gene_id if gene_id else request.form['gene_id']
        fwd = request.form['forward_primer']
        rev = request.form['reverse_primer']
        new_primers = Primers(primers_id=None, gene=Gene(gene), fwd_seq=fwd, rev_seq=rev)
        new_primers.save(get_db())
        return redirect(url_for('pairs', gene_id=gene))
    else:
        return render_template('add.html', primers=None, gene_id=gene_id)
    

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


@app.route('/delete_primers/<primers_id>')
def delete_primers(primers_id):
    primers = Primers.get(primers_id, get_db())
    primers.delete(get_db())
    return redirect(url_for('pairs', gene_id=primers.gene.gene_id))


@app.route('/delete_gene/<gene_id>', methods=['GET', 'POST'])
def delete_gene(gene_id):
    gene = Gene.get(gene_id, get_db())
    gene.delete(get_db())
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
