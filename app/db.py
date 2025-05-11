import sqlite3
import os


def get_connection():
    db_path = os.path.join(os.path.dirname(__file__), "../data/primers_db.db")
    return sqlite3.connect(db_path)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS genes (
            gene_id TEXT PRIMARY KEY,
            sequence TEXT NOT NULL
        );
        ''')
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS primers (
            primers_id TEXT PRIMARY KEY ,
            gene_id TEXT NOT NULL,
            forward_sequence TEXT NOT NULL,
            reverse_sequence TEXT NOT NULL,
            forward_tm FLOAT NOT NULL,
            reverse_tm FLOAT NOT NULL,
            FOREIGN KEY (gene_id) REFERENCES genes(gene_id)
        );
        ''')
    # 'forward_tm FLOAT NOT NULL,
            # reverse_tm FLOAT NOT NULL,'

    # cursor.execute(
    #     '''
    #     CREATE TABLE IF NOT EXISTS TM (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         primers_id TEXT NOT NULL,
    #
    #         FOREIGN KEY (primers_id) REFERENCES primers(id)
    #     );
    #     ''')
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
