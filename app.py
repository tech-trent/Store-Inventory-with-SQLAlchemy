
import csv
import datetime

from peewee import *

db = SqliteDatabase("inventory.db")

class Product(Model):
    
    # The database model used for this project    
    product_id = PrimaryKeyField()
    product_name = TextField(unique = True)
    product_quantity = IntegerField()
    product_price = IntegerField()
    date_updated = DateTimeField()

    class Meta:
        database = db

def make_datetime(string):
    
    # Formats a string in mm/dd/yyyy format into a datetime   
    return datetime.datetime.strptime(string, "%m/%d/%Y")

def dollars_to_cents(string):
    
    # Removes any non-numeric characters (like "$" and ".") for the purpose of returning the number of cents.
    if len(string) > 2:
        return "".join([char for char in string if char.isnumeric()])
    else:
        raise ValueError

def cents_to_dollars(string):
    
    #Converts any number of cents into dollars
    if len(string) < 3:
        zfilled = string.zfill(3)
        return f"${zfilled[0]}.{zfilled[1:]}"
    else:
        return f"${string[:-2]}.{string[-2:]}"

def overwrite_prompt(Id):
    
    # Asks the user if they want to overwrite the existing record at the given ID.
    if input(f"\nRecord already exists. Overwrite existing record? (ID: {Id}) (Y/N) ").lower().strip() != "n":
        return True
    else:
        return False
    

def add_or_update(name, quant, price, date, alert = False):

    # Adds the given data to the database, or, if the name is already taken (which is the only way to raise an
    # integrity error in this case) overwrite the entry that took that name with new, user-defined data.
    # The alert boolean is only set to true if we want to alert the user that they're overwriting en existing
    # record. Alerts are disabled when this function is used to upload data from the CSV file.
    
    try:
        Product.create(
            product_name = name,
            product_quantity = quant,
            product_price = price,
            date_updated = date
        )
        if alert:
            print(f"\nProduct stored with ID number {len(Product.select())}")
    except IntegrityError:
        for old_product in Product.select():
            if name == old_product.product_name and date > old_product.date_updated:
                update = Product.update(
                    product_name = name,
                    product_quantity = quant,
                    product_price = price,
                    date_updated = date
                ).where(Product.product_id == old_product.product_id)
                if not alert:
                    update.execute()
                elif overwrite_prompt(old_product.product_id):
                    update.execute()
                    print("Record overwritten.")

def read_csv(filepath):

    # Function to read the CSV into my database.
    # If this raises an integrity error, we assume it's because multiple entries created at different times exist for
    # the same product. If so, the newer data overwrites the old, as shown by the datetime comparison in the error
    
    with open(filepath) as file:
        reader = csv.reader(file)
        rows = list(reader)
        for row in rows[1:]:
            add_or_update(row[0], row[2], dollars_to_cents(row[1]), make_datetime(row[3]))

def get_by_id(ID):
    
    # V OPTION:

    # Prints out information on a given product after the user enters said product's unique product ID.
    # Index and value errors are handled.   
    # The function returns True or None as an indicator of the input's validity, which will determine
    # if the V-option's new loop needs to re-run or not.
    
    try:
        true_ID = abs(int(ID))
        product_at_ID = Product.select().order_by(Product.product_id)[true_ID - 1]
        if product_at_ID:
            price = str(product_at_ID.product_price)
            print(f"\nItem ID {true_ID}:\n{product_at_ID.product_name}\nIn stock:\t\t{product_at_ID.product_quantity}\nPrice:\t\t\t{cents_to_dollars(price)}\nRecord last updated:\t{datetime.datetime.strftime(product_at_ID.date_updated, '%m/%d/%Y')}")
            return True
        else:
            raise ValueError
    except IndexError:
        print("\nID number too high. Please use a number no higher than the number of database records.")
    except ValueError:
        print("\nPlease type a whole number.")

def add_record():

    # A OPTION:

    # Lets the user add a record to the database. If the name the user chose for the record conflicts with existing
    # data, the newer of the two will replace the older. If an integrity error occurs for any other reason, such
    # as the user entering a null value, their input will be disregarded.
    # Float rather than int is used for product quantity, in case the product is being sold by pounds, ounces, etc.

    try:
        name = input("\nWhat is the name of the product?\t\t").title()
        if not len(name):
            raise ValueError
        add_or_update(
            name,
            abs(float(input("How much of the product is on hand?\t\t"))),
            abs(int(input("How much does a single unit cost, in cents?\t"))),
            datetime.datetime.today(),
            True
        )

    except ValueError:
        print("\nInvalid entry. Ensure the name isn't empty, the quantity is a number, and the price is in cents (type $1.23 as 123)")

def backup():

    # B OPTION:
    # Backs up the existing database to a new CSV.

    with open("backup.csv", "w+", newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(["product_id", "product_name", "product_quantity", "product_price", "date_updated"])
        for product in Product.select().order_by(Product.product_id):
            writer.writerow([product.product_id, product.product_name, product.product_quantity, product.product_price, datetime.datetime.strftime(product.date_updated, "%Y-%m-%d %H:%M:%S")])
    print("\nBackup successful. File name: backup.csv")

if __name__ == "__main__":
    db.connect()
    db.create_tables([Product], safe = True)
    read_csv("inventory.csv")
    option = None
    while not option == "q":
        option = input("\nV) View a record using its ID number\nA) Add a product to the inventory database\nB) Back up the database to a CSV file\nQ) Quit\n\nWhat would you like to do? ").lower().strip()
        if option == "v":

            # New loop to continue asking for user's input until it becomes usable by the program
            while not get_by_id(input("\nProduct ID number: ")):
                pass
        elif option == "a":
            add_record()
        elif option == "b":
            backup()
        elif option != "q":
            print("\nPlease enter V, A, B or Q. All actions are described in the following menu:")

    # Q OPTION
    
    print("\nThank you for using the database program! Have a nice day!")
    
    # Since time.sleep is only used in this very specific instance at the end of my code, I chose to import it here for its first and only use.
    from time import sleep 
    sleep(3)
    quit()
