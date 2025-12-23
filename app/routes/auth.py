from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.user import User, RoleEnum
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == RoleEnum.ADMIN:
                return redirect(url_for('admin.dashboard'))
            elif user.role == RoleEnum.MANICURISTA:
                return redirect(url_for('manicurist.agenda'))
            elif user.role == RoleEnum.CLIENTE:
                return redirect(url_for('client.reserve'))
        else:
            flash('Credenciales incorrectas')

    return render_template('auth/login.html')


@auth_bp.route('/auth/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/auth/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        if request.form['password'] != request.form['confirm_password']:
            flash('Las contraseñas no coinciden')
            return redirect(url_for('auth.register'))

        user = User(
            name=request.form['name'],
            email=request.form['email'],
            cellphone=request.form['phone'],
            role=RoleEnum.CLIENTE
        )
        user.set_password(request.form['password'])

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')
