from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from app.utils.decorators import role_required
from app.models.enums import RoleEnum
from app.models.service import Service
from app.models.user import User
from app.models.reservation import Reservation
from app.extensions import db
from sqlalchemy import extract, func
from werkzeug.security import generate_password_hash


bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/servicios')
@login_required
@role_required(RoleEnum.ADMIN)
def servicios():
    servicios = Service.query.all()
    return render_template('admin/servicios.html', servicios=servicios)


@bp.route('/servicios/nuevo', methods=['GET', 'POST'])
@login_required
@role_required(RoleEnum.ADMIN)
def nuevo_servicio():
    if request.method == 'POST':
        servicio = Service(
            nombre=request.form['nombre'],
            precio=request.form['precio'],
            duracion=request.form['duracion']
        )
        db.session.add(servicio)
        db.session.commit()
        return redirect(url_for('admin.servicios'))

    return render_template('admin/nuevo_servicio.html')


@bp.route('/servicios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(RoleEnum.ADMIN)
def editar_servicio(id):
    servicio = Service.query.get_or_404(id)

    if request.method == 'POST':
        servicio.nombre = request.form['nombre']
        servicio.precio = request.form['precio']
        servicio.duracion = request.form['duracion']

        db.session.commit()
        return redirect(url_for('admin.servicios'))

    return render_template('admin/editar_servicio.html', servicio=servicio)

@bp.route('/servicios/eliminar/<int:id>')
@login_required
@role_required(RoleEnum.ADMIN)
def eliminar_servicio(id):
    servicio = Service.query.get_or_404(id)
    db.session.delete(servicio)
    db.session.commit()
    return redirect(url_for('admin.servicios'))

@bp.route('/dashboard')
@login_required
@role_required(RoleEnum.ADMIN)
def dashboard():
    total_users = User.query.count()
    total_services = Service.query.count()
    total_reservations = Reservation.query.count()

    # Meses del año
    months = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]

    # Servicios por mes
    services_per_month = []
    income_per_month = []

    for i in range(1, 13):
        count = Reservation.query.filter(extract('month', Reservation.date)==i).count()
        total_income = db.session.query(func.sum(Service.precio)).join(Reservation).filter(extract('month', Reservation.date)==i).scalar() or 0
        services_per_month.append(count)
        income_per_month.append(total_income)

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_services=total_services,
                           total_reservations=total_reservations,
                           months=months,
                           services_per_month=services_per_month,
                           income_per_month=income_per_month)

@bp.route('/usuarios')
@login_required
@role_required(RoleEnum.ADMIN)
def usuarios():
    usuarios = User.query.all()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@bp.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
@role_required(RoleEnum.ADMIN)
def nuevo_usuario():
    if request.method == 'POST':
        password_plana = request.form['password']

        user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=generate_password_hash(password_plana),
            role=request.form['role'],
            cellphone=request.form['cellphone'],
        )

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin.usuarios'))

    return render_template('admin/nuevo_usuario.html')



@bp.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(RoleEnum.ADMIN)
def editar_usuario(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        if request.form['password']:
            user.password = request.form['password']  # recuerda hashear
        user.role = request.form['role']
        user.cellphone = request.form['cellphone']
        db.session.commit()
        return redirect(url_for('admin.usuarios'))
    return render_template('admin/editar_usuario.html', user=user)


@bp.route('/usuarios/eliminar/<int:id>')
@login_required
@role_required(RoleEnum.ADMIN)
def eliminar_usuario(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin.usuarios'))


@bp.route('/reservas')
@login_required
@role_required(RoleEnum.ADMIN)
def reservas():
    reservas = (
        Reservation.query
        .order_by(Reservation.date, Reservation.time)
        .all()
    )
    total = sum(r.service.precio for r in reservas)

    return render_template(
        'admin/reservas.html',
        reservas=reservas,
        total=total
    )

@bp.route('/reservas/eliminar/<int:id>')
@login_required
@role_required(RoleEnum.ADMIN)
def eliminar_reserva(id):
    reserva = Reservation.query.get_or_404(id)
    db.session.delete(reserva)
    db.session.commit()
    return redirect(url_for('admin.reservas'))

@bp.route('/reservas/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(RoleEnum.ADMIN)
def editar_reserva(id):
    reserva = Reservation.query.get_or_404(id)
    services = Service.query.all()
    manicurists = User.query.filter_by(role=RoleEnum.MANICURISTA).all()

    if request.method == 'POST':
        reserva.date = request.form['date']
        reserva.start_time = request.form['start_time']
        reserva.end_time = request.form['end_time']
        reserva.service_id = request.form['service']
        reserva.manicurista_id = request.form['manicurist']

        db.session.commit()
        return redirect(url_for('admin.reservas'))

    return render_template(
        'admin/editar_reserva.html',
        reserva=reserva,
        services=services,
        manicurists=manicurists
    )
