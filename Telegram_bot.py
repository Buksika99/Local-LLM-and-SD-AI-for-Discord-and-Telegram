import logging
import requests, json, re, random, datetime, os, base64
from dotenv import load_dotenv
from PIL import Image, PngImagePlugin
from pyrogram import Client
from pyrogram import filters as pyrogram_filters
from typing import Any
import asyncio
from datetime import datetime, time
import Selfie_Prompt_Generator

# Get the current time
current_time = datetime.now()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

timer_interval_for_periodical_messages = random.randint(300, 3600)
print(f'Timer interval for messages: {timer_interval_for_periodical_messages}')
timer_interval_for_periodical_selfies = random.randint(300, 3600)
print(f'Timer interval for selfie: {timer_interval_for_periodical_selfies}')
user_message_interaction = False
user_image_interaction = False


# Prompt generator, for the selfie for now
def import_prompt_generator(the_input=None):
    choices = [
        (6, "SFW_Cowboy_Shot_Prompt_Generator", "Cowboy Shot"),
        (3, "SFW_Portray_Prompt_Generator", "Portray"),
        (1, "NSFW_Cowboy_Shot_Prompt_Generator", "NSFW")
    ]

    for weight, module_name, prompt_type in choices:
        if the_input == prompt_type:
            the_input = (weight, module_name, prompt_type)
            break

    if the_input is None:
        # If the input doesn't match any prompt type, choose randomly
        the_input = random.choices(choices, weights=[weight for weight, _, _ in choices])[0]

    module_name, prompt_type = the_input[1], the_input[2]
    SFW_Prompt_Generator = __import__(str(module_name), fromlist=[''])
    DATA_random_json_loaded = SFW_Prompt_Generator.load_random_json()

    print(prompt_type)
    return [SFW_Prompt_Generator, DATA_random_json_loaded]


async def get_prompt(get_prompt_conversation_history, user, text):
    prompt = get_prompt_conversation_history + f"{user}: {text}\n{char_name}:"
    response = await Payload_for_text_generation(prompt)
    return response


load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
LLM_URL = os.getenv("LLM_URL")
TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
SD_URL = os.getenv("SD_URL")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

botSD_and_LLM = Client(
    "SD_and_LLM",
    api_id=TELEGRAM_API_ID,
    api_hash=TELEGRAM_API_HASH,
    bot_token=TELEGRAM_BOT_TOKEN
)


def split_text(text):
    parts = re.split(r'\n[a-zA-Z]', text)
    return parts


def load_character_data(lodad_character_data_characters_folder):
    load_character_data_characters = []

    for filename in os.listdir(lodad_character_data_characters_folder):
        if filename.endswith('.json'):
            with open(os.path.join(lodad_character_data_characters_folder, filename)) as read_file:
                character_data = json.load(read_file)
                load_character_data_characters.append(character_data)

    return load_character_data_characters


# Select a character
def select_character(selected_characters):
    for i, character in enumerate(selected_characters):
        print(f"{i + 1}. {character['char_name']}")
    selected_char = int(input("Select a character: ")) - 1
    return selected_characters[selected_char]


def initialize_telegram_bot(characters_name, characters_greeting):
    global conversation_history
    with open(f'conversation_history_{characters_name}.txt', 'a+') as file:
        file.seek(0)
        chathistory = file.read()

    # Assuming chathistory is a string, not a dictionary
    conversation_history = f"{characters_name}'s Persona: {selected_character['char_persona']}\n" + \
                           f"World Scenario: {selected_character['world_scenario']}\n" + \
                           f"Character dislikes: {selected_character['char_dislikes']}\n" + \
                           f"Character likes: {selected_character['char_likes']}\n" + \
                           f"Characters age: {selected_character['char_age']}\n" + \
                           f"Characters gender: {selected_character['char_gender']}\n" + \
                           f'<START>\n' + \
                           f'{characters_name}: {characters_greeting}\n{chathistory}'

    memory_file = f'memory_file_{characters_name}.txt'

    with open(memory_file, 'a+') as file:
        file.seek(0)
        chathistory = file.read()

    # Assuming memory_file is a string, not a dictionary
    memory_file = f"{characters_name}'s Persona: {selected_character['char_persona']}\n" + \
                  f"World Scenario: {selected_character['world_scenario']}\n" + \
                  f"Character dislikes: {selected_character['char_dislikes']}\n" + \
                  f"Character likes: {selected_character['char_likes']}\n" + \
                  f"Characters age: {selected_character['char_age']}\n" + \
                  f"Characters gender: {selected_character['char_gender']}\n" + \
                  f'<START>\n' + \
                  f'{characters_name}: {characters_greeting}\n{chathistory}'

    return conversation_history, memory_file


# Load character data
characters_folder = 'Characters'
characters = load_character_data(characters_folder)

# Select a character
selected_character = select_character(characters)
char_name = selected_character["char_name"]
char_greeting = selected_character["char_greeting"]

# Initialize Telegram bot
conversation_history, memory_file = initialize_telegram_bot(char_name, char_greeting)


# Use this to build the timed response

def save_current_time_into_text_file():
    # Convert the current time to a string representation
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

    # Save the current time to a file, for example
    with open(f"current_time_{char_name}.txt", "a") as file:
        file.write(f"{current_time_str} \n\n")


def update_and_get_last_known_time():
    # Read the last known time from the file
    try:
        with open(f"current_time_{char_name}.txt", "r") as file:
            lines = file.readlines()
            if lines:
                last_known_time_str = lines[-2].strip()  # Assuming the last known time is on the second-to-last line
            else:
                last_known_time_str = None
    except FileNotFoundError:
        last_known_time_str = None

    # Clear the contents of the file
    open(f"current_time_{char_name}.txt", "w").close()

    # Convert the current time to a string representation
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

    # Save the current time to the file
    with open(f"current_time_{char_name}.txt", "a") as file:
        file.write(f"{current_time_str}\n\n")

    return last_known_time_str

