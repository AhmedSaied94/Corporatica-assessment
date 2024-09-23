from flask import request
from flask_restful import Resource, fields, marshal_with, reqparse
from marshmallow import ValidationError
from sqlalchemy import Numeric, Text, and_, cast, or_
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest

from app.db import db
from app.helpers import generate_random_filename, secure_filename
from app.tabular_data.models import TabularDataFile, TabularDataFileHeader, TabularDataFileRow
from app.tabular_data.schemas import (
    PaginationSchema,
    TabularDataFileFilterSchema,
    TabularDataFileHeaderSchema,
    TabularDataFileSchema,
    TabularDataFileUpdateSchema,
)
from app.tabular_data.service import TabularDataService
from config import Config

# Define the fields for the tabular data file header response
tabular_data_file_header_fields = {
    "id": fields.Integer,
    "tabular_data_file_id": fields.Integer,
    "header": fields.String,
    "index": fields.Integer,
    "created_at": fields.DateTime,
    "updated_at": fields.DateTime,
}


# Define the fields for the tabular data file row response
tabular_data_file_row_fields = {
    "id": fields.Integer,
    "tabular_data_file_id": fields.Integer,
    "row_data": fields.Raw,
    "index": fields.Integer,
    "created_at": fields.DateTime,
    "updated_at": fields.DateTime,
}


# Define the fields for the tabular data file response
tabular_data_file_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "path": fields.String,
    "created_at": fields.DateTime,
    "updated_at": fields.DateTime,
    "headers": fields.List(fields.Nested(tabular_data_file_header_fields)),
    "rows": fields.List(fields.Nested(tabular_data_file_row_fields)),
    "statistics": fields.Raw,
}


class TabularDataFileResource(Resource):
    """
    This resource class handles the tabular data file endpoints.
    """

    # @marshal_with(tabular_data_file_fields)
    def post(self, tabular_data_file_id, filters=None):
        """
        return a tabular data file while also filtering the tabular data headers to return only the headers
            that user what to see
        also filtering the tabular data rows by the the row_data field to return only the rows that user what to see eg.
        row_data eg. row_data = [
            {
                'header_id': 'value',
                'row_value': 'value',
                'operator': 'like' or 'eq' or 'gt' or 'lt' or 'gte' or 'lte' or in or not in
            },
        ]
        rows_filter_operator = 'and' or 'or' this is the operator that will be used to combine the rows filter
        """
        if filters is None:
            filters = request.get_json()
        assert isinstance(filters, dict)
        # Parse the request arguments
        try:
            body = TabularDataFileFilterSchema().load(filters)
        except ValidationError as e:
            return e.messages, 400
        except Exception as e:
            return {"message": str(e)}, 400

        # Query the tabular data file by its id
        tabular_data_file = TabularDataFile.query.filter_by(id=tabular_data_file_id).first()
        page = body["page"]
        page_size = body["page_size"]
        if not tabular_data_file:
            return {"message": "Tabular data file not found."}, 400

        # Filter the headers of the tabular data file
        with db.session.no_autoflush:
            order_by = body.get("rows_order_by", "index")
            if order_by.startswith("-"):
                order_by = order_by[1:]
                direction = "desc"
            else:
                direction = "asc"
            if order_by in [header.header for header in tabular_data_file.headers]:
                # Cast the JSON field to TEXT for ordering
                order_by = getattr(cast(TabularDataFileRow.row_data[order_by], Text), direction)()
            else:
                # Default ordering
                order_by = getattr(TabularDataFileRow.index, direction)()
            all_headers = TabularDataFileHeader.query.filter_by(tabular_data_file_id=tabular_data_file_id).all()
            if body.get("headers"):
                tabular_data_file.headers = (
                    TabularDataFileHeader.query.filter(
                        TabularDataFileHeader.tabular_data_file_id == tabular_data_file_id,
                        TabularDataFileHeader.id.in_(body["headers"]),
                    )
                    .order_by(TabularDataFileHeader.index)
                    .all()
                )
                if not tabular_data_file.headers:
                    return {"message": "No headers found."}, 400
            # Filter the rows of the tabular data file
            operator = and_ if body["rows_filter_operator"] == "and" else or_

            row_operator_map = {
                "eq": lambda x, y: cast(x, Numeric) == y,
                "gt": lambda x, y: cast(cast(x, Text), Numeric) > y,
                "lt": lambda x, y: cast(cast(x, Text), Numeric) < y,
                "gte": lambda x, y: cast(cast(x, Text), Numeric) >= y,
                "lte": lambda x, y: cast(cast(x, Text), Numeric) <= y,
                "in": lambda x, y: x.in_(y),
                "notin": lambda x, y: x.notin_(y),
                "like": lambda x, y: x.like(f"%{y}%"),
            }
            if body.get("rows"):

                filter_args = []
                for row in body["rows"]:
                    header = TabularDataFileHeader.query.filter_by(id=row["header_id"]).first()
                    if header:
                        json_field = TabularDataFileRow.row_data[header.header]
                        filter_args.append(row_operator_map[row["operator"]](json_field, row["row_value"]))

                pagination = (
                    TabularDataFileRow.query.filter(
                        TabularDataFileRow.tabular_data_file_id == tabular_data_file_id, operator(*filter_args)
                    )
                    .order_by(order_by)
                    .paginate(page=page, per_page=page_size, error_out=False)
                )

            else:
                pagination = (
                    TabularDataFileRow.query.filter_by(tabular_data_file_id=tabular_data_file_id)
                    .order_by(order_by)
                    .paginate(page=page, per_page=page_size, error_out=True)
                )

            if pagination._query_offset >= pagination.total:
                return {"message": "Page out of range."}, 400

            tabular_data_file.rows = pagination.items

            tabular_data_file.statistics = TabularDataService.statistics_from_TabularDataFile(tabular_data_file)
        print("tabular_data_file rows length", len(tabular_data_file.rows))
        return {
            **TabularDataFileSchema().dump(tabular_data_file),
            "rows_count": len(tabular_data_file.rows),
            "pagination": PaginationSchema().dump(pagination),
            "all_headers": TabularDataFileHeaderSchema().dump(all_headers, many=True),
        }

    # @marshal_with(tabular_data_file_fields)
    def put(self, tabular_data_file_id):
        """
        update a tabular data file.
        """

        # Parse the request arguments
        try:
            body = TabularDataFileUpdateSchema().load(request.get_json())
        except ValidationError as e:
            return e.messages, 400
        except Exception as e:
            return {"message": str(e)}, 400

        # Query the tabular data file by its id
        tabular_data_file = TabularDataFile.query.filter_by(id=tabular_data_file_id).first()
        if not tabular_data_file:
            return {"message": "Tabular data file not found."}, 404

        # Update the tabular data file
        tabular_data_file.name = body.get("name", tabular_data_file.name)

        # Update the rows of the tabular data file
        if body.get("rows"):
            last_index = (
                TabularDataFileRow.query.filter_by(tabular_data_file_id=tabular_data_file_id)
                .order_by(TabularDataFileRow.index.desc())
                .first()
                .index
            )
            for row in body["rows"]:
                tabular_data_file_row = TabularDataFileRow.query.filter_by(id=row.get("id")).first()
                if tabular_data_file_row:
                    tabular_data_file_row.row_data = row["row_data"]
                else:
                    tabular_data_file_row = TabularDataFileRow(
                        tabular_data_file_id=tabular_data_file_id, row_data=row["row_data"], index=last_index + 1
                    )
                    last_index += 1
                    db.session.add(tabular_data_file_row)

        db.session.commit()

        return self.post(tabular_data_file_id, body.get("filters", {}))

    def delete(self, tabular_data_file_id):
        """
        delete a tabular data file.
        """

        # Query the tabular data file by its id
        tabular_data_file = TabularDataFile.query.filter_by(id=tabular_data_file_id).first()
        if not tabular_data_file:
            return {"message": "Tabular data file not found."}, 404

        # Delete the tabular data file
        db.session.delete(tabular_data_file)
        db.session.commit()

        return {"message": "Tabular data file deleted."}, 204


