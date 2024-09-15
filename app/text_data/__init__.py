from flask import Blueprint

from app.text_data.resources import (
    TextAnalysisResource,
    TextCategorizeResource,
    TextSearchResource,
    TextSimilarityResource,
    TextVisualizeResource,
    TextWordCloudResource,
)

text_blueprint = Blueprint("text", __name__)

text_blueprint.add_url_rule("/analysis", view_func=TextAnalysisResource.as_view("text_analysis_resource"))
text_blueprint.add_url_rule("/categorize", view_func=TextCategorizeResource.as_view("text_categorize_resource"))
text_blueprint.add_url_rule("/similarity", view_func=TextSimilarityResource.as_view("text_similarity_resource"))
text_blueprint.add_url_rule("/visualize", view_func=TextVisualizeResource.as_view("text_visualize_resource"))
text_blueprint.add_url_rule("/search", view_func=TextSearchResource.as_view("text_search_resource"))
text_blueprint.add_url_rule("/wordcloud", view_func=TextWordCloudResource.as_view("text_wordcloud_resource"))
