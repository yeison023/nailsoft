from app.extensions import db
from datetime import datetime, timedelta
from app.models.enums import ReservationStatus

class Reservation(db.Model):
    __tablename__ = 'reservation'

    id = db.Column(db.Integer, primary_key=True)

    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)

    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    manicurista_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)

    status = db.Column(
        db.Enum(ReservationStatus),
        default=ReservationStatus.PENDIENTE,
        nullable=False
    )
    cellphone = db.Column(db.String(20), nullable=True)
    location = db.Column(db.Enum("SPA", "DOMICILIO", name="reservation_location"), nullable=False, default="SPA")
    address = db.Column(db.String(255), nullable=True) # Solo si location es "DOMICILIO"

    # Relaciones (MUY IMPORTANTE)
    client = db.relationship('User', foreign_keys=[client_id])
    manicurista = db.relationship('User', foreign_keys=[manicurista_id])
    service = db.relationship('Service')

    # 🔹 HORA INICIO (alias elegante)
    @property
    def start_time(self):
        return self.time

    # 🔹 HORA FIN CALCULADA
    @property
    def end_time(self):
        start = datetime.combine(self.date, self.time)
        end = start + timedelta(minutes=self.service.duracion)
        return end.time()
