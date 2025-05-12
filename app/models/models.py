import sqlite3
from abc import ABC, abstractmethod
from typing import Self


class TableClass(ABC):
    @abstractmethod
    def save(self, con: sqlite3.Connection):
        pass

    @abstractmethod
    def delete(self, con: sqlite3.Connection):
        pass

    @abstractmethod
    def get(*args, con: sqlite3.Connection):
        pass

    @abstractmethod
    def all(*args, con: sqlite3.Connection) -> list[Self]:
        pass


class Gene(TableClass):

    def __init__(self, gene_id: str, seq: str=''):
        self._gene_id = gene_id
        self._seq = seq
        self._saved = False

    def __str__(self):
        return self._gene_id

    @property
    def gene_id(self):
        return self._gene_id

    @property
    def seq(self):
        return self._seq

    @gene_id.setter
    def gene_id(self, gene_id: str):
        if gene_id != self.gene_id:
            self._saved = False
        self.gene_id = gene_id

    @seq.setter
    def seq(self, seq: str):
        if seq != self._seq:
            self._saved = False
        self._seq = seq.upper()

    def save(self, con: sqlite3.Connection):
        if self._saved:
            return
        if not Gene.get(self.gene_id, con):
            con.execute('''
                        INSERT INTO genes 
                        (gene_id, sequence) 
                        VALUES (?, ?);
                        ''',
                        (self._gene_id, self._seq))
        else:
            con.execute('''
                UPDATE genes 
                SET sequence = ?
                WHERE gene_id = ?;
                ''',
                        (self._seq, self._gene_id))
        con.commit()
        self._saved = True


    def delete(self, con: sqlite3.Connection):
        con.execute('DELETE FROM primers WHERE gene_id = ?', (self._gene_id,))
        con.execute('DELETE FROM genes WHERE gene_id = ?', (self._gene_id,))
        con.commit()
        self._saved = False


    @staticmethod
    def get(gene_id: str, con: sqlite3.Connection):
        cursor = con.execute('SELECT * FROM genes where gene_id=?;', (gene_id,))
        genes_row = cursor.fetchone()
        if not genes_row:
            return None
        g = Gene(*genes_row[:2])
        g._saved = True
        return g

    @staticmethod
    def all(con: sqlite3.Connection):

        all_genes = [Gene(*row[:2])
                       for row in con.execute('SELECT * FROM genes;')]
        
        print(all_genes)

        for primers in all_genes:
            primers._saved = True
        return all_genes


class Primers(TableClass):
    def __init__(self, 
                 primers_id: int,
                 gene: Gene,
                 fwd_seq: str, rev_seq: str):
        
        self._primers_id = primers_id
        self._gene = gene
        self._fwd_seq = fwd_seq
        self._rev_seq = rev_seq
        self._fwd_tm = self._calculate_tm(fwd_seq)
        self._rev_tm = self._calculate_tm(rev_seq)
        self._saved = False

    @property
    def primers_id(self):
        return self._primers_id
    
    @property
    def gene(self):
        return self._gene

    @property
    def fwd_seq(self):
        return self._fwd_seq

    @property
    def rev_seq(self):
        return self._rev_seq

    @property
    def fwd_tm(self):
        return self._fwd_tm

    @property
    def rev_tm(self):
        return self._rev_tm

    @primers_id.setter
    def primers_id(self, primers_id: str):
        if primers_id != self.primers_id:
            self._saved = False
        self.primers_id = primers_id

    @gene.setter
    def gene(self, gene: str):
        if gene.gene_id != self.gene_id:
            self._saved = False
        self.gene.gene_id = gene.gene_id

    @fwd_seq.setter
    def fwd_seq(self, fwd_seq: str):
        if fwd_seq != self._fwd_seq:
            self._saved = False
        self._fwd_seq = fwd_seq

    @rev_seq.setter
    def rev_seq(self, rev_seq: str):
        if rev_seq != self._rev_seq:
            self._saved = False
        self._rev_seq = rev_seq

    @staticmethod
    def _calculate_tm(sequence) -> float:
        sequence = sequence.upper()
        a = sequence.count('A')
        t = sequence.count('T')
        g = sequence.count('G')
        c = sequence.count('C')
        return 2 * (a + t) + 4 * (g + c)

    def save(self, con: sqlite3.Connection):
        if self._saved:
            return
        
        if not self.gene._saved:
            self.gene.save(con)

        if not Primers.get(self.primers_id, con):
            cursor = con.execute('''
                INSERT INTO primers 
                (gene_id, forward_sequence, reverse_sequence, forward_tm, reverse_tm) 
                VALUES (?, ?, ?, ?, ?);
            ''', (
                self.gene.gene_id,
                self._fwd_seq,
                self._rev_seq,
                self.fwd_tm,
                self.rev_tm
            ))
            self._primers_id = cursor.lastrowid
        else:
            con.execute('''
                UPDATE primers 
                SET gene_id = ?,
                    forward_sequence = ?, 
                    reverse_sequence = ?,
                    forward_tm = ?,
                    reverse_tm = ?
                WHERE primers_id = ?;
            ''', (
                self.gene.gene_id,
                self._fwd_seq,
                self._rev_seq,
                self._fwd_tm,
                self._rev_tm,
                self._primers_id
            ))
        con.commit()
        self._saved = True

    def delete(self, con: sqlite3.Connection):
        con.execute('DELETE FROM primers WHERE primers_id = ?;', (self.primers_id,))
        con.commit()
        self._saved = False

    @staticmethod
    def get(primers_id: int, con: sqlite3.Connection):

            cursor = con.execute('SELECT * FROM primers where primers_id=?;', (primers_id,))
            primers_row = cursor.fetchone()

            if not primers_row:
                return None

            gene = Gene.get(primers_row[1], con)
            p = Primers(primers_row[0], gene, primers_row[2], primers_row[3])
            p._saved = True
            return p
    
    
    @staticmethod
    def get_by_gene(gene_id: str, con: sqlite3.Connection) -> list[Self]:
        cursor = con.execute(
            'SELECT primers_id FROM primers WHERE gene_id = ?;', (gene_id,))
        primer_ids = [row[0] for row in cursor.fetchall()]
        return [Primers.get(pid, con) for pid in primer_ids]


    @staticmethod
    def all(con: sqlite3.Connection) -> list[Self]:
        cursor = con.execute('SELECT * FROM primers;')
        all_primers = []
        
        for row in cursor:

            gene = Gene.get(row[1], con)

            primer = Primers(
                primers_id=row[0],
                gene=gene,
                fwd_seq=row[2],
                rev_seq=row[3]
            )
            primer._saved = True
            all_primers.append(primer)
        
        return all_primers
