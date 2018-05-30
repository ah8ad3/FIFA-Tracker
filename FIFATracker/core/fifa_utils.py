from datetime import date, timedelta

def get_team_name(all_teams, teamid):
    for t in all_teams:
        if int(t['teamid']) == int(teamid):
            return t['teamname']
            
class FifaDate():

    def convert_days_to_py_date(self, days):
        """Convert birthdate or playerjointeamdate into python datetime.date format."""

        return date(year=1582, month=10, day=14) + timedelta(days=int(days))

    def convert_to_py_date(self, fifa_date):
        """Convert FIFA Date format into python datetime.date format."""
        fifa_date = str(fifa_date)
        if len(fifa_date) == 4:
            # Date contains only year 
            return date(year=int(fifa_date), month=7, day=1)
        elif len(fifa_date) == 8:
            return date(int(fifa_date[:4]), int(fifa_date[4:6]), int(fifa_date[6:]))  
        else:
            return date(year=2017, month=7, day=1)

    def convert_age_to_birthdate(self, current_date, age):
        """Convert Player Age to birthdate for futher database query"""

        start_date = date(year=1582, month=10, day=14)
        current_date = self.convert_to_py_date(fifa_date=current_date)

        birthdate = date(year=current_date.year - int(age), month=current_date.month, day=current_date.day) 
        return (birthdate - start_date).days

    def convert_to_fifa_date(self, current_date):
        """Return days since 14.10.1582 to current date"""
        start_date = date(year=1582, month=10, day=14)
        current_date = self.convert_to_py_date(fifa_date=current_date)
        return (current_date - start_date).days

class PlayerAge():
    def __init__(self, birth_date=141279, current_date=20170701):
        self.birth_date = FifaDate().convert_days_to_py_date(days=birth_date)
        self.current_date = FifaDate().convert_to_py_date(fifa_date=current_date)
        self.age = self.get_age()

    def get_age(self):
        """returns age of your player"""
        return self.current_date.year - self.birth_date.year - ((self.current_date.month, self.current_date.day) < (self.birth_date.month, self.birth_date.day))


