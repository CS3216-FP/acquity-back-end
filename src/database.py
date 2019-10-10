import uuid
from contextlib import contextmanager

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    String,
    create_engine,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from src.config import APP_CONFIG

_base = declarative_base()


class Base(_base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), on_update=func.now()
    )

    def asdict(self):
        d = {}
        columns = self.__table__.columns.keys()

        for col in columns:
            item = getattr(self, col)

            if isinstance(item, uuid.UUID):
                d[col] = str(item)
            else:
                d[col] = item
        return d


class User(Base):
    __tablename__ = "users"

    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    can_buy = Column(Boolean, nullable=False)
    can_sell = Column(Boolean, nullable=False)

    orders = relationship("SellOrder", back_populates="seller")


class Security(Base):
    __tablename__ = "securities"

    name = Column(String, nullable=False, unique=True)

    sell_orders = relationship("SellOrder", back_populates="security")
    buy_orders = relationship("BuyOrder", back_populates="security")


class SellOrder(Base):
    __tablename__ = "sell_orders"

    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    security_id = Column(UUID, ForeignKey("securities.id"), nullable=False)
    number_of_shares = Column(Float, nullable=False)
    price = Column(Float, nullable=False)

    user = relationship("User", back_populates="sell_orders")
    matches = relationship("Match", back_populates="sell_order")
    security = relationship("Security", back_populates="sell_orders")


class BuyOrder(Base):
    __tablename__ = "buy_orders"

    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    security_id = Column(UUID, ForeignKey("securities.id"), nullable=False)
    number_of_shares = Column(Float, nullable=False)
    price = Column(Float, nullable=False)

    user = relationship("User", back_populates="buy_orders")
    matches = relationship("Match", back_populates="buy_order")
    security = relationship("Security", back_populates="buy_orders")


class Match(Base):
    __tablename__ = "matches"

    buy_order_id = Column(UUID, ForeignKey("buy_orders.id"), nullable=False)
    sell_order_id = Column(UUID, ForeignKey("sell_orders.id"), nullable=False)
    number_of_shares = Column(Float, nullable=False)
    price = Column(Float, nullable=False)

    buy_order = relationship("BuyOrder", back_populates="matches")
    sell_order = relationship("SellOrder", back_populates="matches")


engine = create_engine(APP_CONFIG["DATABASE_URL"])


Session = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
