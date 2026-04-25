import json


class SRD_2014_Loader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.abilities = []
            cls._instance.alignments = []
            cls._instance.armors = []
            cls._instance.backgrounds = []
            cls._instance.background_benefits = []
            cls._instance.char_classes = []
            cls._instance.class_features = []
            cls._instance.class_feature_items = []
            cls._instance.conditions = []
            cls._instance.creatures = []
            cls._instance.creature_actions = []
            cls._instance.creature_action_attacks = []
            cls._instance.creature_sets = []
            cls._instance.creature_traits = []
            cls._instance.creature_types = []
            cls._instance.damage_types = []
            cls._instance.documents = []
            cls._instance.environments = []
            cls._instance.feats = []
            cls._instance.feat_benefits = []
            cls._instance.items = []
            cls._instance.item_categories = []
            cls._instance.item_rarities = []
            cls._instance.item_sets = []
            cls._instance.languages = []
            cls._instance.rules = []
            cls._instance.sizes = []
            cls._instance.skills = []
            cls._instance.species = []
            cls._instance.species_traits = []
            cls._instance.spells = []
            cls._instance.spell_casting_options = []
            cls._instance.spell_schools = []
            cls._instance.weapons = []
            cls._instance.weapon_properties = []
            cls._instance.weapon_property_assignments = []
        return cls._instance

    def load_json(self, category: str):

        categories = {
            "Abilities": (r'./jsons/srd-2014/Ability.json', self.abilities),
            "Alignments": (r'./jsons/srd-2014/Alignment.json', self.alignments),
            "Armors": (r'./jsons/srd-2014/Armor.json', self.armors),
            "Backgrounds": (r'./jsons/srd-2014/Background.json', self.backgrounds),
            "BackgroundBenefits": (r'./jsons/srd-2014/BackgroundBenefit.json', self.background_benefits),
            "CharacterClasses": (r'./jsons/srd-2014/CharacterClass.json', self.char_classes),
            "ClassFeatures": (r'./jsons/srd-2014/ClassFeature.json', self.class_features),
            "ClassFeatureItems": (r'./jsons/srd-2014/ClassFeatureItem.json', self.class_feature_items),
            "Conditions": (r'./jsons/srd-2014/Condition.json', self.conditions),
            "Creatures": (r'./jsons/srd-2014/Creature.json', self.creatures),
            "CreatureActions": (r'./jsons/srd-2014/CreatureAction.json', self.creature_actions),
            "CreatureActionAttacks": (r'./jsons/srd-2014/CreatureActionAttack.json', self.creature_action_attacks),
            "CreatureSets": (r'./jsons/srd-2014/CreatureSet.json', self.creature_sets),
            "CreatureTraits": (r'./jsons/srd-2014/CreatureTrait.json', self.creature_traits),
            "CreatureTypes": (r'./jsons/srd-2014/CreatureType.json', self.creature_types),
            "DamageTypes": (r'./jsons/srd-2014/DamageType.json', self.damage_types),
            "Documents": (r'./jsons/srd-2014/Document.json', self.documents),
            "Environments": (r'./jsons/srd-2014/Environment.json', self.environments),
            "Feats": (r'./jsons/srd-2014/Feat.json', self.feats),
            "FeatBenefits": (r'./jsons/srd-2014/FeatBenefit.json', self.feat_benefits),
            "Items": (r'./jsons/srd-2014/Item.json', self.items),
            "ItemCategories": (r'./jsons/srd-2014/ItemCategory.json', self.item_categories),
            "ItemRarities": (r'./jsons/srd-2014/ItemRarity.json', self.item_rarities),
            "ItemSets": (r'./jsons/srd-2014/ItemSet.json', self.item_sets),
            "Languages": (r'./jsons/srd-2014/Language.json', self.languages),
            "Rules": (r'./jsons/srd-2014/Rule.json', self.rules),
            "Sizes": (r'./jsons/srd-2014/Size.json', self.sizes),
            "Skills": (r'./jsons/srd-2014/Skill.json', self.skills),
            "Species": (r'./jsons/srd-2014/Species.json', self.species),
            "SpeciesTraits": (r'./jsons/srd-2014/SpeciesTrait.json', self.species_traits),
            "Spells": (r'./jsons/srd-2014/Spell.json', self.spells),
            "SpellCastingOptions": (r'./jsons/srd-2014/SpellCastingOption.json', self.spell_casting_options),
            "SpellSchools": (r'./jsons/srd-2014/SpellSchool.json', self.spell_schools),
            "Weapons": (r'./jsons/srd-2014/Weapon.json', self.weapons),
            "WeaponProperties": (r'./jsons/srd-2014/WeaponProperty.json', self.weapon_properties),
            "WeaponPropertyAssignments":
                (r'./jsons/srd-2014/WeaponPropertyAssignment.json', self.weapon_property_assignments)
        }

        path, var = categories.get(category, ("", ""))

        if path == "" or var == "":
            raise KeyError("Key not found")

        with open(path, 'r', encoding='utf-8', errors='replace') as cat:
            cat_data = json.load(cat)
            for trait in cat_data:
                var.append(trait['fields'])

    def load_json_multiple(self, categories: list):

        for cat in categories:
            self.load_json(cat)

        return
