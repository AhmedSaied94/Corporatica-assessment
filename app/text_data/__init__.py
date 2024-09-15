from flask import Blueprint

from app.text_data.resources import TextAnalysisResource

text_blueprint = Blueprint("text", __name__)

text_blueprint.add_url_rule("/analysis", view_func=TextAnalysisResource.as_view("text_analysis_resource"))