save_current_time_into_text_file()
last_known_time = update_and_get_last_known_time()

print(f"Last known time: {last_known_time}")


async def generate_random_message_using_memory_file():
    global memory_file  # "memory"
    prompt = memory_file + f"{char_name}"
    response = await Payload_for_text_generation(prompt)

    return response


async def generate_random_message_using_conversation_history():
    global conversation_history  # "memory"
    prompt = conversation_history + f"{char_name}"
    response = await Payload_for_text_generation(prompt)

    return response


async def Payload_for_text_generation(prompt):
    response = requests.post(
        f"{LLM_URL}/api/v1/generate",
        json={
            "prompt": prompt,
            "use_story": False,
            "use_memory": False,
            "use_authors_note": False,
            "use_world_info": False,
            "max_context_length": 2048,
            "max_length": 160,
            "rep_pen": 1.1,
            "rep_pen_range": 1024,
            "rep_pen_slope": 0.7,
            "temperature": 0.9,
            "tfs": 0.97,
            "top_a": 0.75,
            "top_k": 0,
            "top_p": 0.5,
            "typical": 0.19,
            "sampler_order": [6, 5, 4, 3, 2, 1, 0],
            "singleline": True,
            "frmttriminc": True,
            "frmtrmblln": False
        }
    )
    return response


async def update_history_and_send_response(message, user_message, response_text):
    global conversation_history
    print(f" USER MESSAGE: ***{len(user_message)}***")
    if len(user_message) != 0:
        conversation_history += f"{message.from_user.first_name}: {user_message}\n{char_name}:{response_text}\n"
        with open(f'conversation_history_{char_name}.txt', "a") as f:
            f.write(
                f"{message.from_user.first_name}: {user_message}\n{char_name}:{response_text}\n")
    else:
        conversation_history += f"{char_name}:{response_text}\n"
        with open(f'conversation_history_{char_name}.txt', "a") as f:
            f.write(f"{char_name}:{response_text}\n")
    await botSD_and_LLM.send_message(chat_id=TELEGRAM_CHAT_ID, text=response_text)


async def generate_and_send_message(chosen_method, char_name):
    global memory_file, conversation_history

    if chosen_method == "memory_file":
        response: Any = await generate_random_message_using_memory_file()
    else:
        response: Any = await generate_random_message_using_conversation_history()

    if response.status_code == 200:
        text = split_text(response.json()['results'][0]['text'])[0]
        response_text = text.replace("  ", "")

        if chosen_method == "memory_file":
            memory_file += f"{char_name}:{response_text}\n"
            with open(f"memory_file_{char_name}.txt", "a") as f:
                f.write(f"{char_name}:{response_text}\n")
        else:
            conversation_history += f"{char_name}:{response_text}\n"

        random_message = response_text.strip()
        if random_message:
            await botSD_and_LLM.send_message(chat_id=TELEGRAM_CHAT_ID, text=random_message)


async def send_extra_message(chosen_method, char_name):
    global memory_file, conversation_history

    if chosen_method == "memory_file":
        extra_response: Any = await generate_random_message_using_memory_file()
    else:
        extra_response: Any = await generate_random_message_using_conversation_history()

    if extra_response.status_code == 200:
        extra_results = extra_response.json()["results"]
        extra_text = extra_results[0]["text"]
        extra_response_text = split_text(extra_text)[0]
        extra_response_text = extra_response_text.replace("  ", "")

        if chosen_method == "memory_file":
            memory_file += f"{char_name}:{extra_response_text}\n"
            with open(f"memory_file_{char_name}.txt", "a+") as f:
                f.write(f"{char_name}:{extra_response_text}\n")
        else:
            conversation_history += f"{char_name}:{extra_response_text}\n"

        extra_message = extra_response_text.strip()
        if extra_message:
            await botSD_and_LLM.send_message(chat_id=TELEGRAM_CHAT_ID, text=extra_message)


async def send_messages_periodically():
    global timer_interval_for_periodical_messages, memory_file, conversation_history, char_name
    while True:
        if random.random() < 0.5:
            chosen_method = "memory_file"
        else:
            chosen_method = "conversation_history"

        await generate_and_send_message(chosen_method, char_name)

        random_number = random.random()
        counter = 0

        while random_number < 0.3 and counter < 1:
            print(f'Send extra messages with a 30% chance (Has to be less than 0.3): {random_number}')
            if random.random() < 0.3:
                chosen_method = "memory_file"
            else:
                chosen_method = "conversation_history"

            await send_extra_message(chosen_method, char_name)

            counter += 1
            random_number = random.random()

        print(f"Chosen method: {chosen_method}")
        timer_interval_for_periodical_messages = random.randint(300, 3600)
        print(str(timer_interval_for_periodical_messages) + " send msg local")


async def generate_selfie_and_send():
    prompt = ("masterpiece, best quality, high quality, beautiful women, gorgeous, masterpiece, \n"
              "1girl, solo, upper body, portray, Raiden Shogun, braid, selfie, cleavage, kimono, purple hair, long hair, purple eyes, (medium breasts:1.2)")
    # What will be sent to StableDiffusion's API
    payload = await Payload_for_images(prompt)

    r = requests.post(url=f'{SD_URL}/sdapi/v1/txt2img', json=payload).json()

    for i in r['images']:
        # Extract image data
        image_data = i.split(",", 1)[0]

        # Define image path
        image_path = "selfie.png"

        # Decode base64 and save image
        decode_and_save_base64(image_data, image_path)

        # Load the image using Image.open
        image = Image.open(image_path)

        # Prepare payload and send request to obtain PNG info
        png_payload = {"image": "data:image/png;base64," + i}
        response2 = requests.post(url=f'{SD_URL}/sdapi/v1/png-info', json=png_payload)

        # Create PngInfo object and add text
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))

        # Save image with pnginfo
        image.save(image_path, pnginfo=pnginfo)

        # Send photo via bot and set caption
        await botSD_and_LLM.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=open(image_path, 'rb'),
                                       caption="A random selfie to boost your day <3 Hope you like it!")
        # Send an image via bot
        await botSD_and_LLM.send_message(chat_id=TELEGRAM_CHAT_ID, text="Do I look good?")

        # Save the question in conversation history for future conversations
        with open(f'conversation_history_{char_name}.txt', "a") as f:
            f.write(f"{char_name}: *Sent a selfie to you*\n"
                    f"{char_name}: Do I look good?\n\n")

        print(f"Image generated: {image_path}")
        os.remove(image_path)


