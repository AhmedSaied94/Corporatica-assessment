from flask_restful import Resource, reqparse
from werkzeug.exceptions import BadRequest

from app.text_data.schemas import TextAnalysisResponseSchema
from app.text_data.service import TextService


class TextAnalysisResource(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("text", type=str, required=True, help="Text is required")
        try:
            args = parser.parse_args()
        except BadRequest as e:
            return e.data, e.code
        except Exception as e:
            return {"message": str(e)}, 400
        text = args["text"]
        text_service = TextService(text)
        return TextAnalysisResponseSchema().dump(text_service)
