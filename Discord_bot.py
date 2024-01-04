import requests, json, random, os, re, datetime
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio
import base64
import aiohttp

YOUR_NAME = "YOUR NAME"


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
    SFW_Prompt_Generator = __import__(module_name, fromlist=[''])
    DATA_random_json_loaded = SFW_Prompt_Generator.load_random_json()

    print(prompt_type)
    return [SFW_Prompt_Generator, DATA_random_json_loaded]


load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
LLM_URL = os.getenv("LLM_URL")
SD_URL = os.getenv("SD_URL")
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID")
DISCORD_USER_ID = int(DISCORD_USER_ID)
timer_interval = random.randint(900, 3600)  # Random interval between 15 and 60 minutes
print(f'Timer interval: {timer_interval}')


def split_text(text):
    parts = re.split(r'\n[a-zA-Z]', text)
    return parts


def get_prompt(get_prompt_conversation_history, user, text):
    return {
        "prompt": get_prompt_conversation_history + f"{user}: {text}\n{char_name}:",
        "use_story": False,
        "use_memory": False,
        "use_authors_note": False,
        "use_world_info": False,
        "max_context_length": 2048,
        "max_length": 120,
        "rep_pen": 1.05,
        "rep_pen_range": 400,
        "rep_pen_slope": 0.3,
        "temperature": 1.33,
        "tfs": 0.84,
        "top_a": 0,
        "top_k": 13,
        "top_p": 1,
        "typical": 1,
        "sampler_order": [6, 0, 1, 2, 3, 4, 5],
        "singleline": True,
        "frmttriminc": True,
        "frmtrmblln": False
    }


# Load the characters
def load_character_data(lodad_character_data_characters_folder):
    load_character_data_characters = []

    for filename in os.listdir(lodad_character_data_characters_folder):
        if filename.endswith('.json'):
            with open(os.path.join(lodad_character_data_characters_folder, filename)) as read_file:
                character_data = json.load(read_file)
                image_file_jpg = f"{os.path.splitext(filename)[0]}.jpg"
                image_file_png = f"{os.path.splitext(filename)[0]}.png"
                if os.path.exists(os.path.join(lodad_character_data_characters_folder, image_file_jpg)):
                    character_data['char_image'] = os.path.join(lodad_character_data_characters_folder, image_file_jpg)
                elif os.path.exists(os.path.join(lodad_character_data_characters_folder, image_file_png)):
                    character_data['char_image'] = os.path.join(lodad_character_data_characters_folder, image_file_png)

                load_character_data_characters.append(character_data)

    return load_character_data_characters


# Select a character
def select_character(selected_characters):
    for i, character in enumerate(selected_characters):
        print(f"{i + 1}. {character['char_name']}")
    selected_char = int(input("Select a character: ")) - 1
    return selected_characters[selected_char]


def initialize_discord_bot(token, characters_name, characters_greeting):
    intents = discord.Intents.default()
    intents.messages = True
    intents.dm_messages = True
    intents.message_content = True  # Add this line
    bot = commands.Bot(command_prefix='!', intents=intents)

    # Assuming selected_character is defined before this function call
    conversation_history = (
        f"{characters_name}'s Persona: {selected_character['char_persona']}\n"
        f"World Scenario: {selected_character['world_scenario']}\n"
        f"Character dislikes: {selected_character['char_dislikes']}\n"
        f"Character likes: {selected_character['char_likes']}\n"
        f"Characters age: {selected_character['char_age']}\n"
        f"Characters gender: {selected_character['char_gender']}\n"
        f'<START>\n'
        f'"{characters_name}: {characters_greeting}\n'
    )

    memory_file = (
        f"{characters_name}'s Persona: {selected_character['char_persona']}\n"
        f"World Scenario: {selected_character['world_scenario']}\n"
        f"Character dislikes: {selected_character['char_dislikes']}\n"
        f"Character likes: {selected_character['char_likes']}\n"
        f"Characters age: {selected_character['char_age']}\n"
        f"Characters gender: {selected_character['char_gender']}\n"
        f'<START>\n'
        f'"{characters_name}: {characters_greeting}\n'
    )

    return bot, conversation_history, memory_file