class PlayerWage:
    # All modifiers are defined in "playerwage.ini", "PlayerWageDomesticPrestigeMods.csv" and "PlayerWageProfitabilityMods.csv"
    def __init__(self, ovr = 0, age = 0, posid = 0, player_team = None, currency=1):
        if player_team:
            self.ovr = ovr
            self.age = age
            self.posid = posid
            self.leagueid = player_team['league']['leagueid']
            self.club_domestic_prestige = player_team['team']['domesticprestige']
            self.club_profitability = player_team['team']['profitability']
            '''
            print('----------class PlayerWage--------------')
            print(self.leagueid)
            print(self.club_domestic_prestige )
            print(self.club_profitability)
            '''

            '''
            [CONVERSION]
            USDOLLAR = 1.12
            EURO = 1.0
            POUND = 0.88
            '''
            currency_conversion = (1.12, 1.0, 0.88)
            try:
                self.currency = currency_conversion[currency]
            except IndexError:
                self.currency = currency_conversion[1] # Euro

            self.wage = self._calculate_player_wage()
        else:
            self.wage = 500
        self.formated_wage = "{:,}".format(self.wage)

    def _calculate_player_wage(self):
        league_mod = self._ovr_factor(self.ovr) * self.currency * ( self._league_factor(self.leagueid) * self._domestic_presitge(self.leagueid, self.club_domestic_prestige) * self._profitability(self.leagueid, self.club_profitability))
        age_mod = (league_mod * self._age_factor(self.age)) / 100.00
        pos_mod = (league_mod * self._position_factor(self.posid)) / 100.00

        player_wage = int(self._round_to_player_wage(league_mod + age_mod + pos_mod))

        if player_wage < 500:
            player_wage = 500
        return player_wage

    def _league_factor(self, leagueid):
        factors = {
            13: 70,     # England Premier League
            53: 43,     # Spain Primera
            31: 45,     # Italy Serie A
            19: 50,     # Germany Bundesliga 1
            16: 40,     # France Ligue 1
            10: 22,     # Netherlands
            14: 30,     # England Championship
            20: 20,     # Germany Bundesliga 2
            83: 8,      # Korea
            308: 18,    # Portugal
            54: 12,     # Spain Segunda A
            56: 8,      # Sweden
            189: 20,    # Switzerland
            39: 15,     # MLS
            17: 10,     # France Ligue 2
            341: 25,    # Mexico
            335: 6,     # Chile
            336: 4,     # Colombia
            67: 33,     # Russia
            80: 22,     # Austria
            4: 21,      # Belgium
            1: 20,      # Denmark
            41: 10,     # Norway
            68: 32,     # Turkey
            60: 8,      # England League One
            66: 13,     # Poland
            350: 25,    # Saudi Arabia
            351: 8,     # Australia
            353: 15,    # Argentina
            61: 8,      # England League Two
            50: 10,     # Scotland
            65: 3,      # Ireland
            7: 15,      # Brazil
            349: 14,    # Japan J1
        }

        try:
            return factors[leagueid]
        except KeyError:
            return 20   # Default League Modifier

    def _ovr_factor(self, ovr):
        factors = (20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 45, 45, 45, 45, 45, 45, 45, 45, 45, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 60, 60, 60, 60, 60, 60, 80, 80, 80, 120, 120, 120, 250, 250, 250, 300, 300, 300, 420, 420, 420, 500, 500, 500, 600, 600, 600, 650, 650, 850, 850, 1000, 1000, 1300, 1300, 1300, 1800, 1800, 2000, 2000, 2000, 3000, 3000, 5000, 5000, 5000)
        try:
            return factors[ovr]
        except IndexError:
            return 0

    def _age_factor(self, age):
        factors = (-60, -60, -60, -60, -60, -60, -60, -60, -60, -60, -60, -60, -60, -60, -60, -60, -60, -35, -35, -35, -10, -10, 0, 0, 0, 10, 15, 15, 20, 20, 15, 15, 15, 15, 15, -15, -15, -15, -15, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20)
        try:
            return factors[age]
        except IndexError:
            return 0

    def _position_factor(self, posid):
        factors = (-30, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, 0, 0, 0, 0, 0, 0, 0, 0 , 10, 10, 10, 10, 10, 10, 10, 10)
        try:
            return factors[posid]
        except IndexError:
            return factors[0]

    def _domestic_presitge(self, leagueid, club_domestic_prestige):
        domestic_prestige_table = {
            0: (0,1.2,1.2,1.4,1.4,1.5,1.8,1.8,1.8,2,2,),                     
            13: (0,1,1,1.1,1.1,1.3,1.3,1.5,1.6,1.6,1.7,), 
            53: (0,0.8,0.8,0.8,0.9,0.9,0.9,1,1,1.5,3.5,), 
            31: (0,0.7,0.8,1,1,1.5,1.5,1.6,1.7,1.7,2,), 
            19: (0,1,1,1,1.1,1.1,1.1,1.4,1.2,1.6,2,), 
            16: (0,1,1,1.2,1.2,1.3,1.3,1.4,1.5,1.6,1.6,), 
            10: (0,1,1,1,1,1.1,1.1,1.2,1.2,1.5,1.5,), 
            14: (0,0.8,0.8,1,1,1.8,1.8,1.8,1.8,2.2,2.2,), 
            20: (0,1.2,1.2,1.4,1.4,1.5,1.8,1.8,1.8,2,2,), 
            32: (0,1,1,1,1.1,1.1,1.1,1.2,1.2,1.2,1.2,), 
            83: (0,1.4,1.4,1.5,1.5,1.5,1.6,1.6,1.6,2,2,), 
            308: (0,1,1,1.1,1.1,1.2,1.2,1.3,1.3,1.4,1.4,), 
            54: (0,1.1,1.1,1.2,1.2,1.3,1.3,1.4,1.4,1.5,1.5,), 
            56: (0,1,1,1.2,1.2,1.4,1.4,1.5,1.5,2,2,), 
            189: (0,1,1,1,1,1.3,1.3,1.6,1.6,1.8,1.8,), 
            39: (0,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,), 
            17: (0,1.1,1.1,1.2,1.2,1.3,1.3,1.4,1.4,1.5,1.5,), 
            341: (0,1,1,1,1,1.5,1.5,2,2,2.5,2.5,), 
            335: (0,1.5,1.5,1.5,1.5,1.5,1.6,1.8,2,2,2.3,), 
            336: (0,1.2,1.2,1.2,1.2,1.4,1.4,2,2.5,2.5,3,), 
            67: (0,1,1,1,1.2,1.2,1.2,1.4,1.4,1.6,1.8,), 
            80: (0,1.2,1.2,1.2,1.4,1.4,1.6,1.7,1.7,1.8,1.8,), 
            4: (0,1.2,1.2,1.2,1.4,1.4,1.4,1.5,1.5,2,2,), 
            1: (0,1.2,1.2,1.2,1.4,1.4,1.4,1.5,1.5,2,2,), 
            41: (0,1,1,1,1.1,1.1,1.2,1.2,1.2,1.5,1.5,), 
            68: (0,1,1,1,1,1.2,1.2,1.6,1.6,2,2,), 
            60: (0,1.8,1.8,1.8,2.1,2.1,2.1,2.3,2.3,2.5,2.5,), 
            66: (0,1,1,1.2,1.3,1.3,1.6,1.6,1.8,1.8,1.8,), 
            350: (0,1.2,1.2,1.2,1.4,1.4,1.6,1.8,2,2,2,), 
            351: (0,1,1,1,1,1.2,1.2,1.4,1.4,1.4,1.4,), 
            353: (0,2,2,2,2,2.2,2.2,2.4,2.4,2.6,2.6,), 
            61: (0,2,2,2,2.5,2.5,2.5,3,3,3,3,), 
            50: (0,1,1,1,1,1,1,1,1,5,5,), 
            65: (0,1.5,1.5,1.5,1.7,1.7,1.7,2,2,2,2,), 
            7: (0,2,2,2,2,2.2,2.6,3,3.2,3.2,3.2,), 
            349: (0,1.2,1.2,1.2,1.4,1.4,1.6,1.8,2,2,2,), 
            2076: (0,1.2,1.2,1.4,1.4,1.5,1.8,1.8,1.8,2,2,),
        }
        
        try:
            return domestic_prestige_table[leagueid][club_domestic_prestige]
        except KeyError:
            return domestic_prestige_table[0][0]

    def _profitability(self, leagueid, club_profitability):
        profitability_table = {
            0: (0,1.5,1.5,1.4,1.4,1.2,1.2,1.1,1.1,1,1,), 
            13: (0,1.6,1.6,1.5,1.5,1.3,1.3,1,1,1,1,), 
            53: (0,1.5,1.5,1.5,1.4,1.4,1.2,1.2,1,0.8,0.8,), 
            31: (0,2,1.8,1.4,1.4,1.2,1,0.9,0.8,0.8,0.7,), 
            19: (0,1.5,1.5,1.5,1.2,1.2,1,1,1,1,1,), 
            16: (0,2,1.8,1.8,1.5,1.2,1,1,1,0.8,0.8,), 
            10: (0,1.5,1.5,1.3,1.2,1.1,1,1,0.9,0.8,0.8,), 
            14: (0,1.8,1.8,1.6,1.6,1.3,1.3,1.1,1.1,0.8,0.8,), 
            20: (0,1.6,1.6,1.5,1.5,1.4,1.2,1.1,0.8,0.7,0.7,), 
            32: (0,1.1,1.1,1,1,1,0.9,0.9,0.8,0.8,0.8,), 
            83: (0,1.6,1.6,1.5,1.5,1.4,1.4,1.2,1.2,1,1,), 
            308: (0,1.5,1.5,1.3,1.3,1.1,1.1,1,1,0.8,0.8,), 
            54: (0,1.6,1.6,1.5,1.5,1.4,1.4,1.3,1.3,1.2,1.2,), 
            56: (0,1.5,1.5,1.4,1.4,1.2,1.2,1.1,1.1,1,1,), 
            189: (0,2,2,1.5,1.5,1.3,1.3,1,1,1,1,), 
            39: (0,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,), 
            17: (0,1.6,1.6,1.5,1.5,1.4,1.4,1.3,1.3,1.2,1.2,), 
            341: (0,2,1.8,1.6,1.4,1.2,1.2,1,1,0.8,0.8,), 
            335: (0,2,2,2,2,1.4,1.4,1.2,1.2,1,1,), 
            336: (0,1.1,1.1,1.1,1.1,1,1,1,0.8,0.8,0.8,), 
            67: (0,2,2,1.8,1.8,1.7,1.7,1.7,1.4,1.4,1.4,), 
            80: (0,1.8,1.8,1.6,1.4,1.2,1,1,1,0.8,0.8,), 
            4: (0,1.4,1.4,1.2,1.1,1.1,1.1,1.1,1.1,1,1,), 
            1: (0,1.4,1.4,1.2,1.1,1.1,1.1,1.1,1.1,1,1,), 
            41: (0,1.2,1.2,1.2,1.1,1.1,1.1,1,1,1,1,), 
            68: (0,1.8,1.8,1.6,1.4,1.2,1,1,1,1,1,), 
            60: (0,1.6,1.6,1.6,1.5,1.5,1.5,1.4,1.4,1,1,), 
            66: (0,1.2,1.2,1,1,1,1,0.9,0.9,0.8,0.8,), 
            350: (0,1.5,1.5,1.5,1.5,1.5,1.5,1.3,1.2,1,1,), 
            351: (0,2.5,2.5,2,2,1.5,1.5,1,1,1,1,), 
            353: (0,1.2,1.2,1.1,1.1,1,1,0.9,0.9,0.8,0.8,), 
            61: (0,1.8,1.8,1.8,1.8,1.8,1.5,1.5,1.5,1.5,1.5,), 
            50: (0,2,2,2,2,2,1.8,1.8,1.8,1.8,1.8,), 
            65: (0,1.6,1.6,1.6,1.5,1.5,1.5,1.4,1.4,1.3,1.3,), 
            7: (0,1.5,1.5,1.5,1.2,1.2,1.2,1.2,1,1,1,), 
            349: (0,1,1,1,1,0.8,0.8,0.7,0.7,0.7,0.7,), 
            2076: (0,1.6,1.6,1.5,1.5,1.4,1.2,1.1,0.8,0.7,0.7,),
        } 
    
        try:
            return profitability_table[leagueid][club_profitability]
        except KeyError:
            return profitability_table[0][0]

    def _round_to_player_wage(self, summed_wage):
        divisor = 0
        if summed_wage <= 1000.00:
            divisor = 50
        elif summed_wage <= 10000.00:
            divisor = 100
        elif summed_wage <= 50000.00:
            divisor = 500
        elif summed_wage <= 100000.00:
            divisor = 1000
        elif summed_wage <= 200000.00:
            divisor = 5000
        elif summed_wage <= 1000000.00:
            divisor = 10000
        elif summed_wage <= 5000000.00:
            divisor = 50000
        else:
            divisor = 100000
        
        reminder = summed_wage % divisor
        if reminder >= divisor / 2:
            return summed_wage + (divisor - reminder)
        else:
            return summed_wage - reminder
    

