import json
import argparse
from PIL import Image
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter


def main(args):
    with open(args.json_path) as f:
        telegram_data = json.load(f)
        if args.total == True:
            chat_list = telegram_data["chats"]["list"]
        else:
            chat_list = [telegram_data]
        for chat in chat_list:
            try:
                name = chat["name"]
                print(name)
            except KeyError:
                name = None

            words_concat = ""
            links = ""
            for message in chat["messages"]:
                if message["type"] == "message" and type(message["text"]) == type(""):
                    words_concat += message["text"]
                    words_concat += " "
                elif type(message["text"]) == type([]):
                    for message_part in message["text"]:
                        if type(message_part) == type({}):
                            links += message_part["text"]
                            links += " "
                        else:
                            words_concat += message_part
            with open(f"{args.out}/{name}.txt", "w") as of:
                of.write(words_concat)

            words_dict = dict()
            words = words_concat.split(" ")
            for word in words:
                if word in words_dict:
                    words_dict[word] += 1
                else:
                    words_dict[word] = 1

            if args.remove_top:
                d = Counter(words_dict)
                d.most_common()
                top_k = int(0.02 * len(d))
                for k, v in d.most_common(top_k):
                    del words_dict[k]
            
            if args.denylist:
                with open("denylist.txt") as bl:
                    denylist = bl.read().splitlines()
                    print(denylist)
                    d = Counter(words_dict)
                    d.most_common()
                    for k, v in d.items():
                        if k in denylist:
                            del words_dict[k]

                
            wordcloud = WordCloud().generate_from_frequencies(words_dict)
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.axis("off")
            plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse the result.json data of telegram chats, concatenate each chat into a different txt, to be used with an external word cloud program, and visualize a simple word cloud"
    )
    parser.add_argument(
        "--json_path",
        required=True,
        help="Path to the json file saved from telegram desktop",
    )
    parser.add_argument(
        "--total",
        default=False,
        action="store_true",
        help="True if the json file contains all the chats, False if its the json of a single chat",
    )
    parser.add_argument(
        "--remove_top",
        default=False,
        action="store_true",
        help="Typically the top 2% are articles, conjunctions and other non interesting words",
    )
    parser.add_argument(
        "--denylist",
        default=False,
        action="store_true",
        help="Remove the denylist words",
    )
    parser.add_argument(
        "--out",
        default="out",
        help="Directory where txt will be saved",
    )
    args = parser.parse_args()
    main(args)