#
#
# Load character data
characters_folder = 'Characters'
characters = load_character_data(characters_folder)

# Select a character
selected_character = select_character(characters)
char_name = selected_character["char_name"]
char_greeting = selected_character["char_greeting"]
#
# Initialize Discord bot
bot, conversation_history, memory_file = initialize_discord_bot(DISCORD_BOT_TOKEN, char_name, char_greeting)


# Escape reserved characters to allow markdown formatting
def escape_message(message):
    reserved_chars = r'[]()~`>#+-=|{}.!</'
    escaped_chars = [f'\\{c}' if c in reserved_chars else c for c in message]
    return ''.join(escaped_chars)


# If you send a message, they will with either 1 or 2 lines of text.

last_bot_message = None


async def send_messages():
    global timer_interval, memory_file, conversation_history
    print("already_started")
    print(timer_interval)
    await asyncio.sleep(timer_interval)
    print("second timer")

    while True:
        current_time = datetime.datetime.now().time()  # Implement that the bot can't send message randomly after midnight
        if random.random() < 0.5:
            response = generate_random_message()
            chosen_method = "memory_file"
        else:
            response = generate_random_message_alternative()
            chosen_method = "conversation_history"

        if response.status_code == 200:
            results = response.json()["results"]
            text = results[0]["text"]
            response_text = split_text(text)[0]
            response_text = response_text.replace("  ", "")

            if chosen_method == "memory_file":
                memory_file += f"{char_name}:{response_text}\n"
                conversation_history += f"{char_name}:{response_text}\n"
                with open(f"memory_file_{char_name}.txt", "a") as f:
                    f.write(f"{char_name}:{response_text}\n")
                with open(f"conversation_history_{char_name}.txt", "a") as f:
                    f.write(f"{char_name}:{response_text}\n")
            else:
                conversation_history += f"{char_name}:{response_text}\n"
                with open(f"conversation_history_{char_name}.txt", "a") as f:
                    f.write(f"{char_name}:{response_text}\n")

            random_message = response_text.strip()
            if random_message:
                user = bot.get_user(DISCORD_USER_ID)
                await user.send(random_message)

            random_number = random.random()
            counter = 0

            while random_number < 0.3 and counter < 1:
                print(f'Send extra messages with a 30% chance (Has to be less than 0.3): {random_number}')
                if random.random() < 0.3:
                    extra_response = generate_random_message()
                    chosen_method = "memory_file"
                else:
                    extra_response = generate_random_message_alternative()
                    chosen_method = "conversation_history"

                if extra_response.status_code == 200:
                    extra_results = extra_response.json()["results"]
                    extra_text = extra_results[0]["text"]
                    extra_response_text = split_text(extra_text)[0]

                    if chosen_method == "memory_file":
                        memory_file += f"{char_name}:{extra_response_text} is this buk\n"
                        with open(f"memory_file_{char_name}.txt", "a+") as f:
                            f.write(f"{char_name}:{extra_response_text}\n")
                    else:
                        conversation_history += f"{char_name}:{extra_response_text}\n"
                        with open(f"conversation_history_{char_name}.txt", "a+") as f:
                            f.write(f"{char_name}:{extra_response_text}\n")

                counter += 1
                random_number = random.random()

        print(f"Chosen method: {chosen_method}")
        timer_interval = random.randint(900, 3600)
        print(str(timer_interval) + " send msg local")
        await asyncio.sleep(timer_interval)


