import Portfolio
import os
import shutil
import pickle
import datetime as dt



def create_new_user():
    # Creates a username to reference a defined portfolio
    file = open("usernames.txt", "r")
    open_file = file.read()
    file.close()
    name = input("Username:\n" )
    while name in open_file:
        print("Username already taken! Try again.")
        name = input("Username:\n")
    new_file = open("usernames.txt", "w")
    for line in open_file:
        if line != None:
            new_file.write(line)
    new_file.write("\n"+name)
    new_file.close()
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
            shutil.rmtree(user_dir) # Remove the username folder and all associated files
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
    response = input("1) View Current Allocations \n3) Initialize Portfolio \n4) Add/Edit Transactions")
    if response == '1':

        portfolio.get_value(date=dt.date.today(), indiv_print=True) # Returns value by share, total cash, and current total value
        manage_portfolio() # Return to previous menu
    elif response == '2':
        portfolio.get_log()
    elif response == '3':
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
        manage_portfolio()
    elif response == '4':
        response = input("1) Buy  \n2) Sell  \n3) Remove Transaction \n 4) Exit")
        if response == '1':
            keep_adding = True
            while keep_adding:
                stock = input("Add stock ticker:")
                date = input("Add date (mm/dd/yyyy):")
                volume_shares = float(input("Add number of shares:"))
                amount = float(input("Total value:"))
                portfolio.get_share_name_dict()
                share = portfolio.share_names[stock]
                portfolio.cash_bal += amount
                portfolio.buy(share,amount, date, volume_shares)
                exit = input("Buy another stock? y/n")
                if exit == 'n':
                    pickle.dump(portfolio, open(user_dir + '/portfolio', 'wb'))
                    break
            manage_portfolio()
        elif response == '2':
            keep_adding = True
            while keep_adding:
                stock = input("Add stock ticker:")
                date = input("Add date (mm/dd/yyyy):")
                volume_shares = float(input("Add number of shares:"))
                amount = float(input("Total value:"))
                portfolio.get_share_name_dict()
                share = portfolio.share_names[stock]
                portfolio.cash_bal += amount
                portfolio.sell(share, amount, date, volume_shares)
                exit = input("Sell another stock? y/n")
                if exit == 'n':
                    pickle.dump(portfolio, open(user_dir + '/portfolio', 'wb'))
                    break
        elif response == '3':
            keep_adding = True
            while keep_adding:
                log = portfolio.get_log()
                print(log)
                #Need to work out a way to remove a transaction from the log and adjust portfolio as neccesary
                # For example, if we wanted to remove the sale of a stock we would need to remove that entry in to the log
                # and then we would need to add back the amount of stock to the portfolio at the price/volume it was sold for.
                remove = input('Select transaction # to remove/edit or press x to return to previous menu')
                if int(remove) in log.index:
                    transaction_to_remove = log.iloc[int(remove)] # Select the transaction by its index from the full dataframe
                    print(transaction_to_remove)
                    portfolio.get_share_name_dict() # Create the dictionary of share names to share objects
                    confirm = input('1) Remove? 2) Exit')
                    if confirm == '1':
                        share = transaction_to_remove['Share']
                        share = portfolio.share_names[share] # Looks up the share name to the correct share object in the portfolio
                        share_vol = float(transaction_to_remove['Volume'])
                        amount = float(transaction_to_remove['Amount'])
                        if transaction_to_remove['Action'] == 'Buy':
                            portfolio.shares[share] -= share_vol
                            portfolio.cash_bal += amount
                        elif transaction_to_remove['Action'] == 'Sell':
                            portfolio.shares[share] += share_vol
                            portfolio.cash_bal -= amount
                        for key in portfolio.log:
                            portfolio.log[key] = portfolio.log[key].pop(int(remove))
                        #portfolio.log = log.drop(int(remove)).reset_index() # Remove the selected transaction from the dataframe and reset the index
                        # Undo the transaction
                        exit = input("Remove another transaction? y/n")
                        if exit == 'n':
                            pickle.dump(portfolio, open(user_dir + '/portfolio', 'wb'))
                            break
                    elif confirm == '2':
                        break


                    confirm = input('Are you sure you want to remove the transaction')

                        #add code to remove a sale
                elif remove == 'x':
                    break
                else:
                    'Command not recognized'

        elif response == '4':
            manage_portfolio()

if __name__ == "__main__":
    running = True
while running:
    file = open("usernames.txt", "r")
    usernames = file.read()
    file.close()
    response = input("Select User: " + usernames + "\n Or: \n  1) Create New User \n 2) Exit \n")
    if response == '1':
        create_new_user()
    elif response == '2':
        running = False
    elif response in usernames:
        user = str(response)
        user_dir = str("Users/"+user)
        print("Welcome back " + user + "!")
        user_menu()