class PlayerValue:
    # All modifiers are defined in "playervalues.ini"
    def __init__(self, ovr=0, pot=0, age=0, posid=0, currency=1, value=None):
        if value:
            self.value = value
            self.formated_value = "{:,}".format(self.value)
        else:
            self.ovr = int(ovr)
            self.pot = int(pot)
            self.age = int(age)
            self.posid = int(posid)
            '''
            [CONVERSION]
            USDOLLAR = 1.12
            EURO = 1.0
            POUND = 0.88
            '''
            currency_conversion = (1.12, 1.0, 0.88)
            try:
                self.currency = currency_conversion[int(currency)]
            except IndexError:
                self.currency = currency_conversion[1] # Euro

            self.value = self._calculate_player_value()
            self.formated_value = "{:,}".format(self.value)

    def _calculate_player_value(self):
        basevalue = self._ovr_factor(self.ovr) * self.currency
        pos_mod = basevalue * self._position_factor(self.posid)
        pot_mod = basevalue * self._pot_factor(self.pot - self.ovr)
        age_mod = basevalue * self._age_factor(self.age, self.posid)
        player_value = self._sum_factors(basevalue, pos_mod, pot_mod, age_mod)

        if player_value < 0:
            player_value = basevalue/10

        if player_value < 1000:
            player_value = 10000 # Player value can't be lower than 10 000    

        return int(player_value)

    def _round_to_player_value(self, summed_value):
        divisor = 0
        if summed_value <= 5000.00:
            divisor = 50
        elif summed_value <= 10000.00:
            divisor = 1000
        elif summed_value <= 50000.00:
            divisor = 5000
        elif summed_value <= 250000.00:
            divisor = 10000
        elif summed_value <= 1000000.00:
            divisor = 25000
        elif summed_value <= 5000000.00:
            divisor = 100000
        else:
            divisor = 500000
        
        reminder = summed_value % divisor
        if reminder > divisor / 2:
            return summed_value + (divisor - reminder)
        else:
            return summed_value - reminder

    def _ovr_factor(self, ovr):
        factors = (1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 15000, 15000, 15000, 15000, 15000, 15000, 15000, 15000, 15000, 15000, 20000, 25000, 34000, 40000, 46000, 54000, 61000, 70000, 86000, 105000, 140000, 170000, 205000, 250000, 305000, 365000, 435000, 515000, 605000, 710000, 1200000, 1600000, 2100000, 2700000, 3800000, 4500000, 5200000, 6000000, 7000000, 8500000, 10000000, 12000000, 15000000, 17500000, 21000000, 26000000, 30000000, 34000000, 40000000, 45000000, 52000000, 60000000, 68000000, 75000000, 83000000, 90000000, 110000000, 120000000, 140000000, 150000000, 200000000)
        try:
            return factors[ovr]
        except IndexError:
            return 0

    def _position_factor(self, posid):
        factors = (-40, -15, -18, -18, -15, -15, -15, -18, -18, -15, -15, -15, 15, 12, 12, 12, 15, 15, 15, 15, 18, 18, 18, 15, 18, 18, 18, 15)
        try:
            return (factors[posid] / 100)
        except IndexError:
            return (factors[0] / 100)

    def _pot_factor(self, remaining_potential):
        if remaining_potential <= 0: return 0
        
        factors = (0, 15, 20, 25, 30, 35, 40, 45, 55, 65, 75, 90, 100, 120, 160, 160, 160, 160, 160, 160, 160, 190, 190, 190, 190, 190, 190, 190, 190, 190, 190, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235)
        
        if remaining_potential > len(factors):
            return (factors[-1] / 100)

        try:
            return (factors[remaining_potential] / 100)
        except IndexError:
            return 0
    
    def _age_factor(self, age, posid):
        factors = (18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 30, 42, 50, 48, 48, 48, 48, 46, 44, 40, 35, 30, 25, 15, 0, -25, -40, -50, -65, -65, -65, -75, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000)

        if age > len(factors):
            return (factors[-1] / 100)

        if posid == 0 and age >= 28:
            age -= 2

        try:
            return (factors[age] / 100)
        except IndexError:
            return (factors[-1] / 100)

    def _sum_factors(self, basevalue, *args):
        summed_value = basevalue
        for a in args:
            summed_value += a

        return int(self._round_to_player_value(summed_value))

