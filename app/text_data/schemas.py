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
        return obj.analyze_sentiment()

    def get_entities(self, obj: TextService):
        return obj.get_named_entities()

    def get_keywords(self, obj: TextService):
        return obj.get_keywords()

    def get_summary(self, obj: TextService):
        return obj.summarize_text()

    def get_word_count(self, obj: TextService):
        return obj.get_word_count()

    def get_character_count(self, obj: TextService):
        return obj.get_character_count()

    def get_sentence_count(self, obj: TextService):
        return obj.get_sentence_count()

    def get_paragraph_count(self, obj: TextService):
        return obj.get_paragraph_count()
