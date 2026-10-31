"""Memory across applications, so one document or one faculty member cannot serve two institutions."""
import json
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (id INTEGER PRIMARY KEY, bundle TEXT UNIQUE, institution TEXT, verdict TEXT,
    failed INTEGER, review INTEGER, passed INTEGER, created TEXT DEFAULT CURRENT_TIMESTAMP, report TEXT);
CREATE TABLE IF NOT EXISTS documents (app INTEGER, sha256 TEXT, name TEXT, cert_no TEXT);
CREATE TABLE IF NOT EXISTS faculty (app INTEGER, faculty_id TEXT, name TEXT);
"""


class Registry:
    def __init__(self, path=":memory:"):
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path), check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)

    def document_elsewhere(self, sha256, cert_no):
        return self.db.execute(
            "SELECT a.institution, d.name, d.sha256 = ? AS same_file FROM documents d JOIN applications a ON a.id = d.app "
            "WHERE d.sha256 = ? OR (d.cert_no != '' AND d.cert_no = ?)", (sha256, sha256, cert_no or "")).fetchall()

    def faculty_elsewhere(self, faculty_id):
        return self.db.execute("SELECT a.institution, f.name FROM faculty f JOIN applications a ON a.id = f.app "
                               "WHERE f.faculty_id = ?", (faculty_id,)).fetchall()

    def record(self, report) -> int:
        bundle = "".join(sorted(d["sha256"] for d in report.documents))
        old = self.db.execute("SELECT id FROM applications WHERE bundle = ?", (bundle,)).fetchone()
        if old:
            self.db.execute("DELETE FROM documents WHERE app = ?", (old["id"],))
            self.db.execute("DELETE FROM faculty WHERE app = ?", (old["id"],))
            self.db.execute("DELETE FROM applications WHERE id = ?", (old["id"],))
        cur = self.db.execute(
            "INSERT INTO applications (bundle, institution, verdict, failed, review, passed, report) VALUES (?,?,?,?,?,?,?)",
            (bundle, report.institution, report.verdict, report.count("FAIL"), report.count("NEEDS REVIEW"),
             report.count("PASS"), json.dumps(report.to_dict())))
        app = cur.lastrowid
        self.db.executemany("INSERT INTO documents VALUES (?,?,?,?)",
                            [(app, d["sha256"], d["name"], d.get("cert_no", "")) for d in report.documents])
        self.db.executemany("INSERT INTO faculty VALUES (?,?,?)", [(app, i, n) for i, n in report.faculty])
        self.db.commit()
        return app

    def queue(self):
        """Riskiest first: failures, then items for review."""
        return [dict(r) for r in self.db.execute(
            "SELECT id, institution, verdict, failed, review, passed, created FROM applications "
            "ORDER BY failed DESC, review DESC, id DESC")]

    def report(self, app):
        row = self.db.execute("SELECT report FROM applications WHERE id = ?", (app,)).fetchone()
        return json.loads(row["report"]) if row else None
