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

    def __init__(self, gene_id: str, seq: str):
        self._gene_id = gene_id
        self._seq = seq
        self._saved = False

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
        self._seq = seq

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
                SET fsequence = ?, 
                WHERE gene_id = ?;
                ''',
                        (self._seq, self._gene_id))
        con.commit()
        self._saved = True

    def delete(self, con: sqlite3.Connection):
        con.execute('DELETE FROM genes WHERE gene_id = ?;',
                    (self.gene_id,))
        con.commit()
        self._saved = False

    @staticmethod
    def get(gene_id: str, con: sqlite3.Connection):
        cursor = con.execute('SELECT * FROM genes where gene_id=?;', (gene_id,))
        genes_row = cursor.fetchone()
        if not genes_row:
            return None
        g = Primers(*genes_row[:2])
        g._saved = True
        return g

    @staticmethod
    def all(con: sqlite3.Connection):

        all_genes = [Primers(*primers_row[:3])
                       for primers_row in con.execute('SELECT * FROM genes;')]
        for primers in all_genes:
            primers._saved = True
        return all_genes


class Primers(TableClass):
    def __init__(self, gene_id: str, fwd_seq: str, rev_seq: str):
        self._gene_id = gene_id
        self._fwd_seq = fwd_seq
        self._rev_seq = rev_seq
        self._fwd_tm = self._calculate_tm(fwd_seq)
        self._rev_tm = self._calculate_tm(rev_seq)
        self._saved = False

    @property
    def gene_id(self):
        return self._gene_id

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

    @gene_id.setter
    def gene_id(self, gene_id: str):
        if gene_id != self.gene_id:
            self._saved = False
        self.gene_id = gene_id

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
        if not Primers.get(self.gene_id, con):
            con.execute('''
                        INSERT INTO primers 
                        (gene_id, forward_sequence, reverse_sequence, forward_tm, reverse_tm) 
                        VALUES (?, ?, ?, ?, ?);
                        ''',
                        (self._gene_id,
                         self._fwd_seq,
                         self._rev_seq,
                         self.fwd_tm,
                         self.rev_tm
                         ))
        else:
            con.execute('''
                UPDATE primers 
                SET forward_sequence = ?, 
                    reverse_sequence = ?,
                    forward_tm = ?,
                    reverse_tm = ?
                WHERE gene_id = ?;
                ''', (
                self._fwd_seq,
                self._rev_seq,
                self._fwd_tm,
                self._rev_tm,
                self._gene_id
            ))
        con.commit()
        self._saved = True

    def delete(self, con: sqlite3.Connection):
        con.execute('DELETE FROM primers WHERE gene_id = ?;', (self.gene_id,))
        con.commit()
        self._saved = False

    @staticmethod
    def get(gene_id: str, con: sqlite3.Connection):
        cursor = con.execute('SELECT * FROM primers where gene_id=?;', (gene_id,))
        primers_row = cursor.fetchone()
        if not primers_row:
            return None
        p = Primers(*primers_row[:3])
        p._saved = True
        return p

    @staticmethod
    def all(con: sqlite3.Connection) -> list[Self]:

        all_primers = [Primers(*primers_row[:3])
                       for primers_row in con.execute('SELECT * FROM primers;')]
        for primers in all_primers:
            primers._saved = True
        return all_primers