async def handle_message(context, message, user_message):
    global timer_interval, conversation_history
    timer_interval = random.randint(900, 3600)
    print(f'Sleep after message sent: {timer_interval}')

    prompt = get_prompt(conversation_history, message.author.name, user_message)
    response = requests.post(f"{LLM_URL}/api/v1/generate", json=prompt)

    if response.status_code == 200:
        text = split_text(response.json()['results'][0]['text'])[0]
        response_text = text.replace("  ", "")

        await update_history_and_send_response(context, message, user_message, response_text)

        num_subsequent_responses = random.randint(0, 1)
        print(f'Number of subsequent responses: {num_subsequent_responses}')

        for _ in range(num_subsequent_responses):
            contextless_prompt = get_prompt(conversation_history, message.author.name, "")
            subsequent_response = requests.post(f"{LLM_URL}/api/v1/generate", json=contextless_prompt)

            if subsequent_response.status_code == 200:
                subsequent_response_text = split_text(subsequent_response.json()['results'][0]['text'])[0]

                if subsequent_response_text.strip():
                    await update_history_and_send_response(context, message, "", subsequent_response_text)


async def update_history_and_send_response(context, message, user_message, response_text):
    global conversation_history

    if user_message.strip():  # Check if user_message is not empty or only contains whitespace

        with open(f'conversation_history_{char_name}.txt', "a") as f:
            f.write(f"{YOUR_NAME}: {user_message}\n")

    if response_text.strip():  # Check if response_text is not empty or only contains whitespace

        with open(f'conversation_history_{char_name}.txt', "a") as f:
            f.write(f"{char_name}:{response_text}\n")

    await context.send(response_text)


def generate_random_message():
    global memory_file  # "memory"

    # prompt = f"{char_name}'s Persona: {data['char_persona']}\n" + \
    #     f"{memory_file}\n" + \
    #     f'{char_name}:'

    response = requests.post(
        f"{LLM_URL}/api/v1/generate",
        json={
            "prompt": memory_file + f"{char_name}:",
            "use_story": False,
            "use_memory": False,
            "use_authors_note": False,
            "use_world_info": False,
            "max_context_length": 2048,
            "max_length": 120,
            "rep_pen": 1.15,
            "rep_pen_range": 2048,
            "rep_pen_slope": 3.4,
            "temperature": 0.8,
            "tfs": 1,
            "top_a": 0,
            "top_k": 13,
            "top_p": 0.9,
            "typical": 1,
            "sampler_order": [6, 0, 1, 2, 3, 4, 5],
            "singleline": True,
            "frmttriminc": True,
            "frmtrmblln": False
        }
    )

    return response


def generate_random_message_alternative():
    global conversation_history  # "memory"

    response = requests.post(
        f"{LLM_URL}/api/v1/generate",
        json={
            "prompt": conversation_history + f"{char_name}:",
            "use_story": False,
            "use_memory": False,
            "use_authors_note": False,
            "use_world_info": False,
            "max_context_length": 2048,
            "max_length": 120,
            "rep_pen": 1.15,
            "rep_pen_range": 2048,
            "rep_pen_slope": 3.4,
            "temperature": 0.8,
            "tfs": 1,
            "top_a": 0,
            "top_k": 13,
            "top_p": 0.9,
            "typical": 1,
            "sampler_order": [6, 0, 1, 2, 3, 4, 5],
            "singleline": True,
            "frmttriminc": True,
            "frmtrmblln": False
        }
    )

    return response


# Between a random time interval, the bot will send you a message from either



def Random_Negative_Prompt_Selector():
    return random.choice(["counterfit_negative_long", "counterfit_negative_other", "SFW_negative_only",
                          "counterfit_negative_long_TRY_TEST", "counterfit_negative_long_TRY_TEST_With_Positive",
                          "SFW_negative_only_now_with_positive_test", "counterfit_negative_long_with_Positive"])


