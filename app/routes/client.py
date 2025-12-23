from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app.models.reservation import Reservation
from app.models.user import User
from app.models.service import Service
from app.models.enums import RoleEnum
from app.extensions import db
from datetime import datetime, time as dt_time, timedelta

bp = Blueprint('client', __name__, url_prefix='/client')

HORA_INICIO = dt_time(7, 0)
HORA_FIN = dt_time(20, 0)

@bp.route('/reserve', methods=['GET', 'POST'])
@login_required
def reserve():

    manicurists = User.query.filter_by(role=RoleEnum.MANICURISTA).all()
    services = Service.query.all()

    if request.method == 'POST':
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        start_time = datetime.strptime(request.form['time'], '%H:%M').time()
        manicurista_id = int(request.form['manicurist'])
        service_id = int(request.form['service'])
        location = request.form['location']
        cellphone = request.form.get('cellphone', current_user.cellphone)
        address = request.form.get('address', None)

        # Definir costo adicional por domicilio
        additional_cost = 20000 if location == 'DOMICILIO' else 0

        # 📆 VALIDAR DÍA
        if date.weekday() > 5:
            flash('❌ Solo se permiten reservas de lunes a sábado')
            return redirect(url_for('client.reserve'))

        # ⏰ VALIDAR HORARIO
        if not (HORA_INICIO <= start_time <= HORA_FIN):
            flash('❌ Horario permitido: 7:00 a.m. a 8:00 p.m.')
            return redirect(url_for('client.reserve'))

        # 🧑‍🔧 VALIDAR MANICURISTA
        manicurist = User.query.get_or_404(manicurista_id)
        if manicurist.role != RoleEnum.MANICURISTA:
            abort(400)

        # ⏱️ CALCULAR HORA FIN SEGÚN SERVICIO
        service = Service.query.get_or_404(service_id)
        start_dt = datetime.combine(date, start_time)
        end_dt = start_dt + timedelta(minutes=service.duracion)
        end_time = end_dt.time()

        if end_time > HORA_FIN:
            flash('❌ El servicio termina fuera del horario permitido')
            return redirect(url_for('client.reserve'))

        # 🔍 VALIDAR CRUCE DE HORARIOS
        reservations = Reservation.query.filter_by(
        manicurista_id=manicurista_id,
        date=date
        ).all()

        for r in reservations:
            r_start = r.time
            r_end = (datetime.combine(date, r.time) + timedelta(minutes=r.service.duracion)).time()

        conflict = False
        for r in reservations:
            if r_start < end_time and r_end > start_time:
                conflict = True
                break

        if conflict:
            flash('❌ La manicurista ya tiene una reserva en ese horario')
            return redirect(url_for('client.reserve'))

        # ✅ CREAR RESERVA
        reservation = Reservation(
        date=date,
        time=start_time,   # 👈 ESTA es la columna real
        client_id=current_user.id,
        manicurista_id=manicurista_id,
        service_id=service_id,
        location=location,
        cellphone=current_user.cellphone,
        address=address
        )


        db.session.add(reservation)
        db.session.commit()
        reservation.total_price = reservation.service.precio + additional_cost

        flash('✅ Reserva creada exitosamente')
        return redirect(url_for('client.reserve'))

    return render_template(
        'client/reserve.html',
        manicurists=manicurists,
        services=services
    )

@bp.route('/mis-reservas')
@login_required
def mis_reservas():

    reservas = (
        Reservation.query
        .filter_by(client_id=current_user.id)
        .order_by(Reservation.date.desc(), Reservation.time)
        .all()
    )
    return render_template(
        'client/mis_reservas.html',
        reservas=reservas
    )