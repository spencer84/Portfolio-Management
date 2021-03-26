import Portfolio
import os
import pickle
import datetime as dt



def create_new_user():
    # Creates a username to reference a defined portfolio
    file = open("usernames.txt", "r")
    name = input("Username:\n" )
    while name in file.read():
        print("Username already taken! Try again.")
        name = input("Username:\n")
    file = open("usernames.txt", "a")
    file.write("\n"+name)
    file.close()
    # Add sub-folder to the 'Users' folder
    try:
        os.mkdir("Users/"+name)
    except FileExistsError:
        print("Directory " , name ,  " already exists")


def user_menu():
    response = input("1) Analyze Portfolio \n 2) Manage Portfolio \n 3) Switch User \n 4) Delete User")
    if response == '1':
        print("Sorry, don't have that functionality yet")
        user_menu()
    elif response == '2':
        manage_portfolio()
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

# Create a sub-menu for analyzing the portfolio

# Create a sub-menu for managing the portfolio
def manage_portfolio():
    # Retrieve the portfolio object / identify if one exists
    try:
        portfolio = pickle.load(open(user_dir+'/portfolio', 'rb'))
    except (FileNotFoundError,EOFError):
        proceed = input('No portfolio exists for this user--create one? y/n')
        if proceed == 'y':
            portfolio = Portfolio.Portfolio(shares={})
            pickle.dump(portfolio,open(user_dir+'/portfolio', 'wb'))
    # Set up a sub-menu for management options
    # Pull up a view of the current distribution
    response = input("1) View Current Allocations \n2) Initialize Portfolio \n3) Add/Edit Transactions")
    if response == '1':
        portfolio.get_asset_values(date=dt.date.today())
        print(portfolio.asset_values)
        # Get a breakdown of all assets, rather than just an equity/bond allocation
        manage_portfolio() # Return to previous menu
    elif response == '2':
        keep_adding = True
        shares = {}
        while keep_adding:
            stock = input("Add stock ticker:")
            date = input("Add date (mm/dd/yyyy):")
            volume_shares = input("Add number of shares:")
            amount = input("Total value:")
            shares[stock] = [date, volume_shares, amount]
            exit = input("Add another stock? y/n")
            if exit == 'n':
                portfolio.manual_setup(shares)
                pickle.dump(portfolio, open(user_dir + '/portfolio', 'wb'))
                # Overwrite the portfolio with the new allocations

                break

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
        user_dir = str("Users/"+user)
        print("Welcome back " + user + "!")
        user_menu()