# User can ask for a selfie
# Maybe could add a "chance" to not send one, maybe acting a bit angry?


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
        self.current_file = None
        self.chosen_character = None
        self.data = import_prompt_generator()[1]
        self.current_first_topwear_layer = None
        self.current_second_topwear_layer = None
        self.current_full_bottomwear = None
        self.current_partial_bottomwear = None
        self.current_full_attire = None

    async def reset(self, reset_command):
        if reset_command == "Confirm":
            self.__init__()
            return f"The attributes have been reseted."

    async def set_custom_full_attire(self, full_attire):
        try:
            selectable_full_attire = self.data['SFW']['appearance']['attire']['full_attire']
        except KeyError:
            selectable_full_attire = self.data['NSFW']['appearance']['attire']['full_attire']

        if (full_attire in selectable_full_attire.keys()) and self.current_full_attire is None:
            self.current_full_attire = selectable_full_attire[full_attire]
            return f"Full attire was changed to {full_attire}"
        else:
            return f"{full_attire} is not in {selectable_full_attire.keys()}"

    async def full_attire_selected(self):
        print(f"Currently chosen full attire {self.current_full_attire}")
        if self.current_full_attire is not None:
            returnable_full_attire = self.current_full_attire
            self.current_full_attire = None
            return returnable_full_attire

    async def set_custom_partial_bottomwear(self, partial_bottomwear):
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

    async def partial_bottomwear_selected(self):
        print(f"Currently chosen partial bottomwear {self.current_partial_bottomwear}")
        if self.current_partial_bottomwear is not None:
            returnable_partial_bottomwear = self.current_partial_bottomwear
            self.current_partial_bottomwear = None
            print(returnable_partial_bottomwear)
            return returnable_partial_bottomwear

    async def set_custom_full_bottomwear(self, full_bottomwear):
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

    async def full_bottomwear_selected(self):
        print(f"Currently chosen full bottomwear {self.current_full_bottomwear}")
        if self.current_full_bottomwear is not None:
            returnable_full_bottomwear = self.current_full_bottomwear
            self.current_full_bottomwear = None
            return returnable_full_bottomwear

    async def set_custom_second_topwear_layer(self, second_topwear_layer):
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

    async def second_topwear_layer_selected(self):
        print(f"Currently chosen second layer topwear {self.current_second_topwear_layer}")
        if self.current_second_topwear_layer is not None:
            returnable_second_topwear_layer = self.current_second_topwear_layer
            self.current_second_topwear_layer = None
            return returnable_second_topwear_layer

    async def set_custom_file(self, file):
        acceptable_list = ["Portray", "Cowboy Shot", "NSFW"]
        if file in acceptable_list:
            self.current_file = file
            _, new_data = import_prompt_generator(file)
            self.data = new_data  # Update self.data with the new data
            return f"File changed to {file}"
        else:
            return f"{file} is not in {acceptable_list}"

    async def random_file_selector(self):
        print(f"Currently chosen file {self.current_file}")
        if self.current_file is not None:
            returnable_file = self.current_file
            self.current_file = None
            return returnable_file

    async def set_custom_model_model(self, new_model):
        if new_model in self.models:
            self.current_model = new_model
            return f"Model changed to {new_model}"
        else:
            return f"{new_model} is not inside {self.models.keys()}"

    async def random_model_selector(self, model):
        print(self.current_model)

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

        # If a current_model is provided and it's in the model_mapping, use it
        if self.current_model is not None and self.current_model in model_mapping:
            random_model_chosen_here = model_mapping[self.current_model]
            self.current_model = None  # Reset current_model to None after using it

        return random_model_chosen_here

    async def set_custom_resolution_and_hr(self, resolution):
        self.current_resolution = resolution
        return f"Resolution changed to {resolution}"

    async def random_resolution_selector(self):
        print(self.current_resolution)
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

    async def set_custom_sampler(self, sampler):
        if sampler in self.sampler_list:
            self.current_sampler = sampler
            return f"Sampler changed to {sampler}"
        else:
            return f"{sampler} is not inside {self.sampler_list}"

    async def random_sampler_selector(self):
        print(self.current_sampler)
        returnable_sampler = random.choice(self.sampler_list)

        if self.current_sampler is not None and self.current_sampler in self.sampler_list:
            returnable_sampler = self.current_sampler
            self.current_sampler = None

        return returnable_sampler

    async def set_custom_amount_of_pics(self, amount_of_pics):
        if amount_of_pics in range(1, 4):
            self.amount_of_pics = amount_of_pics
            return f"Amount of pictures to be sent changed to {amount_of_pics}"
        else:
            return f"{amount_of_pics} is not between 1 and 3 "

    async def random_amount_of_pics(self):
        returnable_amount_of_pics = random.choice(range(1, 4))

        if self.amount_of_pics != 0 and self.amount_of_pics in list(range(1, 4)):
            returnable_amount_of_pics = self.amount_of_pics
            self.amount_of_pics = 0

        return returnable_amount_of_pics

    async def set_custom_character(self, chosen_character):
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

    async def character_selected(self):
        print(f"currently chosen character {self.chosen_character}")
        returnable_character_selected = self.chosen_character
        if self.chosen_character is not None:
            returnable_character_selected = self.chosen_character
            self.chosen_character = None

        return returnable_character_selected

    async def set_custom_first_topwear_layer(self, first_topwear_layer):
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

    async def first_topwear_layer_selected(self):
        print(f"Currently chosen first layer topwear {self.current_first_topwear_layer}")
        if self.current_first_topwear_layer is not None:
            returnable_first_topwear_layer = self.current_first_topwear_layer
            self.current_first_topwear_layer = None
            await returnable_first_topwear_layer


