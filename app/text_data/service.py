from io import BytesIO
from typing import List

import nltk
import numpy as np
from matplotlib import pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE
from transformers import pipeline
from wordcloud import WordCloud

# Initialize NLTK resources
nltk.download("vader_lexicon")

# Initialize transformers for summarization
summarizer = pipeline("summarization")

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

    def summarize_text(self, max_length: int = 100, min_length: int = 50, length_penalty: float = 2.0):
        return summarizer(self.text, max_length=max_length, min_length=min_length, do_sample=False)[0]["summary_text"]

    def analyze_sentiment(self):
        return sia.polarity_scores(self.text)

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
        return img_io.read()

    def get_named_entities(self):
        return pipeline("ner")(self.text)

    def visualize_tsne(
        self, text2: str, n_components: int = 2, perplexity: int = 30, n_iter: int = 1000, random_state: int = 42
    ):

        # Create matrix
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform([self.text, text2])

        # Apply TSNE
        tsne = TSNE(n_components=n_components, perplexity=perplexity, n_iter=n_iter, random_state=random_state)
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

    def search_text(self, query: str):
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform([self.text])
        query_vector = vectorizer.transform([query])

        # Calculate cosine similarity
        similarity = np.dot(matrix, query_vector.T).flatten()
        results_list = [
            {"sentence": sentence, "similarity": similarity} for sentence, similarity in zip([self.text], similarity)
        ]
        sorted_results = sorted(results_list, key=lambda x: x["similarity"], reverse=True)
        return sorted_results

    def categorize_text(self, categories: List[str]) -> str:
        return np.random.choice(categories)