class PlayerName():
    def __init__(self, player, dict_cached_queries, fifa_edition=18):
        self.fifa_edition = int(fifa_edition)
        self.player = player
        try:
            self.dc_player_names = dict_cached_queries['q_dcplayernames']
        except KeyError:
            self.dc_player_names = None

        try:    
            self.edited_player_names = dict_cached_queries['q_edited_player_names']
        except KeyError:
            self.edited_player_names = None

        self.playername = self.set_player_name()


    def set_player_name(self):
        if self.fifa_edition == 18:
            dcplayernames_start_index = 34000
        else:
            dcplayernames_start_index = 30000

        name = {
            'firstname': int(self.player.firstname_id or 0),
            'lastname': int(self.player.lastname_id or 0),
            'commonname': int(self.player.commonname_id or 0),
            'playerjerseyname': int(self.player.playerjerseyname_id or 0),
        }
      
        if name['firstname'] == 0 and name['lastname'] == 0 and self.edited_player_names is not None:
            for i in range(len(self.edited_player_names)):
                if self.edited_player_names[i].playerid == self.player.playerid:
                    name['firstname'] = self.edited_player_names[i].firstname
                    name['lastname'] = self.edited_player_names[i].surname
                    name['commonname'] = self.edited_player_names[i].commonname 
                    name['playerjerseyname'] = self.edited_player_names[i].playerjerseyname
                    break
        elif self.dc_player_names is not None:
            for key in name:
                if name[key] >= dcplayernames_start_index:
                    # Get playername from dcplayernames
                    name[key] = self.get_dcplayername(name[key])
                else:
                    # Get playername from playernames
                    get_attr = getattr(self.player, key, None)
                    if get_attr is not None and get_attr.name is not None:
                        name[key] = get_attr.name
                    else:
                        name[key] = ""


        # This name will be displayed on website
        if name['commonname']:
            name['knownas'] = name['commonname']
        else:
            name['knownas'] = " ".join((str(name['firstname']), str(name['lastname'])))

        return name

    def get_dcplayername(self, nameid):
        if self.dc_player_names is None:
            return 0
            
        for i in range(len(self.dc_player_names)):
            if self.dc_player_names[i].nameid == nameid:
                return self.dc_player_names[i].name
        
        return nameid

class FifaTeam():
    def __init__(self, teamid, dict_cached_queries):
        pass

