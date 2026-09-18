from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    log_level: str = "INFO"
    ethereum_rpc_url: str
    poll_interval_seconds: int = 15
    min_value_eth_to_forward: float = 1.0
    risk_engine_url: str = "http://127.0.0.1:8000"

    class Config:
        env_file = ".env"


settings = Settings()
