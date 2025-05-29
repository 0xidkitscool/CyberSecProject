from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'  #session handling

def query_db(query, args=(), one=False):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        search_term = request.form['query']
        results = query_db(f"SELECT * FROM data WHERE info LIKE '%{search_term}%'")
    return render_template('index.html', results=results)

@app.route('/admin.html', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'ReallySecure123!':
            session['admin'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('admin.html', error="Invalid credentials")
    return render_template('admin.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    users = query_db("SELECT * FROM users")
    return render_template('dashboard.html', users=users)

@app.route('/delete/<int:user_id>')
def delete_user(user_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)

