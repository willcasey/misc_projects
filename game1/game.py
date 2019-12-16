import numpy as np
from models import Database

class Glob:
    def __init__(self, game_id):
        self.nations = dict()
        self.positions = dict()
        self.db = Database(log_table_name='game_log', game_id = game_id)
        self.db.drop_game_log_table()
        self.db.create_game_log_table()
        self.db.append_game_log_table(action='start_game',details={})
    def create_nation(self, name):
        new_nation = {name: Nation(name=name)}
        self.nations = dict(self.nations, **new_nation)
        self.db.append_game_log_table(action='create_nation',details={"name": name})
    def create_position(self, name, terrain):
        new_position = {name: Position(position_name=name, terrain=terrain)}
        self.positions = dict(self.positions, **new_position)
        self.db.append_game_log_table(action='create_position',details={"name": name, "terrain": terrain})



class Nation:
    def __init__(self, name, public_opinion_score=100):
        self.name = name
        self.infantry_units = []
        self.infantry_units_names = []
        self.artillery_units = []
        self.artillery_units_names = []
        self.militia_units = []
        self.militia_units_names = []

        self.public_opinion_score = public_opinion_score
    def __str__(self):
        return_str = """
        infantry_units: {iu}
        militia_units: {mu}
        artillery_units: {au}
        """.format(iu=[i.name for i in self.infantry_units]
                  ,mu=[i.name for i in self.militia_units]
                  ,au=[i.name for i in self.artillery_units]
                  )
        return return_str

    def __add__(self, other):
        if other.unit_type == 'infantry':
            self.infantry_units.append(other)
            self.infantry_units_names.append(other.name)
        elif other.unit_type == 'artillery':
            self.artillery_units.append(other)
            self.artillery_units_names.append(other.name)
        elif other.unit_type == 'militia':
            self.militia_units.append(other)
            self.militia_units_names.append(other.name)

    def create_unit(self, name, unit_type, position):
        unit_var = Unit(name = name, unit_type = unit_type, position = position, nation=self.name)

        #adding to database
        game.db.append_game_log_table(action='create_unit',details={"name":name, "unit_type" : unit_type, "position": position, "nation": self.name})
        game.db.append_unit_table(name=name, nation=self.name, unit_type=unit_type, position=position, status=unit_var.status, base_mu=unit_var.base_mu
                                 , base_sigma=unit_var.base_sigma, training=unit_var.training, leadership=unit_var.leadership, terrain=unit_var.terrain
                                 , morale=unit_var.morale, experience=unit_var.experience, attacking=unit_var.attacking, defending=unit_var.defending)
        return self + unit_var

    def alter_unit_additive(self, name, additive, mu, sigma):
        """
        name is the name of the unit
        """
        unit = self.units()[name]
        unit.alter_additive(additive=additive, mu=mu, sigma=sigma)

        #adding to database
        game.db.update_unit_table(unit_name=name, unit_nation=unit.nation, update_column=additive, update_value=(mu, sigma))
        game.db.append_game_log_table(action='alter_unit',details={"name":name, "unit_type" : unit.unit_type
                                                                 , "position": unit.position, "nation": unit.nation
                                                                 , "status": unit.status, "additive": additive
                                                                 , "additive_val": (mu, sigma)
                                                                 })

    def units(self, by_unit_type=False):
        if by_unit_type:
            return_dict = {"infantry": dict(zip(self.infantry_units_names,self.infantry_units))
                    , "artillery": dict(zip(self.artillery_units_names,self.artillery_units))
                    , "militia": dict(zip(self.militia_units_names,self.militia_units))}
        else:
            return_dict = dict(
                        dict(zip(self.infantry_units_names,self.infantry_units))
                    , **dict(zip(self.artillery_units_names,self.artillery_units))
                    , **dict(zip(self.militia_units_names,self.militia_units))
                          )
        return return_dict

    def attack(self, units, attack_position):
        """
        units are units to be included in the attack
        attack_position is the object location of the attack
        """
        attacker_units = [self.units()[u] for u in units]
        defender_units = game.positions[attack_position].current_occupying_units()[1]
        b = Battle(attacker=self.name, defender='other', attacker_units=attacker_units, defender_units=defender_units, position=attack_position)
        br = b.battle()[2]
        print(br)
        print(b.battle_results(battle_results=br))

class Position:
    def __init__(self, position_name, terrain):
        self.position_name = position_name
        self.terrain = terrain
        self.occupying_nation = None
        self.occupying_units = None

    def current_occupying_units(self):
        occupying_units = []
        occupying_units_obj = []
        for n in game.nations:
            nation = game.nations[n]
            for u in nation.units(by_unit_type=False):
                unit = nation.units(by_unit_type=False)[u]
                if unit.position == self.position_name and unit.status == 1:
                    occupying_units_obj.append(unit)
                    occupying_units.append((unit.nation, unit.name))
        return occupying_units, occupying_units_obj

