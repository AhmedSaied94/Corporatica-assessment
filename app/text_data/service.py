import re
from io import BytesIO
from typing import Dict, List

import nltk
import numpy as np
from matplotlib import pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline
from wordcloud import WordCloud

# Initialize NLTK resources
nltk.download("vader_lexicon")
nltk.download("punkt")
nltk.download("punkt_tab")

# Initialize transformers for summarization, named entity recognition, and sentiment analysis
summarizer = pipeline(
    "summarization", model="facebook/bart-base", tokenizer="facebook/bart-base", framework="pt"
)  # replace with "facebook/bart-base" for better results
entity_recognizer = pipeline(
    "ner",
    model="dbmdz/bert-large-cased-finetuned-conll03-english",
    tokenizer="dbmdz/bert-large-cased-finetuned-conll03-english",
)
sentiment_analyzer = pipeline(
    "sentiment-analysis", model="distilbert-base-uncased", tokenizer="distilbert-base-uncased"
)

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Initialize TF-IDF Vectorizer


class TextService:
    text: str

    def __init__(self, text: str):
        assert text, "Text is required"
        assert isinstance(text, str), "Text must be a string"
        self.text = text

    def get_word_count(self):
        return len(self.text.split())

    def get_character_count(self):
        return len(self.text)

    def get_sentence_count(self):
        return len(nltk.sent_tokenize(self.text))

    def get_paragraph_count(self):
        return len(self.text.split("\n"))

    def summarize_text(self, max_length: int = 100, min_length: int = 50):
        length = self.get_word_count()
        if length < 200:
            length_penalty = 1.5
        elif length < 500:
            length_penalty = 1.2
        else:
            length_penalty = 1.0

        return summarizer(self.text, max_length=max_length, min_length=min_length, length_penalty=length_penalty)[0][
            "summary_text"
        ]

    def analyze_sentiment(self):
        return sia.polarity_scores(self.text)

    def analyze_sentiment_transformers(self):
        return sentiment_analyzer(self.text)

    def get_keywords(self, n_keywords: int = 10) -> List[str]:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=n_keywords)
        matrix = vectorizer.fit_transform([self.text])
        feature_names = vectorizer.get_feature_names_out()
        scores = np.array(matrix.sum(axis=0)).flatten()
        keywords_scores = list(zip(feature_names, scores))
        sorted_keywords = sorted(keywords_scores, key=lambda x: x[1], reverse=True)
        return [keyword for keyword, score in sorted_keywords]

    def generate_word_cloud(
        self, n_words: int = 100, max_font_size: int = 100, width: int = 800, height: int = 400
    ) -> bytes:
        wordcloud = WordCloud(
            width=width, height=height, max_words=n_words, max_font_size=max_font_size, background_color="white"
        ).generate(self.text)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        img_io = BytesIO()
        plt.savefig(img_io, format="PNG")
        img_io.seek(0)
        return img_io

    def get_named_entities(self):
        chunk_size = 256
        chunks = [self.text[i : i + chunk_size] for i in range(0, self.get_character_count(), chunk_size)]

        entities = []
        for chunk in chunks:
            result = entity_recognizer(chunk)
            entities.extend(result)

        return [
            {
                "entity": entity["entity"],
                "score": float(entity["score"]),
                "index": entity["index"],
                "start": entity["start"],
                "end": entity["end"],
                "word": entity["word"],
            }
            for entity in entities
        ]

    def visualize_tsne(
        self,
        texts: List[str],
    ):

        # Create matrix
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform([self.text, *texts])

        # Apply TSNE
        tsne = TSNE(
            n_components=2,
            perplexity=len(texts) // 2,
            n_iter=300,
            random_state=42,
        )
        embeddings = tsne.fit_transform(matrix.toarray())

        # Plot the embeddings
        plt.figure(figsize=(10, 6))
        plt.scatter(embeddings[:, 0], embeddings[:, 1])
        plt.title("t-SNE Visualization")
        plt.xlabel("Component 1")
        plt.ylabel("Component 2")

        # save the plot to a byte stream
        img_io = BytesIO()
        plt.savefig(img_io, format="PNG")
        img_io.seek(0)
        plt.close()

        return img_io

    def get_similarity(self, text2: str):
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform([self.text, text2])
        similarity = np.dot(matrix, matrix.T).toarray()
        return float(similarity[0, 1])

    def search_text(self, query: str) -> List[dict]:
        sentences = nltk.sent_tokenize(self.text)
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform(sentences)
        query_vector = vectorizer.transform([query])

        # Calculate cosine similarity
        similarity = cosine_similarity(matrix, query_vector).flatten()

        results_list = [{"sentence": sentence, "similarity": similarity[idx]} for idx, sentence in enumerate(sentences)]

        sorted_results = sorted(results_list, key=lambda x: x["similarity"], reverse=True)

        return sorted_results

    def categorize_text(self, categories: Dict[str, List[str]]) -> Dict[str, int]:
        """
        Categorize self.text into one of the provided categories based on keyword matching.

        :param categories: A dictionary where keys are category names and values are lists of keywords.
        :return: A dictionary where keys are category names and values are their corresponding scores.
        """
        # Initialize a dictionary to keep track of category scores
        category_scores = {category: 0 for category in categories}

        # Normalize the text
        text = self.text.lower()

        # Calculate scores for each category based on keyword matches
        for category, keywords in categories.items():
            for keyword in keywords:
                if re.search(r"\b" + re.escape(keyword.lower()) + r"\b", text):
                    category_scores[category] += 1

        # Return the dictionary of category scores
        return category_scores
