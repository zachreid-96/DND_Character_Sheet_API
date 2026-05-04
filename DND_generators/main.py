from DND_generators.Classes_2014.Bard import Bard2014
from DND_generators.Classes_2014.Barbarian import Barbarian2014
from DND_generators.Classes_2014.Fighter import Fighter2014

if __name__ == "__main__":

    bard = Bard2014()
    bard.build_character(20)
    #bard.level_up(5)
    #print(bard.__dict__)
    sheet = bard.dict_output()
    for k, v in sheet.items():
        print(f"{k}: {v}")

    pass
