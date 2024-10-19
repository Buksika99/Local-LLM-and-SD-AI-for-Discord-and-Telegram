Run a Telegram or Discord AI chatbot locally. It requires KoboldAI, AUTOMATIC1111, some sort of Large Language Model, and Stable Diffusion model.

Running such a program locally can be extremely resource hungry on your PC, mainly your GPU. If you have 8GB or less VRAM, I'd advise you to use either KoboldAI or AUTOMATIC1111 through Google Colab.

First, install the requirements. One way to do this is to navigate to the downloaded folder with your Commandprompt or PowerShell, and run the line "pip install -r requirements.txt".

Edit the .env file with your API's and chat ID's, and even though it's meant to be used locally, you can use Google Colab as an endpoint for KoboldAII or AUTOMATIC1111, or even both.
Edit the JSON files as you seem fit.
Fill out the Character's JSON file accordingly as well and rename it to whatever you want your AI's personality to be called. You can create multiple personalities, the code supports that.

Inside 'Discord.py' rename the 'YOUR_NAME = "YOUR NAME"' line, and insert your own name/nickname into it. After a while when the AI references you, it will call you this name.

Functionalities of this bot:
On Telegram use the /help command, which will give you the currently available commands, and to get more info on a specific command use e.g: /change_character a. This should return something like "a was not found within available characters. Available characters:..."
If an SD model is not installed, it will use the currently selected model instead.

If the code is ran 24/7, the AI could message you randomly throughout the day, either initiating a new conversation or expanding on the last one.
You could say "take a pic", "take a picture", "take a selfie" or something of sorts, the important part is that the words are followed as such, lower/upper case doesn't matter. For example: "AI, if you could, would you tAkE a Picture?". This should prompt the AI to send you a picture.
Bad example: "AI, a picture! Could you take one?". This will not prompt the AI to send you a picture.

Same thing applies for the Discord part of this bot, however it's still in developement, not as complete as the Telegram part. For example, there is no "help" command built in yet or "take a selfie".
For discord commands, it is not "/" like with Telegram, but "!". So instead of "/change_character", it is !change_character".

"take a selfie"'s character for now is "hard coded", if you want you need to manually rewrite that part of the code.

Executable.py is currently under works, future function will be an "exe" to be run, prompting you if you want to use EITHER Telegram or Discord.

