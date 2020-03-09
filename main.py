import ast
import json
from getpass import getpass

import requests
from requests import RequestException

import pinyin
import pickle

from tqdm import tqdm

from pprint import pprint

from config import ling_user_name, ling_password

'''
# Class for fields in Anki with the corresponding attribute at LingQ
# A list of AnkiField objects is used to store which field was assigned which attribute in select_fields()
class AnkiField:
    mField = ""  # The actual name of the field
    mCorrespondingLingqAttribute = ""  # The Corresponding attribute at lingQ, as set by the user

    # simple constructor
    def __init__(self, field, lingq_attribute):
        self.mField = field
        self.mCorrespondingLingqAttribute = lingq_attribute


# Takes a list (l) of dictionaries, extracts the item needed with dict_key,
# and makes one long string of all of those items
# with c added as a separator between each item and the next
def list_of_dicts_to_string(l, dict_key, c):
    string = ""
    for num, item in enumerate(l, start=0):
        string = string + item[dict_key]
        if len(l) > 1 and not num == len(l):
            string = string + c
    return string
'''
'''
# Takes a list (l) of strings, and combines all items into
# one long string with c added as a separator between each item and the next
def list_to_string(l, c):
    string = ""
    for num, item in enumerate(l, start=1):
        string = string + item
        if len(l) > 1 and not num == len(l):
            string = string + c
    return string
'''
'''
# Gets the selected item's number from the user,
# makes sure it is a positive integer within the list's bound and returns it
def select_item_from_list(upper_bound, prompt=""):
    selection = input(prompt)
    while not selection.isdigit() or int(selection) < 1 or int(selection) > upper_bound:
        print("Please select one of the available options:\t")
        selection = input()
    return int(selection)
'''
# Gets the action and parameters sent to Ankiconnect, and returns it as a dictionary
# to be sent as a JSON
def form_request(action, **params):
    # check if the version of Ankiconnect has been set
    '''
    try:
        version
    except NameError:
        # If no, do not send it. Let the server assume it's 6
        return {'action': action, 'params': params}
    else:
        # If yes, send it
    '''

    return {'action': action, 'params': params, 'version': 6}

# sends a request to Ankiconnect containing an action and parameters
# see all requests available here: https://foosoft.net/projects/anki-connect/index.html#supported-actions
def send_request(action, **params):
    # get the request as a dictionary and convert it to a JSON string
    request = json.dumps(form_request(action, **params))
    # URL for communicating with Ankiconnect
    URL = 'http://localhost:8765'

    # send request and return result
    try:
        r = requests.get(URL, data=request)
    except RequestException:
        print("Cannot connect to Ankiconnect.\nPlease make sure Anki is running and that the Ankiconnect extension is "
              "installed.")
        input("\nPress enter to exit...")
        exit(1)
    if not action == 'version' \
            and not json.loads(r.text)["error"] is None \
            and not json.loads(r.text)["error"] == 'cannot create note because it is a duplicate':
        print("ERROR:", json.loads(r.text)["error"])
        print("\nPlease fix the error above, make sure Anki is running and your preferred profile is selected.")
        input("\nPress enter to exit...")
        exit(1)
    return r

'''
# Creates a new Anki deck and returns its name
def create_deck():
    name = input("Enter the new deck's name:\t")
    print("Creating deck...")
    send_request("createDeck", deck=name)
    print("Done creating deck")
    return name
'''

'''
# Allows the user to select which deck to add all the LingQs to
def select_deck():
    # Get all the decks at Anki
    response = send_request("deckNames")
    decks = json.loads(response.text)#["result"]
    # List all decks, prompt the user to select the deck or add a new deck
    print("Which deck do you want to import the LingQs to?")
    print("1- Create a new deck")
    for num, d in enumerate(decks, start=2):
        print(str(num) + "-", d)

    #[DdeR] There is a logic bug here. Needed to add the +1 as the last deck could never be selected    
    d = select_item_from_list(len(decks) + 1)
    # If the user choose to create a deck, call the create_deck() function
    # and select that deck as the one to add all the LingQs to
    # Otherwise, select the deck the user chose
    if d == 1:
        d = create_deck()
    else:
        d = decks[d - 2]
    
    # Return the name of the selected deck
    #return d
    #[DdeR] Hard Coding the deck name TODO: Add to configuration file
    return "LingQ"
'''

