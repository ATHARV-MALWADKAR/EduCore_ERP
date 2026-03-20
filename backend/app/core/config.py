from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "College ERP"
    app_env: str = Field("development", env="APP_ENV")
    secret_key: str = Field("your-super-secret-key-change-me-in-production", env="SECRET_KEY")

    backend_port: int = Field(8000, env="BACKEND_PORT")
    frontend_port: int = Field(3000, env="FRONTEND_PORT")

    # Database type: sqlite or mysql
    db_type: str = Field("sqlite", env="DB_TYPE")
    
    # MySQL Configuration
    db_host: str = Field("localhost", env="DB_HOST")
    db_port: int = Field(3306, env="DB_PORT")
    db_user: str = Field("college_erp_user", env="DB_USER")
    db_password: str = Field("college_erp_password", env="DB_PASSWORD")
    db_name: str = Field("college_erp", env="DB_NAME")

    access_token_expire_minutes: int = Field(
        60, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.app_env == "test":
            return "sqlite:///./test_college_erp.db"
        
        if self.db_type == "sqlite":
            return "sqlite:///./college_erp.db"
        
        # MySQL default
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()