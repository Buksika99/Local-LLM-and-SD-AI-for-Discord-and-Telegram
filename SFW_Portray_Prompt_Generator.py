import json
import random

# Load the JSON data from the file

def load_random_json():
    chosen_json_file = random.choice(["SFW_AI_THING.json", "TEASY_AI_THING.json"])
    print(chosen_json_file)

    # Load the JSON data from the file
    with open(chosen_json_file, "r") as json_file:
        data = json.load(json_file)

    return data

def add_space_after_comma(prompt):
    return ', '.join([word.strip() for word in prompt.split(',')])


def add_text_before_word(sentence, target_word, text_to_add):
    words = sentence.split()
    for i, word in enumerate(words):
        if word == target_word:
            words.insert(i, text_to_add)
            break  # Stop after the first occurrence of the target word
    return ' '.join(words)


def clean_generated_prompt(prompt, data):
    colors = data["colors"]
    # Your existing code to clean prompt
    cleaned_prompt = [item for item in prompt if item and item != ',']
    cleaned_prompt_str = ', '.join(map(str, cleaned_prompt))
    cleaned_prompt_str = cleaned_prompt_str.replace(" , ", "").replace("['", "").replace("']", "").replace("'", "")

    # Adding space after comma based on your requirement
    cleaned_prompt_str = add_space_after_comma(cleaned_prompt_str)

    # Additional functionality to remove standalone occurrences of "yellow" and "blue"
    filtered_items = [item for item in cleaned_prompt_str.split(', ') if item.lower() not in colors]

    # Join the filtered items back into a string
    output_string = ', '.join(filtered_items)
    output_string = add_text_before_word(output_string, "BREAK", " ")
    output_string = output_string.replace("   ", " ").replace("  ", " ")

    if " , " in output_string:
        output_string = output_string.replace(" , ", " ")
        return output_string
    else:
        return output_string


def choose_prop_numbers_amount(list_length):
    if len(list_length) == 1:
        return 1
    else:
        n = random.choice(range(2, len(list_length) + 1))
    return n


def choose_random_item(items):
    return random.choice(items)


def choose_random_items(items, n):
    return random.sample(items, n)


def weighted_choice(options, weights):
    return random.choices(options, weights=weights)


def weighted_emotions(data):
    weights = [4, 1]
    positive_emotion = data["SFW"]["appearance"]["emotions"]["positive"]
    negative_emotion = data["SFW"]["appearance"]["emotions"]["negative"]

    specific_positive_or_negative = random.choices([positive_emotion, negative_emotion], weights=weights)

    if specific_positive_or_negative == [positive_emotion]:
        return choose_random_item(positive_emotion)
    elif specific_positive_or_negative == [negative_emotion]:
        return choose_random_item(negative_emotion)


# This gets the values from a dictionary
def choose_random_value_from_dict(item):
    return choose_random_item((choose_random_item(list(item.values()))))


def returning_a_dictionary_values(input_dict, key):
    if key in input_dict:
        return input_dict[key]
    else:
        return None


def choose_a_character_with_or_without_prereqs(characters):
    weights = [5, 2, 1]
    main_character = characters["Main_Character"]
    character_without_prereq = characters["without_clothing_prerequisite"]
    character_with_prereq = characters["with_clothing_prerequisites"]
    select_character = [main_character, character_without_prereq, character_with_prereq]
    select_weighed_character = weighted_choice(select_character, weights)[0]

    if select_weighed_character == main_character:
        return ["Main_Character", choose_random_item(list(main_character.values()))]
    elif select_weighed_character == character_with_prereq:
        return ["with_clothing_prerequisites", choose_random_item(list(character_with_prereq.values()))]
    else:
        return ["without_clothing_prerequisite", choose_random_item(list(character_without_prereq.values()))]


def handle_special_location(special):
    return ", ".join(choose_random_item(list(special[choose_random_item(list(special))].values())))


def handle_locations(random_locations, data):
    locations = data["SFW"]["locations"]
    random_indoor_location = choose_random_item(list(locations[random_locations].keys()))
    random_indoor_location_all_props = data["SFW"]["locations"][random_locations][random_indoor_location]
    random_indoor_location_some_props = choose_random_items(random_indoor_location_all_props,
                                                            choose_prop_numbers_amount(
                                                                random_indoor_location_all_props))
    random_indoor_location_with_props = [random_indoor_location] + random_indoor_location_some_props
    return ', '.join(random_indoor_location_with_props)


def random_clothing_action(random_topwear, data):
    actions = data["SFW"]["actions"]
    if random_topwear == "shirt":
        return choose_random_item(actions["clothing_actions"]["shirt_actions"])


