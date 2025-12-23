from app.models.reservation import Reservation

def hay_cruce(manicurista_id, fecha, inicio, fin):
    return Reservation.query.filter(
        Reservation.manicurista_id == manicurista_id,
        Reservation.fecha == fecha,
        Reservation.hora_inicio < fin,
        Reservation.hora_fin > inicio
    ).first() is not None
