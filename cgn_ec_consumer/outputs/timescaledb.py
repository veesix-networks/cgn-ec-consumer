from structlog import get_logger
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import bindparam
from cgn_ec_consumer.models.enums import NATEventEnum
from cgn_ec_consumer.models.metrics import (
    NATPortMapping,
    NATAddressMapping,
    NATPortBlockMapping,
    NATSessionMapping,
)

from cgn_ec_consumer.outputs.base import BaseOutput

logger = get_logger("cgn-ec.outputs.timescaledb")


class TimeScaleDBOutput(BaseOutput):
    def __init__(
        self,
        address: str,
        port: int,
        username: str,
        password: str,
        database: str = "cgnat",
        batch_size: int = 10000,
        preprocessors: list[str] = [],
    ):
        self.address = address
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.batch_size = batch_size
        self.preprocessors = preprocessors
        self._engine: Engine = None
        self._session: Session = None

    def setup(self):
        self._engine = self._get_engine()
        self._session = self._get_session(self._engine)
        self._create_tables_if_not_exist()

    def _get_engine(self):
        return create_engine(
            f"postgresql+psycopg://{self.username}:{self.password}@{self.address}:{self.port}/{self.database}"
        )

    def _get_session(self, engine: Engine, **kwargs) -> Session:
        session = sessionmaker(engine)
        return session

    def _create_tables_if_not_exist(self):
        try:
            from cgn_ec_consumer.models.metrics import Base

            Base.metadata.create_all(self._engine)
        except SQLAlchemyError as err:
            logger.error(f"Failed to create all tables due to error: {err}")
            raise

    def process_metrics(self, metrics: list[dict]) -> bool:
        if not self._engine or not self._session:
            self.setup()

        event_map = {
            NATAddressMapping: [],
            NATPortBlockMapping: [],
            NATSessionMapping: [],
            NATPortMapping: [],
        }

        for metric in metrics:
            # We temporarily process the metric without 'type' and then add it back
            # in the event other metrics want to deal with it
            metric_type = metric.get("type")
            if not metric_type:
                continue

            type_value = None
            if "type" in metric:
                type_value = metric.pop("type")

            try:
                match metric_type:
                    case NATEventEnum.SESSION_MAPPING:
                        event_map[NATSessionMapping].append(metric)
                    case NATEventEnum.ADDRESS_MAPPING:
                        event_map[NATAddressMapping].append(metric)
                    case NATEventEnum.PORT_MAPPING:
                        event_map[NATPortMapping].append(metric)
                    case NATEventEnum.PORT_BLOCK_MAPPING:
                        event_map[NATPortBlockMapping].append(metric)
            finally:
                if type_value is not None:
                    metric["type"] = type_value

        conn = self._engine.raw_connection()
        try:
            cursor = conn.cursor()
            for event_model, model_metrics in event_map.items():
                if not model_metrics:
                    continue

                compiled = (
                    event_model.__table__.insert()
                    .values(
                        **{
                            key: bindparam(key)
                            for key in event_model.__table__.columns.keys()
                        }
                    )
                    .compile(dialect=self._engine.dialect)
                )

                # Batch inserts
                for i in range(0, len(model_metrics), self.batch_size):
                    batch = model_metrics[i : i + self.batch_size]

                    if compiled.positional:
                        args = [
                            tuple(
                                metric[col.name]
                                for col in event_model.__table__.columns
                            )
                            for metric in batch
                        ]
                    else:
                        args = batch

                    logger.info(f"Executing batch insert of size: {len(batch)}")
                    cursor.executemany(str(compiled), args)
            conn.commit()
        except Exception as e:
            logger.error(f"Error during raw DBAPI insert: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

        logger.debug("Processed TimescaleDB Metrics")
        return True
