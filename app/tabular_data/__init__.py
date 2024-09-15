from flask import Blueprint

tabular_blueprint = Blueprint("tabular", __name__)

from app.tabular_data.resources import NewTabularDataFileResource, TabularDataFileResource, TabularDataFilesResource

# Register the routes for the tabular data blueprint
tabular_blueprint.add_url_rule(
    "/files/new", view_func=NewTabularDataFileResource.as_view("new_tabular_data_file_resource")
)
tabular_blueprint.add_url_rule(
    "/files/<int:tabular_data_file_id>", view_func=TabularDataFileResource.as_view("tabular_data_file_resource")
)
tabular_blueprint.add_url_rule("/files", view_func=TabularDataFilesResource.as_view("tabular_data_files_resource"))