class ModelManager:
    def __init__(self):
        self.current_model = None
        self.current_resolution = None
        self.current_sampler = None
        self.sampler_list = [
            "DPM++ 2M Karras",
            "DPM++ SDE Karras",
            "DPM++ 2M SDE Exponential",
            "DPM++ 2M SDE Karras",
            "Euler a",
            "Euler",
            "Heun",
            "DPM2",
            "Restart",
            "DPM++ 2S a",
            "DPM++ SDE",
            "DPM++ 2M SDE Heun Karras",
            "DPM++ 2M SDE Heun Exponential",
            "DPM++ 3M SDE Karras",
            "DPM++ 3M SDE Exponential",
            "DPM2 Karras",
            "DPM2 a Karras",
            "DPM++ 2S a Karras"
        ]
        self.models = {
            "Anything_V4_5": "anything-v4.5-pruned.ckpt [e4b17ce185]",
            "Anyhen_20": "anyhentai_20.safetensors [61bc7001e8]",
            "AbyssOrangeSFW": "abyssorangemix2SFW_abyssorangemix2Sfw.safetensors [b644d850c9]",
            "AbyyOrangeNSFW": "abyssorangemix2NSFW_abyssorangemix2Nsfw.safetensors [61f21f5915]",
            "Anigen_9": "aingexp_exp9.safetensors [9d20eb2533]",
            "FluffyMarshmallow": "fluffymarshmallow_v20.safetensors [f724feaff8]",
            "Hassaku": "hassakuHentaiModel_v11.safetensors [973cb455d0]",
            "Kaywaii": "kaywaii_v40.safetensors [8cbe0df383]",
            "Kizuki": "kizukiCheckpointMix_animeHentaiV1.safetensors [d9da6cdda0]",
            "Nightcolor": "nightcolorBoxModel_colorBOX.safetensors [93a20525f5]",
            "DivineElegance_V9": "divineelegancemix_V9.safetensors [6e8e316b68]",
            "voidmix": "voidmixFp16Bf16_v4.safetensors [04adbc2816]",
            "divineanimemix_V2": "divineanimemix_V2.safetensors [21e8ae2ff3]",
            "dreamsArchive_V2": "dreamsArchive_sketchydreamsRev2.safetensors [eec4296ec4]",
            "sakushimixFinal": "sakushimixFinished_sakushimixFinal.safetensors [b4703d513b]"
        }
        self.amount_of_pics = 0
        self.data = import_prompt_generator()[1]
        self.current_file = None
        self.chosen_character = None
        self.current_first_topwear_layer = None
        self.current_second_topwear_layer = None
        self.current_full_bottomwear = None
        self.current_partial_bottomwear = None
        self.current_location = None  # Add location
        self.current_first_topwear_layer_closed = None  # Make this work somehow
        self.current_first_topwear_layer_open = None  # Make this work somehow
        self.current_full_attire = None

        # First get first_toplayer, then ask in one /function for open or closed AND what's inside that dict, so
        # 1st: "shirt", 2nd: "open, open shirt" or 1st: "hoodie", 2nd: "open, partially open oversized hoodie"
        # ask for "state of clothing" and specific

    def set_custom_full_attire(self, full_attire):
        try:
            selectable_full_attire = self.data['SFW']['appearance']['attire']['full_attire']
        except KeyError:
            selectable_full_attire = self.data['NSFW']['appearance']['attire']['full_attire']

        if (full_attire in selectable_full_attire.keys()) and self.current_full_attire is None:
            self.current_full_attire = selectable_full_attire[full_attire]
            return f"Full attire was changed to {full_attire}"
        else:
            return f"{full_attire} is not in {selectable_full_attire.keys()}"

    def full_attire_selected(self):
        print(f"Currently chosen full attire {self.current_full_attire}")
        if self.current_full_attire is not None:
            returnable_full_attire = self.current_full_attire
            self.current_full_attire = None
            return returnable_full_attire

    def reset(self, reset_command):
        if reset_command == "Confirm":
            self.__init__()
            return f"The attributes have been reseted."

    def set_custom_partial_bottomwear(self, partial_bottomwear):
        try:
            selectable_partial_bottomwear = self.data['SFW']['appearance']['attire']['pieces_of_attire']['bottomwear'][
                'partial_bottomwear']
        except KeyError:
            selectable_partial_bottomwear = self.data['NSFW']['appearance']['attire']['pieces_of_attire']['bottomwear'][
                'partial_bottomwear']

        if (partial_bottomwear in selectable_partial_bottomwear.keys()) and self.current_full_bottomwear is None:
            modified_dict = {
                partial_bottomwear: selectable_partial_bottomwear[partial_bottomwear]
            }
            self.current_partial_bottomwear = modified_dict
            return f'Partial bottomwear was changed to {partial_bottomwear}'
        else:
            return f'{partial_bottomwear} is not in {selectable_partial_bottomwear.keys()}, or {self.current_full_bottomwear} is not None.'

    def partial_bottomwear_selected(self):
        print(f"Currently chosen partial bottomwear {self.current_partial_bottomwear}")
        if self.current_partial_bottomwear is not None:
            returnable_partial_bottomwear = self.current_partial_bottomwear
            self.current_partial_bottomwear = None
            return returnable_partial_bottomwear

    def set_custom_full_bottomwear(self, full_bottomwear):
        try:
            selectable_full_bottomwear = self.data['SFW']['appearance']['attire']['pieces_of_attire']['bottomwear'][
                'full_bottomwear']
        except KeyError:
            selectable_full_bottomwear = self.data['NSFW']['appearance']['attire']['pieces_of_attire']['bottomwear'][
                'full_bottomwear']

        if full_bottomwear in selectable_full_bottomwear.keys() and self.current_partial_bottomwear is None:
            modified_dict = {
                full_bottomwear: selectable_full_bottomwear[full_bottomwear]
            }
            self.current_full_bottomwear = modified_dict
            return f'Full bottomwear was changed to {full_bottomwear}'
        else:
            return f'{full_bottomwear} is not in {selectable_full_bottomwear.keys()}, or {self.current_partial_bottomwear} is not None.'

    def full_bottomwear_selected(self):
        print(f"Currently chosen full bottomwear {self.current_full_bottomwear}")
        if self.current_full_bottomwear is not None:
            returnable_full_bottomwear = self.current_full_bottomwear
            self.current_full_bottomwear = None
            return returnable_full_bottomwear

    def set_custom_second_topwear_layer(self, second_topwear_layer):
        try:
            selectable_second_topwear_layer = \
                self.data['SFW']['appearance']['attire']['pieces_of_attire']['topwear'][
                    'topwear_second_layer']
        except KeyError:
            selectable_second_topwear_layer = \
                self.data['NSFW']['appearance']['attire']['pieces_of_attire']['topwear'][
                    'topwear_second_layer']

        if second_topwear_layer in selectable_second_topwear_layer.keys():
            # Modify the dictionary structure before returning
            modified_dict = {
                second_topwear_layer: selectable_second_topwear_layer[second_topwear_layer]
            }
            self.current_second_topwear_layer = modified_dict
            return f'Second layer of topwear changed to: {second_topwear_layer}'
        else:
            return f'{second_topwear_layer} is not in {selectable_second_topwear_layer.keys()}'

    def second_topwear_layer_selected(self):
        print(f"Currently chosen second layer topwear {self.current_second_topwear_layer}")
        if self.current_second_topwear_layer is not None:
            returnable_second_topwear_layer = self.current_second_topwear_layer
            self.current_second_topwear_layer = None
            return returnable_second_topwear_layer

    def set_custom_file(self, file):
        acceptable_list = ["Portray", "Cowboy Shot", "NSFW"]
        if file in acceptable_list:
            self.current_file = file
            _, new_data = import_prompt_generator(file)
            self.data = new_data  # Update self.data with the new data
            return f"File changed to {file}"
        else:
            return f"{file} is not in {acceptable_list}"

    def random_file_selector(self):
        print(f"Currently chosen file {self.current_file}")
        if self.current_file is not None:
            returnable_file = self.current_file
            self.current_file = None
            return returnable_file

    def set_custom_model_model(self, new_model):
        if new_model in self.models:
            self.current_model = new_model
            return f"Model changed to {new_model}"
        else:
            return f"{new_model} is not inside {self.models.keys()}"

    def random_model_selector(self, model):
        print(f"Currently chosen model {self.current_model}")

        model_mapping = {
            "Anything_V4_5": "anything-v4.5-pruned.ckpt [e4b17ce185]",
            "Anyhen_20": "anyhentai_20.safetensors [61bc7001e8]",
            "AbyssOrangeSFW": "abyssorangemix2SFW_abyssorangemix2Sfw.safetensors [b644d850c9]",
            "AbyyOrangeNSFW": "abyssorangemix2NSFW_abyssorangemix2Nsfw.safetensors [61f21f5915]",
            "Anigen_9": "aingexp_exp9.safetensors [9d20eb2533]",
            "FluffyMarshmallow": "fluffymarshmallow_v20.safetensors [f724feaff8]",
            "Hassaku": "hassakuHentaiModel_v11.safetensors [973cb455d0]",
            "Kaywaii": "kaywaii_v40.safetensors [8cbe0df383]",
            "Kizuki": "kizukiCheckpointMix_animeHentaiV1.safetensors [d9da6cdda0]",
            "Nightcolor": "nightcolorBoxModel_colorBOX.safetensors [93a20525f5]",
            "DivineElegance_V9": "divineelegancemix_V9.safetensors [6e8e316b68]",
            "voidmixFp_v4": "voidmixFp16Bf16_v4.safetensors [04adbc2816]",
            "divineanimemix_V2": "divineanimemix_V2.safetensors [21e8ae2ff3]",
            "dreamsArchive_V2": "dreamsArchive_sketchydreamsRev2.safetensors [eec4296ec4]",
            "sakushimixFinal": "sakushimixFinished_sakushimixFinal.safetensors [b4703d513b]"
        }

        if model == "NSFW_Cowboy_Shot_Prompt_Generator":
            model_mapping = {
                "Anything_V4_5": "anything-v4.5-pruned.ckpt [e4b17ce185]",
                "Anyhen_20": "anyhentai_20.safetensors [61bc7001e8]",
                "AbyyOrangeNSFW": "abyssorangemix2NSFW_abyssorangemix2Nsfw.safetensors [61f21f5915]",
                "Kizuki": "kizukiCheckpointMix_animeHentaiV1.safetensors [d9da6cdda0]"}

        random_model_chosen_here = random.choice(list(model_mapping.values()))

        # If a current_model is provided, and it's in the model_mapping, use it
        if self.current_model is not None and self.current_model in model_mapping:
            random_model_chosen_here = model_mapping[self.current_model]
            self.current_model = None  # Reset current_model to None after using it

        return random_model_chosen_here

    def set_custom_resolution_and_hr(self, resolution):
        self.current_resolution = resolution
        return f"Resolution changed to {resolution}"

    def random_resolution_selector(self):
        print(f"Currently chosen resolution {self.current_resolution}")
        resolutions = [[192, 320, 4], [384, 640, 2], [384, 640, 2.5], [512, 768, 2], [512, 768, 1],
                       [768, 1152, 1], [512, 1152, 1], [512, 1152, 1.7], [128, 320, 4],
                       [256, 512, 3], [448, 832, 1.7],
                       [448, 640, 2], [448, 640, 2.5], [448, 640, 1.5],
                       [448, 640, 1.75]]  # [0] = Width, [1] = Height [2] = Resolution Scale

        returnable_resolotion = random.choice(resolutions)

        if self.current_resolution is not None:
            returnable_resolotion = self.current_resolution
            self.current_resolution = None

        return returnable_resolotion

    def set_custom_sampler(self, sampler):
        if sampler in self.sampler_list:
            self.current_sampler = sampler
            return f"Sampler changed to {sampler}"
        else:
            return f"{sampler} is not inside {self.sampler_list}"

    def random_sampler_selector(self):
        print(f"Currently chosen sampler {self.current_sampler}")
        returnable_sampler = random.choice(self.sampler_list)

        if self.current_sampler is not None and self.current_sampler in self.sampler_list:
            returnable_sampler = self.current_sampler
            self.current_sampler = None

        return returnable_sampler

    def set_custom_amount_of_pics(self, amount_of_pics):
        if amount_of_pics in range(1, 4):
            self.amount_of_pics = amount_of_pics
            return f"Amount of pictures to be sent changed to {amount_of_pics}"
        else:
            return f"{amount_of_pics} is not between 1 and 3 "

    def random_amount_of_pics(self):
        returnable_amount_of_pics = 1

        if self.amount_of_pics != 0 and self.amount_of_pics in list(range(1, 4)):
            returnable_amount_of_pics = self.amount_of_pics
            self.amount_of_pics = 0

        return returnable_amount_of_pics

    def set_custom_character(self, chosen_character):
        try:
            selectable_characters = self.data['SFW']['characters']
        except KeyError:
            # Handle the case where 'SFW' is not present, default to 'NSFW'
            selectable_characters = self.data['NSFW']['characters']

        available_characters = []
        for character_type, characters_dict in selectable_characters.items():
            for char_in_dict_name, char_info in characters_dict.items():
                available_characters.append(char_in_dict_name)
                if char_in_dict_name == chosen_character:
                    self.chosen_character = [character_type, char_info]
                    return f"Character was changed to {chosen_character}, {character_type},{char_info}"

        available_characters_str = ', '.join(available_characters)
        return f"{chosen_character} was not found within available characters. Available characters: {available_characters_str}"

    def character_selected(self):
        print(f"currently chosen character {self.chosen_character}")
        returnable_character_selected = self.chosen_character
        if self.chosen_character is not None:
            returnable_character_selected = self.chosen_character
            self.chosen_character = None

        return returnable_character_selected

    def set_custom_first_topwear_layer(self, first_topwear_layer):
        try:
            selectable_first_topwear_layer = \
                self.data['SFW']['appearance']['attire']['pieces_of_attire']['topwear'][
                    'topwear_first_layer']
        except KeyError:
            selectable_first_topwear_layer = \
                self.data['NSFW']['appearance']['attire']['pieces_of_attire']['topwear'][
                    'topwear_first_layer']

        if first_topwear_layer in selectable_first_topwear_layer.keys():
            # Modify the dictionary structure before returning
            modified_dict = {
                first_topwear_layer: selectable_first_topwear_layer[first_topwear_layer]
            }
            self.current_first_topwear_layer = modified_dict
            return f'First layer of topwear changed to: {first_topwear_layer}'
        else:
            return f'{first_topwear_layer} is not in {selectable_first_topwear_layer.keys()}'

    def first_topwear_layer_selected(self):
        print(f"Currently chosen first layer topwear {self.current_first_topwear_layer}")
        if self.current_first_topwear_layer is not None:
            returnable_first_topwear_layer = self.current_first_topwear_layer
            self.current_first_topwear_layer = None
            return returnable_first_topwear_layer


