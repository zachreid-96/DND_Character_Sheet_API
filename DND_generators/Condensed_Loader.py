import json
from pathlib import Path

# noinspection PyAttributeOutsideInit
class Loader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.class_barbarian = {}
            cls._instance.class_bard = {}
            cls._instance.class_cleric = {}
            cls._instance.class_druid = {}
            cls._instance.class_fighter = {}
            cls._instance.class_monk = {}
            cls._instance.class_paladin = {}
            cls._instance.class_ranger = {}
            cls._instance.class_rogue = {}
            cls._instance.class_sorcerer = {}
            cls._instance.class_warlock = {}
            cls._instance.class_wizard = {}

            cls._instance.item_armor = {}
            cls._instance.item_weapons = {}

            cls._instance.spells = {}

            cls._instance.json_masterlist = {
                "Barbarian": fr"{Path(__file__).parent}/jsons/SRD_2014_Condensed/Classes/Barbarian.json",
                "Bard": fr"{Path(__file__).parent}/jsons/SRD_2014_Condensed/Classes/Bard.json",
                "Cleric": fr"{Path(__file__).parent}/jsons/SRD_2014_Condensed/Classes/Cleric.json",
                "Druid": fr"{Path(__file__).parent}/jsons/SRD_2014_Condensed/Classes/Druid.json",
                "Fighter": fr"{Path(__file__).parent}/jsons/SRD_2014_Condensed/Classes/Fighter.json",
                "Monk": fr"{Path(__file__).parent}/jsons/SRD_2014_Condensed/Classes/Monk.json",
                "Paladin": fr"{Path(__file__).parent}/jsons/SRD_2014_Condensed/Classes/Paladin.json",
                "Ranger": fr"{Path(__file__).parent}/jsons/SRD_2014_Condensed/Classes/Ranger.json",
                "Rogue": fr"{Path(__file__).parent}/jsons/SRD_2014_Condensed/Classes/Rogue.json",
                "Sorcerer": fr"{Path(__file__).parent}/jsons/SRD_2014_Condensed/Classes/Sorcerer.json",
                "Warlock": fr"{Path(__file__).parent}/jsons/SRD_2014_Condensed/Classes/Warlock.json",
                "Wizard": fr"{Path(__file__).parent}/jsons/SRD_2014_Condensed/Classes/Wizard.json",
                "Armor": fr"{Path(__file__).parent}/jsons/SRD_2014_Condensed/Items/Armor.json",
                "Weapons": fr"{Path(__file__).parent}/jsons/SRD_2014_Condensed/Items/Weapons.json",
                "Spells": fr"{Path(__file__).parent}/jsons/SRD_2014_Condensed/Spells/Spells.json"
            }

        return cls._instance

    def load_json(self, _var):

        if _var == "Fighter" and self.class_fighter == {}:
            with open(self.json_masterlist.get(_var), 'r', encoding='utf-8', errors='replace') as file:
                self.class_fighter = json.load(file)

        return

    def load_barbarian(self):

        with open(self.json_masterlist.get("Barbarian"), 'r', encoding='utf-8', errors='replace') as file:
            self.class_barbarian = json.load(file)

    def load_bard(self):

        with open(self.json_masterlist.get("Bard"), 'r', encoding='utf-8', errors='replace') as file:
            self.class_bard = json.load(file)

    def load_cleric(self):

        with open(self.json_masterlist.get("Cleric"), 'r', encoding='utf-8', errors='replace') as file:
            self.class_cleric = json.load(file)

    def load_druid(self):

        with open(self.json_masterlist.get("Druid"), 'r', encoding='utf-8', errors='replace') as file:
            self.class_druid = json.load(file)

    def load_fighter(self):

        with open(self.json_masterlist.get("Fighter"), 'r', encoding='utf-8', errors='replace') as file:
            self.class_fighter = json.load(file)

    def load_monk(self):

        with open(self.json_masterlist.get("Monk"), 'r', encoding='utf-8', errors='replace') as file:
            self.class_monk = json.load(file)

    def load_paladin(self):

        with open(self.json_masterlist.get("Paladin"), 'r', encoding='utf-8', errors='replace') as file:
            self.class_paladin = json.load(file)

    def load_ranger(self):

        with open(self.json_masterlist.get("Ranger"), 'r', encoding='utf-8', errors='replace') as file:
            self.class_ranger = json.load(file)

    def load_rogue(self):

        with open(self.json_masterlist.get("Rogue"), 'r', encoding='utf-8', errors='replace') as file:
            self.class_rogue = json.load(file)

    def load_sorcerer(self):

        with open(self.json_masterlist.get("Sorcerer"), 'r', encoding='utf-8', errors='replace') as file:
            self.class_sorcerer = json.load(file)

    def load_warlock(self):

        with open(self.json_masterlist.get("Warlock"), 'r', encoding='utf-8', errors='replace') as file:
            self.class_warlock = json.load(file)

    def load_wizard(self):

        with open(self.json_masterlist.get("Wizard"), 'r', encoding='utf-8', errors='replace') as file:
            self.class_wizard = json.load(file)

    def load_armor(self):

        with open(self.json_masterlist.get("Armor"), 'r', encoding='utf-8', errors='replace') as file:
            self.item_armor = json.load(file)

    def load_weapons(self):

        with open(self.json_masterlist.get("Weapons"), 'r', encoding='utf-8', errors='replace') as file:
            self.item_weapons = json.load(file)

    def load_spells(self):

        with open(self.json_masterlist.get("Spells"), 'r', encoding='utf-8', errors='replace') as file:
            self.spells = json.load(file)
