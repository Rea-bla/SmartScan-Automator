from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid

class Price(Base):
    __tablename__ = "prices"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id     = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    site           = Column(String(100), nullable=False)
    price          = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    url            = Column(Text, nullable=True)
    image_url      = Column(Text, nullable=True)
    in_stock       = Column(Boolean, default=True)
    scraped_at     = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="prices")

    def __repr__(self):
        return f"<Price {self.site} - {self.price} TL>"