class NewTabularDataFileResource(Resource):
    """
    This resource class handles creating a new tabular data file.
    """

    # @marshal_with(tabular_data_file_fields)
    def post(self):
        """
        will create a new tabular data file depending on the user uploaded file.
        the request content type should be multipart/form-data.
        the request should contain the file to upload.
        """

        # Parse the request arguments
        parser = reqparse.RequestParser()
        parser.add_argument(
            "file", type=FileStorage, location="files", required=True, help="The tabular data file to upload."
        )
        try:
            args = parser.parse_args()
        except BadRequest as e:
            return e.data, e.code
        except Exception as e:
            return {"message": str(e)}, 400

        # Check if the file is allowed
        if not args["file"]:
            return {"message": "No file provided."}, 400
        if not self.allowed_file(args["file"].filename):
            return {"message": "File extension not allowed."}, 400

        # Save the file
        filename = secure_filename(args["file"].filename).split(".")[0] + generate_random_filename(
            args["file"].filename
        )
        path = f"{Config.MEDIA_DIR}/{filename}"
        args["file"].save(path)

        # read the tabular data file
        tabular_data_service = TabularDataService(path)
        df = tabular_data_service.process_data()
        # Create the tabular data file
        tabular_data_file = TabularDataService.create_tabular_data_file(
            filename, path, TabularDataService.compute_statistics(df)
        )

        # Create the tabular data file headers

        db.session.add(tabular_data_file)
        db.session.commit()
        db.session.refresh(tabular_data_file)
        try:
            tabular_data_file_headers = TabularDataService.create_tabular_data_file_headers(tabular_data_file, df)
            db.session.add_all(tabular_data_file_headers)
            # db.session.refresh(tabular_data_file_headers)
            # Create the tabular data file rows
            tabular_data_file_rows = TabularDataService.create_tabular_data_file_rows(tabular_data_file, df)

            # Save the tabular data file to the database
            db.session.add_all(tabular_data_file_rows)
        except Exception as e:
            db.session.delete(tabular_data_file)
            db.session.commit()
            return {"message": str(e.args[0])}, 400
        db.session.commit()
        db.session.refresh(tabular_data_file)

        return TabularDataFileSchema().dump(tabular_data_file)

    def allowed_file(self, filename):
        """
        Check if the file extension is allowed.
        """
        ALLOWED_EXTENSIONS = {"csv", "xls", "xlsx"}  # Example extensions
        return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


class TabularDataFilesResource(Resource):
    """
    This resource class handles the tabular data files endpoints.
    """

    @marshal_with(tabular_data_file_fields)
    def get(self):
        """
        return a list of tabular data files.
        """

        # Query all the tabular data files
        tabular_data_files = TabularDataFile.query.all()
        return tabular_data_files