class FifaPlayer():

    def __init__(self, player, username, current_date, dict_cached_queries, currency, fifa_edition):
        self.player = player
        self.username = username
        self.dict_cached_queries = dict_cached_queries
        self.team_player_links = dict_cached_queries['q_team_player_links']
        self.q_teams = dict_cached_queries['q_teams']
        self.league_team_links = dict_cached_queries['q_league_team_links']
        self.leagues = dict_cached_queries['q_leagues']
        self.release_clauses = dict_cached_queries['q_release_clauses']

        # FIFA 18/FIFA 17
        self.fifa_edition = fifa_edition

        # Current Date
        self.current_date = current_date
        self.current_date_py = FifaDate().convert_to_py_date(fifa_date=self.current_date)

        try:
            self.query_player_loans = dict_cached_queries['q_player_loans']
        except KeyError:
            self.query_player_loans = None

        # Currency
        try:
            self.currency = int(currency)
        except KeyError:
            self.currency = 1 # Set Euro as default currency

        self.player_teams = self.set_teams()

        # q_dcplayernames & q_edited_player_names
        self.player_name = PlayerName(self.player, self.dict_cached_queries, self.fifa_edition).playername

        # Player Age
        self.player_age = PlayerAge(self.player.birthdate, current_date)

        # Player Value
        if self.currency == 0:
            # USD
            self.player_value = PlayerValue(self.player.overallrating, self.player.potential, self.player_age.age, self.player.preferredposition1, self.currency, self.player.value_usd)
        elif self.currency == 2:
            # GBP
            self.player_value = PlayerValue(self.player.overallrating, self.player.potential, self.player_age.age, self.player.preferredposition1, self.currency, self.player.value_gbp)
        else:
            # EURO by default
            self.player_value = PlayerValue(self.player.overallrating, self.player.potential, self.player_age.age, self.player.preferredposition1, self.currency, self.player.value_eur)
            
        # Player Wage (slow)
        try:
            self.player_wage = PlayerWage(self.player.overallrating, self.player_age.age, self.player.preferredposition1, self.player_teams['club_team'], int(self.currency))
        except KeyError as e:
            #print('KeyError: {}'.format(e))
            self.player_teams['club_team'] = {
                'team': {'teamid': 0, 'teamname': "Not Found"},
                'league': {'leagueid': 0, 'leaguename': "Not Found"}, 
            }
            self.player_wage = PlayerWage()
        self.release_clause = self.get_release_clause()
        self.player_contract = self.set_contract()
        self.traits = self.set_traits()
        self.headshot = self.set_headshot()
        self.bodytype = self.get_bodytype()
        self.boots = self.get_boots_name()
        self.haircolor = self.get_hair_color()

    def get_hair_color(self):
        haircolors = (
            'Blonde',
            'Black',
            'Ash Blonde',
            'Dark Brown',
            'Platinum Blonde',
            'Light Brown',
            'Brown',
            'Red',
            'White',
            'Gray',
            'Green',
            'Violet', 
        )

        try:
            return haircolors[int(self.player.haircolorcode)]
        except Exception as e:
            return  "{}. Unknown".format(self.player.haircolorcode)

    def get_bodytype(self):
        bodytypes = (
            '0. Invalid',
            '1. Lean',
            '2. Normal',
            '3. Stocky',
            '4. Lean',
            '5. Normal',
            '6. Stocky',
            '7. Lean',
            '8. Normal',
            '9. Stocky',
            '10. Messi',
            '11. Very Tall and Lean',
            '12. Akinfenwa',
            '13. Courtois',
            '14. Neymar',
            '15. Shaqiri',
            '16. Cristiano Ronaldo',
            '17. Leroux (Only Women)',
        )

        try:
            return bodytypes[int(self.player.bodytypecode)]
        except Exception as e:
            return  "{}. Unknown".format(self.player.bodytypecode)

    def get_boots_name(self):
        boots_names = (
            '0. Invalid',
            '1. EA Black/White',
            '2. EA Black/White',
            '3. EA Black/White',
            '4. EA Black/White',
            '5. EA Black/White',
            '6. EA Black/White',
            '7. EA Black/White',
            '8. EA Black/White',
            '9. EA Black/White',
            '10. EA Black/White',
            '11. EA Black/White',
            '12. EA Black/White',
            '13. EA Black/White',
            '14. EA Black/White',
            '15. EA Black/White',
            '16. EA Black/White',
            '17. EA Black/White',
            '18. EA Black/White',
            '19. EA Black/White',
            '20. EA Black/White',
            '21. Adidas Ace 17+ PURECONTROL Magnetic Storm',
            '22. Adidas Ace 17+ PURECONTROL Energy Aqua',
            '23. Adidas Ace 17+ PURECONTROL Thunder Storm',
            '24. EA Black/White',
            '25. EA Black/White',
            '26. Adidas Ace 17+ Purple/Red/Black',
            '27. Adidas Copa 17.1 Dust Storm',
            '28. EA Black/White',
            '29. Adidas Copa 17.1 Ocean Storm',
            '30. Adidas NEMEZIZ 17.0 Magnetic Storm',
            '31. Adidas NEMEZIZ 17.0 Ocean Storm',
            '32. Adidas NEMEZIZ 17.0 Black',
            '33. EA Black/White',
            '34. EA Black/White',
            '35. Adidas NEMEZIZ 17.1 White/Red',
            '36. Joma Vulcano 2.0',
            '37. Hummel Rapid X Blade Bluebird',
            '38. EA Black/White',
            '39. EA Black/White',
            '40. Adidas X17+ 360SPEED FG Magnetic Storm',
            '41. Adidas X17+ 360SPEED FG Ocean Storm',
            '42. Adidas X17+ 360SPEED FG Thunder Storm',
            '43. EA Black/White',
            '44. EA Black/White',
            '45. Nike Mercurial Veloce III Dynamic',
            '46. Nike Tiempo Legacy III',
            '47. Nike Magista Onda II Dynamic Fit',
            '48. Nike Hypervenom Phatal III',
            '49. EA Black/White',
            '50. EA Black/White',
            '51. EA Black/White',
            '52. EA Black/White',
            '53. EA Black/White',
            '54. EA Black/White',
            '55. EA Black/White',
            '56. EA Black/White',
            '57. EA Black/White',
            '58. EA Black/White',
            '59. EA Black/White',
            '60. EA Black/White',
            '61. EA Black/White',
            '62. EA Black/White',
            '63. Nike Mercurial Superfly V CR7 Dynamic',
            '64. EA Black/White',
            '65. Puma evoPower Vigor 1 Red Coral/Silver/Black',
            '66. EA Black/White',
            '67. Puma One 17.1 White/Black',
            '68. EA Black/White',
            '69. EA Black/White',
            '70. EA Black/White',
            '71. Umbro Medusae 2 Electric Blue',
            '72. Umbro Velocita 3 Yellow/Blue',
            '73. Umbro Velocita 3 Yellow',
            '74. EA Black/White',
            '75. EA Black/White',
            '76. EA Black/White',
            '77. Umbro Velocita 3 Blue',
            '78. Umbro Velocita 3 Black/Blue',
            '79. Umbro Velocita 3 Black',
            '80. Nike Mercurial Vapor XI Yellow/Black',
            '81. EA Black/White',
            '82. EA Black/White',
            '83. Under Armour Clutchfit Force 3.0 Black/Orange',
            '84. Under Armour Clutchfit Force 3.0 Yellow',
            '85. Under Armour Spotlight White/Red/Black',
            '86. Under Armour Spotlight Green/Black',
            '87. New Balance Visaro 2.0 Green',
            '88. New Balance Visaro 2.0 Black',
            '89. EA Black/White',
            '90. EA Black/White',
            '91. EA Black/White',
            '92. EA Black/White',
            '93. EA Black/White',
            '94. EA Black/White',
            '95. EA Black/White',
            '96. Mizuno Morelia Neo II Blue',
            '97. Mizuno Morelia Neo II Orange',
            '98. EA Black/White',
            '99. EA Black/White',
            '100. EA Black/White',
            '101. EA Black/White',
            '102. EA Black/White',
            '103. EA Black/White',
            '104. EA Black/White',
            '105. Asics DS Light X-Fly 3',
            '106. Asics DS Light X-Fly 3 SL',
            '107. Nike Tiempo Legend V White/Black/Red',
            '108. Nike Hypervenom Phantom White / Black / Total Orange / Volt / Pink',
            '109. Nike Magista Obra White/Black/Pink Blast/Volt',
            '110. Nike Tiempo Mystic V FG White/Black/Total Orange',
            '111. Puma Evopower 1.3 Yellow/Atomic Blue',
            '112. PUMA evoSPEED SL Safety Yellow',
            '113. New Balance Visaro Red Wine/Green',
            '114. New Balance Visaro Black/Green',
            '115. New Balance Visaro Black/Yellow',
            '116. New Balance Visaro Orange',
            '117. New Balance Furon Green/Blue',
            '118. New Balance Visaro White/Yellow',
            '119. Umbro Geo Flare ProSafety Yellow Camo/Chrome/Black',
            '120. Umbro Velocita 2.0 dazzling blue/white/fiery coral',
            '121. Umbro Medusae - Black / White / Turquoise',
            '122. Umbro UX-1 Black',
            '123. Nike Mercurial Superfly White / Black / Volt / Total Orange / Hyper Pink',
            '124. Nike Mercurial Superfly V Crimson/Yellow/Pink/Black',
            '125. Adidas adiPURE III Black',
            '126. Adidas ACE 16.1 Primeknit Womens White/Solar Gold/Shock',
            '127. Adidas X 15.1 Fwhite/Blue/Red',
            '128. Umbro Medusa Blue/Red',
            '129. EA Black/White',
            '130. Adidas ACE 16.1 Dark Space',
            '131. Adidas ACE 16.1 Mercury Pack',
            '132. Adidas ACE 16.1 Viper Pack',
            '133. Adidas ACE 16.1 Stellar Pack',
            '134. Adidas ACE 16.1 Speed of Light',
            '135. Adidas Ace 16+ Dark Space',
            '136. Adidas Ace 16+ Mercury Pack',
            '137. Adidas Ace 16+ Viper Pack',
            '138. Adidas Ace 16+ Speed of Light',
            '139. Adidas Ace 16+ Stellar Pack',
            '140. Adidas adiZero 99Gram',
            '141. Adidas Messi 16.1 Speed of Light',
            '142. Adidas Messi 16.1 Mercury Pack',
            '143. Adidas Messi 16+ Blackout',
            '144. Adidas Messi 16+ Mercury Pack',
            '145. Adidas Messi 16+ Speed of Light',
            '146. Adidas X 16.1 Dark Space',
            '147. Adidas X 16.1 Mercury Pack',
            '148. Adidas X 16.1 Speed of Light',
            '149. Adidas X 16.1 Viper Pack',
            '150. Adidas X 16.1 Stellar Pack',
            '151. Adidas X 16+ Dark Space',
            '152. Adidas X 16+ Intersport',
            '153. Adidas X 16+ Mercury Pack',
            '154. Adidas X 16+ Speed of Light',
            '155. Adidas X 16+ Viper Pack',
            '156. Adidas X 16+ Stellar Pack',
            '157. Adidas Ace 16+ Pure Control Silver',
            '158. Adidas X 16.1 Dark Space/White',
            '159. Asics DS Light X-Fly 2 Pearl/White/Electric Blue',
            '160. Asics Lethal Legacy Flash Yellow/Black',
            '161. Asics Menace 3 Spice Orange/White',
            '162. Lotto Zhero Gravity VIII 700  Orange/White',
            '163. Joma Champion Max Black/Yellow',
            '164. Joma Champion Max Blue/Green/White',
            '165. ???',
            '166. Joma Propulsion Lite Fluo Yellow',
            '167. Mizuno Basara 101 KL - Black/Green Gecko',
            '168. Mizuno Morelia II Blue',
            '169. Mizuno Wave Ignitus 4 Blue',
            '170. Mizuno Wave Ignitus 4 Red',
            '171. New Balance Furon Bright Cherry/Galaxy/Firefly',
            '172. New Balance Visaro Galaxy/Bright Cherry/Firefly',
            '173. Nike Hypervenom Phantom II Pure Platinum/Black/Green',
            '174. Nike Hypervenom Phantom II Volt/Black/Hyper Turq',
            '175. Nike Hypervenom Phantom II Wolf Grey/Total Orange/Black/Black-Volt',
            '176. Nike Magista Total Crimson/Black/Volt',
            '177. Nike Magista Obra White/Black/Pink Blast/Volt',
            '178. Nike Magista Obra II Pure Platinum/Black/Ghost Green',
            '179. Nike Magista Obra II Volt/Black/Total Orange/Pink',
            '180. Nike Mercurial Superfly V Pure Platinum/Black/Ghost Green',
            '181. Nike Mercurial Superfly V Crimson/Yellow/Pink/Black',
            '182. Nike Mercurial Superfly White / Black / Volt / Total Orange / Hyper Pink',
            '183. Nike Tiempo Legend VI Clear Jade/Black/Volt',
            '184. Nike Tiempo Mystic V FG White/Black/Total Orange',
            '185. Nike Tiempo Legend VI Wolf Grey/Black/Clear Jade',
            '186. Pirma Brasil Accurate Aqua/Silver',
            '187. Pirma Supreme Spry Black/Green',
            '188. Pirma Supreme Spry Black/Red',
            '189. Puma evoPower 1.3 Tricks Yellow Pink',
            '190. Puma evoPower 1.3 Blue/Red',
            '191. Puma evoPower 1.3 Red/Black',
            '192. Puma evoSpeed SL White/Red',
            '193. Puma evoSpeed SL White/Red',
            '194. Puma evoSpeed 1.5 Tricks Yellow Pink',
            '195. Puma evoTouch Pro Black/Green',
            '196. Umbro Medusae Black/White/Bluebird',
            '197. Umbro Medusae Grenadine/White/Black',
            '198. Umbro Medusae White/Black/Grenadine',
            '199. Umbro UX-Accuro Black/Metallic/Grenadine',
            '200. Umbro UX-Accuro Grenadine/Black',
            '201. Umbro UX-Accuro White/Black/Bluebird',
            '202. Umbro Velocita II  Black/White/Grenadine',
            '203. Umbro Velocita II Bluebird/White',
            '204. Umbro Velocita II Red/White',
            '205. Under Armour Clutchfit Black/Rocket Red/White',
            '206. Under Armour Clutchfit High-Vis Yellow/Black/Red',
            '207. Under Armour Spotlight Pro 2.0Rocket Red/High Vis Yellow',
            '208. Under Armour Spotlight Pro 2.0Rocket White/Black',
            '209. Adidas Ace 17+ PURECONTROL White/Blue',
            '210. Adidas Ace 17+ PURECONTROL Black',
            '211. Adidas Ace 17+ PURECONTROL Black/Blue',
            '212. Adidas Ace 17+ PURECONTROL Red/Black',
            '213. Adidas Ace 17+ PURECONTROL Solar Green',
            '214. Adidas Ace 17+ PURECONTROL Camouflage',
            '215. Adidas Messi 16+ Blue/Red',
            '216. Adidas Messi 16+ Gold/Black',
            '217. Adidas Messi 16+ White/Red',
            '218. Adidas X17 Blue/Red',
            '219. Adidas X17 Black',
            '220. Adidas X17 Red/Black',
            '221. Adidas X17 Solar Green',
            '222. Adidas X17.1 Camouflage',
            '223. Adidas Copa 17.1 Red/White',
            '224. Adidas Copa 17.1 Black/White',
            '225. Adidas Copa 17.1 Blue/White',
            '226. Adidas Copa 17.1 Black/Gold',
            '227. Adidas Copa 17.1 Silver/Gold',
            '228. EA Black/White',
            '229. Adidas Copa 17.1 White/Black',
            '230. Adidas X17.1 Women Core Black',
            '231. Adidas Ace 17+ White/Black',
            '232. Puma evoPower 17 green',
            '233. Puma evospeed 17 green',
            '234. Puma evospeed white/blue',
            '235. Nike Hypervenom Phantom III Green/Orange',
            '236. Nike Magista Obra II Red',
            '237. Nike Mercurial Superfly V Green',
            '238. Nike Tiempo Mystic V Yellow',
            '239. Nike Mercurial Superfly EA SPORTS',
            '240. Nike Hypervenom Phantom III White/Darkblue',
            '241. Nike Magista Obra II White/Yellow',
            '242. Nike Mercurial Superfly V Pink/White',
            '243. Nike Tiempo V White/Green',
            '244. Mizuno Morelia II Blue',
            '245. Mizuno Morelia II Red',
            '246. New Balance Furon Bright Cherry/Galaxy/Firefly',
            '247. New Balance Visaro Galaxy/Bright Cherry/Firefly',
            '248. New Balance Furon 2.0 Red',
            '249. New Balance Visaro 2.0 Grey/Red',
            '250. Umbro Velocita II Purple',
            '251. Umbro Medusae II Purple',
            '252. Umbro Velocita II Green/Purple',
            '253. Nike Hypervenom Phantom III NJR X Jordan',
            '254. EA Black/White',
        )
        
        try:
            return boots_names[int(self.player.shoetypecode)]
        except Exception as e:
            return  "{}. Unknown".format(self.player.shoetypecode)

    def set_traits(self):
        all_traits = list()
        trait1 = int(self.player.trait1)
        trait2 = int(self.player.trait2)

        if trait1 > 0:
            trait1_names = [
                "Inflexibility",
                "Long Throw-in",
                "Power Free kick",
                "Diver",
                "Injury prone",
                "Injury free",
                "Avoids using weaker foot",
                "Dives into tackles",
                "Tries to beat defensive line",
                "Selfish",
                "Leadership",
                "Argues With Referee",
                "Early crosser",
                "Finesse shot",
                "Flair",
                "Long passer",
                "Long shot taker",
                "Skilled dribbling",
                "Playmaker",
                "GK up for corners",
                "Puncher",
                "GK Long throw",
                "Power header",
                "GK One on One",
                "Giant throw-in",
                "Outsite foot shot",
                "Fans favourite",
                "Swerve Pass",
                "Second Wind",
                "Acrobatic Clearance",
            ]

            trait1_binary = bin(trait1)[2:]
            i = 0
            for t in reversed(trait1_binary):
                if t == '1':
                    all_traits.append(trait1_names[i])
                i += 1

        if trait2 > 0:
            trait2_names = [
                "Skilled Dribbling",
                "Flair Passes",
                "Fancy Flicks",
                "Stutter Penalty",
                "Chipped Penalty",
                "Bicycle Kicks",
                "Diving Header",
                "Driven Pass",
                "GK Flat Kick",
                "One Club Player",
                "Team Player",
                "Chip shot",
                "Technical Dribbler",
                "Rushes Out Of Goal",
                "Backs Into Player",
                "Set Play Specialist",
                "Takes Finesse Free Kicks",
                "Target Forward",
                "Cautious With Crosses",
                "Comes For Crossess",
                "Blames Teammates",
                "Saves with Feet",
                "Set Play Specialist",
                "Tornado Skillmove",
            ]

            trait2_binary = bin(trait2)[2:]
            i = 0
            for t in reversed(trait2_binary):
                if t == '1':
                    all_traits.append(trait2_names[i])
                i += 1

        # remove ',' from the end of string
        #if len(all_traits) >= 1: return all_traits[:-1]
             
        return all_traits

    def get_release_clause(self):
        for i in range(len(self.release_clauses)):
            if self.release_clauses[i].playerid == self.player.playerid:
                clause = self.release_clauses[i].release_clause
                self.formated_release_clause = "{:,}".format(clause)
                return clause

        return 0

    def set_headshot(self):
        if self.player.playerid < 280000:
            return "heads/p{playerid}.png".format(playerid=self.player.playerid)
        else:
            return "youthheads/p{headtypecode}{haircolorcode:02d}.png".format(headtypecode=self.player.headtypecode, haircolorcode=self.player.haircolorcode) 

    def update_positions(self):
        available_positions = ('GK', 'SW', 'RWB', 'RB', 'RCB', 'CB', 'LCB', 'LB', 'LWB', 'RDM', 'CDM', 'LDM', 'RM', 'RCM', 'CM', 'LCM', 'LM', 'RAM', 'CAM', 'LAM', 'RF', 'CF', 'LF', 'RW', 'RS', 'ST', 'LS', 'LW', 'SUB', 'RES')
        if -1 < self.player.preferredposition1 < len(available_positions):
            self.player.preferredposition1 = available_positions[self.player.preferredposition1]

        if -1 < self.player.preferredposition2 < len(available_positions):
            self.player.preferredposition2 = available_positions[self.player.preferredposition2]

        if -1 < self.player.preferredposition3 < len(available_positions):
            self.player.preferredposition3 = available_positions[self.player.preferredposition3]

        if -1 < self.player.preferredposition4 < len(available_positions):
            self.player.preferredposition4 = available_positions[self.player.preferredposition4]

    def set_contract(self):
        contract = dict()
        
        contract['jointeamdate'] = FifaDate().convert_days_to_py_date(days=self.player.playerjointeamdate)
        contract['enddate'] = FifaDate().convert_to_py_date(fifa_date=self.player.contractvaliduntil)

        contract['isloanedout'] = 0
        if self.query_player_loans is None:
            return contract

        for i in range(len(self.query_player_loans)):
            if self.query_player_loans[i].playerid == self.player.playerid:
                for j in range(len(self.q_teams)):
                    if int(self.query_player_loans[i].teamidloanedfrom) == int(self.q_teams[j].teamid):
                        contract['isloanedout'] = 1
                        contract['loan'] = vars(self.query_player_loans[i])
                        contract['enddate']  = FifaDate().convert_to_py_date(fifa_date=self.query_player_loans[i].loandateend)
                        contract['loanedto_clubid'] = self.player_teams['club_team']['team']['teamid']
                        contract['loanedto_clubname'] = self.player_teams['club_team']['team']['teamname']
                        self.player_teams['club_team']['team'] = vars(self.q_teams[j])
                        return contract

        return contract


    def set_teams(self):
        teams = {}
        max_teams = 2
        league = None
        
        for i in range(len(self.team_player_links)):
            if int(self.team_player_links[i].playerid) == int(self.player.playerid):
                for j in range(len(self.q_teams)):
                    if int(self.q_teams[j].teamid) == int(self.team_player_links[i].teamid):
                        league = self.get_league(self.q_teams[j].teamid)
                        if league:
                            if league[1].leagueid == 78 or league[1].leagueid == 2136:
                                # Men's National or Women's National
                                teams['national_team'] = {
                                    'team': vars(self.q_teams[j]),
                                    'team_links': vars(self.team_player_links[i]),
                                    'league': vars(league[0]),
                                    'league_links': vars(league[1]),
                                } 
                            else:
                                teams['club_team'] = {
                                    'team': vars(self.q_teams[j]),
                                    'team_links': vars(self.team_player_links[i]),
                                    'league': vars(league[0]),
                                    'league_links': vars(league[1]),
                                } 
                        
                        if len(teams) >= max_teams:
                            # Player can only have club team and national team
                            return teams
        return teams


    def get_league(self, teamid):
        for i in range(len(self.league_team_links)):
            if self.league_team_links[i].teamid == teamid:
                for j in range(len(self.leagues)):
                    if self.leagues[j].leagueid == self.league_team_links[i].leagueid:
                        return self.leagues[j], self.league_team_links[i]

        return None