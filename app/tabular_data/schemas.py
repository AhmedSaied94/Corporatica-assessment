from marshmallow import EXCLUDE, Schema, fields, validate

from app.tabular_data.models import TabularDataFile, TabularDataFileHeader, TabularDataFileRow


class TabularDataFileHeaderSchema(Schema):
    """
    This class represents the schema for the tabular data file header.
    """

    class Meta:
        model = TabularDataFileHeader
        fields = ("id", "tabular_data_file_id", "header", "index", "created_at", "updated_at")


class TabularDataFileRowSchema(Schema):
    """
    This class represents the schema for the tabular data file row.
    """

    class Meta:
        model = TabularDataFileRow
        fields = ("id", "tabular_data_file_id", "row_data", "index", "created_at", "updated_at")


class TabularDataFileSchema(Schema):
    """
    This class represents the schema for the tabular data file.
    """

    headers = fields.Nested(TabularDataFileHeaderSchema, many=True)
    rows = fields.Nested(TabularDataFileRowSchema, many=True)

    class Meta:
        model = TabularDataFile
        fields = ("id", "name", "path", "created_at", "updated_at", "headers", "rows", "statistics")


class TabularDataFileRowFilterSchema(Schema):
    """
    This class represents the schema for the tabular data file row filter.
    """

    header_id = fields.Integer(required=True)
    # row_value = will be a dynamic field based on the header
    row_value = fields.Raw(required=True)
    # operator = should be one of the following 'like' or 'eq' or 'gt' or 'lt' or 'gte' or 'lte' or in or not in
    operator = fields.String(
        required=True, validate=validate.OneOf(["like", "eq", "gt", "lt", "gte", "lte", "in", "notin"])
    )


class TabularDataFileFilterSchema(Schema):
    """
    This class represents the schema for the tabular data file filter.
    """

    headers = fields.List(fields.Integer(), required=False)
    rows = fields.List(fields.Nested(TabularDataFileRowFilterSchema), required=False)
    rows_filter_operator = fields.String(required=False, validate=validate.OneOf(["and", "or"]), missing="and")
    rows_order_by = fields.String(required=False)
    page = fields.Integer(required=False, missing=1, validate=validate.Range(min=1))
    page_size = fields.Integer(required=False, missing=10, validate=validate.Range(min=5, max=100))


class TabularDataFileRowAddSchema(Schema):
    """
    This class represents the schema for adding a new row to the tabular data file.
    """

    row_data = fields.Dict(required=True)
    id = fields.Integer(required=False)

    class Meta:
        unknown = EXCLUDE


class TabularDataFileUpdateSchema(Schema):
    """
    This class represents the schema for updating the tabular data file.
    """

    name = fields.String(required=False)
    rows = fields.List(fields.Nested(TabularDataFileRowAddSchema), required=False)
    filters = fields.Nested(TabularDataFileFilterSchema, required=False)

    class Meta:
        unknown = EXCLUDE


class PaginationSchema(Schema):
    page = fields.Int(required=True)
    per_page = fields.Int(required=True)
    total = fields.Int(required=True)
    pages = fields.Int(required=True)
    prev_num = fields.Int()
    next_num = fields.Int()
