user_choice = input("Which program should run? Discord/Telegram: ")

if user_choice.lower().title() == "Discord":
    import Discord_bot
elif user_choice.lower().title() == "Telegram":
    import Telegram_bot
else:
    print("Invalid choice. Please enter 'Discord' or 'Telegram'.")
