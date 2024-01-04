import json
import random
import re


# Load the JSON data from the file

def load_random_json():
    chosen_json_file = "NSFW_AI_THING.json"
    print(chosen_json_file)

    # Load the JSON data from the file
    with open(chosen_json_file, "r") as json_file:
        data = json.load(json_file)

    return data


def add_space_after_comma(prompt):
    return ', '.join([word.strip() for word in prompt.split(',')])


def add_space_after_break(text):
    # Use regular expression to find occurrences of "BREAK" and add space around it
    result = re.sub(r'(BREAK)', r' \1 ', text)
    return result


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
    weights = [5, 1]
    positive_emotion = data["NSFW"]["appearance"]["emotions"]["positive"]
    negative_emotion = data["NSFW"]["appearance"]["emotions"]["negative"]

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
    locations = data["NSFW"]["locations"]
    random_indoor_location = choose_random_item(list(locations[random_locations].keys()))
    random_indoor_location_all_props = data["NSFW"]["locations"][random_locations][random_indoor_location]
    random_indoor_location_some_props = choose_random_items(random_indoor_location_all_props,
                                                            choose_prop_numbers_amount(
                                                                random_indoor_location_all_props))
    random_indoor_location_with_props = [random_indoor_location] + random_indoor_location_some_props
    return ', '.join(random_indoor_location_with_props)


# Takes either indoors/outdoors or special
def handle_posture(location, data):
    actions = data["NSFW"]["actions"]
    if location == "outdoors" or "outdoors" in location:
        return choose_random_value_from_dict(actions["posture"]["posture_outdoors"])
    else:
        return choose_random_value_from_dict(actions["posture"]["posture_indoors"])


def random_clothing_action(random_partial_bottomwear, random_specific_bottomwear, random_topwear, data):
    actions = data["NSFW"]["actions"]
    if random_partial_bottomwear == "skirt":
        add = "(pussy:1.3), pussy peek"
        return choose_random_item(actions["clothing_actions"]["skirt_actions"])
    if random_topwear == "shirt":
        add = "nipples, nipple peek"
        return choose_random_item(actions["clothing_actions"]["shirt_actions"])
    if random_topwear == "hoodie":
        return choose_random_item(actions["clothing_actions"]["hoodie_actions"])
    if random_topwear == "sweater":
        return choose_random_item(actions["clothing_actions"]["sweater_actions"])
    if random_specific_bottomwear == "jeans" and random_topwear != "hoodie" and random_topwear != "sweater":
        return choose_random_item(actions["clothing_actions"]["jeans_action"])


def random_color_chooser(data):
    return choose_random_item(data["colors"])


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
                                   topwear_first_layer_dict_key, topwear_second_layer_dict_key, data, user_selected_second_topwear_layer=None):
    shirt_actions = data["NSFW"]["actions"]["clothing_actions"]["shirt_actions"]
    hoodie_actions = data["NSFW"]["actions"]["clothing_actions"]["hoodie_actions"]
    sweater_actions = data["NSFW"]["actions"]["clothing_actions"]["sweater_actions"]
    exposed_body_parts = data["NSFW"]["appearance"]["exposed_bodyparts"]["topwear_upper_body"]
    exposed_body_parts_open = data["NSFW"]["appearance"]["exposed_bodyparts"]["topwear_open"]
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

    if topwear_first_layer_dict_key == "sweater":
        add_topwear_layer_to_returnable_list(" " + choose_random_item(sweater_actions))

    if topwear_second_layer_dict_key == "hoodie":
        add_topwear_layer_to_returnable_list(" " + choose_random_item(hoodie_actions))

    specific_first_topwear_layer = format_topwear_layer(random_specified_first_layer_topwear,
                                                        topwear_first_layer_dict_key)

    if user_selected_second_topwear_layer is not None:
        specific_second_topwear_layer = format_topwear_layer(random_specified_second_layer_topwear,
                                                             topwear_second_layer_dict_key)
    else:
        if random.random() < 0.6:
            specific_second_topwear_layer = ""
        else:
            specific_second_topwear_layer = format_topwear_layer(random_specified_second_layer_topwear,
                                                                 topwear_second_layer_dict_key)
    undergarment = random_color_chooser(data) + " " + random_topwear_undergarment

    if first_layer_open_or_closed == "open" and second_layer_open_or_closed == "open":
        if random.random() < 0.4:
            the_returnable_list.append(choose_random_item(exposed_body_parts_open))

        add_topwear_layer_to_returnable_list(
            f"{specific_first_topwear_layer}, {specific_second_topwear_layer}, {undergarment}, (open clothing:1.3), (nipples:1.3), nipple, breasts, breasts apart")
    else:
        the_returnable_list.append(choose_random_item(exposed_body_parts))
        add_topwear_layer_to_returnable_list(f"{specific_first_topwear_layer}, {specific_second_topwear_layer}")

    return the_returnable_list


