from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str
    redis_url: str

    # Anthropic
    anthropic_api_key: str

    # Pinecone
    pinecone_api_key: str
    pinecone_index_name: str = "medical-guidelines"

    # Auth
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Notifications
    sendgrid_api_key: str = ""
    sendgrid_from_email: str = "noreply@yourdomain.com"
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    # App
    environment: str = "development"
    confidence_threshold: float = 0.65
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


settings = Settings()
