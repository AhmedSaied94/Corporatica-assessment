from flask import request, send_file
from flask_restful import Resource, reqparse
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest

from app.text_data.schemas import TextAnalysisResponseSchema, TextCategorizeRequestSchema, TextVisualizeRequestSchema
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
        response = TextAnalysisResponseSchema().dump(text_service)
        return response


class TextVisualizeResource(Resource):

    def post(self):
        try:
            body = TextVisualizeRequestSchema().load(request.get_json())
        except ValidationError as e:
            return e.messages, 400
        except Exception as e:
            return {"message": str(e)}, 400
        text_service = TextService(body["text"])
        return send_file(
            text_service.visualize_tsne(body["texts"]),
            download_name="tsne.png",
            as_attachment=True,
        )


class TextWordCloudResource(Resource):

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
        return send_file(text_service.generate_word_cloud(), download_name="word_cloud.png", as_attachment=True)


class TextSearchResource(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("text", type=str, required=True, help="Text is required")
        parser.add_argument("query", type=str, required=True, help="Query is required")
        try:
            args = parser.parse_args()
        except BadRequest as e:
            return e.data, e.code
        except Exception as e:
            return {"message": str(e)}, 400

        text = args["text"]
        query = args["query"]
        text_service = TextService(text)
        return text_service.search_text(query)


class TextSimilarityResource(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("text", type=str, required=True, help="Text is required")
        parser.add_argument("text2", type=str, required=True, help="Text is required")
        try:
            args = parser.parse_args()
        except BadRequest as e:
            return e.data, e.code
        except Exception as e:
            return {"message": str(e)}, 400
        text = args["text"]
        text2 = args["text2"]
        text_service = TextService(text)
        result = text_service.get_similarity(text2)
        return {"similarity": result}


class TextCategorizeResource(Resource):

    def post(self):
        try:
            body = TextCategorizeRequestSchema().load(request.get_json())
        except ValidationError as e:
            return e.messages, 400
        except Exception as e:
            return {"message": str(e)}, 400
        text_service = TextService(body["text"])
        return text_service.categorize_text(body["categories"])
