from enum import Enum
import enum

class RoleEnum(str, Enum):
    ADMIN = "admin"
    MANICURISTA = "manicurista"
    CLIENTE = "cliente"

class ReservationStatus(enum.Enum):
    PENDIENTE = "pendiente"
    CONFIRMADO = "confirmado"
    RECHAZADO = "rechazado"
    FINALIZADO = "finalizado"