class Unit:
    def __init__(self, name, unit_type, position, nation, status=1
                 , training=(0, 0), leadership=(0, 0), terrain=(0, 0), morale=(0, 0), experience=(0, 0)):
        self.name = name
        self.unit_type = unit_type
        self.base_mu = self.unit_bases()['mu']
        self.base_sigma = self.unit_bases()['sigma']
        self.position = position
        self.nation = nation
        self.status = status
        self.training = training
        self.leadership = leadership
        self.terrain = terrain
        self.morale = morale
        self.experience = experience
        self.attacking = self.unit_bases()['attacking']
        self.defending= self.unit_bases()['defending']
        self.active_duty = 1
        self.active_duty_cost = self.unit_bases()['active_duty_cost']
        self.reserve_cost = self.active_duty_cost//10


    def __str__(self):
        return """
                  Unit Name: {name}
                  Unit Type: {unit_type}
                  Nation   : {nation}
                  Position : {position}
                  """.format(name=self.name
                             , unit_type=self.unit_type
                             , position = self.position
                             , nation = self.nation)

    def get_attributes(self):
        for attr in self.__dict__:
            print(attr, " : ", getattr(self, attr))
        print("final_attack_attributes : ", self.battle_attributes(attacking=True))
        print("final_defense_attributes : ", self.battle_attributes(attacking=False))

    def unit_bases(self):
        unit_bases_dict = { 'infantry' :  {'mu': 10, 'sigma': 5, 'attacking': (-1, 2), 'defending': (3, 0), 'active_duty_cost': 10 }
                            ,'militia'  :  {'mu': 5, 'sigma': 10, 'attacking': (-5, 0), 'defending': (5, 5), 'active_duty_cost': 3}
                            ,'artillery':  {'mu': 30, 'sigma': 10, 'attacking': (10, 5), 'defending': (0, 0), 'active_duty_cost': 20}
                            }
        return unit_bases_dict[self.unit_type]


    def alter_additive(self, additive, mu, sigma):
        """
        Alters the current additive scores
        """
        additive_features = self.current_additives()[additive]

        if additive == 'training':
            self.training = (additive_features[0] + mu, additive_features[1] + sigma)
        elif additive == 'leadership':
            self.leadership = (additive_features[0] + mu, additive_features[1] + sigma)
        elif additive == 'terrain':
            self.terrain = (additive_features[0] + mu, additive_features[1] + sigma)
        elif additive == 'morale':
            self.morale = (additive_features[0] + mu, additive_features[1] + sigma)
        elif additive == 'experience':
            self.experience = (additive_features[0] + mu, additive_features[1] + sigma)


    def current_additives(self):
        additives = {       'training': self.training
                          , 'leadership': self.leadership
                          , 'terrain': self.terrain
                          , 'morale': self.morale
                          , 'experience': self.experience
                          }
        return additives

    def current_additives_result(self):
        additives_list = [self.current_additives()[k] for k in self.current_additives()]
        return {'mu': sum([a[0] for a in additives_list]), 'sigma': sum([a[1] for a in additives_list])}

    def battle_attributes(self, attacking=False):
        """
        finds final battle attributes
        """
        additives_score = self.current_additives_result()
        if attacking:
            mu = self.base_mu + additives_score['mu'] + self.attacking[0]
            sigma = self.base_sigma + additives_score['sigma'] + self.attacking[1]
        else:
            mu = self.base_mu + additives_score['mu'] + self.defending[0]
            sigma = self.base_sigma + additives_score['sigma'] + self.defending[1]
        if sigma < 1:
            sigma = 1
        if mu < 1:
            mu = 1
        return {"mu": mu, "sigma": sigma}

    def battlescore(self, attacking=False):
        """
        gets final battle score
        """
        battlescore = self.battle_attributes(attacking)
        return np.abs(np.random.normal(loc=battlescore['mu'], scale=battlescore['sigma']))




