from contextlib import asynccontextmanager
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy import MetaData

class Database:
	_instance = None

	def __new__(cls, *args, **kwargs) -> 'Database':
		if cls._instance is None:
			cls._instance = super().__new__(cls)
			cls._instance._initialized = False
		return cls._instance

	def __init__(self, database_uri: str, all_bases: List[declarative_base] = [], db_echo: bool = True) -> None:
		"""
		Initialize the Database instance.
		
		Args:
			database_uri (str): The URI for the database connection.
			all_bases (List[declarative_base], optional): List of declarative base classes to combine metadata.
		"""
		assert isinstance(all_bases, list), f"{type(all_bases)} is not a List"
		
		if self._initialized:
			return
		
		self._initialized = True

		self.engine = create_async_engine(database_uri, echo=db_echo)
		self.async_session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False, autocommit=False)
		self.combined_meta_data = MetaData()
		
		self._combined_all_meta_data(all_bases)
		
	def _combined_all_meta_data(self, all_bases: List[Optional[DeclarativeMeta]]) -> None:
		"""
		Combine metadata from all declarative base classes.
		
		Args:
			all_bases (List[Optional[DeclarativeMeta]]): List of declarative base classes.
		"""
		for declarative_base in all_bases:
			assert isinstance(declarative_base, DeclarativeMeta), f"{type(declarative_base)} is not DeclarativeMeta"
			for (table_name, table) in declarative_base.metadata.tables.items():
				self.combined_meta_data._add_table(table_name, table.schema, table)

	async def db_connect(self) -> AsyncSession:
		"""
		Connect to the database and return an async session.
		
		Returns:
			AsyncSession: An async session object for database operations.
		"""
		if not self.engine:
			raise Exception("Database engine is not initialized.")

		return self.async_session
	
	async def init_models(self) -> None:
		"""
		Initialize database models by creating tables.
		"""
		async with self.engine.begin() as conn:
			await conn.run_sync(self.combined_meta_data.create_all)

	@asynccontextmanager
	async def get_db(self, autocommit: bool = False) -> AsyncSession:
		"""
		Context manager to get a database session.

		Args:
			autocommit (bool, optional): Whether to autocommit transactions.

		Yields:
			AsyncSession: An async session object for database operations.
		"""
		if not self.engine:
			raise Exception("Database engine is not initialized.")

		session_maker = await self.db_connect()
		session = session_maker()

		try:
			yield session
			if autocommit:
				await session.commit()
		
		except Exception as e:
			await session.rollback()
			raise e
		
		finally:
			await session.close()
