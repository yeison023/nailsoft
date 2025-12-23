from flask import Blueprint, abort, redirect, render_template, url_for
from flask_login import login_required, current_user
from app.models.reservation import Reservation
from app.models.enums import ReservationStatus, RoleEnum
from app.utils.decorators import role_required
from app.extensions import db

bp = Blueprint('manicurist', __name__, url_prefix='/manicurist')

@bp.route('/agenda')
@login_required
@role_required(RoleEnum.MANICURISTA)
def agenda():

    reservations = (
        Reservation.query
        .filter_by(manicurista_id=current_user.id)
        .order_by(Reservation.date, Reservation.time)
        .all()
    )

    return render_template('manicurist/agenda.html', reservations=reservations)

@bp.route('/reserva/<int:id>/estado/<string:estado>')
@login_required
@role_required(RoleEnum.MANICURISTA)
def cambiar_estado(id, estado):

    reserva = Reservation.query.get_or_404(id)

    if reserva.manicurista_id != current_user.id:
        abort(403)

    if estado not in ['confirmado', 'rechazado', 'finalizado', 'pendiente']:
        abort(400)

    reserva.status = ReservationStatus[estado.upper()]
    db.session.commit()

    return redirect(url_for('manicurist.agenda'))