class Battle:
    def __init__(self, attacker, defender, attacker_units, defender_units, position):
        self.attacker = attacker
        self.defender = defender
        self.attacker_units = attacker_units
        self.defender_units = defender_units
        self.position = position

    def combined_score_distribution(self):
        attacker_combined = (np.sum([i.battle_attributes()['mu'] for i in self.attacker_units]),np.sqrt(np.sum([(i.battle_attributes()['sigma']**2) for i in self.attacker_units])))
        defender_combined = (np.sum([i.battle_attributes()['mu'] for i in self.defender_units]),np.sqrt(np.sum([(i.battle_attributes()['sigma']**2) for i in self.defender_units])))
        return attacker_combined, defender_combined

    def simulate_even_outcome_battle(self):
        """
        The purpose of this is to simulate a battle where the expected scores are equivalent

        """
        attacker_combined, defender_combined = self.combined_score_distribution()
        if attacker_combined[0] >= defender_combined[0]:
            simulation_mu = attacker_combined[0]
        else:
            simulation_mu = defender_combined[0]
        simulation = (np.random.normal(loc=simulation_mu, scale=attacker_combined[1], size=10000) - np.random.normal(loc=simulation_mu, scale=defender_combined[1], size=10000))
        return simulation

    def battle_thresholds(self):
        """
        this generates the thresholds of victory from the 'equivalent-simulation'
        std*0.5 == draw
        std*1 == victory but no territory acquired
                 morale +/- 5
                 loser can retreat if possible

        std*2 == rout with territory aquried
                 morale + 10 for victor troops in battle
                 morale + 3 for victor troops not in battle
                 morale -4 for loser troops not in battle
        """
        simulation = self.simulate_even_outcome_battle()
        sim_std = np.std(simulation)
        thresholds = {'rout': sim_std*2, 'victory': sim_std, 'draw': sim_std*0.5}
        return thresholds


    def battle(self):
        attacker_score = sum([i.battlescore(attacking=True) for i in self.attacker_units])
        defender_score = sum([i.battlescore() for i in self.defender_units])
        result_difference = attacker_score - defender_score
        return attacker_score, defender_score, result_difference

    def battle_results(self, battle_results):
        battle_thresholds = self.battle_thresholds()
        if np.abs(battle_results) <= battle_thresholds['draw']:
            print('draw')
            self.battle_results_unit_updates('draw')

        elif battle_results > battle_thresholds['draw'] and battle_results <= battle_thresholds['rout']:
            print("attacker victory")
            self.battle_results_unit_updates('attacker victory')

        elif battle_results > battle_thresholds['rout']:
            print("attacker rout")
            self.battle_results_unit_updates('attacker rout')

        elif battle_results < battle_thresholds['draw']*-1 and battle_results >= battle_thresholds['rout']*-1:
            print("defender victory")
            self.battle_results_unit_updates('defender victory')

        elif battle_results < battle_thresholds['rout']*-1:
            print("defender rout")
            self.battle_results_unit_updates('defender rout')


    def battle_results_unit_updates(self, result):
        """
        this updates additives of the units in the battle based on the result of the battle
        """
        if result == 'draw':
            for u in self.attacker_units:
                u.alter_additive(additive='morale', mu=-1, sigma=0)
                u.alter_additive(additive='experience', mu=1, sigma=0)
            for u in self.defender_units:
                u.alter_additive(additive='morale', mu=1, sigma=0)
                u.alter_additive(additive='experience', mu=1, sigma=0)
        elif result == 'attacker victory':
            for u in self.attacker_units:
                u.alter_additive(additive='morale', mu=5, sigma=0)
                u.alter_additive(additive='experience', mu=1, sigma=0)
            for u in self.defender_units:
                u.alter_additive(additive='morale', mu=-5, sigma=0)
                u.alter_additive(additive='experience', mu=1, sigma=0)
        elif result == 'attacker rout':
            for u in self.attacker_units:
                u.alter_additive(additive='morale', mu=10, sigma=0)
                u.alter_additive(additive='experience', mu=1, sigma=0)
            for u in self.defender_units:
                u.status = 0
        elif result == 'defender victory':
            for u in self.attacker_units:
                u.alter_additive(additive='morale', mu=-5, sigma=0)
                u.alter_additive(additive='experience', mu=1, sigma=0)
            for u in self.defender_units:
                u.alter_additive(additive='morale', mu=5, sigma=0)
                u.alter_additive(additive='experience', mu=1, sigma=0)
        elif result == 'defender rout':
            for u in self.attacker_units:
                u.status = 0
            for u in self.defender_units:
                u.alter_additive(additive='morale', mu=10, sigma=0)
                u.alter_additive(additive='experience', mu=1, sigma=0)



def main(g):
    """
    initialize the game
    This is only here for testing purposes. the real game would have users
    initialize certain properties like the nations
    """
    for j in ['U', 'G', 'R']:
        g.create_nation(name=j)
    for p in [('a1', 'plains'), ('a2', 'mountains'), ('a3', 'plains'), ('a4', 'river'), ('a5', 'river')]:
        g.create_position(name=p[0], terrain=p[1])
    return g

game = main(Glob(game_id=1))