model_manager = ModelManager()


@botSD_and_LLM.on_message(pyrogram_filters.command(["change_full_attire"]))
def Change_Full_attire(client, message):
    msgs = message.text.split(' ', 1)
    if len(msgs) == 1:
        message.reply_text("Format: /change_full_attire <full attire>")
        return

    new_full_attire = msgs[1]
    response = model_manager.set_custom_full_attire(new_full_attire)
    message.reply_text(response)


@botSD_and_LLM.on_message(pyrogram_filters.command(["reset_parameters"]))
def Reset_Parameters(client, message):
    msgs = message.text.split(' ', 1)
    if len(msgs) == 1:
        message.reply_text("Format: /reset_parameters < Confirm >")
        return

    reset_command = msgs[1]
    response = model_manager.reset(reset_command)
    message.reply_text(response)


@botSD_and_LLM.on_message(pyrogram_filters.command(["change_partial_bottomwear"]))
def Change_Full_Bottomwear(client, message):
    msgs = message.text.split(' ', 1)
    if len(msgs) == 1:
        message.reply_text("Format: /change_partial_bottomwear <partial bottomwear>")
        return

    new_partial_bottomwear = msgs[1]
    response = model_manager.set_custom_partial_bottomwear(new_partial_bottomwear)  # will receive "shirt"
    message.reply_text(response)