model_manager = ModelManager()


@bot.command(name='change_partial_bottomwear')
async def change_partial_bottomwear(ctx, new_partial_bottomwear):
    response = await model_manager.set_custom_partial_bottomwear(new_partial_bottomwear)
    await ctx.send(response)


@bot.command(name="change_full_bottomwear")
async def Change_Full_Bottomwear(ctx, *, new_full_bottomwear):
    response = await model_manager.set_custom_full_bottomwear(new_full_bottomwear)  # will receive "shirt"
    await ctx.send(response)


@bot.command(name="change_first_topwear_layer")
async def Change_First_Topwear_Layer(ctx, *, new_first_topwear_layer):
    response = await model_manager.set_custom_first_topwear_layer(new_first_topwear_layer)  # will receive "shirt"
    await ctx.send(response)


@bot.command(name="change_character")
async def Change_Character(ctx, *, new_character):
    response = await model_manager.set_custom_character(new_character)  # will receive "Raiden"
    await ctx.send(response)

@bot.command(name="change_model")
async def change_model_input(ctx, *, new_model):
    response = await model_manager.set_custom_model_model(new_model)
    await ctx.send(response)

@bot.command(name="change_resolution")
async def Change_Resolution(ctx, *, resolution):
    try:
        width_str, height_str, scale_str = map(str.strip, resolution.split(','))

        # Convert width and height to integers
        width, height = int(width_str), int(height_str)

        # Convert scale to float with two decimal places
        scale = round(float(scale_str), 2)
        response = await model_manager.set_custom_resolution_and_hr([width, height, scale])
        await ctx.send(response)

    except ValueError as e:
        await ctx.send(f"Error parsing resolution: {str(e)}, resolution is not being changed.")


@bot.command(name="change_sampler")
async def Change_Sampler(ctx, *, sampler):
    response = await model_manager.set_custom_sampler(sampler)
    await ctx.send(response)

@bot.command(name="change_number_of_pics")
async def Change_Number_Of_Pics(ctx, *, number_of_pics):
    try:
        number_of_pics = int(number_of_pics)
        response = await model_manager.set_custom_amount_of_pics(number_of_pics)
        await ctx.send(response)
    except ValueError as e:
        await ctx.send(f"Error parsing number of pics {str(e)}, number of pics is not being changed.")
@bot.command(name="change_file")
async def Change_File(ctx, *, new_file):
    response = await model_manager.set_custom_file(new_file)
    await ctx.send(response)


# Models base parameters that are used for "payloads"
async def model_base_params(chosen_model):
    model = await model_manager.random_model_selector(chosen_model)
    random_sampler = await model_manager.random_sampler_selector()
    resolution = await model_manager.random_resolution_selector()
    amount_of_selfies = await model_manager.random_amount_of_pics()
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
        'amount_of_selfies': amount_of_selfies,
        'random_resolution': resolution,
        'random_negative_prompt': random_negative_prompt,
        'random_cfg_scale': random_cfg_scale,
        'hr_true_or_false': hr_true_or_false,
        'vae': VAE,
        'vae_override': VAE_Override
    }
    return result


