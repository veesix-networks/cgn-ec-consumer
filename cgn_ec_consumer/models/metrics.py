from sqlalchemy import DateTime, SmallInteger, Integer, VARCHAR, Column
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import PrimaryKeyConstraint


Base = declarative_base()

class MetricBase(Base):
    __abstract__ = True


class NATSessionMapping(MetricBase):
    __tablename__ = "session_mapping"
    __table_args__ = (
        PrimaryKeyConstraint(
            "timestamp", "host", "event", "src_ip", "src_port", "dst_ip", "dst_port"
        ),
        {"timescaledb_hypertable": {"time_column_name": "timestamp"}},
    )

    timestamp = Column(DateTime(timezone=True))
    host = Column(INET)
    event = Column(Integer)
    vrf_id = Column(VARCHAR, nullable=True)
    protocol = Column(SmallInteger)
    src_ip = Column(INET)
    src_port = Column(Integer)
    x_ip = Column(INET)
    x_port = Column(Integer)
    dst_ip = Column(INET)
    dst_port = Column(Integer)


class NATAddressMapping(MetricBase):
    __tablename__ = "address_mapping"
    __table_args__ = (
        PrimaryKeyConstraint("timestamp", "host", "event", "vrf_id", "src_ip", "x_ip"),
        {"timescaledb_hypertable": {"time_column_name": "timestamp"}},
    )

    timestamp = Column(DateTime(timezone=True))
    host = Column(INET)
    event = Column(SmallInteger)
    vrf_id = Column(VARCHAR, nullable=True)
    src_ip = Column(INET)
    x_ip = Column(INET)


class NATPortMapping(MetricBase):
    __tablename__ = "port_mapping"
    __table_args__ = (
        PrimaryKeyConstraint(
            "timestamp",
            "host",
            "event",
            "protocol",
            "src_ip",
            "x_ip",
            "x_ip",
            "x_port",
        ),
        {"timescaledb_hypertable": {"time_column_name": "timestamp"}},
    )

    timestamp = Column(DateTime(timezone=True))
    host = Column(INET)
    event = Column(SmallInteger)
    vrf_id = Column(VARCHAR, nullable=True)
    protocol = Column(SmallInteger)
    src_ip = Column(INET)
    src_port = Column(Integer)
    x_ip = Column(INET)
    x_port = Column(Integer)


class NATPortBlockMapping(MetricBase):
    __tablename__ = "port_block_mapping"
    __table_args__ = (
        PrimaryKeyConstraint(
            "timestamp",
            "host",
            "event",
            "src_ip",
            "x_ip",
            "start_port",
            "end_port",
        ),
        {"timescaledb_hypertable": {"time_column_name": "timestamp"}},
    )

    timestamp = Column(DateTime(timezone=True))
    host = Column(INET)
    event = Column(SmallInteger)
    vrf_id = Column(VARCHAR, nullable=True)
    src_ip = Column(INET)
    x_ip = Column(INET)
    start_port = Column(Integer)
    end_port = Column(Integer)
