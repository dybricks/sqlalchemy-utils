import sqlalchemy as sa

json = None
try:
    import anyjson as json
except ImportError:
    pass

import six
from sqlalchemy.dialects.postgresql.base import ischema_names
from ..exceptions import ImproperlyConfigured

try:
    from sqlalchemy.dialects.postgresql import JSON
    has_postgres_json = True
except ImportError:
    class PostgresJSONType(sa.types.UserDefinedType):
        """
        Text search vector type for postgresql.
        """
        def get_col_spec(self):
            return 'json'

    ischema_names['json'] = PostgresJSONType
    has_postgres_json = False


class JSONType(sa.types.TypeDecorator):
    """
    JSONType offers way of saving JSON data structures to database. On
    PostgreSQL the underlying implementation of this data type is 'json' while
    on other databases its simply 'text'.

    ::


        from sqlalchemy_utils import JSONType


        class Product(Base):
            __tablename__ = 'product'
            id = sa.Column(sa.Integer, autoincrement=True)
            name = sa.Column(sa.Unicode(50))
            details = sa.Column(JSONType)


        product = Product()
        product.details = {
            'color': 'red',
            'type': 'car',
            'max-speed': '400 mph'
        }
        session.commit()
    """
    impl = sa.UnicodeText

    def __init__(self):
        if json is None:
            raise ImproperlyConfigured(
                'JSONType needs anyjson package installed.'
            )

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            # Use the native JSON type.
            if has_postgres_json:
                return dialect.type_descriptor(JSON())
            else:
                return dialect.type_descriptor(PostgresJSONType())
        else:
            return dialect.type_descriptor(self.impl)

    def process_bind_param(self, value, dialect):
        if dialect.name == 'postgresql':
            return value
        if value is not None:
            value = six.text_type(json.dumps(value))
        return value

    def process_result_value(self, value, dialect):
        if dialect.name == 'postgresql':
            return value
        if value is not None:
            value = json.loads(value)
        return value
