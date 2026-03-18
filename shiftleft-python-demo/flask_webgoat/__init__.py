
def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)  # PRECOGS_FIX: use a random secret key

    db_path = Path(DB_FILENAME)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(DB_FILENAME)
    create_table_query = """CREATE TABLE IF NOT EXISTS user
    (id INTEGER PRIMARY KEY, username TEXT, password TEXT, access_level INTEGER)"""
    conn.execute(create_table_query)

    hashed_password = generate_password_hash('maximumentropy')  # PRECOGS_FIX: store hashed password
    insert_admin_query = """INSERT INTO user (id, username, password, access_level)
    VALUES (1, 'admin', ?, 0)"""  # PRECOGS_FIX: use parameterized query
    conn.execute(insert_admin_query, (hashed_password,))  # PRECOGS_FIX: use parameterized query
    conn.commit()
    conn.close()

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