import pandas as pd
import random
from . import poem_generator as pg
from . import object_detection as od

def parse_poem_csv():
    """
    Reads in the dataset of inspiring poems and chooses 10 random poems to read
    into files and populate the inspiring poems folder.
    """
    df = pd.read_csv("flaskr/PoetryFoundationData.csv")

    # choose 10 random indexes
    indexes = []
    for i in range(10):
        rand_idx = random.randint(0, 13855)
        if rand_idx not in indexes:
            indexes.append(rand_idx)

    # extract title and poem at each index
    for idx in indexes:
        title = df['Title'][idx]
        title = title.strip()
        if '/' in title: # skip because '/' is not allowed in file names
            continue

        # read poem to file with title as file name
        filename = "-".join(title.split())
        file_path = f'flaskr/inspiring_poems/{filename}.txt'
        new_file = open(file_path, 'w')
        poem = df['Poem'][idx]
        new_file.write(poem)
        new_file.close()


def main():
    """
    Executes the main steps of poetry generation using a PoemGenerator object.
    """
    num_sentences = 5

    # get themes from object detection
    themes = od.detect_objects_in_images()

    # if no images in folder or no objects were detected
    if themes == None:
        return ("temp", "*NO IMAGES*")

    generator = pg.PoemGenerator()

    # initialization steps

    generator.read_poem_files_to_strings()
    generator.parse_inspiring_poems()
    generator.parse_themes(themes)

    # generation step

    poem = generator.generate_poem(num_sentences, themes)

    # evaluation/revision steps

    themed_poem = generator.improve_poem_themes(poem)
    avg_pol, avg_sub = generator.evaluate_sentiment(themed_poem)

    goal_pol = (avg_pol + 0.01) * 1.05
    goal_sub = (avg_sub + 0.01) * 1.05

    updated_poem = generator.improve_poem_sentiment\
                            (themed_poem, goal_pol, goal_sub)

    # reformat step

    final_poem = generator.reformat_poem(updated_poem)

    # final artifact
    
    final_text = final_poem.text
    final_name = final_poem.name

    return (final_name, final_text)