@botSD_and_LLM.on_message(pyrogram_filters.command(["change_full_bottomwear"]))
def Change_Full_Bottomwear(client, message):
    msgs = message.text.split(' ', 1)
    if len(msgs) == 1:
        message.reply_text("Format: /change_full_bottomwear <full bottomwear>")
        return

    new_full_bottomwear = msgs[1]
    response = model_manager.set_custom_full_bottomwear(new_full_bottomwear)  # will receive "shirt"
    message.reply_text(response)


@botSD_and_LLM.on_message(pyrogram_filters.command(["change_first_topwear_layer"]))
def Change_First_Topwear_Layer(client, message):
    msgs = message.text.split(' ', 1)
    if len(msgs) == 1:
        message.reply_text("Format: /change_first_topwear_layer <first topwear layer>")
        return

    new_first_topwear_layer = msgs[1]
    response = model_manager.set_custom_first_topwear_layer(new_first_topwear_layer)  # will receive "shirt"
    message.reply_text(response)


@botSD_and_LLM.on_message(pyrogram_filters.command(["change_second_topwear_layer"]))
def Change_Second_Topwear_Layer(client, message):
    msgs = message.text.split(' ', 1)
    if len(msgs) == 1:
        message.reply_text("Format: /change_second_topwear_layer <second topwear layer>")
        return

    new_second_topwear_layer = msgs[1]
    response = model_manager.set_custom_second_topwear_layer(new_second_topwear_layer)  # will receive "shirt"
    message.reply_text(response)


