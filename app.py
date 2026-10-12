from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'clave_secreta'

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            control TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def inicio():
    if 'usuario' in session:
        return redirect(url_for('principal'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT nombre, control, email, password FROM usuarios WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and user[3] == password:
            session['usuario'] = user[0]
            session['control'] = user[1]
            session['email'] = user[2]
            return redirect(url_for('principal'))
        else:
            error = "Correo o contraseña incorrectos, o cuenta no registrada."
            
    return render_template('login.html', error=error)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    error = None
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        control = request.form.get('control')
        email = request.form.get('email')
        password = request.form.get('password')

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT email FROM usuarios WHERE email = ?', (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            error = "Este correo ya está registrado."
            conn.close()
        else:
            cursor.execute('INSERT INTO usuarios (nombre, control, email, password) VALUES (?, ?, ?, ?)',
                           (nombre, control, email, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))

    return render_template('registro.html', error=error)

@app.route('/principal')
def principal():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    return render_template(
        'principal.html', 
        usuario=session.get('usuario'),
        control=session.get('control'),
        email=session.get('email')
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)