async def take_a_selfie_test(message):
    user_selected_file = await model_manager.random_file_selector()
    user_selected_character = await model_manager.character_selected()
    user_selected_first_topwear_layer = await model_manager.first_topwear_layer_selected()
    user_selected_second_topwear_layer = await model_manager.second_topwear_layer_selected()
    user_selected_full_bottomwear = await model_manager.full_bottomwear_selected()
    user_selected_partial_bottomwear = await model_manager.partial_bottomwear_selected()
    prompt_generator_module = import_prompt_generator(user_selected_file)[0]
    base_param = await model_base_params(prompt_generator_module)
    generated_prompt = prompt_generator_module.generated_prompt(
        user_selected_character=user_selected_character,
        user_selected_first_topwear_layer=user_selected_first_topwear_layer,
        user_selected_second_topwear_layer=user_selected_second_topwear_layer,
        user_selected_full_bottomwear=user_selected_full_bottomwear,
        user_selected_partial_bottomwear=user_selected_partial_bottomwear
    )
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
        # "hr_negative_prompt": "sketch, duplicate, ugly, huge eyes, text, logo, monochrome, worst face, (bad and mutated hands:1.3), (worst quality:1.7), (low quality:1.7), (blurry:1.7), horror, geometry, bad prompt, (bad hands), (missing fingers), multiple limbs, bad anatomy, (interlocked fingers:1.2),(interlocked leg:1.2), Ugly Fingers, (extra digit and hands and fingers and legs and arms:1.4), crown braid,, (deformed fingers:1.2), (long fingers:1.2),succubus wings, horn, succubus horn, succubus hairstyle, (bad-artist-anime), bad-artist, bad hand",
        # "hr_prompt": "raiden shogun, purple hair, purple eyes, from front, cowboy shot, from front, parted lips, medium hair, blunt bangs, hair twirling, kneeling, indoors, ferris wheel, cityscape, window, bare shoulders, camisole, camisole, yellow jacket, yellow open jacket, yellow jeans, yellow jeans,\ncinematic lighting, dramatic lighting, beautiful woman, gorgeous, masterpiece, high quality, best quality,",
        "hr_resize_x": 0,
        "hr_resize_y": 0,
        "hr_scale": base_param["random_resolution"][2],
        "hr_second_pass_steps": 35,
        "hr_upscaler": "Latent (nearest)",
        "n_iter": 1,
        "negative_prompt": "",
        "override_settings": {
            "sd_model_checkpoint": base_param["random_model"],
            "sd_vae": base_param['vae'],
            "sd_vae_overrides_per_model_preferences": base_param['vae_override']
        },
        "override_settings_restore_afterwards": True,
        "prompt": "1girl, solo, " + generated_prompt,
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

    async with aiohttp.ClientSession() as session:
        async with session.post(url=f'{SD_URL}/sdapi/v1/txt2img', json=payload) as response:
            r = await response.json()

    for i, image_data in enumerate(r['images']):
        image_path = f"taken_selfie_{i}.png"
        user_id = message.author.id

        user = await bot.fetch_user(user_id)

        with open(image_path, 'wb') as file:
            file.write(base64.b64decode(image_data))

        if user:
            try:
                with open(image_path, 'rb') as file:
                    await user.send(file=discord.File(file))
                print(f"Image sent to {user.name}")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print(f"User not found. {user_id}")

        os.remove(image_path)



@bot.event
async def on_message(message):
    print(message.content)
    if message.author == bot.user:
        return

    if "take a selfie" in message.content.lower():
        await message.channel.send("Sent you a selfie <3")
        await take_a_selfie_test(message)


    elif "!" not in message.content[0]:
        user_message = message.content
        context = await bot.get_context(message)
        await handle_message(context, message, user_message)

    await bot.process_commands(message)


# Draw an image that the user wants, with random base parameters

