from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# localhost por mientras, cambiar luego
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/suscripciones_db"

engine = create_async_engine(DATABASE_URL, echo=True)

# crea las tablas automaticamente
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# sesion para manejar peticiones a la base de datos
async def get_session():
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session