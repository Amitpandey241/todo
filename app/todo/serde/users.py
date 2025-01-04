from marshmallow import Schema, fields
from .tasks import TaskSchema


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)  # Use `load_only` for security
    tasks = fields.Nested(TaskSchema, many=True, dump_only=True)
