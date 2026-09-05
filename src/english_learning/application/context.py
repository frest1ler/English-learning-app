"""Dependencies shared by presentation pages."""

from dataclasses import dataclass
from logging import Logger

from data.database import LearningDatabase

from english_learning.infrastructure.database import bootstrap_database
from english_learning.infrastructure.logging import configure_logging
from english_learning.infrastructure.paths import AppPaths
from english_learning.infrastructure.settings import AppConfig


@dataclass
class ApplicationContext:
    paths: AppPaths
    config: AppConfig
    database: LearningDatabase
    logger: Logger

    @classmethod
    def create(cls) -> "ApplicationContext":
        paths = AppPaths.discover()
        config = AppConfig.from_environment()
        logger = configure_logging(paths, config.log_level)
        logger.info("Starting English Learning App")
        database = bootstrap_database(paths)
        return cls(paths=paths, config=config, database=database, logger=logger)
