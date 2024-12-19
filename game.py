import random
import time

class Game:
    def __init__(self):
        self.state_label = 'not started'
        self.state = 'initialized'
        self.year = 2025
        self.company1 = Company()
        self.company2 = Company()

        # Seed the random number generator with the current time
        random.seed(time.time())

        self.last_player = random.randint(1, 2)
        self.start_player = self.last_player # Needed to let each round be started by different player

    def calculate_revenue(self):
        if self.company1.price > self.company2.price:
            winner = self.company2
            loser = self.company1
        elif self.company1.price < self.company2.price:
            winner = self.company1
            loser = self.company2
        elif self.company1.price == self.company2.price:
            if self.last_player == 1:
                winner = self.company2
                loser = self.company1
            elif self.last_player == 2:
                winner = self.company1
                loser = self.company2
            else:
                raise Exception("Sorry, last turn value should be 1 or 2.") 
            
        else:
            raise Exception("Sorry, prices should be either equal or one should be higher.")
        
        new_capital_winner = winner.capital + (100-loser.loyals)*winner.price
        new_capital_loser = loser.capital + loser.loyals*loser.price
        winner.set_capital(new_capital_winner)
        loser.set_capital(new_capital_loser)

    def get_next_player_index(self):
        return(int(self.last_player == 1))
    
    def set_last_player(self):
        self.last_player = 2 if self.last_player == 1 else 1
    
    def set_next_state(self, decision = None):
        match self.state:
            case 'initialized':
                self.state = 'loyals1'
            case 'loyals1':
                self.state = 'loyals2'
            case 'loyals2':
                self.state = 'first_bid1'
            case 'first_bid1':
                self.state = 'first_bid2'
            case 'first_bid2':
                if self.company1.last_decision or self.company2.last_decision:
                    self.state = 'bid'
                else:
                    self.state = 'wrap_up'
            case 'bid':
                if self.company1.price == 10 and self.company2.price == 10:
                    print("Hey ganz schön niedrig")
                    self.state = 'wrap_up'
                elif not decision:
                    print("Decision: ", decision)
                    self.state = 'wrap_up'
                else:
                    self.state = 'bid'

    def get_modal_data(self):
        print(self.state)

        match self.state:
            case state if state in ['loyals1', 'loyals2']:
                return({'message': 'Do you want to get 30 loyal customers for this year for an investment of 250 €?', 'choices': ['Yes', 'No']})
            case state if state in ['first_bid1', 'first_bid2', 'bid']:
                    return({'message': 'Do you want to lower your price per unit?', 'choices': ['Yes', 'No']})
            case 'wrap_up':
                return({'message': 'Look at the revenue made.', 'choices': []})

    def resolve_decision(self, decision, player):
        company = self.company1 if player == 1 else self.company2

        match self.state:
            case state if state in ['loyals1', 'loyals2']:
                if decision:
                    company.get_loyals()
            case state if state in ['first_bid1', 'first_bid2', 'bid']:
                if decision:
                    company.decrease_price()
                    company.last_decision = decision
            
        self.set_last_player()

class Company:
    def __init__(self):
        self.capital = 500
        self.loyals = 0
        self.price = 50
        self.last_decision = False

    def decrease_price(self):
        if self.price > 10:
            self.price = self.price - 10

    def set_capital(self, new_value):
        self.capital = new_value

    def get_loyals(self):
        if self.loyals == 0:
            self.loyals = 30
            self.capital = self.capital - 250