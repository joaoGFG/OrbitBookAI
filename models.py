from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Numeric, DateTime, Date, ForeignKey
from sqlalchemy import Sequence as SASequence
from sqlalchemy.orm import relationship
from database import Base


class Role(Base):
    __tablename__ = "ROLE"
    id_role = Column(Integer, SASequence('SEQ_ROLE'), primary_key=True)
    name_role = Column(String(100), nullable=False, unique=True)
    description = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    users = relationship("UserOrbit", back_populates="role_obj")


class DestinationType(Base):
    __tablename__ = "DESTINATION_TYPES"
    id_destination_types = Column(Integer, SASequence('SEQ_DESTINATION_TYPES'), primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(String(260), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    destinations = relationship("Destination", back_populates="destination_type")


class BookingStatus(Base):
    __tablename__ = "BOOKING_STATUSES"
    id_booking_statuses = Column(Integer, SASequence('SEQ_BOOKING_STATUSES'), primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    bookings = relationship("Booking", back_populates="status_obj")


class UserOrbit(Base):
    __tablename__ = "USERS_ORBIT"
    id_users_orbit = Column(Integer, SASequence('SEQ_USERS_ORBIT'), primary_key=True)
    name = Column(String(260), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    id_role = Column(Integer, ForeignKey("ROLE.id_role"), nullable=False)
    role_obj = relationship("Role", back_populates="users")
    bookings = relationship("Booking", back_populates="user")
    ai_recommendations = relationship("AIRecomendation", back_populates="user")

    @property
    def id(self):
        return self.id_users_orbit

    @property
    def nome(self):
        return self.name

    @property
    def role(self):
        return self.role_obj.name_role if self.role_obj else None

    @property
    def criado_em(self):
        return self.created_at


class Destination(Base):
    __tablename__ = "DESTINATIONS"
    id_destinations = Column(Integer, SASequence('SEQ_DESTINATIONS'), primary_key=True)
    name = Column(String(260), nullable=False)
    description = Column(String(1000), nullable=False)
    distance_km = Column(Numeric(15), nullable=False)
    base_price = Column(Numeric(15), nullable=False)
    capacity = Column(Integer, nullable=False)
    image_url = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    id_destination_types = Column(Integer, ForeignKey("DESTINATION_TYPES.id_destination_types"), nullable=False)
    destination_type = relationship("DestinationType", back_populates="destinations")
    bookings = relationship("Booking", back_populates="destination")

    @property
    def id(self):
        return self.id_destinations

    @property
    def nome(self):
        return self.name

    @property
    def tipo(self):
        return self.destination_type.name if self.destination_type else None

    @property
    def descricao(self):
        return self.description

    @property
    def preco_base(self):
        return self.base_price

    @property
    def capacidade_max(self):
        return self.capacity

    @property
    def ativo(self):
        return 1


class AIRecomendation(Base):
    __tablename__ = "AI_RECOMENDATION"
    id_ai_recomendation = Column(Integer, SASequence('SEQ_AI_RECOMENDATION'), primary_key=True)
    prompt_used = Column(String(700), nullable=False)
    response_text = Column(String(500), nullable=False)
    model_used = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    id_users_orbit = Column(Integer, ForeignKey("USERS_ORBIT.id_users_orbit"), nullable=False)
    user = relationship("UserOrbit", back_populates="ai_recommendations")
    bookings = relationship("Booking", back_populates="ai_recommendation")


class Booking(Base):
    __tablename__ = "BOOKINGS"
    id_bookings = Column(Integer, SASequence('SEQ_BOOKINGS'), primary_key=True)
    departure_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=False)
    total_price = Column(Numeric(15, 2), nullable=False)
    num_passengers = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    id_users_orbit = Column(Integer, ForeignKey("USERS_ORBIT.id_users_orbit"), nullable=False)
    id_destinations = Column(Integer, ForeignKey("DESTINATIONS.id_destinations"), nullable=False)
    id_ai_recomendation = Column(Integer, ForeignKey("AI_RECOMENDATION.id_ai_recomendation"), nullable=True)
    id_booking_statuses = Column(Integer, ForeignKey("BOOKING_STATUSES.id_booking_statuses"), nullable=False)
    user = relationship("UserOrbit", back_populates="bookings")
    destination = relationship("Destination", back_populates="bookings")
    ai_recommendation = relationship("AIRecomendation", back_populates="bookings")
    status_obj = relationship("BookingStatus", back_populates="bookings")
    passengers = relationship("Passager", back_populates="booking")
    payment = relationship("Payment", back_populates="booking", uselist=False)
    review = relationship("Review", back_populates="booking", uselist=False)

    @property
    def id(self):
        return self.id_bookings

    @property
    def usuario_id(self):
        return self.id_users_orbit

    @property
    def destino_id(self):
        return self.id_destinations

    @property
    def status(self):
        return self.status_obj.name if self.status_obj else None

    @property
    def num_passageiros(self):
        return self.num_passengers

    @property
    def valor_total(self):
        return self.total_price

    @property
    def criado_em(self):
        return self.created_at

    @property
    def atualizado_em(self):
        return self.created_at


class Review(Base):
    __tablename__ = "REVIEWS"
    id_reviews = Column(Integer, SASequence('SEQ_REVIEWS'), primary_key=True)
    rating = Column(Float, nullable=False)
    comentario = Column(String(300))
    created_at = Column(DateTime, default=datetime.utcnow)
    id_bookings = Column(Integer, ForeignKey("BOOKINGS.id_bookings"), nullable=False, unique=True)
    booking = relationship("Booking", back_populates="review")

    @property
    def id(self):
        return self.id_reviews

    @property
    def booking_id(self):
        return self.id_bookings

    @property
    def nota(self):
        return self.rating

    @property
    def usuario_id(self):
        return self.booking.id_users_orbit if self.booking else None

    @property
    def destino_id(self):
        return self.booking.id_destinations if self.booking else None

    @property
    def criado_em(self):
        return self.created_at


class Passager(Base):
    __tablename__ = "PASSAGERS"
    id_passagers = Column(Integer, SASequence('SEQ_PASSAGERS'), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    data_nasc = Column(Date, nullable=False)
    cpf = Column(String(11), nullable=False, unique=True)
    name = Column(String(260), nullable=False)
    id_bookings = Column(Integer, ForeignKey("BOOKINGS.id_bookings"), nullable=False)
    booking = relationship("Booking", back_populates="passengers")


class Payment(Base):
    __tablename__ = "PAYMENTS"
    id_payments = Column(Integer, SASequence('SEQ_PAYMENTS'), primary_key=True)
    method = Column(String(100), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    status = Column(String(100), nullable=False)
    paid_at = Column(DateTime)
    id_bookings = Column(Integer, ForeignKey("BOOKINGS.id_bookings"), nullable=False, unique=True)
    booking = relationship("Booking", back_populates="payment")