'''
# Allows the user to select which model to add all the LingQs with
# returns that model's name
def select_model():
    # Get all the model names from Ankiconnect
    response = send_request("modelNames")
    # Convert the result from a JSON string to a dictionary
    # and store the result as a list of strings
    models = json.loads(response.text)["result"]
    # Prompt the user to select a model and list all the models available
    print("Select the model you would like all your LingQs to be added with:")
    for num, model in enumerate(models, start=1):
        print(str(num) + "-", model)
    # Allow the user to select the model
    model = select_item_from_list(len(models))
    # return the model at the position the user selected
    #return models[model - 1]
    #[DdeR] Hardcoding the model name
    return 'LingQ'
'''

# Receives the username and password of the LingQ account,
# longs into that account, and retrieves all the LingQs the user has
# Returning them as a list of dictionaries
def retrieve_lingqs(username=ling_user_name, password=ling_password):
    print("Connecting to LingQ...")
    # Get the API key for the account
    auth = requests.post("https://www.lingq.com/api/api-token-auth/",
                         data={'username': username, 'password': password})
    # If the response has a status code of 400 (Bad Request error), print the error message and return 1 (unsuccessful)
    if auth.status_code == 400:
        print("HTTP ERROR 400: ", auth.text)
        return 1
    # convert API key from JSON string to dictionary and store its token
    api_key = ast.literal_eval(auth.text)["token"]

    # Add the API key as a header to be used in URL's
    headers = {'Authorization': 'Token {}'.format(api_key)}

    # Get the languages the user has at LingQ
    response = requests.get('https://www.lingq.com/api/languages/', headers=headers)
    languages = json.loads(response.text)

    # Let the user select which language to import
    #print("Select the language you would like to import:")
    #for num, language in enumerate(languages, start=1):
    #    print(str(num) + "-" + language["title"])
    #language = select_item_from_list(len(languages))
    #[DdeR] Hardcoding language to be Chinese
    language = 3

    # Get all LingQs from that language.
    print("Retrieving all LingQs for", languages[language - 1]["title"])
    print("This may take several minutes\nPlease wait...")
    # The URL should be https://www.lingq.com/api/languages/(language code here)/lingqs
    response = requests.get('https://www.lingq.com/api/languages/' + languages[language - 1]["code"] + '/lingqs',
                            headers=headers)
    # convert the response from a JSON string to a list
    data = json.loads(response.text)
    print("Done.\n")
    return data


# Allows the user to select which fields in the model to store which LingQ attributes in
# Receives the model name (By default that would be the basic model) and returns a list of AnkiField
# objects with each storing the field name and the corresponding LingQ attribute
'''
def select_fields(model="Basic"):
    # Get a list of all the fields in the model selected
    response = send_request("modelFieldNames", modelName=model)
    # Convert the response from a JSON string to a dictionary and get the result item
    # of that dictionary, which should be a list of all the fields stored in fields_available
    fields_available = json.loads(response.text)#["result"]
    # Make a list of AnkiField objects and initialize it with all the mFields member variables with
    # items from fields_available
    fields = []
    for i in range(len(fields_available)):
        fields.append(AnkiField(fields_available[i], ""))
    lingq_attributes_available = LINGQ_ATTRIBUTES[:]

    print("\nPlease select which fields in the model \"" + model +
          "\" to correspond with which LingQ attribute.")
    while len(fields_available) > 0:
        for num, field in enumerate(fields_available, start=1):
            print(str(num) + "-", field)
        field = select_item_from_list(len(fields_available), "Select the field:\t")

        print("\n1- Keep this field empty")
        for num, lingq_attribute in enumerate(lingq_attributes_available, start=2):
            print(str(num) + "-", lingq_attribute.capitalize())
        lingq_attribute = select_item_from_list(len(lingq_attributes_available) + 1,
                                                "Select the lingq attribute to store in the field \"" +
                                                fields_available[field - 1] + "\" :\t")

        if not lingq_attribute == 1:
            for num, f in enumerate(fields, start=0):
                if f.mField == fields_available[field - 1]:
                    fields[num].mCorrespondingLingqAttribute = lingq_attributes_available[lingq_attribute - 2]
            lingq_attributes_available.pop(lingq_attribute - 2)
        fields_available.pop(field - 1)
        print()

    #field should be a list of type AnkiField -> .mField (Anki Field e.g.
    #'Front' or 'Back'), .mCorrespondingLingqAttribute (dictionary key of Lingq
    #Attributes)

    return fields


def add_notes(deck, fields, lingqs):
    print("Adding notes.\nThis may take a very long time.\nPlease be patient...")
    fields_dict = {}
    lingqs_added = len(lingqs)
    for lingq in lingqs:
        # Skip LingQs that are known
        if lingq["status"] == 3:
            lingqs_added -= 1
            continue
        for f in fields:
            if f.mCorrespondingLingqAttribute == LINGQ_ATTRIBUTES[1]:
                fields_dict[f.mField] = list_of_dicts_to_string(lingq[f.mCorrespondingLingqAttribute], "text", '\n')
            elif f.mCorrespondingLingqAttribute == LINGQ_ATTRIBUTES[4]:
                fields_dict[f.mField] = list_to_string(lingq[f.mCorrespondingLingqAttribute], ', ')
            elif f.mCorrespondingLingqAttribute == "":
                fields_dict[f.mField] = ""
            else:
                fields_dict[f.mField] = lingq[f.mCorrespondingLingqAttribute]
        response = json.loads(send_request("addNote", note={"deckName": deck,
                                                            "modelName": model,
                                                            "fields": fields_dict,
                                                            "options": {"allowDuplicate": False},
                                                            "tags": []}).text)
        if response["error"] is None:
            print(
                "Added LingQ \"" + lingq['term'] + "\"" + (("{:>" + str(45 - len(lingq["term"]) + 3) + "}").format(
                    " as a note with the ID:" + str(response["result"]))))
        else:
            print("Error adding LingQ \"" + lingq['term'] + "\":", response["error"])
            lingqs_added -= 1
     print("Done adding", lingqs_added, " LingQs as notes to", deck, ".")
'''

