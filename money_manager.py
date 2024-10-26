import sys

class Record:
    """Represent a record."""
    def __init__(self, category, description, amount):
        self._category = category
        self._description = description
        self._amount = amount

    @property
    def category(self):
        return self._category

    @property
    def description(self):
        return self._description

    @property
    def amount(self):
        return self._amount

    def __repr__(self):
        return f"Record('{self._category}','{self._description}',{self._amount})"

    def __eq__(self, other):
        return self.category == other.category and self.description == other.description \
                and self.amount == other.amount

class Records:
    """Maintain a list of all the 'Record's and the initial amount of money."""
    def __init__(self):
        try: 
            fh = open('records.txt','r')
        except FileNotFoundError: #file does not exist        
            try:
                initial_money = int(input('How much money do you have? '))
            except ValueError: #input string that cannot convert to an integer
                sys.stderr.write('Invalid value for money. Set to 0 by default.\n')
                initial_money = 0
            records = []
        else:
            try:
                str_money = fh.readline()
                initial_money = int(str_money)            
                L = fh.readlines()
                assert str_money != '' #No lines in the file
            except (ValueError, AssertionError): #first line is not an integer, no lines in file, line is not a record
                sys.stderr.write(f'Invalid format in records.txt. Deleting the contents.\n')
                try:
                    initial_money = int(input('How much money do you have? '))
                except ValueError: #(1)input string that cannot convert to an integer
                    sys.stderr.write('Invalid value for money. Set to 0 by default.\n')
                    initial_money = 0
                records = []
            else:
                print('Welcome back!')
                records = [eval(line[:-1]) for line in L] 
            fh.close()
        self._initial_money = initial_money
        self._records = records

    def add(self, add_record, categories):
        try:
            category = add_record.split()[0]
            description = add_record.split()[1]
            amount = int(add_record.split()[2])
            assert len(add_record.split()) == 3 
        except (AssertionError, IndexError): #(3)cannot split into a list of 3 strings
            sys.stderr.write("The format of a record should be like this: meal breakfast -50.\nFail to add a record.\n")
        except ValueError: #(4)cannot be converted to integer
            sys.stderr.write("Invalid value for money.\nFail to add a record.\n")
        else:   
            record = Record(category, description, amount)
            if not categories.is_category_valid(category):
                sys.stderr.write('The specified category is not in the category list.\nYou can check the category \
list by command "view categories".\nFail to add a record.\n')        
            else:
                self._records.append(record)                 

    def view(self):
        money = self._initial_money
        print("Here's your expense and income records:")
        if len(self._records) > 0:
            print(f"{'No.':<5}{'Category':<15}{'Description':<15}{'Amount':>6}")
            print('='*4,'='*14,'='*14,'='*9)       
            for i,j in enumerate(self._records,1):                
                print(f"{i:<5}{j.category:<15}{j.description:<15}{j.amount:<10}")
                money += j.amount
            print('='*45)
        else: 
            print("There is no record yet.")
        print("Now you have %d dollars." % money)       

    def delete(self, del_record):
        if len(self._records) > 0:
            try:
                index = int(del_record.split()[0])
                category = del_record.split()[1]
                description = del_record.split()[2]
                amount = int(del_record.split()[3])
                assert len(del_record.split()) == 4
            except (ValueError, IndexError, AssertionError): #(5)invalid form 
                sys.stderr.write("Invalid format. Fail to delete a record.\nThe format should be like that:\
1 meal breakfast -50\n")
            else:
                record = Record(category, description, amount)
                if (index,record) not in enumerate(self._records,1): #record want to delete does not exit 
                    sys.stderr.write(f'There is no record with "{del_record}". Fail to delete a record.\n')
                else:                
                    self._records.pop(index-1)
        else:
            print("There is no record to delete.")
       
    def find(self, target_categories):  
        target_records = list(filter(lambda x: x.category in target_categories, self._records)) #containing only those records from self._records whose category is present in the target_categories list
        if len(target_records) == 0:
            print(f'There is no record with category "{target_categories[0]}"')
        else:
            print(f'Here\'s your expense and income records under category "{target_categories[0]}":')
            print(f"{'No.':<5}{'Category':<15}{'Description':<15}{'Amount':>6}")
            print('='*4,'='*14,'='*14,'='*9)       
            sub_money = 0
            for i,j in enumerate(self._records,1):
                if j in target_records:
                    print(f"{i:<5}{j.category:<15}{j.description:<15}{j.amount:<10}")
                    sub_money += j.amount
            print('='*45)
            print(f"The total amount above is {sub_money}.")

    def save(self):
        with open('records.txt','w') as fh_record:        
            fh_record.write(str(self._initial_money))
            fh_record.write('\n')            
            for i in self._records:
                fh_record.write(str(i))
                fh_record.write('\n')

class Categories:
    """Maintain the category list and provide some methods."""
    def __init__(self):
        self._categories = ['expense', ['food', ['meal', 'snack', 'drink'], \
                            'transportation', ['bus', 'railway']], \
                            'income',['salary', 'bonus']]
                            
    def view(self):
        def view_categories(categories, level = 0):
            if type(categories) == list:
                for i in categories: 
                    view_categories(i,level+1)
            else:
                print(f'{" "*2*level}- {categories}')  
        view_categories(self._categories)
      
    def is_category_valid(self, category):
        def recursion_check(L, category):
            if type(L) == list: 
                for i in L: 
                    p = recursion_check(i, category)
                    if p == True:
                        return True
                return False
            else:
                return L == category            
        return recursion_check(self._categories, category)
            
    def find_subcategories(self, category):
        def find_subcategories_gen(category, categories, found = False):
            if type(categories) == list:
                for index, child  in enumerate(categories):
                    yield from find_subcategories_gen(category, child, found) #recursive traversal, If an item is a list, it recursively calls itself with that sublist. This recursion continues until it reaches the deepest level of subcategories.
                    if child == category and index + 1 < len(categories) and \
                       type(categories[index+1]) == list: # When the generator encounters a category (a string) instead of a sublist, it compares the category with the provided category argument. If the category matches or if it's already found a match (denoted by the found flag), it yields the category.               
                        yield from find_subcategories_gen(category,categories[index+1],True) #: The found flag is used to indicate if the desired category has been found. Once the desired category is found, the found flag is set to True, and subsequent categories encountered are considered subcategori
            else:
                if categories == category or found == True: #If a category matches the desired category or if it's marked as a subcategory (due to the flag), it yields that category.
                    yield categories            
        return list(find_subcategories_gen(category, self._categories))
        
categories = Categories()
records = Records()

while True:
    command = input('\nWhat do you want to do (add / view / delete / view categories / find / exit)? ')
    if command == 'add':
        record = input('Add an expense or income record with category, \
description, and amount (separate by space): \n')
        records.add(record, categories)
    elif command == 'view':
        records.view()
    elif command == 'delete':
        delete_record = input("Which record do you want to delete? ")
        records.delete(delete_record)
    elif command == 'view categories':
        categories.view()
    elif command == 'find':
        category = input('Which category do you want to find? ')
        target_categories = categories.find_subcategories(category)        
        records.find(target_categories)
    elif command == 'exit':
        records.save()
        break
    else:
        sys.stderr.write('Invalid command. Try again.\n')
