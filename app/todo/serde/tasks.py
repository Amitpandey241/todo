from marshmallow import Schema, fields


class TaskSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    is_completed = fields.Bool(required=False, default=False)
    due_date = fields.DateTime(allow_none=True, format='iso')
    created_at = fields.DateTime(dump_only=True, format='iso')
    updated_at = fields.DateTime(dump_only=True, format='iso')
    user_id = fields.Int(required=True)
