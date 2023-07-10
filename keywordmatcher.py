from pythainlp.tokenize import word_tokenize
from fuzzywuzzy import fuzz
import json

class KeywordMatcher:
    def __init__(self, symptoms, threshold=90):
        self.symptoms = symptoms
        self.threshold = threshold

    def find_matching_keywords(self, user_input):
        user_tokens = word_tokenize(user_input, engine="newmm")
        matching_keywords = []

        for symptom in self.symptoms:
            symptom_tokens = word_tokenize(symptom, engine="newmm")

            for user_token in user_tokens:
                for symptom_token in symptom_tokens:
                    similarity = fuzz.ratio(user_token, symptom_token)

                    if similarity >= self.threshold:
                        matching_keywords.append(symptom)
                        break

        return matching_keywords

if __name__ == "__main__":
    with open('data/fever.json', 'r', encoding='utf-8') as f:
        symptom_names = json.load(f)

    matcher = KeywordMatcher(symptom_names, threshold=90)
    user_input = "ชักไปสองชั่วโมงที่เเล้วละรู้สึกกระหม่อมโป่งตึง"
    matching_keywords = set(matcher.find_matching_keywords(user_input))
    print(matching_keywords)