@botSD_and_LLM.on_message(pyrogram_filters.command(["change_character"]))
def Change_Character(client, message):
    msgs = message.text.split(' ', 1)
    if len(msgs) == 1:
        message.reply_text("Format: /change_character <character_name>")
        return

    new_character = msgs[1]

    response = model_manager.set_custom_character(new_character)  # will receive "Raiden"
    message.reply_text(response)


@botSD_and_LLM.on_message(pyrogram_filters.command(["change_model"]))
def change_model_input(client, message):
    msgs = message.text.split(' ', 1)
    if len(msgs) == 1:
        message.reply_text("Format: /change_model <model_name>")
        return

    new_model = msgs[1]
    response = model_manager.set_custom_model_model(new_model)

    message.reply_text(response)


@botSD_and_LLM.on_message(pyrogram_filters.command(["change_resolution"]))
def Change_Resolution(client, message):
    msgs = message.text.split(' ', 1)
    if len(msgs) != 2:
        message.reply_text("Invalid number of arguments. Usage: /change_resolution WIDTH, HEIGHT, SCALE")
        return

    resolution_str = msgs[1]
    try:
        # Split the comma-separated values
        width_str, height_str, scale_str = map(str.strip, resolution_str.split(','))

        # Convert width and height to integers
        width, height = int(width_str), int(height_str)

        # Convert scale to float with two decimal places
        scale = round(float(scale_str), 2)

        response = model_manager.set_custom_resolution_and_hr([width, height, scale])

        message.reply_text(response)

    except ValueError as e:
        message.reply_text(f"Error parsing resolution: {str(e)}, resolution is not being changed.")


@botSD_and_LLM.on_message(pyrogram_filters.command(["change_sampler"]))
def Change_Sampler(client, message):
    msgs = message.text.split(' ', 1)
    if len(msgs) == 1:
        message.reply_text("Format: /change_sampler <sampler_name>")
        return

    new_sampler = msgs[1]
    response = model_manager.set_custom_sampler(new_sampler)

    message.reply_text(response)


@botSD_and_LLM.on_message(pyrogram_filters.command(["change_number_of_pics"]))
def Change_Number_Of_Pics(client, message):
    msgs = message.text.split(' ', 1)
    if len(msgs) != 2 and msgs[1] != int:
        message.reply_text("Format: /change_number_of_pics <number of images>")
        return

    try:
        new_amount_of_pics = int(msgs[1])
    except ValueError:
        message.reply_text("Please enter a valid integer.")
        return

    response = model_manager.set_custom_amount_of_pics(new_amount_of_pics)

    message.reply_text(response)


@botSD_and_LLM.on_message(pyrogram_filters.command(["change_file"]))
def Change_File(client, message):
    msgs = message.text.split(' ', 1)
    if len(msgs) == 1:
        message.reply_text("Format: /change_file <file>")
        return

    new_file = msgs[1]
    response = model_manager.set_custom_file(new_file)

    message.reply_text(response)


def Random_Negative_Prompt_Selector():
    return random.choice(["counterfit_negative_long", "counterfit_negative_other", "SFW_negative_only",
                          "counterfit_negative_long_TRY_TEST", "counterfit_negative_long_TRY_TEST_With_Positive",
                          "SFW_negative_only_now_with_positive_test", "counterfit_negative_long_with_Positive",
                          "old_V4_512x1152", "counterfit_negative_long_NSFW", "OLD_SFW_NSFW", "OLD_NSFW"])


def encode_file_to_base64(path):
    with open(path, 'rb') as file:
        return base64.b64encode(file.read()).decode('utf-8')


def decode_and_save_base64(base64_str, save_path):
    with open(save_path, "wb") as file:
        file.write(base64.b64decode(base64_str))


# Models base parameters that are used for "payloads"
def model_base_params(chosen_model):
    model = model_manager.random_model_selector(chosen_model)
    random_sampler = model_manager.random_sampler_selector()
    resolution = model_manager.random_resolution_selector()
    amount_of_images = model_manager.random_amount_of_pics()
    random_negative_prompt = Random_Negative_Prompt_Selector()
    random_cfg_scale = random.choice([7, 9])
    VAE = "Automatic"
    VAE_Override = True

    hr_true_or_false = True
    if resolution[2] == 1:
        hr_true_or_false = False

    if (model == "abyssorangemix2NSFW_abyssorangemix2Nsfw.safetensors [61f21f5915]"
            or model == "abyssorangemix2SFW_abyssorangemix2Sfw.safetensors [b644d850c9]"):
        random_sampler = "Euler a"

    if model == "anything-v4.5-pruned.ckpt [e4b17ce185]":
        if random.random() < 0.5:
            VAE = "None"
            VAE_Override = False
        else:
            VAE = VAE
            VAE_Override = VAE_Override

    result = {
        'random_model': model,
        'random_sampler': random_sampler,
        'amount_of_images': amount_of_images,
        'random_resolution': resolution,
        'random_negative_prompt': random_negative_prompt,
        'random_cfg_scale': random_cfg_scale,
        'hr_true_or_false': hr_true_or_false,
        'vae': VAE,
        'vae_override': VAE_Override
    }
    return result


