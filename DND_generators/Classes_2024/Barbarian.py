from ..Condensed_Loader import Loader
from ..utilities.die_roller import roll_die

class Barbarian2024:

    def __init__(self):

        self.loader = Loader()

        self.name = ""
        self.level = 0
        self.hit_die = [0, ""]
        self.armor_class = 10
        self.hit_points = 0

        self.attacks = 1
        self.rage = 0
        self.rage_bonus = 0

        self.strength = 0
        self.dexterity = 0
        self.constitution = 0
        self.intelligence = 0
        self.wisdom = 0
        self.charisma = 0

        self.strength_modifier = 0
        self.dexterity_modifier = 0
        self.constitution_modifier = 0
        self.intelligence_modifier = 0
        self.wisdom_modifier = 0
        self.charisma_modifier = 0

        self.proficiency_bonus = 0
        self.ranged_bonus = 0
        self.ac_bonus = 0
        self.onehanded_bonus = 0

        self.armor = None
        self.weapons = None
        self.shield = None
        self.attacks = None

        self.attack_bonus = 0
        self.damage_bonus = 0

        self.primary_abilities = ["strength", "constitution"]

        self.proficiencies = {}

        self.subclass = None
        self.subclass_name = None

        self.loader.load_barbarian()

    def build_character(self, level=1):

        self.name = self.loader.class_barbarian['class_name']
        self.hit_die = self.loader.class_barbarian['hit_die']
        self.level = level

        self.strength = self.loader.class_barbarian['starting_abilities']['standard_based']['strength']
        self.dexterity = self.loader.class_barbarian['starting_abilities']['standard_based']['dexterity']
        self.constitution = self.loader.class_barbarian['starting_abilities']['standard_based']['constitution']
        self.intelligence = self.loader.class_barbarian['starting_abilities']['standard_based']['intelligence']
        self.wisdom = self.loader.class_barbarian['starting_abilities']['standard_based']['wisdom']
        self.charisma = self.loader.class_barbarian['starting_abilities']['standard_based']['charisma']

        self.strength_modifier = (self.strength - 10) // 2
        self.dexterity_modifier = (self.dexterity - 10) // 2
        self.constitution_modifier = (self.constitution - 10) // 2
        self.intelligence_modifier = (self.intelligence - 10) // 2
        self.wisdom_modifier = (self.wisdom - 10) // 2
        self.charisma_modifier = (self.charisma - 10) // 2

        self.attacks = self.loader.class_barbarian['attacks']
        self.rage = self.loader.class_barbarian['rage']
        self.rage_bonus = self.loader.class_barbarian['rage_bonus']

        self.proficiency_bonus = self.loader.class_barbarian['bonuses']['proficiency_bonus']
        self.ranged_bonus = self.loader.class_barbarian['bonuses']['ranged_bonus']
        self.ac_bonus = self.loader.class_barbarian['bonuses']['armor_class_bonus']
        self.onehanded_bonus = self.loader.class_barbarian['bonuses']['one_handed_bonus']

        self.proficiencies = self.loader.class_barbarian['proficiencies']

        self.hit_points = roll_die(f"{self.hit_die[0]}{self.hit_die[1]}", True) + self.constitution_modifier
        self.armor_class = 10 + self.dexterity_modifier + self.ac_bonus

        if level == 1:
            self.get_starting_equipment()
        else:
            self.level_up_wrapper(level)

        self.get_attack_damage_bonus()

        return

    def get_attack_damage_bonus(self):

        for weapon in self.weapons:
            key = list(weapon.keys())[0]
            if 'range' in weapon[key].keys():
                weapon[key]['attack_bonus'] = self.dexterity_modifier + self.proficiency_bonus
                weapon[key]['damage_bonus'] = self.dexterity_modifier
                if 'Finesse' in weapon[key]['properties']:
                    if (self.strength_modifier + self.proficiency_bonus >
                            self.dexterity_modifier + self.proficiency_bonus):
                        weapon[key]['attack_bonus'] = self.strength_modifier + self.proficiency_bonus
                        weapon[key]['damage_bonus'] = self.strength_modifier
            elif 'range' not in weapon[key].keys():
                weapon[key]['attack_bonus'] = self.strength_modifier + self.proficiency_bonus
                weapon[key]['damage_bonus'] = self.strength_modifier
                if 'Finesse' in weapon[key]['properties']:
                    if (self.dexterity_modifier + self.proficiency_bonus >
                            self.strength_modifier + self.proficiency_bonus):
                        weapon[key]['attack_bonus'] = self.dexterity_modifier + self.proficiency_bonus
                        weapon[key]['damage_bonus'] = self.dexterity_modifier

        return

    def get_starting_equipment(self):
        self.loader.load_armor()
        self.loader.load_weapons()

        if not self.armor:
            self.armor_class = 10 + self.dexterity_modifier + self.constitution_modifier
        else:
            self.armor_class = 10 + self.dexterity_modifier + self.ac_bonus

        self.weapons = []
        self.weapons.append({"Greataxe": self.loader.item_weapons["Martial Melee Weapons"]["Greataxe"]})
        self.weapons.append({"Handaxe": self.loader.item_weapons["Simple Melee Weapons"]["Handaxe"]})
        self.weapons.append({"Handaxe": self.loader.item_weapons["Simple Melee Weapons"]["Handaxe"]})

        self.get_attack_damage_bonus()

    def get_best_armor(self, use_shield, stealth=True):

        self.loader.load_armor()

        proficient_check = []
        for proficient_armor in self.proficiencies['armor']:
            if "all" in proficient_armor.lower():
                proficient_check.append("Light Armor")
                proficient_check.append("Medium Armor")
                proficient_check.append("Heavy Armor")
            elif "light" in proficient_armor.lower():
                proficient_check.append("Light Armor")
            elif "medium" in proficient_armor.lower():
                proficient_check.append("Medium Armor")
            elif "heavy" in proficient_armor.lower():
                proficient_check.append("Heavy Armor")
            elif "shields" in proficient_armor.lower():
                proficient_check.append("Shields")

        best_armor_ac = 0
        best_shield_ac = 0
        best_shield = None

        for category in self.loader.item_armor:
            if category in proficient_check:
                if category != "Shields":
                    for armor in self.loader.item_armor[category]:
                        if self.loader.item_armor[category][armor]['stealth_disadvantage'] == str(stealth):
                            continue
                        if self.loader.item_armor[category][armor]['min_strength'] > self.strength:
                            continue
                        if self.loader.item_armor[category][armor]['add_dexmod'] == "True":
                            if self.loader.item_armor[category][armor]['dexmod_cap'] == 0:
                                if (self.loader.item_armor[category][armor]['base_ac'] +
                                        self.dexterity_modifier > best_armor_ac):
                                    self.armor = {armor: self.loader.item_armor[category][armor]}
                                    self.armor_class = (self.loader.item_armor[category][armor]['base_ac'] +
                                                        self.dexterity_modifier)
                            else:
                                if self.dexterity_modifier < self.loader.item_armor[category][armor]['dexmod_cap']:
                                    if (self.loader.item_armor[category][armor]['base_ac'] +
                                            self.dexterity_modifier > best_armor_ac):
                                        self.armor = {armor: self.loader.item_armor[category][armor]}
                                        self.armor_class = (self.loader.item_armor[category][armor]['base_ac'] +
                                                            self.dexterity_modifier)
                                else:
                                    if (self.loader.item_armor[category][armor]['base_ac'] +
                                            self.loader.item_armor[category][armor]['dexmod_cap'] > best_armor_ac):
                                        self.armor = {armor: self.loader.item_armor[category][armor]}
                                        self.armor_class = (self.loader.item_armor[category][armor]['base_ac'] +
                                                            self.loader.item_armor[category][armor]['dexmod_cap'])

                        else:
                            if self.loader.item_armor[category][armor]['base_ac'] > best_armor_ac:
                                self.armor = {armor: self.loader.item_armor[category][armor]}
                                self.armor_class = (self.loader.item_armor[category][armor]['base_ac'])
                elif category == "Shields" and use_shield:
                    for shield in self.loader.item_armor[category]:
                        if self.loader.item_armor[category][shield]['min_strength'] > self.strength:
                            continue
                        if self.loader.item_armor[category][shield]['armor_class_bonus'] > best_shield_ac:
                            best_shield_ac = self.loader.item_armor[category][shield]['armor_class_bonus']
                            best_shield = {shield: self.loader.item_armor[category][shield]}

                    self.shield = best_shield
                    self.armor_class += best_shield_ac

    def get_best_weapon(self, use_shield):

        self.loader.load_weapons()

        proficient_check = []
        for proficient_weapon in self.proficiencies['weapons']:
            if "simple weapons" in proficient_weapon.lower():
                proficient_check.append("Simple Melee Weapons")
                proficient_check.append("Simple Ranged Weapons")
            elif "martial weapons" in proficient_weapon.lower():
                proficient_check.append("Martial Melee Weapons")
                proficient_check.append("Martial Ranged Weapons")
            elif proficient_weapon.lower()[-1] == 's':
                proficient_check.append(proficient_weapon.lower()[:-1])

        best_attack_die = 0
        best_weapon = []

        die_rank = {
            "d0": 0,
            "d1": 1,
            "d4": 2,
            "d6": 3,
            "d8": 4,
            "d10": 5,
            "d12": 6,
            "d20": 7
        }

        range_preference = False
        melee_preference = False

        if self.dexterity_modifier > self.strength_modifier:
            range_preference = True
        else:
            melee_preference = True

        for category in self.loader.item_weapons:
            if category in proficient_check:
                for weapon in self.loader.item_weapons[category]:
                    if use_shield and "Two-Handed" in self.loader.item_weapons[category][weapon]['properties']:
                        continue
                    if range_preference and not any('range' in elem.lower() for elem in category.split()):
                        if "Finesse" in self.loader.item_weapons[category][weapon]['properties']:
                            pass
                        else:
                            continue
                    if melee_preference and any('range' in elem.lower() for elem in category.split()):
                        if "Finesse" in self.loader.item_weapons[category][weapon]['properties']:
                            pass
                        else:
                            continue
                    die_pos = die_rank.get(
                        f"d{self.loader.item_weapons[category][weapon]['damage']['die'].split('d')[1]}")
                    if die_pos > best_attack_die:
                        best_weapon.clear()
                        best_weapon.append({weapon: self.loader.item_weapons[category][weapon]})
                        # print(1, {weapon: self.loader.item_weapons[category][weapon]})
                        best_attack_die = die_pos
                    elif die_pos == best_attack_die:
                        best_weapon.append({weapon: self.loader.item_weapons[category][weapon]})
                        # print(2, {weapon: self.loader.item_weapons[category][weapon]})
                        best_attack_die = die_pos

            if category not in proficient_check:
                for weapon in self.loader.item_weapons[category]:
                    if any(elem in weapon.lower() for elem in proficient_check):
                        if use_shield and "Two-Handed" in self.loader.item_weapons[category][weapon]['properties']:
                            continue
                        die_pos = die_rank.get(
                            f"d{self.loader.item_weapons[category][weapon]['damage']['die'].split('d')[1]}")
                        if die_pos > best_attack_die:
                            best_weapon.clear()
                            best_weapon.append({weapon: self.loader.item_weapons[category][weapon]})
                            # print(3, {weapon: self.loader.item_weapons[category][weapon]})
                            best_attack_die = die_pos
                        elif die_pos == best_attack_die:
                            best_weapon.append({weapon: self.loader.item_weapons[category][weapon]})
                            # print(4, {weapon: self.loader.item_weapons[category][weapon]})
                            best_attack_die = die_pos

        self.weapons = best_weapon

        return

    def level_up(self, level: int):

        features = self.loader.class_barbarian['level_features'][f'level_{level}']
        self.proficiency_bonus = features['proficiency_bonus']
        self.attacks = features['attacks']
        self.rage = features['rage']
        self.rage_bonus = features['rage_bonus']

        if features['asi_bonus'] > 0:
            if level == 4:
                self.strength += features['asi_bonus']
            if level == 8:
                self.strength += features['asi_bonus']
            if level == 12:
                self.constitution += features['asi_bonus']
            if level == 16:
                self.constitution += features['asi_bonus']
            if level == 19:
                self.dexterity += features['asi_bonus']

        if level == 3:
            self.subclass = self.loader.class_barbarian['subclasses']
            self.subclass_name = list(self.loader.class_barbarian['subclasses'])[0]

        if level == 20:
            self.strength += 4
            self.constitution += 4

        if self.subclass:
            if f"level_{level}" in self.loader.class_barbarian['subclasses'][self.subclass_name]:
                level_data = self.loader.class_barbarian['subclasses'][self.subclass_name][f"level_{level}"]

        self.hit_points += roll_die(f"{self.hit_die[0]}{self.hit_die[1]}", False) + self.constitution_modifier
        self.level = level

        self.strength_modifier = (self.strength - 10) // 2
        self.dexterity_modifier = (self.dexterity - 10) // 2
        self.constitution_modifier = (self.constitution - 10) // 2
        self.intelligence_modifier = (self.intelligence - 10) // 2
        self.wisdom_modifier = (self.wisdom - 10) // 2
        self.charisma_modifier = (self.charisma - 10) // 2

        if not self.armor:
            self.armor_class = 10 + self.dexterity_modifier + self.constitution_modifier
        else:
            self.armor_class = 10 + self.dexterity_modifier + self.ac_bonus

        self.get_best_armor(use_shield=False, stealth=False)
        self.get_best_weapon(use_shield=False)

        self.get_attack_damage_bonus()

        return

    def level_up_wrapper(self, levels: int):

        if levels <= 1:
            return

        for level in range(2, levels + 1):
            self.level_up(level)

        return

    def print_char(self):

        die_rank = {
            "d0": 0,
            "d1": 1,
            "d4": 2,
            "d6": 3,
            "d8": 4,
            "d10": 5,
            "d12": 6,
            "d20": 7
        }
        max_damage = None
        best_attack_die = 0

        print(f"Level {self.level} {self.name}"
              f"\tAC: {self.armor_class} \tHP: {self.hit_points}")
        print(f"Attacks: {self.attacks} \tRage: {self.rage} \tRage Bonus: {self.rage_bonus:+>2}")
        print(f"STR: {self.strength} ({self.strength_modifier:+>2}) \tDEX: {self.dexterity} "
              f"({self.dexterity_modifier:+>2}) \tCON: {self.constitution} ({self.constitution_modifier:+>2})")
        print(f"INT: {self.intelligence} ({self.intelligence_modifier:+>2}) \tWIS: {self.wisdom} "
              f"({self.wisdom_modifier:+>2}) \tCHA: {self.charisma} ({self.charisma_modifier:+>2})")
        print(f"Proficiency Bonus: {self.proficiency_bonus}\t\tAttack Bonus: {self.attack_bonus}\t\t"
              f"Damage Bonus: {self.damage_bonus}")
        print(f"Shield: {self.shield}")
        print(f"Armor: {self.armor}")
        print(f"Weapons:")
        for weapon in self.weapons:
            print(f"\t{weapon}")

            key = list(weapon.keys())[0]
            print(f"\t\tAttack: {weapon[key]['attack_bonus']:+>2}\t\tDamage: {weapon[key]['damage_bonus']:+>2}"
                  f"\t\tMDPT: {(roll_die(f"{weapon[key]['damage']['die']:+>2}", True) +
                                weapon[key]['damage_bonus']) * self.attacks}")