def check_if_upper_body(random_camera_angle):
    if random_camera_angle == "upper body":
        return random_camera_angle == "upper body"
    if random_camera_angle == "portrait":
        return random_camera_angle == "portrait"


def random_color_chooser(data):
    return choose_random_item(data["colors"])


def handle_camera_angle(data):
    composition = data['SFW']["composition"]["camera_angle"]
    upper_body = data['SFW']["composition"]["camera_angle"]["upper body"]["upper_body_from_front"]
    portrait = data['SFW']["composition"]["camera_angle"]["portrait"]["portrait_from_front"]
    skimpy_from_front = data['SFW']["composition"]["camera_focus"]["skimpy_from_front"]
    upper_or_portrait = choose_random_item(["upper body", "portrait"])
    random_composition = choose_random_value_from_dict(composition[upper_or_portrait])
    if random.random() < 0.3:
        random_skimpy_from_front = choose_random_item(skimpy_from_front)
        return [upper_or_portrait, random_skimpy_from_front, "from front"]
    else:
        return [upper_or_portrait, " ", random_composition]


def random_topwear_selection(first_layer):
    first_layer_category = random.choice(list(first_layer.keys()))
    first_layer_style = random.choice(list(first_layer[first_layer_category].keys()))
    first_layer_item = random.choice(first_layer[first_layer_category][first_layer_style])
    return [first_layer_category, first_layer_style, first_layer_item]


def random_layer_selectors(first_layer, second_layer):
    options = [first_layer, second_layer, [first_layer, second_layer], ""]
    return choose_random_item(options)


def generate_random_topwear_layers(random_specified_first_layer_topwear, random_specified_second_layer_topwear,
                                   first_layer_open_or_closed,
                                   second_layer_open_or_closed, random_topwear_undergarment,
                                   topwear_first_layer_dict_key, topwear_second_layer_dict_key, data):
    shirt_actions = data["SFW"]["actions"]["clothing_actions"]["shirt_actions"]
    exposed_body_parts = data["SFW"]["appearance"]["exposed_bodyparts"]["topwear_upper_body"]
    exposed_body_parts_open = data["SFW"]["appearance"]["exposed_bodyparts"]["topwear_open"]
    the_returnable_list = []

    def format_topwear_layer(item, dict_key):
        random_color = random_color_chooser(data)
        formatted_topwear_returner = f"BREAK ({random_color} {dict_key}:1.3), {random_color} {item if item else ''}"
        return formatted_topwear_returner

    def add_topwear_layer_to_returnable_list(item):
        if item:
            the_returnable_list.append(item)

    if topwear_first_layer_dict_key == "shirt":
        add_topwear_layer_to_returnable_list(" " + choose_random_item(shirt_actions))

    specific_first_topwear_layer = format_topwear_layer(random_specified_first_layer_topwear,
                                                        topwear_first_layer_dict_key)
    specific_second_topwear_layer = format_topwear_layer(random_specified_second_layer_topwear,
                                                         topwear_second_layer_dict_key)
    undergarment = random_color_chooser(data) + " " + random_topwear_undergarment

    if first_layer_open_or_closed == "open" and second_layer_open_or_closed == "open":
        the_returnable_list.append(choose_random_item(exposed_body_parts_open))
        add_topwear_layer_to_returnable_list(
            f"{specific_first_topwear_layer}, {specific_second_topwear_layer}, {undergarment}, (open clothing:1.3)")
    else:
        the_returnable_list.append(choose_random_item(exposed_body_parts))
        add_topwear_layer_to_returnable_list(f"{specific_first_topwear_layer}, {specific_second_topwear_layer}")

    return the_returnable_list


def main_or_no_prereq_for_leotard(characters):
    main_character = characters["Main_Character"]
    character_without_prereq = characters["without_clothing_prerequisite"]
    if choose_random_item([main_character, character_without_prereq]) == main_character:
        return choose_random_item(list(main_character.values()))
    else:
        return choose_random_item(list(character_without_prereq.values()))