# Maybe could add a "chance" to not send one, maybe acting a bit angry?
@botSD_and_LLM.on_message(pyrogram_filters.regex(r'\b(take\s*a\s*(pic|picture))\b', re.IGNORECASE))
async def take_a_pic(client, message):
    global user_image_interaction
    user_selected_file = model_manager.random_file_selector()
    user_selected_character = model_manager.character_selected()
    user_selected_first_topwear_layer = model_manager.first_topwear_layer_selected()
    user_selected_second_topwear_layer = model_manager.second_topwear_layer_selected()
    user_selected_full_bottomwear = model_manager.full_bottomwear_selected()
    user_selected_partial_bottomwear = model_manager.partial_bottomwear_selected()
    user_selected_full_attire = model_manager.full_attire_selected()
    prompt_generator_module = import_prompt_generator(user_selected_file)[0]
    base_param = model_base_params(prompt_generator_module)
    generated_prompt = prompt_generator_module.generated_prompt(
        user_selected_character=user_selected_character,
        user_selected_first_topwear_layer=user_selected_first_topwear_layer,
        user_selected_second_topwear_layer=user_selected_second_topwear_layer,
        user_selected_full_bottomwear=user_selected_full_bottomwear,
        user_selected_partial_bottomwear=user_selected_partial_bottomwear,
        user_selected_full_attire=user_selected_full_attire
    )

    user_image_interaction = True

    K = await message.reply_text("Sure thing, one sec :*")

    payload = await Payload_for_images(f'"1girl, solo, " + {generated_prompt}')

    r = requests.post(url=f'{SD_URL}/sdapi/v1/txt2img', json=payload).json()

    for i in r['images']:
        image_data = i.split(",", 1)[0]

        # Process the first type of image
        await process_image(message, image_data, "pic.png", "Your pic!")


# Draw an image that the user wants, with random base parameters
@botSD_and_LLM.on_message(pyrogram_filters.command(["draw"]))
async def draw(client, message):
    msgs = message.text.split(' ', 1)
    if len(msgs) == 1:
        await message.reply_text("Format : /draw < text to image >")
        return
    msg = msgs[1]

    K = await message.reply_text("Drawing the image, one sec :*")

    payload = await Payload_for_images(msg)

    r = requests.post(url=f'{SD_URL}/sdapi/v1/txt2img', json=payload).json()

    for i in r['images']:
        image_data = i.split(",", 1)[0]
        await process_image(message, image_data, "drawn_picture.png", f"Image of {msg}")


async def process_image(message, image_data, image_path, caption):
    # Decode base64 and save image
    decode_and_save_base64(image_data, image_path)

    # Load the image using Image.open
    image = Image.open(image_path)

    png_payload = {"image": "data:image/png;base64," + encode_file_to_base64(image_path)}
    response2 = requests.post(url=f'{SD_URL}/sdapi/v1/png-info', json=png_payload)

    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text("parameters", response2.json().get("info"))

    # Save image with pnginfo
    image.save(image_path, pnginfo=pnginfo)

    await message.reply_photo(
        photo=image_path,
        caption=caption
    )

    os.remove(image_path)


@botSD_and_LLM.on_message(pyrogram_filters.command(["help"]))
async def help_function(client, message):
    await message.reply_text("The following commands are available: \n"
                             "/start \n"
                             "/reset_parameters \n"
                             "/change_model \n"
                             "/change_resolution \n"
                             "/change_sampler \n"
                             "/change_number_of_pics \n"
                             "/change_file \n"
                             "/change_character \n"
                             "/change_partial_bottomwear \n"
                             "/change_full_bottomwear \n"
                             "/change_first_topwear_layer \n"
                             "/change_second_topwear_layer \n"
                             "/change_full_attire")  # FINISH THIS


@botSD_and_LLM.on_message(pyrogram_filters.command(["start"], prefixes=["/", "!"]))
async def start(client, message):
    Photo = "Starting_Image.png"
    await message.reply_photo(
        photo=Photo,
        caption=
        f"Hi, I'm {char_name}! You can chat with me and exchange pictures!")

    #     buttons = [[
    #         InlineKeyboardButton("Add to your group",
    #                              url="http://t.me/botname?startgroup=true"),
    #     ]] https://docs.pyrogram.org/api/types/ <- If ever want to add something extra

async def Take_A_Selfie(client, message):
    prompt_payload = Selfie_Prompt_Generator.generated_prompt()

    K = await message.reply_text("Gimme a sec, I'll fix my hair :*")

    payload_to_send = f"(selfie:1.3), 1girl, solo, {prompt_payload}"
    payload = await Payload_for_images(payload_to_send)

    r = requests.post(url=f'{SD_URL}/sdapi/v1/txt2img', json=payload).json()

    for i in r['images']:
        image_data = i.split(",", 1)[0]
        await process_image(message, image_data, "drawn_picture.png", f"Your selfie <3")


@botSD_and_LLM.on_message(pyrogram_filters.text & pyrogram_filters.private)
async def handle_message(client, message):
    global timer_interval_for_periodical_messages, user_message_interaction

    timer_interval_for_periodical_messages = random.randint(300, 3600)
    users_message = message.text.split(' ', 1)
    users_message_in_string = ' '.join(users_message)

    if re.search(r'\b(take\s*a\s*(pic|picture))\b', users_message_in_string, re.IGNORECASE):
        print("User asked to take a picture. Bot will generate a picture instead of a response.")
        await take_a_pic(client, message)

    if re.search(r'\b(take\s*a\s*selfie)\b', users_message_in_string, re.IGNORECASE):
        print("User asked to take a selfie. Bot will generate a selfie instead of a response.")
        await Take_A_Selfie(client, message)

    if users_message_in_string.startswith("/"):
        print("User is changing parameters.")
        return

    user_message_interaction = True
    print(f"Has the user interacted? {user_message_interaction}")

    response = await get_prompt(conversation_history, message.from_user.first_name, users_message_in_string)

    if response.status_code == 200:
        text = split_text(response.json()['results'][0]['text'])[0]
        response_text = text.replace("  ", "")
        await update_history_and_send_response(message, users_message_in_string, response_text)

        num_subsequent_responses = random.randint(0, 1)
        print(f'Number of subsequent responses: {num_subsequent_responses}')
        for _ in range(num_subsequent_responses):
            subsequent_response = await get_prompt(conversation_history, message.from_user.first_name, "")
            if subsequent_response.status_code == 200:
                subsequent_response_text = split_text(subsequent_response.json()['results'][0]['text'])[0]
                if subsequent_response_text.strip():
                    await update_history_and_send_response(message, "", subsequent_response_text)


