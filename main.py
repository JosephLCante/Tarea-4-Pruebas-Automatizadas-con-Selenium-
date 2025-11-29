import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "devkey")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "app.db"))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Logging setup
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, "app.log")

logger = logging.getLogger("selenium_crud_app")
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(log_file, maxBytes=2*1024*1024, backupCount=5, encoding='utf-8')
formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)
werk = logging.getLogger('werkzeug')
werk.setLevel(logging.INFO)
if not any(isinstance(h, RotatingFileHandler) for h in werk.handlers):
    werk.addHandler(handler)

def log_and_flash(message, category="info"):
    if category in ("danger", "error"):
        logger.error(message)
        flash(message, "danger")
    elif category == "warning":
        logger.warning(message)
        flash(message, "warning")
    elif category == "success":
        logger.info(message)
        flash(message, "success")
    else:
        logger.info(message)
        flash(message, "info")

# MODELOS
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
    try:
        db.create_all()
        if not User.query.filter_by(email="admin@example.com").first():
            u = User(email="admin@example.com", password="password123")
            db.session.add(u)
            db.session.commit()
            logger.info("Usuario de prueba creado: admin@example.com")
    except Exception as e:
        logger.exception("Error creando la base de datos o usuario de prueba: %s", e)

# Manejo global de excepciones
@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception("Unhandled exception: %s", e)
    flash("Ocurrió un error en el servidor. Revisa los logs.", "danger")
    return redirect(url_for("students")) if session.get("user_id") else redirect(url_for("login"))

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
        try:
            user = User.query.filter_by(email=email, password=password).first()
            if user:
                session["user_id"] = user.id
                logger.info("Login exitoso: %s", email)
                log_and_flash("Inicio de sesión exitoso", "success")
                return redirect(url_for("students"))
            else:
                logger.warning("Login fallido: %s", email)
                log_and_flash("Email o contraseña incorrectos", "danger")
        except Exception as e:
            logger.exception("Error durante login para %s: %s", email, e)
            log_and_flash("Error en autenticación. Revisa logs.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    user_id = session.get("user_id")
    session.clear()
    logger.info("Usuario %s cerró sesión", user_id)
    return redirect(url_for("login"))

@app.route("/students")
def students():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    try:
        students = Student.query.all()
        return render_template("students_list.html", students=students)
    except Exception as e:
        logger.exception("Error obteniendo lista de estudiantes: %s", e)
        log_and_flash("Error cargando estudiantes. Revisa logs.", "danger")
        return render_template("students_list.html", students=[])

@app.route("/students/create", methods=["GET","POST"])
def create_student():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    if request.method == "POST":
        nombre = request.form.get("nombre")
        edad = request.form.get("edad")
        curso = request.form.get("curso")
        email = request.form.get("email")
        logger.debug("POST /students/create data: nombre=%s edad=%s curso=%s email=%s", nombre, edad, curso, email)
        if not nombre or not edad or not curso or not email:
            log_and_flash("Intento de crear estudiante con campos incompletos", "danger")
            return render_template("student_form.html", student=None)
        try:
            edad_int = int(edad)
        except Exception as e:
            logger.exception("Edad inválida al crear estudiante: %s", edad)
            log_and_flash("Edad debe ser un número", "danger")
            return render_template("student_form.html", student=None)
        try:
            s = Student(nombre=nombre, edad=edad_int, curso=curso, email=email)
            db.session.add(s)
            db.session.commit()
            logger.info("Estudiante creado: %s (%s)", nombre, email)
            log_and_flash("Estudiante creado correctamente", "success")
            return redirect(url_for("students"))
        except Exception as e:
            logger.exception("Error al crear estudiante: %s", e)
            log_and_flash("Error al crear estudiante. Revisa logs.", "danger")
            return render_template("student_form.html", student=None)
    return render_template("student_form.html", student=None)

@app.route("/students/edit/<int:id>", methods=["GET","POST"])
def edit_student(id):
    if not session.get("user_id"):
        return redirect(url_for("login"))
    s = Student.query.get_or_404(id)
    if request.method == "POST":
        logger.debug("POST /students/edit/%s data: %s", id, request.form)
        s.nombre = request.form.get("nombre")
        try:
            s.edad = int(request.form.get("edad"))
        except Exception as e:
            logger.exception("Edad inválida al editar estudiante id=%s", id)
            log_and_flash("Edad debe ser un número", "danger")
            return render_template("student_form.html", student=s)
        s.curso = request.form.get("curso")
        s.email = request.form.get("email")
        if not s.nombre or not s.edad or not s.curso or not s.email:
            log_and_flash("Intento de actualizar con campos incompletos", "danger")
            return render_template("student_form.html", student=s)
        try:
            db.session.commit()
            logger.info("Estudiante actualizado id=%s nombre=%s", id, s.nombre)
            log_and_flash("Estudiante actualizado", "success")
            return redirect(url_for("students"))
        except Exception as e:
            logger.exception("Error al actualizar estudiante id=%s: %s", id, e)
            log_and_flash("Error al actualizar. Revisa logs.", "danger")
            return render_template("student_form.html", student=s)
    return render_template("student_form.html", student=s)

@app.route("/students/delete/<int:id>", methods=["POST"])
def delete_student(id):
    if not session.get("user_id"):
        return redirect(url_for("login"))
    try:
        s = Student.query.get_or_404(id)
        db.session.delete(s)
        db.session.commit()
        logger.info("Estudiante eliminado id=%s nombre=%s", id, s.nombre)
        log_and_flash("Estudiante eliminado", "success")
    except Exception as e:
        logger.exception("Error al eliminar estudiante id=%s: %s", id, e)
        log_and_flash("Error al eliminar. Revisa logs.", "danger")
    return redirect(url_for("students"))

if __name__ == "__main__":
    app.run(debug=True)
