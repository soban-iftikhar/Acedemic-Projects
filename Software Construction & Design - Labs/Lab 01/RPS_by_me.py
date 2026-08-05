import random;

exit = False;

while not exit:
    player_choice = input("Press 1 to play rock, 2 to play paper or 3 to play scissors: ");
    computer_choice = random.randint(1, 3);

    # Basic Game Logic
    if player_choice == "1":
        print("You chose rock.");
        if computer_choice == 1:
            print("Computer chose rock. It's a tie!");
        elif computer_choice == 2:
            print("Computer chose paper. Computer wins!");
        else:
            print("Computer chose scissors. You win!");
    elif player_choice == "2":
        print("You chose paper.");
        if computer_choice == 1:
            print("Computer chose rock. You win!");
        elif computer_choice == 2:
            print("Computer chose paper. It's a tie!");
        else:
            print("Computer chose scissors. Computer wins!");
    elif player_choice == "3":
        print("You chose scissors.");
        if computer_choice == 1:
            print("Computer chose rock. Computer wins!");
        elif computer_choice == 2:
            print("Computer chose paper. You win!");
        else:
            print("Computer chose scissors. It's a tie!");
    else:
        print("Invalid choice. Please press 1 to play rock, 2 to play paper or 3 to play scissors");

    # Quit option
    quit_choice = input("Do you want to quit? (y/n): ");
    if quit_choice.lower() == "y":
            exit = True;
            print("Thanks for playing!");
    elif quit_choice.lower() == "n":
            exit = False;
            print("Ready for another round!")
    else:
            print("Invalid input. Continuing the game.");