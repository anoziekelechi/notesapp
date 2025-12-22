

APP_MODE=development
DATABASE_URL=postgresql+asyncpg://echezonz:app123456:5432/fastapidb
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=djangotesting25@gmail.com
MAIL_PASSWORD=fduz yktx fkiu wanf
MAIL_SSL_TLS=False
MAIL_FROM=djangotesting25@gmail.com
MAIL_STARTTLE=True
USE_CREDENTIALS=True
MAIL_FROM_NAME=ecommerce
VALIDATE_CERTS=True
SECRET_KEY=mysecret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=20
REFRESH_TOKEN_EXPIRES_DAYS=7

class AppMode(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"

class Settings(BaseSettings):
    app_mode:AppMode = Field(default=AppMode.PRODUCTION) 
    DATABASE_URL: str
    APP_NAME: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_PORT: int
    MAIL_TLS: bool
    MAIL_SSL: bool
    MAIL_SERVER: str
    broker: str
    backend: str
    
    
    model_config = SettingsConfigDict(
    env_file = None, #None, #lets docker injects
    env_file_encoding='utf-8',
    extra="ignore",
    case_sensitive=False,
    )
    
    
    
    def is_production(self) -> bool:
        return self.app_mode == AppMode.PRODUCTION
    
    def is_development(self) -> bool:
        return self.app_mode == AppMode.DEVELOPMENT
    
    
   

@lru_cache()
def get_settings() -> Settings:
    return Settings()
