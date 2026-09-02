from pydantic_settings import BaseSettings
from pydantic import Field

class ServiceSettings(BaseSettings):
    """Enterprise configuration for checkout microservice."""
    service_name: str = Field(default="checkout-api")
    service_version: str = Field(default="v2.4.1")
    mongo_uri: str = Field(default="mongodb://localhost:27017/")
    database_name: str = Field(default="ecommerce_prod")
    collection_name: str = Field(default="cart_items")
    slo_p99_latency_threshold_ms: float = Field(default=20.0)
    sample_benchmark_size: int = Field(default=15)

    class Config:
        env_file = ".env"
        extra = "ignore"

service_config = ServiceSettings()
