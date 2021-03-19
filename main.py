import Portfolio


def create_new_user():
    file = open("usernames.txt", "r")
    name = input("Username:\n" )
    while name in file.read():
        print("Username already taken! Try again.")
        name = input("Username:\n")
    file = open("usernames.txt", "a")
    file.write("\n"+name)
    file.close()


def user_menu():
    response = input("1) Analyze Portfolio \n 2) Manage Portfolio \n 3) Switch User \n 4) Delete User")
    if response == '1':
        print("Sorry, don't have that functionality yet")
        user_menu()
    elif response == '2':
        print("Sorry, don't have that functionality yet")
        user_menu()
    elif response == '3':
        print("Returning to main menu...")
    elif response == '4':
        confirm = input('Are you sure you want to delete the profile:' + user+"?\n y/n" )
        if 'y' in confirm:
            with open("usernames.txt", "r") as file:
                lines = file.readlines()
            file.close()
            with open("usernames.txt", "w") as new_file:
                for line in lines:
                    if not line.startswith(user):
                        new_file.write(line)
            new_file.close()
        else:
            user_menu()




if __name__ == "__main__":
    running = True
while running:
    file = open("usernames.txt", "r")
    usernames = file.read()
    file.close()
    response = input("Select User: \n" + usernames + "\n Or: \n  1) Create New User \n 2) Exit \n")
    if response == '1':
        create_new_user()
    elif response == '2':
        running = False
    elif response in usernames:
        user = str(response)
        print("Welcome back " + response + "!")
        user_menu()