def generate_prompt_Portray_SFW(data, **kwargs):
    prompt = []
    SFW = data['SFW']
    appearance = SFW['appearance']
    composition = SFW["composition"]
    locations = SFW["locations"]
    special = SFW["special"]
    actions = SFW["actions"]
    attire = appearance["attire"]
    pieces_of_attire = attire["pieces_of_attire"]
    topwear = pieces_of_attire["topwear"]
    topwear_undergarment = topwear["topwear_undergarment"]
    topwear_first_layer = topwear["topwear_first_layer"]
    topwear_second_layer = topwear["topwear_second_layer"]
    full_attire = attire["full_attire"]
    prefix = SFW["PREFIX"]
    leotard = full_attire["leotard"]
    characters = SFW["characters"]
    weights = [4, 1]
    random_number_between_half_and_one = round(random.uniform(0.5, 1), 2)
    random_character_for_leotard = main_or_no_prereq_for_leotard(characters)
    user_selected_character = kwargs.get('user_selected_character', None)
    user_selected_first_topwear_layer = kwargs.get('user_selected_first_topwear_layer', None)
    user_selected_second_topwear_layer = kwargs.get('user_selected_second_topwear_layer', None)

    if user_selected_character is None:
        random_chosen_character = choose_a_character_with_or_without_prereqs(characters)
    else:
        random_chosen_character = user_selected_character
    chosen_character = random_chosen_character

    if user_selected_first_topwear_layer is not None:
        topwear_first_layer = user_selected_first_topwear_layer

    if user_selected_second_topwear_layer is not None:
        topwear_second_layer = user_selected_second_topwear_layer

    # Composition
    random_camera_composition = handle_camera_angle(data)

    # For potential IF statements
    # random_location returns: "indoors" or "outdoors"
    random_location = choose_random_item(list(locations))
    special_or_default_location = weighted_choice([locations, special], weights)
    character_with_clothing_predetermined = True


    # Appearance
    random_emotion = weighted_emotions(data)

    random_mouth_states = choose_random_item(appearance["face_tags"]["mouth"])
    random_hair_length = choose_random_item(appearance["hair"]["hair_length"])
    random_hair_variant = choose_random_item(appearance["hair"]["hair_variants"])
    random_jewelry = choose_random_value_from_dict(appearance["jewelry"])
    random_topwear_undergarment = choose_random_value_from_dict(topwear_undergarment)

    topwear_first_layer_dict_key, first_layer_open_or_closed, random_specified_first_layer_topwear = random_topwear_selection(
        topwear_first_layer)
    topwear_second_layer_dict_key, second_layer_open_or_closed, random_specified_second_layer_topwear = random_topwear_selection(
        topwear_second_layer)

    randomly_selecting_topwear_layers = generate_random_topwear_layers(
        random_specified_first_layer_topwear,
        random_specified_second_layer_topwear,
        first_layer_open_or_closed,
        second_layer_open_or_closed,
        random_topwear_undergarment,
        topwear_first_layer_dict_key,
        topwear_second_layer_dict_key,
        data
    )

    # Locations
    random_special_full_theme = handle_special_location(special)
    random_location_with_props = handle_locations(random_location, data)

    # Actions
    random_where_the_character_looks = choose_random_item(actions["general_actions"]["looking"])
    random_hand_actions = choose_random_item(actions["general_actions"]["hand_actions"])

    prompt.append(prefix)
    prompt.append(random_camera_composition)
    prompt.append(random_emotion)
    prompt.append(random_mouth_states)
    prompt.append(random_hair_length and random_hair_variant)
    prompt.append(random_where_the_character_looks)
    prompt.append(random_hand_actions)

    if random.random() < 0.1:
        prompt.append(f"<lora:more_details_0.5-1:{random_number_between_half_and_one}>")

    if chosen_character[0] == "without_clothing_prerequisite" or chosen_character[0] == "Main_Character":
        prompt.append(chosen_character[1])
        character_with_clothing_predetermined = False  # If character has a clothing predetermined, this stays false

    if special_or_default_location == [special] and (
            user_selected_first_topwear_layer is not None or user_selected_second_topwear_layer is not None):
        if character_with_clothing_predetermined:
            prompt.append(random_character_for_leotard)
        prompt.append(random_special_full_theme)
        return prompt

    prompt.append(random_location)
    prompt.append(random_location_with_props)

    if random.random() < 0.33 and character_with_clothing_predetermined == False:  # If character is without clothing prerequisite AND less than 0.3
        if second_layer_open_or_closed == "open" or user_selected_second_topwear_layer is not None:
            prompt.append(
                f" BREAK ({random_color_chooser(data)} leotard:1.3) BREAK {choose_random_item(leotard)} BREAK ({topwear_second_layer_dict_key}:1.3) BREAK ({random_specified_second_layer_topwear}:1.3) BREAK")  # madoka in leotard here
        else:
            prompt.append(
                f" BREAK ({random_color_chooser(data)} leotard:1.3) BREAK {choose_random_item(leotard)} BREAK")
        return prompt

    if chosen_character[0] == "with_clothing_prerequisites":
        prompt.append(chosen_character[1])
        return prompt

    prompt.append(randomly_selecting_topwear_layers)

    return prompt


def generated_prompt(**kwargs):
    data = load_random_json()
    generated_prompt_in_function = generate_prompt_Portray_SFW(data, **kwargs)
    generated_prompt_in_function = clean_generated_prompt(generated_prompt_in_function, data)
    print(generated_prompt_in_function)
    return generated_prompt_in_function

