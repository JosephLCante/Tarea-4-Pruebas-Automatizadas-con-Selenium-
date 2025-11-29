import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "devkey")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "app.db"))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# MODELOS (aquí dentro, sin archivo models.py separado)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    curso = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)

# Crear BD y usuario de prueba
with app.app_context():
    db.create_all()
    if not User.query.filter_by(email="admin@example.com").first():
        u = User(email="admin@example.com", password="password123")
        db.session.add(u)
        db.session.commit()

# Rutas
@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("students"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session["user_id"] = user.id
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for("students"))
        else:
            flash("Email o contraseña incorrectos", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/students")
def students():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    students = Student.query.all()
    return render_template("students_list.html", students=students)

@app.route("/students/create", methods=["GET","POST"])
def create_student():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    if request.method == "POST":
        nombre = request.form.get("nombre")
        edad = request.form.get("edad")
        curso = request.form.get("curso")
        email = request.form.get("email")
        if not nombre or not edad or not curso or not email:
            flash("Todos los campos son obligatorios", "danger")
            return render_template("student_form.html", student=None)
        try:
            edad_int = int(edad)
        except:
            flash("Edad debe ser un número", "danger")
            return render_template("student_form.html", student=None)
        s = Student(nombre=nombre, edad=edad_int, curso=curso, email=email)
        db.session.add(s)
        db.session.commit()
        flash("Estudiante creado correctamente", "success")
        return redirect(url_for("students"))
    return render_template("student_form.html", student=None)

@app.route("/students/edit/<int:id>", methods=["GET","POST"])
def edit_student(id):
    if not session.get("user_id"):
        return redirect(url_for("login"))
    s = Student.query.get_or_404(id)
    if request.method == "POST":
        s.nombre = request.form.get("nombre")
        try:
            s.edad = int(request.form.get("edad"))
        except:
            flash("Edad debe ser un número", "danger")
            return render_template("student_form.html", student=s)
        s.curso = request.form.get("curso")
        s.email = request.form.get("email")
        if not s.nombre or not s.edad or not s.curso or not s.email:
            flash("Todos los campos son obligatorios", "danger")
            return render_template("student_form.html", student=s)
        db.session.commit()
        flash("Estudiante actualizado", "success")
        return redirect(url_for("students"))
    return render_template("student_form.html", student=s)

@app.route("/students/delete/<int:id>", methods=["POST"])
def delete_student(id):
    if not session.get("user_id"):
        return redirect(url_for("login"))
    s = Student.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    flash("Estudiante eliminado", "success")
    return redirect(url_for("students"))

if __name__ == "__main__":
    app.run(debug=True)
