import os
import sqlite3
from pathlib import Path

from flask import Flask, g

DB_FILENAME = "database.db"


def query_db(query, args=(), one=False, commit=False):
    with sqlite3.connect(DB_FILENAME) as conn:
        # vulnerability: Sensitive Data Exposure
        conn.set_trace_callback(print)
        cur = conn.cursor().execute(query, args)
        if commit:
            conn.commit()
        return cur.fetchone() if one else cur.fetchall()


def create_app():
    import os
    import sqlite3
    from pathlib import Path
    from werkzeug.security import generate_password_hash

    app = Flask(__name__)
    # PRECOGS_FIX: Do not hard-code secrets; read from environment and fall back to a securely generated key
    secret = os.environ.get("FLASK_SECRET_KEY")
    if secret:
        app.secret_key = secret
    else:
        # Generate a strong ephemeral key to avoid embedding secrets in source. For production, require FLASK_SECRET_KEY.
        app.secret_key = os.urandom(32)

    db_path = Path(DB_FILENAME)
    if db_path.exists():
        db_path.unlink()

    with sqlite3.connect(DB_FILENAME) as conn:
        create_table_query = """CREATE TABLE IF NOT EXISTS user
        (id INTEGER PRIMARY KEY, username TEXT, password TEXT, access_level INTEGER)"""
        conn.execute(create_table_query)

        # PRECOGS_FIX: Store admin password as a secure hash instead of plaintext
        hashed = generate_password_hash("maximumentropy")
        insert_admin_query = "INSERT INTO user (id, username, password, access_level) VALUES (1, ?, ?, ?)"
        conn.execute(insert_admin_query, ("admin", hashed, 0))
        conn.commit()

    with app.app_context():
        from . import actions
        from . import auth
        from . import status
        from . import ui
        from . import users

        app.register_blueprint(actions.bp)
        app.register_blueprint(auth.bp)
        app.register_blueprint(status.bp)
        app.register_blueprint(ui.bp)
        app.register_blueprint(users.bp)
        return app