def winter(data):
    winter = data["NSFW"]["winter"]
    return choose_random_item(list(winter.values()))


def generate_bottomwear(random_bottomwear_type, random_specific_bottomwear, random_bottomwear, data):
    random_color = random_color_chooser(data)
    if random_bottomwear_type == "partial_bottomwear":
        actions = data["NSFW"]["actions"]
        bottomwear_prompt = []
        if random_bottomwear == "skirt":
            random_chosen_skirt_action = choose_random_item(actions["clothing_actions"]["skirt_actions"])
            bottomwear_prompt.append(
                f"BREAK {random_color} {random_bottomwear} BREAK ({random_color} {random_specific_bottomwear}:1.3), {random_chosen_skirt_action}")
        elif random_bottomwear == "jeans":
            random_chosen_jeans_action = choose_random_item(actions["clothing_actions"]["jeans_action"])
            bottomwear_prompt.append(
                f"BREAK {random_color} {random_bottomwear} BREAK ({random_color} {random_specific_bottomwear}:1.3), {random_chosen_jeans_action}")

        else:
            bottomwear_prompt.append(
                f"BREAK {random_color} {random_bottomwear} BREAK ({random_color} {random_specific_bottomwear}:1.3)")

        if random.random() < 0.5:
            bottomwear_prompt.append(choose_random_item(data["legwear"]))
        return bottomwear_prompt
    else:
        return f"BREAK {random_color} {random_bottomwear} BREAK ({random_color} {random_specific_bottomwear}:1.3)"

def main_or_no_prereq_for_leotard(characters):
    main_character = characters["Main_Character"]
    character_without_prereq = characters["without_clothing_prerequisite"]
    if choose_random_item([main_character, character_without_prereq]) == main_character:
        return choose_random_item(list(main_character.values()))
    else:
        return choose_random_item(list(character_without_prereq.values()))