@bot.command(name='draw')
async def draw(ctx, *, message):
    try:
        msgs = message
        print(msgs)
        await ctx.reply("Drawing the image, one sec :*")

        prompt_generator_module = import_prompt_generator()
        base_param = await model_base_params(prompt_generator_module)  # Such as resolutions, what model, CFG scale, etc.

        if random.random() < 0.4:
            base_param["random_resolution"][0], base_param["random_resolution"][1] = base_param["random_resolution"][1], \
                base_param["random_resolution"][0]
            base_param["random_resolution"] = base_param["random_resolution"]

        payload = {
            # "alwayson_scripts": {
            #     "Aesthetic embeddings": {
            #         "args": [0.9, 5, "0.0001", False, "None", "", 0.1, False]
            #     },
            #
            #     "Refiner": {
            #         "args": [False, "", 0.8]
            #     },
            #     "Seed": {
            #         "args": [-1, False, -1, 0, 0, 0]
            #     },
            # },
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
            # "hr_negative_prompt": "sketch, duplicate, ugly, huge eyes, text, logo, monochrome, worst face, (bad and mutated hands:1.3), (worst quality:1.7), (low quality:1.7), (blurry:1.7), horror, geometry, bad prompt, (bad hands), (missing fingers), multiple limbs, bad anatomy, (interlocked fingers:1.2),(interlocked leg:1.2), Ugly Fingers, (extra digit and hands and fingers and legs and arms:1.4), crown braid,, (deformed fingers:1.2), (long fingers:1.2),succubus wings, horn, succubus horn, succubus hairstyle, (bad-artist-anime), bad-artist, bad hand",
            # "hr_prompt": "raiden shogun, purple hair, purple eyes, from front, cowboy shot, from front, parted lips, medium hair, blunt bangs, hair twirling, kneeling, indoors, ferris wheel, cityscape, window, bare shoulders, camisole, camisole, yellow jacket, yellow open jacket, yellow jeans, yellow jeans,\ncinematic lighting, dramatic lighting, beautiful woman, gorgeous, masterpiece, high quality, best quality,",
            "hr_resize_x": 0,
            "hr_resize_y": 0,
            "hr_scale": base_param["random_resolution"][2],
            "hr_second_pass_steps": 35,
            "hr_upscaler": "Latent (nearest)",
            "n_iter": 1,
            "negative_prompt": "",
            "override_settings": {
                "sd_model_checkpoint": base_param["random_model"]
            },
            "override_settings_restore_afterwards": True,
            "prompt": msgs,
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

        async with aiohttp.ClientSession() as session:
            async with session.post(url=f'{SD_URL}/sdapi/v1/txt2img', json=payload) as response:
                r = await response.json()

        for i, image_data in enumerate(r['images']):
            # Define unique image path for each iteration
            image_path = f"selfie_{i}.png"
            user_id = DISCORD_USER_ID

            # Get the user object
            user = await bot.fetch_user(user_id)

            with open(image_path, 'wb') as file:
                file.write(base64.b64decode(image_data))

            if user:
                try:
                    # Open the image file
                    with open(image_path, 'rb') as file:
                        # Send the file to the user
                        await user.send(file=discord.File(file, 'selfie.png'))
                    print(f"Image sent to {user.name}")
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print(f"User not found. {user_id}")

            os.remove(image_path)
        print("Image generation and sending completed successfully.")
    except Exception as e:
        print(f"Error: {e}")
        await ctx.reply("An error occurred during image generation.")


async def generate_selfie_and_send():

    prompt_generator_module = import_prompt_generator()
    base_param = await model_base_params(prompt_generator_module)

    # What will be sent to StableDiffusion's API
    payload = {
        # "alwayson_scripts": {
        #     "Aesthetic embeddings": {
        #         "args": [0.9, 5, "0.0001", False, "None", "", 0.1, False]
        #     },
        #
        #     "Refiner": {
        #         "args": [False, "", 0.8]
        #     },
        #     "Seed": {
        #         "args": [-1, False, -1, 0, 0, 0]
        #     },
        # },
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
        # "hr_negative_prompt": "sketch, duplicate, ugly, huge eyes, text, logo, monochrome, worst face, (bad and mutated hands:1.3), (worst quality:1.7), (low quality:1.7), (blurry:1.7), horror, geometry, bad prompt, (bad hands), (missing fingers), multiple limbs, bad anatomy, (interlocked fingers:1.2),(interlocked leg:1.2), Ugly Fingers, (extra digit and hands and fingers and legs and arms:1.4), crown braid,, (deformed fingers:1.2), (long fingers:1.2),succubus wings, horn, succubus horn, succubus hairstyle, (bad-artist-anime), bad-artist, bad hand",
        # "hr_prompt": "raiden shogun, purple hair, purple eyes, from front, cowboy shot, from front, parted lips, medium hair, blunt bangs, hair twirling, kneeling, indoors, ferris wheel, cityscape, window, bare shoulders, camisole, camisole, yellow jacket, yellow open jacket, yellow jeans, yellow jeans,\ncinematic lighting, dramatic lighting, beautiful woman, gorgeous, masterpiece, high quality, best quality,",
        "hr_resize_x": 0,
        "hr_resize_y": 0,
        "hr_scale": base_param["random_resolution"][2],
        "hr_second_pass_steps": 35,
        "hr_upscaler": "Latent (nearest)",
        "n_iter": 1,
        "negative_prompt": "",
        "override_settings": {
            "sd_model_checkpoint": base_param["random_model"]
        },
        "override_settings_restore_afterwards": True,
        "prompt": "masterpiece, best quality, high quality, beautiful women, gorgeous, masterpiece, 1girl, solo, Raiden Shogun, selfie, cleavage, kimono, purple hair, long hair, purple eyes, (medium breasts:1.2)",
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

    r = requests.post(url=f'{SD_URL}/sdapi/v1/txt2img', json=payload).json()

    for i, image_data in enumerate(r['images']):
        # Define unique image path for each iteration
        image_path = f"selfie_{i}.png"
        user_id = DISCORD_USER_ID

        # Get the user object
        user = await bot.fetch_user(user_id)

        with open(image_path, 'wb') as file:
            file.write(base64.b64decode(image_data))

        if user:
            try:
                # Open the image file
                with open(image_path, 'rb') as file:
                    # Send the file to the user
                    await user.send(file=discord.File(file, 'selfie.png'))
                print(f"Image sent to {user.name}")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print(f"User not found. {user_id}")

        os.remove(image_path)


# Define a variable to track whether the bot has been running
bot_has_started = False


# Function to handle sending selfies periodically
async def send_selfie_periodically():
    global bot_has_started
    while True:
        if bot_has_started:
            should_send_selfie = random.random() < 0.33  # Adjust probability as needed
            if should_send_selfie:
                # Pass the correct ctx argument when calling generate_selfie_and_send
                await generate_selfie_and_send()
            # Sleep for a random interval between 300 and 3600 seconds
            await asyncio.sleep(random.randint(300, 3600))
        else:
            # Delay the start of the selfie check for 5 minutes
            await asyncio.sleep(300)
            print(f"Sleeping for 5 minutes")
            bot_has_started = True


# Extracting lines for a possible image that depicts the past conversation
def extract_last_n_lines(extract_last_n_lines_conversation_history, n):
    with open(extract_last_n_lines_conversation_history, 'r') as file:
        lines = file.readlines()
        non_empty_lines = [extract_last_n_lines_line.strip() for extract_last_n_lines_line in lines if
                           extract_last_n_lines_line.strip()]
        return non_empty_lines[-n:]


file_name = f'conversation_history_{char_name}.txt'
num_lines_to_extract = 6
extracted_lines = extract_last_n_lines(file_name, num_lines_to_extract)

output_text = ""  # Variable to store the output
for line in extracted_lines:
    output_text += line + "\n"  # Appending each line to the output_text variable

print(output_text)  # This will display the extracted lines


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    bot.loop.create_task(send_selfie_periodically())
    bot.loop.create_task(send_messages())


bot.run(DISCORD_BOT_TOKEN)

###############################