async def Payload_for_images(prompt_payload):
    user_selected_file = model_manager.random_file_selector()
    prompt_generator_module = import_prompt_generator(user_selected_file)[0]
    base_param = model_base_params(prompt_generator_module)
    payload = {
        "batch_size": 1,
        "cfg_scale": base_param["random_cfg_scale"],
        "comments": {

        },
        "denoising_strength": 0.7,
        "disable_extra_networks": False,
        "do_not_save_grid": False,
        "do_not_save_samples": False,
        "send_images": True,
        "save_images": True,
        "enable_hr": base_param["hr_true_or_false"],
        "height": base_param["random_resolution"][1],
        "hr_resize_x": 0,
        "hr_resize_y": 0,
        "hr_scale": base_param["random_resolution"][2],
        "hr_second_pass_steps": 35,
        "hr_upscaler": "Latent (nearest)",
        "n_iter": base_param["amount_of_images"],
        "negative_prompt": "",
        "override_settings": {
            "sd_model_checkpoint": base_param["random_model"]
        },
        "override_settings_restore_afterwards": True,
        "prompt": f"{prompt_payload}",
        "restore_faces": False,
        "s_churn": 0.0,
        "s_min_uncond": 0,
        "s_noise": 1.0,
        "s_tmax": None,
        "s_tmin": 0.0,
        "sampler_name": base_param["random_sampler"],
        "script_args": [

        ],
        "script_name": None,
        "seed": -1,
        "seed_enable_extras": True,
        "seed_resize_from_h": -1,
        "seed_resize_from_w": -1,
        "steps": 35,
        "styles": [
            base_param["random_negative_prompt"]
        ],
        "subseed": -1,
        "subseed_strength": 0,
        "tiling": False,
        "width": base_param["random_resolution"][0]
    }
    return payload


def is_between_midnight_and_six():
    now = datetime.now().time()
    midnight = time(0, 0)
    six_am = time(6, 0)

    return midnight <= now < six_am


# Example usage
is_it_between_midnight_and_six_in_the_morning = is_between_midnight_and_six()


async def periodically_scheduler(message_type):
    global timer_interval_for_periodical_messages, timer_interval_for_periodical_selfies
    global user_message_interaction, user_image_interaction

    while True:
        if message_type == "message":
            if is_it_between_midnight_and_six_in_the_morning is False:
                print(f"{timer_interval_for_periodical_messages} DELAYED")
                await asyncio.sleep(timer_interval_for_periodical_messages)
                if not user_message_interaction:
                    await send_messages_periodically()
                    user_message_interaction = False
            else:
                print(f"It is currently {current_time}, bot will sleep for 15 minutes.")
                await asyncio.sleep(900)
                if user_message_interaction:
                    await send_messages_periodically()
                    user_message_interaction = False
        elif message_type == "selfie":
            if is_it_between_midnight_and_six_in_the_morning is False:
                print(f"{timer_interval_for_periodical_selfies} DELAYED")
                await asyncio.sleep(timer_interval_for_periodical_selfies)
                if not user_image_interaction:
                    await generate_selfie_and_send()
                    user_image_interaction = False
            else:
                print(f"It is currently {current_time}, bot will sleep for 15 minutes.")
                await asyncio.sleep(900)
                if user_image_interaction:
                    await generate_selfie_and_send()
                    user_image_interaction = False


# async def periodically_sent_message_scheduler():
#     global timer_interval_for_periodical_messages, user_message_interaction
#     while True:
#         print(f"{timer_interval_for_periodical_messages} DELAYED")
#         await asyncio.sleep(timer_interval_for_periodical_messages)
#         if user_message_interaction == False:
#             await send_messages_periodically()
#         elif user_message_interaction == True:
#             user_message_interaction = False
#
# async def periodically_sent_selfie_scheduler():
#     global timer_interval_for_periodical_selfies, user_image_interaction
#     while True:
#         print(f"{timer_interval_for_periodical_selfies} DELAYED")
#         await asyncio.sleep(timer_interval_for_periodical_selfies)
#         if user_image_interaction == False:
#             await generate_selfie_and_send()
#         elif user_image_interaction == True:
#             user_image_interaction = False





# Start the scheduler in the background
loop = asyncio.get_event_loop()
# To schedule periodic messages
loop.create_task(periodically_scheduler("message"))
# To schedule periodic selfies
loop.create_task(periodically_scheduler("selfie"))
# loop.create_task(periodically_sent_message_scheduler())
# loop.create_task(periodically_sent_selfie_scheduler())

# Run the Pyrogram client
botSD_and_LLM.run()

# Build a "selfie" function, with a "selfie" JSON. «DONE»
# If sending something from memory or the time since last message is more than 5 hours, make the bot comment on that.
# Also make the bot take time into account, like "take a pic" should return with a picture at night or day, depending on time
# Create a JSON file or .txt file where the date is being stored, then do some calculations to determine when was the last message
# hours before, or days before, and add the according "context" to the prompt. Day -> Yesterday -> Day before yesterday -> 3 days ago
#

# If current date - last date <= 5 hours, then into the bot's prompt, write something like
# Last interaction was 5 hours ago, USER may be busy or was SLEEPING
