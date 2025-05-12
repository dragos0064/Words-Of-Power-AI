import json
from sentence_transformers import SentenceTransformer, util
import requests
from time import sleep
import random

host = "http://10.41.186.9:8000"
post_url = f"{host}/submit-word"
get_url = f"{host}/get-word"
status_url = f"{host}/status"

NUM_ROUNDS = 10
# Load your destroyer mapping
with open("destruction_list.json", "r") as f:
    destroyers = json.load(f)

# Load improved model
model = SentenceTransformer('thenlper/gte-large')  # More powerful model for better semantic matching


def smart_words(thing):
    destructive_keywords = ["fire", "earthquake", "flood", "war", "virus", "lava", "tsunami", "hurricane", "bomb",
                            "explosion"]
    emotional_keywords = ["sadness", "fear", "anger", "trauma", "depression", "ignorance"]

    thing_lower = thing.lower()

    if any(word in thing_lower for word in destructive_keywords):
        return thing_lower, "destruction"
    elif any(word in thing_lower for word in emotional_keywords):
        return "threat", thing_lower
    else:
        return "threat", "destruction"


def generate_sentences(destroyers, thing, threat_word="threat", effect_word="damage"):
    sentences = []
    meta = []
    for destroyer_name in destroyers.keys():
        # Assume each destroyer can have standard verbs
        verbs = ["destroy", "damage", "break", "neutralize"]
        for verb in verbs:
            sentence = f"{destroyer_name} can {verb} a {thing}."
            sentences.append(sentence)
            meta.append(destroyer_name)
    return sentences, meta


def score_sentences(sentences, queries):
    query_embs = model.encode(queries)
    sentence_embs = model.encode(sentences)
    scores = [util.cos_sim(qe, sentence_embs)[0] for qe in query_embs]
    final_scores = scores[0]
    for s in scores[1:]:
        final_scores = final_scores.maximum(s)
    return final_scores


def what_beats(word):
    threshold = 0.65
    top_k = 20

    random_thing = word
    threat_word, effect_word = smart_words(random_thing)
    sentences, meta = generate_sentences(destroyers, random_thing, threat_word, effect_word)
    queries = [
        f"destroying {random_thing}",
        f"causing damage to {random_thing}",
        f"eroding {random_thing}",
        f"breaking {random_thing}",
        f"ending {random_thing}",
        f"neutralizing {random_thing}"
    ]
    scores = score_sentences(sentences, queries)
    destroyer_scores = []
    for i in range(len(sentences)):
        destroyer_name = meta[i]
        score = float(scores[i])
        if score > threshold:
            destroyer_scores.append((destroyer_name, score))
    destroyer_scores = sorted(destroyer_scores, key=lambda x: x[1], reverse=True)[:top_k]
    destroyers_that_work = sorted(set(name for name, _ in destroyer_scores))
    print(f"\nFound {len(destroyers_that_work)} destroyers that can affect '{random_thing}':")
    for destroyer_name in destroyers_that_work:
        print(f"- {destroyer_name}")
    # Build name to ID mapping
    name_to_id = {name: idx + 1 for idx, name in enumerate(destroyers.keys())}

    # Find the cheapest destroyer
    cheapest_destroyer = None
    lowest_price = float('inf')

    for destroyer_name in destroyers_that_work:
        destroyer_info = destroyers.get(destroyer_name)
        if destroyer_info and "price" in destroyer_info:
            price = destroyer_info["price"]
            if price < lowest_price:
                lowest_price = price
                cheapest_destroyer = destroyer_name

    if cheapest_destroyer:
        item_id = name_to_id.get(cheapest_destroyer, "unknown")
        print(f"\nCheapest destroyer: {cheapest_destroyer} (Price: {lowest_price}, ID: {item_id})\n")
    else:
        print("\nNo destroyer found!\n")

    return item_id


def play_game(player_id):
    def get_round():
        print("test")
        print(get_url)
        response = requests.get(get_url)
        print(response.json())
        sys_word = response.json()['word']
        round_num = response.json()['round']
        return (sys_word, round_num)

    submitted_rounds = []
    round_num = 0

    while round_num != NUM_ROUNDS:
        print(submitted_rounds)
        sys_word, round_num = get_round()
        while round_num == 0 or round_num in submitted_rounds:
            sys_word, round_num = get_round()

        if round_num > 1:
            status = requests.post(status_url, json={"player_id": player_id}, timeout=2)
            print(status.json())

        choosen_word = what_beats(sys_word)
        data = {"player_id": player_id, "word_id": choosen_word, "round_id": round_num}
        response = requests.post(post_url, json=data, timeout=5)
        submitted_rounds.append(round_num)
        print("POST: !!!!!!!!!!!!!!!!")
        print(response.json())


if _name_ == "_main_":
    play_game("5GunoI8K")