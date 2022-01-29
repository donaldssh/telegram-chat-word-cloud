import json
import argparse
from PIL import Image
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter


def main(args):
    with open(args.json_path, encoding='utf-8') as f:
        telegram_data = json.load(f)
        if args.total == True:
            chat_list = telegram_data["chats"]["list"]
        else:
            chat_list = [telegram_data]
        for chat in chat_list:
            try:
                name = chat["name"]
                print('Chat with: \t', name)
            except KeyError:
                name = None              
            try:
                start_date = chat["messages"][0]["date"][:10]
            except KeyError:
                start_date = None           
            try:
                end_date = chat["messages"][-1]["date"][:10]
            except KeyError:
                end_date = None
              
            s = 0
            e = len(chat["messages"])
            
            # if range of dates is selected
            if args.start_date != None:
                for idx in range(s,e):
                    if chat["messages"][idx]["date"][:10] == args.start_date:
                        start_date = args.start_date
                        s = idx
                        break
            print('Start date: \t', start_date)
                        
            if args.end_date != None:
                for idx in range(s,e):
                    if chat["messages"][idx]["date"][:10] == args.end_date:
                        end_date = args.end_date
                        e = idx
                        break
            print('End date: \t', end_date)            

            words_concat = ""
            links = ""
            for message in chat["messages"][s:e]:
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
            with open(f"{args.out}\{name}.txt", "w", encoding='utf-8') as of: 
                of.write(words_concat)

            words_dict = dict()
            
            #polish
            if args.polish:
                words_concat = words_concat.replace("(","")
                words_concat = words_concat.replace(")","")
                words_concat = words_concat.replace(".","")
                words_concat = words_concat.replace(",","")
                words_concat = words_concat.replace("!","")
                words_concat = words_concat.replace("?","")
                words_concat = words_concat.lower()
            
            words = words_concat.split(" ")
            for word in words:
                if word in words_dict:
                    words_dict[word] += 1
                else:
                    words_dict[word] = 1
            with open(f"{args.out}\{name}_dict.txt", "w", encoding='utf-8') as of: 
                for item in words_dict:
                    line = item + ", " + str(words_dict[item])
                    of.write(line+"\n")
                    
            #if find a word
            if args.find != None:
                word = args.find
                if word in words_dict:
                    print("Occurencies of word '" + word +"': " + str(words_dict[word]))
                else:
                    print("No occurrences of word '" + word +"'")

            if args.remove_top:
                d = Counter(words_dict)
                d.most_common()
                top_k = int(args.k * len(d))
                for k, v in d.most_common(top_k):
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
        "--polish",
        default=False,
        action="store_true",
        help="Typically there are a lot of punctuation and upper letters in a conversation.",
    )
    parser.add_argument(
        "--k",
        default=0.02,
        type=float,
        help="Percentage of words to be removed",
    )
    parser.add_argument(
        "--start_date",
        default=None,
        help="Start date in format 'yyyy-mm-dd'",
    )
    parser.add_argument(
        "--end_date",
        default=None,
        help="End date in format 'yyyy-mm-dd'",
    )
    parser.add_argument(
        "--find",
        default=None,
        help="Search occurencies of a word",
    )
    parser.add_argument(
        "--out",
        default="out",
        help="Directory where txt will be saved",
    )
    args = parser.parse_args()
    main(args)
