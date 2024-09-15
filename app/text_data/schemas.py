import time

from marshmallow import Schema, fields

from app.text_data.service import TextService


class TextAnalysisResponseSchema(Schema):

    text = fields.Method("get_text")
    sentiment = fields.Method("get_sentiment")
    entities = fields.Method("get_entities")
    keywords = fields.Method("get_keywords")
    summary = fields.Method("get_summary")
    word_count = fields.Method("get_word_count")
    character_count = fields.Method("get_character_count")
    sentence_count = fields.Method("get_sentence_count")
    paragraph_count = fields.Method("get_paragraph_count")

    class Meta:
        fields = (
            "text",
            "sentiment",
            "entities",
            "keywords",
            "summary",
            "word_count",
            "character_count",
            "sentence_count",
            "paragraph_count",
        )

    def get_text(self, obj: TextService):
        return obj.text

    def get_sentiment(self, obj: TextService):
        start = time.perf_counter()
        result = obj.analyze_sentiment_transformers()
        end = time.perf_counter()
        print(f"Time taken for sentiment analysis: {end - start}")
        return result

    def get_entities(self, obj: TextService):
        start = time.perf_counter()
        result = obj.get_named_entities()
        end = time.perf_counter()
        print(f"Time taken for entity recognition: {end - start}")
        return result

    def get_keywords(self, obj: TextService):
        start = time.perf_counter()
        result = obj.get_keywords()
        end = time.perf_counter()
        print(f"Time taken for keyword extraction: {end - start}")
        return result

    def get_summary(self, obj: TextService):
        start = time.perf_counter()
        result = obj.summarize_text()
        end = time.perf_counter()
        print(f"Time taken for summarization: {end - start}")
        return result

    def get_word_count(self, obj: TextService):
        return obj.get_word_count()

    def get_character_count(self, obj: TextService):
        return obj.get_character_count()

    def get_sentence_count(self, obj: TextService):
        start = time.perf_counter()
        result = obj.get_sentence_count()
        end = time.perf_counter()
        print(f"Time taken for sentence count: {end - start}")
        return result

    def get_paragraph_count(self, obj: TextService):
        return obj.get_paragraph_count()


# category will be Dict[str, List[str]] where key is the category name and value is a list of texts

TextCategorizeRequestSchema = Schema.from_dict(
    {
        "text": fields.Str(required=True, description="Text to categorize"),
        "categories": fields.Dict(
            keys=fields.Str(),
            values=fields.List(fields.Str(), required=True, description="List of texts for each category"),
            required=True,
            description="Categories and their texts",
        ),
    }
)

TextVisualizeRequestSchema = Schema.from_dict(
    {
        "text": fields.Str(required=True, description="Text to visualize"),
        "texts": fields.List(fields.Str(), required=True, description="List of texts"),
    }
)
