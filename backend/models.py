from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import date

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    email: str = Field(unique=True, index=True)
    contrasena_hash: str
    rol: str = Field(default="usuario")
    
    # Un usuario puede tener muchas suscripciones
    suscripciones: List["Suscripcion"] = Relationship(back_populates="usuario")


class Suscripcion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre_servicio: str
    monto_original: float
    moneda_original: str # Ej: "USD", "EUR", "CLP"
    fecha_proximo_cobro: date
    activa: bool = Field(default=True)
    periodicidad: str = Field(default="mensual")  # mensual o anual para calcular mejor los gastos

    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    
    # Relación inversa
    usuario: Optional[Usuario] = Relationship(back_populates="suscripciones")