#LINGQ_ATTRIBUTES = ['term', 'hints', 'fragment', 'notes', 'tags']
#while True:
    #[DdeR] Hardcoded my own username and password
    #username = input("Enter your LingQ username:\t")
    #password = getpass("Enter your LingQ password:\t")
    #lingqs = retrieve_lingqs(username, password)
    
    #Connect to Lingq API
lingqs = retrieve_lingqs()
    

'''
#example schema return from lingq
{'extended_status': 3,
 'fragment': '这 是 全 中国 的 一个 传统 吗 ， 还是 主要 是 广东 人 的 这种 传统 ？',
 'hints': [{'id': 22104984,
            'locale': 'en',
            'popularity': 124,
            'text': 'whole, entire, complete'}],
 'id': 152424515,
 'notes': '',
 'status': 3,
 'tags': [],
 'term': '全',
 'word': 855610}

term = df[i]['term']
text = df[i]['hints'][0]['text']
fragment = df[i]['fragment']
'''

#Build the front of the card
def build_simplified(item):#, reverse = False):i
    return item['term']

#Build the back of the card
def build_pinyin(item):#, reverse = False):
    return pinyin.get(item['term'], delimiter=' ', format='numerical')

def build_meaning(item):
    return item['hints'][0]['text']

def get_known_words():
    with open('known_words.pkl', 'rb') as f:
        return pickle.load(f)

def update_known_words(known_words):
    with open('known_words.pkl', 'wb') as f:
        pickle.dump(known_words, f)

def reset_pickle():
    with open('known_words.pkl', 'wb') as f:
        pickle.dump([], f)


#Insert the card into Anki via Anki Connect
def insert(known_words, lingqs = lingqs, deck = "Hanping Chinese",
           model="Hanping Chinese Type"):
    for item in tqdm(lingqs):
        if item['term'] not in known_words:
            try:
                if item['status'] != 3:
                    #Print the status of the item
                    #print(item['term'])
                    
                    #Build both the front and the back of the cards
                    #for reverse in [True, False]:
                        #print(reverse)
                        #Build the note
                    note_info = {'Simplified': build_simplified(item),
                                 'Meaning': build_meaning(item),
                                 'Pinyin': build_pinyin(item),
                                 'HanziQuestionEnabler': 'x',
                                 'Traditional': build_simplified(item),
                                 'Notes': '',
                                 'Timestamp': '',
                                 'PronunciationQuestionEnabler':'',
                                 'MeaningQuestionEnabler': '',
                                 'TonesQuestionEnabler':'',
                                 'ListeningQuestionEnabler':''}

                        #Insert the card
                    r = send_request("addNote", note={"deckName": deck,
                                                    "modelName": model,
                                                    "fields": note_info,
                                                    "options": {"allowDuplicate": False},
                                                    "tags": []})

            #Print any exceptions
            except Exception as e:
                print(e)
                print(item)

            known_words.append(item['term'])

    update_known_words(known_words)

known_words = get_known_words()
insert(known_words = known_words)

send_request("sync")