def generate_prompt_Cowboy_Out_Of_Frame_NSFW(data, **kwargs):
    prompt = []
    NSFW = data['NSFW']
    prefix = NSFW["PREFIX"]
    LORA = NSFW['NSFW_LORA']
    LORA_SOLO = LORA['NSFW_LORA_SOLO']
    LORA_SOLO_FRONT = LORA_SOLO['from_front']
    LORA_SOLO_BEHIND = LORA_SOLO['from_behind']
    LORA_TWO = LORA['NSFW_LORA_WITH_BOY']
    appearance = NSFW['appearance']
    camera_angle = data['NSFW']["camera_angle"]
    locations = NSFW["locations"]
    special = NSFW["special"]
    actions = NSFW["actions"]
    attire = appearance["attire"]
    pieces_of_attire = attire["pieces_of_attire"]
    topwear = pieces_of_attire["topwear"]
    topwear_undergarment = topwear["topwear_undergarment"]
    topwear_first_layer = topwear["topwear_first_layer"]
    topwear_second_layer = topwear["topwear_second_layer"]
    bottomwear = pieces_of_attire["bottomwear"]
    full_attire = attire["full_attire"]
    leotard = full_attire["leotard"]
    characters = NSFW["characters"]
    weights = [4, 1]
    random_number_between_half_and_one = round(random.uniform(0.5, 1), 2)
    random_character_for_leotard = main_or_no_prereq_for_leotard(characters)
    user_selected_character = kwargs.get('user_selected_character', None)
    user_selected_first_topwear_layer = kwargs.get('user_selected_first_topwear_layer', None)
    user_selected_second_topwear_layer = kwargs.get('user_selected_second_topwear_layer', None)
    user_selected_full_bottomwear = kwargs.get('user_selected_full_bottomwear', None)
    user_selected_partial_bottomwear = kwargs.get('user_selected_partial_bottomwear', None)
    user_selected_full_attire = kwargs.get('user_selected_full_attire', None)

    user_has_selected_inputs = False

    if user_selected_character is None:
        random_chosen_character = choose_a_character_with_or_without_prereqs(characters)
        user_has_selected_inputs = True
    else:
        random_chosen_character = user_selected_character
    chosen_character = random_chosen_character

    if user_selected_first_topwear_layer is not None:
        topwear_first_layer = user_selected_first_topwear_layer
        user_has_selected_inputs = True

    if user_selected_second_topwear_layer is not None:
        topwear_second_layer = user_selected_second_topwear_layer
        user_has_selected_inputs = True

    if user_selected_full_bottomwear is not None:
        user_has_selected_inputs = True

    if user_selected_partial_bottomwear is not None:
        user_has_selected_inputs = True

    if user_selected_full_attire is not None:
        full_attire = user_selected_full_attire
        user_has_selected_inputs = True

    # For potential IF statements
    if user_selected_partial_bottomwear is not None:
        random_bottomwear_type = "partial_bottomwear"
        random_bottomwear = list(user_selected_partial_bottomwear.keys())[0]
        print(random_bottomwear)
    elif user_selected_full_bottomwear is not None:
        random_bottomwear_type = "full_bottomwear"
        random_bottomwear = list(user_selected_full_bottomwear.keys())[0]
    else:
        random_bottomwear_type = choose_random_item(list(bottomwear))
        random_bottomwear = choose_random_item(list(bottomwear[random_bottomwear_type]))


    # random_location returns: "indoors" or "outdoors"
    random_location = choose_random_item(list(locations))
    special_or_default_location = weighted_choice([locations, special], weights)
    character_with_clothing_predetermined = True

    random_emotion = weighted_emotions(data)

    random_mouth_states = choose_random_item(appearance["face_tags"]["mouth"])
    random_hair_length = choose_random_item(appearance["hair"]["hair_length"])
    random_hair_variant = choose_random_item(appearance["hair"]["hair_variants"])
    random_specific_bottomwear = choose_random_item(bottomwear[random_bottomwear_type][random_bottomwear])

    random_full_attire = choose_random_value_from_dict(full_attire)
    full_attire_or_pieces_of_attire = choose_random_item([full_attire, pieces_of_attire])
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
        data,
        user_selected_second_topwear_layer
    )

    if random.random() < 0.8:
        random_lora_solo = choose_random_value_from_dict(LORA_SOLO_FRONT)
    else:
        random_lora_solo = choose_random_value_from_dict(LORA_SOLO_BEHIND)
    random_lora_two = choose_random_value_from_dict(LORA_TWO)

    random_lora = choose_random_item([random_lora_solo, random_lora_two])

    # Locations
    random_special_full_theme = handle_special_location(special)
    random_location_with_props = handle_locations(random_location, data)
    special_or_regular_location = weighted_choice([random_location, random_special_full_theme], weights=weights)[0]

    # Actions
    random_posture = handle_posture(special_or_regular_location, data)
    random_where_the_character_looks = choose_random_item(actions["general_actions"]["looking"])
    random_hand_actions = choose_random_item(actions["general_actions"]["hand_actions"])

    prompt.append(prefix)
    prompt.append(random_hair_length)
    prompt.append(f"{random_hair_variant}")

    if random.random() < 0.15:
        prompt.append(random_lora)
        prompt.append(chosen_character[1])
        prompt.append(random_location)
        return prompt

    prompt.append(random_emotion)
    prompt.append(random_mouth_states)
    prompt.append(camera_angle)
    if random.random() < 0.3:
        prompt.append(winter(data))

    prompt.append(" BREAK ")
    prompt.append(random_where_the_character_looks)
    if random.random() < 0.1:
        prompt.append(f"<lora:more_details_0.5-1:{random_number_between_half_and_one}>")

    prompt.append(random_posture)

    if chosen_character[0] == "without_clothing_prerequisite" or chosen_character[0] == "Main_Character":
        prompt.append(chosen_character[1])
        character_with_clothing_predetermined = False  # If character has a clothing predetermined, this stays false

    if special_or_default_location == [special] and user_has_selected_inputs == False:
        if character_with_clothing_predetermined:
            prompt.append(random_character_for_leotard)
        prompt.append(random_special_full_theme)
        return prompt

    prompt.append(random_location)
    prompt.append(" BREAK ")
    prompt.append(random_location_with_props)

    if random.random() < 0.33 and character_with_clothing_predetermined == False and user_selected_full_attire is None:  # If character is without clothing prerequisite AND less than 0.3 and not full attire
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

    if user_selected_full_attire is not None:
        prompt.append(random_full_attire)
        return prompt

    if full_attire_or_pieces_of_attire == full_attire:
        prompt.append(f" BREAK ({random_color_chooser(data)} {random_full_attire}:1.3) BREAK ")
    else:
        prompt.append(randomly_selecting_topwear_layers)
        prompt.append(
            generate_bottomwear(random_bottomwear_type, random_specific_bottomwear,
                                random_bottomwear, data))
        prompt.append(
            random_clothing_action(random_bottomwear, random_specific_bottomwear, topwear_first_layer, data))


    return prompt


def generated_prompt(**kwargs):
    data = load_random_json()
    generated_prompt_in_function = generate_prompt_Cowboy_Out_Of_Frame_NSFW(data, **kwargs)
    generated_prompt_in_function = clean_generated_prompt(generated_prompt_in_function, data)
    generated_prompt_in_function = add_space_after_break(generated_prompt_in_function)
    print(generated_prompt_in_function)
    if "<lora:breasts_on_tray:1.3>, breasts on tray, breast rest, tray, holding tray, blush BREAK" in generated_prompt_in_function and random.random() < 0.77:
        generated_prompt_in_function = generated_prompt_in_function.replace(
            "<lora:breasts_on_tray:1.3>, breasts on tray, breast rest, tray, holding tray, blush BREAK", "")
        return generated_prompt_in_function
    else:
        return generated_prompt_in_function

#
i = 1

while i < 2:
    print(generated_prompt())
    i += 1
