from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid

class Product(Base):
    __tablename__ = "products"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name          = Column(String(500), nullable=False)
    category      = Column(String(100), nullable=True)
    brand         = Column(String(100), nullable=True)
    image_url     = Column(Text, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    prices = relationship("Price", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product {self.name}>"