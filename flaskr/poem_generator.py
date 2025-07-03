import spacy
import glob
import contractions
from random import choice
from random import randint
from textblob import TextBlob
from numpy.random import choice as npc

class Sentence():
    """
    Sentence class represents sentences with its text in string form, its list 
    of word tokens, and the original template of dependency structure that the 
    sentence was generated based on.
    """
    def __init__(self, text, token_list, original_template):
        self.text = text
        self.token_list = token_list
        self.original_template = original_template
    
    def __str__(self):
        return self.text


class Poem():
    """
    Poem class represents poems with a name, the list of themes that the poem 
    is inspired by, the poem in string form, and a list of Sentence objects
    representing each sentence in the poem.
    """
    def __init__(self, name, themes, text, sentence_list):
        self.name = name
        self.themes = themes
        self.text = text
        self.sentence_list = sentence_list # list of Sentence objects
        self.num_sentences = len(sentence_list)


    def return_sentence_list_text(self):
        """
        Returns a list of sentences in the string format
        """
        return [sentence.text for sentence in self.sentence_list]
    
    def join_list_to_text(self):
        """
        Updates the text attribute of the poem as the joined list of Sentences
        """
        self.text = "\n".join([sentence.text for \
                               sentence in self.sentence_list])
        return self.text
    
    def __str__(self):
        return self.text


class PoemGenerator():
    """
    PoemGenerator class performs all main features and processes involved in
    the program's poetry generation.
    """
    def __init__(self):
        self.inspiring_poems = dict() # file name to inspiring poem string
        self.generated_poems = dict() # poem name to generated poem string
        self.nlp = spacy.load("en_core_web_sm") # natural language processor
        # list of punctuations to consider for formatting
        self.PUNCTUATIONS = [".", ",", "-RRB-", "''", '""', ':']
        self.word_deps = dict() # word to dict of (dependency tag to word list)
        self.word_categories = dict() # POS tag label to word list
        self.templates = [] # dependency tree templates
        self.polarities = dict() # word to polarity score
        self.subjectivities = dict() # word to subjectivity score
        self.words_in_inspiring_poems = [] # all vocab from inspiring poems


    def read_poem_files_to_strings(self):
        """
        Read files of inspiring poems into dictionary
        """
        for filename in glob.glob("flaskr/inspiring_poems/*.txt"): 
            file = open(filename)
            text = file.read()
            self.inspiring_poems[filename] = text


    def parse_word(self, token):
        """
        Updates POS tag dictionary and sentiment dictionaries according to word
        """
        word = token.text.lower()
        tag = token.tag_
        # add to POS tag dictionary
        if tag in self.word_categories.keys():
            if word not in self.word_categories[tag]:
                self.word_categories[tag].append(word)
        else:
            self.word_categories[tag] = [word]

        # add to sentiment dictionaries
        word_blob = TextBlob(word)
        self.polarities[word] = word_blob.polarity
        self.subjectivities[word] = word_blob.subjectivity
    

    def parse_dep_tree(self, root):
        """
        Takes in a root token and traces the dependency tree by following the
        root's children. Updates the dependency and POS tag dictionaries for
        each word that is parsed.
        """
        children = root.children
        curr_word = root.text
        if curr_word not in self.word_deps.keys():
            self.word_deps[curr_word] = dict()
        deps_dict = self.word_deps[curr_word] # dependency tag to word list
        self.parse_word(root)
        # iterate through the current token's children
        for child in children:
            next_word = child.text
            # dependency tag based on the relationship between root and child
            dep = child.dep_
            if dep in deps_dict.keys():
                word_list = deps_dict[dep]
                if next_word not in deps_dict[dep]: word_list.append(next_word)
            else:
                deps_dict[dep] = [next_word]
            self.parse_dep_tree(child) # recursive call on each child


    def parse_themes(self, themes):
        """
        Parses theme words separately since they might not all be parsed as 
        part of the inspiring poems
        """
        for theme in themes:
            doc = self.nlp(theme)
            for token in doc:
                self.parse_word(token)


    def parse_inspiring_poems(self):
        """
        Parses all inspiring poems sentence by sentence and updates 
        dictionaries for POS tags and dependency tags, and list for sentence
        templates.
        """
        for _, text in self.inspiring_poems.items():
            doc = self.nlp(text)
            # use nlp to separate poem to sentences
            for sentence in doc.sents:
                sentence_str = sentence.text.strip()
                if sentence_str == "":
                    continue

                # remove contractions from the sentence
                expanded_words = []
                for word in sentence_str.split():
                    expanded_words.append(contractions.fix(word))
                sentence_str_without_contractions = \
                                               " ".join(expanded_words).lower()
                
                doc_sent = self.nlp(sentence_str_without_contractions)
                for updated_sentence in doc_sent.sents:
                    for token in updated_sentence:
                        # parse each token in the sentence
                        root = updated_sentence.root
                        self.parse_dep_tree(root)
                        self.parse_word(token)
                        self.words_in_inspiring_poems.append(token.text)
                    
                    # add sentence to the templates list along with the root
                    self.templates.append((sentence_str_without_contractions, \
                                                                        root))
        
    
    def choose_new_child_word(self, child, child_tag, curr_word, new_root_word):
        """
        Selects a new replacement word
        """
        dep = child.dep_
        # small probability of choosing any word that matches the original 
        # child's tag and larger probability of choosing word from words that 
        # have the same dependency relationship with the parent word
        random = npc([True, False], p=[0.2, 0.8])
        new_child_word = ""
        if random or new_root_word not in self.word_deps.keys():
            new_child_word = choice(self.word_categories[child_tag])
        else:
            # if new root word has an entry in word_deps
            if dep in self.word_deps[new_root_word].keys():	
                word_choices = self.word_deps[new_root_word][dep]
            # else, use the old root word's entry instead
            else:
                word_choices = self.word_deps[curr_word][dep]
            
            # filter choices for ones that match the tag of the original child
            updated_word_choices = [word for word in word_choices if word in \
                                        self.word_categories[child_tag]]
            
            # if nothing matches, choose from any word to matches the tag
            if len(updated_word_choices) == 0:
                new_child_word = choice(self.word_categories[child_tag])
            else:
                new_child_word = choice(updated_word_choices)
        return new_child_word


    def generate_sentence_from_root(self, root, new_root_word, str_template, \
                                                                  token_list):
        """
        Takes in a theme word and generates a new sentence using given
        string template and the theme as the root.
        """
        children = root.children
        curr_word = root.text
        token_list[root.i] = new_root_word
        str_template = " ".join(token_list)
        new_sentence = Sentence(str_template, token_list, str_template)
        for child in children:
            # choose a new word for each child
            child_tag = child.tag_
            if child_tag == "_SP":
                continue
            new_child_word = self.choose_new_child_word(child, child_tag, \
                                                    curr_word, new_root_word)
            # recursive call with child as new root
            new_sentence = self.generate_sentence_from_root\
                            (child, new_child_word, str_template, token_list)
        return new_sentence
    

    def generate_sentence_with_themes(self, root, new_root_word, themes, \
                                                str_template, token_list):
        """
        Takes a new root word and generates a new sentence with a string
        template that 
        """
        children = root.children
        curr_word = root.text
        token_list[root.i] = new_root_word
        str_template = " ".join(token_list)
        new_sentence = Sentence(str_template, token_list, str_template)
        for child in children:
            child_tag = child.tag_
            if child_tag == "_SP":
                continue
            # skip over any theme word so that it remains in the sentence
            if child.text in themes:
                str_template = self.generate_sentence_with_themes\
                        (child, child.text, themes, str_template, token_list)
                continue
            new_child_word = self.choose_new_child_word(child, child_tag, \
                                                    curr_word, new_root_word)
            new_sentence = self.generate_sentence_with_themes\
                    (child, new_child_word, themes, str_template, token_list)
        return new_sentence
    

    def add_theme_to_sentence(self, theme_word, theme_tag, themes, sentence):
        """
        Add a theme word to a given sentence without changing the rest of it
        """
        str_template = sentence.text
        token_list = sentence.token_list
        doc = self.nlp(str_template)
        idx = 0
        for token in doc:
            # change a word with the same tag as the theme word to the theme
            if token.tag_ == theme_tag and token.text not in themes:
                token_list[idx] = theme_word
                break
            idx += 1
            
        str_template = " ".join(token_list)

        sentence.text = str_template
        sentence.token_list = token_list

        return sentence


    def get_sentence_template(self, template_choices):
        """
        Chooses a random sentence template and returns it with the root and
        token list.
        """
        sentence, root = choice(template_choices)
        sentence_doc = self.nlp(sentence)
        token_list = []
        for token in sentence_doc:
            token_list.append(token.text)
            
        return (root, sentence, token_list)
    

    def reformat_name(self, name):
        """
        Reformats a given poem name to remove extra spaces next to the 
        punctuations.
        """
        token_list = name.split()

        new_token_list = []
        i = 0
        while i < len(token_list):
            curr_token = token_list[i]
            # reformatting hyphens
            if "HYPH" in self.word_categories.keys():
                if curr_token in self.word_categories["HYPH"]:
                    try:
                        prev_token = new_token_list[-1]
                    except IndexError:
                        prev_token = ""

                    try:
                        next_token = token_list[i+1]
                    except IndexError:
                        next_token = ""

                    # concatenate words before and after the hyphen 
                    new_token = prev_token + curr_token + next_token
                    try:
                        new_token_list.pop()
                    except:
                        pass
                    new_token_list.append(new_token)
                    i += 2 # skip over word after hyphen
                    continue
            
            # reformatting left brackets
            if "-LRB-" in self.word_categories.keys():
                if curr_token in self.word_categories['-LRB-']:
                    try:
                        next_token = token_list[i+1]
                    except IndexError:
                        next_token = ""

                    # concatenate left bracket and word after it
                    new_token = curr_token + next_token
                    new_token_list.append(new_token)
                    i = i + 2 # skip over word after left bracket
                    continue

            is_punct = False
            # reformatting remaining punctuations
            for punct in self.PUNCTUATIONS:
                if punct not in self.word_categories.keys(): continue
                if curr_token in self.word_categories[punct]:
                    try:
                        prev_token = new_token_list[-1]
                    except IndexError:
                        prev_token = ""
                    # concatenating word before punctuation with punctuation
                    new_token = prev_token + curr_token
                    try:
                        new_token_list.pop()
                    except:
                        pass
                    new_token_list.append(new_token)
                    is_punct = True
                    break
            
            if not is_punct:
                new_token_list.append(curr_token)
            
            i += 1
        
        return " ".join(new_token_list)
    

    def reformat_sentence(self, sentence_object):
        """
        Reformats a given poem name to remove extra spaces next to the 
        punctuations.
        """
        token_list = sentence_object.token_list

        new_token_list = []
        i = 0
        while i < len(token_list):
            curr_token = token_list[i]
            # reformatting hyphens
            if "HYPH" in self.word_categories.keys():
                if curr_token in self.word_categories["HYPH"]:
                    try:
                        prev_token = new_token_list[-1]
                    except IndexError:
                        prev_token = ""

                    try:
                        next_token = token_list[i+1]
                    except IndexError:
                        next_token = ""

                    # concatenate words before and after the hyphen 
                    new_token = prev_token + curr_token + next_token
                    try:
                        new_token_list.pop()
                    except:
                        pass
                    new_token_list.append(new_token)
                    i += 2 # skip over word after hyphen
                    continue
            
            # reformatting left brackets
            if "-LRB-" in self.word_categories.keys():
                if curr_token in self.word_categories['-LRB-']:
                    try:
                        next_token = token_list[i+1]
                    except IndexError:
                        next_token = ""
                    # concatenate left bracket and word after it
                    new_token = curr_token + next_token
                    new_token_list.append(new_token)
                    i = i + 2 # skip over word after left bracket
                    continue

            is_punct = False
            # reformatting remaining punctuations
            for punct in self.PUNCTUATIONS:
                if punct not in self.word_categories.keys(): continue
                if curr_token in self.word_categories[punct]:
                    try:
                        prev_token = new_token_list[-1]
                    except IndexError:
                        prev_token = ""

                    # concatenating word before punctuation with punctuation
                    new_token = prev_token + curr_token
                    try:
                        new_token_list.pop()
                    except:
                        pass
                    new_token_list.append(new_token)
                    is_punct = True
                    break
            
            if not is_punct:
                new_token_list.append(curr_token)
            
            i += 1
        
        sentence_object.text = " ".join(new_token_list)

        return sentence_object
    

    def reformat_poem(self, poem):
        """
        Reformats poem by reformatting each sentence.
        """
        new_sentence_list = []
        for sentence in poem.sentence_list:
            new_sentence = self.reformat_sentence(sentence)
            new_sentence_list.append(new_sentence)
        poem.sentence_list = new_sentence_list
        poem.join_list_to_text()

        new_name = self.name_poem(poem.sentence_list)
        new_name = self.reformat_name(new_name)
        poem.name = new_name

        return poem
    

    def name_poem(self, sentence_list):
        """
        Selects a random sequence of words from the poem to be the poem's name.
        """
        sentence = choice(sentence_list).token_list
        sentence_len = len(sentence)
        # set the max length of name at 8 words
        name_len = randint(1, 8) if sentence_len >= 8 \
                                 else randint(1, sentence_len)
        start_idx = randint(0, sentence_len-name_len)
        name_list = sentence[start_idx : start_idx + name_len]
        return " ".join(name_list)


    def generate_poem(self, num_sents, themes):
        """
        Generates a new poem given the number of sentences and the list of
        inspiring themes.
        """
        new_poem_list = []

        # add option to not include any theme word in sentence
        theme_choices = themes + [None] 
        
        for i in range(num_sents):
            new_sentence = None
            theme_word = choice(theme_choices) # choose random theme word

            # generate sentence without consideration for theme words
            if theme_word == None: 
                root, sentence, token_list = self.get_sentence_template\
                                                        (self.templates)
                new_root_word = choice(self.word_categories[root.tag_])
                new_sentence = self.generate_sentence_from_root\
                                    (root, new_root_word, sentence, token_list)
                new_sentence.original_template = sentence
            
            # if theme word isn't in the inspiring poems
            elif theme_word not in self.words_in_inspiring_poems: 
                root, sentence, token_list = self.get_sentence_template\
                                                        (self.templates)
                new_root_word = choice(self.word_categories[root.tag_])
                new_sentence = self.generate_sentence_from_root\
                                    (root, new_root_word, sentence, token_list)
                theme_doc = self.nlp(theme_word)
                theme_tag = ""
                for token in theme_doc:
                    theme_tag = token.tag_
                new_sentence = self.add_theme_to_sentence\
                                    (theme_word, theme_tag, [], new_sentence)
                new_sentence.original_template = sentence

            else: # generate sentence including at least one theme word
                option = choice(["root", "with"])
                if option == "root": # inspiring word as root of sentence
                    # choose random template whose root has same tag as theme
                    updated_templates = [template for template in \
                                        self.templates if theme_word in \
                                        self.word_categories[template[1].tag_]]
                    root, sentence, token_list = self.get_sentence_template\
                                                        (updated_templates)
                    new_sentence = self.generate_sentence_from_root\
                                    (root, theme_word, sentence, token_list)
                    new_sentence.original_template = sentence
                else: # inspiring word kept at original position in sentence
                    # find sentence templates containing theme word
                    templates_with_word = [template for template in \
                                          self.templates if theme_word \
                                          in template[0]]   
                    root, sentence, token_list = self.get_sentence_template\
                                                        (templates_with_word)
                    # choose random new root word
                    new_root_word = choice(self.word_categories[root.tag_])
                    new_sentence = self.generate_sentence_with_themes\
                                    (root, new_root_word, \
                                    [theme_word], sentence, token_list)
                    new_sentence.original_template = sentence

            new_poem_list.append(new_sentence)
            
        new_poem_str = "\n".join([sentence.text for sentence in new_poem_list])

        # generate a name for the poem
        name = ""
        is_unique_name = False
        while not is_unique_name:
            name = self.name_poem(new_poem_list)
            if name not in self.generated_poems.keys():
                is_unique_name = True

        # create new Poem object
        new_poem_object = Poem(name, themes, new_poem_str, new_poem_list)

        self.generated_poems[name] = new_poem_object

        return new_poem_object
    

    def check_poem_themes(self, poem):
        """
        Checks if poem contains all inspiring themes.
        """
        themes = poem.themes
        sentence_list = poem.sentence_list

        num_themes = len(themes)

        # list of booleans corresponding to each theme
        bool_template = [False for i in range(num_themes)]

        num_sentences = poem.num_sentences

        # list of all boolean lists for all sentences in poem
        themes_in_sentences = [bool_template for i in range(num_sentences)]

        # stores whether each theme is contained in the poem
        themes_in_poem = bool_template.copy()

        contains_all_themes = False # whether poem contains all themes

        # iterates over all sentences
        for sentence_num in range(num_sentences):
            # stores whether each theme is contained in current sentence
            contains_themes = bool_template.copy()
            sentence_tokens = sentence_list[sentence_num].token_list
            for token in sentence_tokens: 
                # iterates over all themes for each sentence
                for theme_idx in range(num_themes):
                    if token == themes[theme_idx]:
                        # sentence does contain current theme
                        contains_themes[theme_idx] = True
                        # poem does contain current theme
                        themes_in_poem[theme_idx] = True
            themes_in_sentences[sentence_num] = contains_themes

        if False not in themes_in_poem: contains_all_themes = True

        return contains_all_themes, themes_in_poem, themes_in_sentences
    

    def improve_poem_themes(self, poem):
        """
        Revises poem so that all themes are included in the poem.
        """
        themes = poem.themes
        sentence_list = poem.sentence_list
        num_themes = len(themes)
        num_sentences = poem.num_sentences

        contains_all_themes, themes_in_poem, themes_in_sentences = \
                                                   self.check_poem_themes(poem)

        # if poem already contains all themes, no need to do anything
        if contains_all_themes: return poem

        sentences_with_no_theme = [sentence_num for sentence_num in \
                                    range(num_sentences) if True not in \
                                    themes_in_sentences[sentence_num]]

        # iterates over all themes
        for theme_idx in range(num_themes):
            theme = themes[theme_idx]

            # if this theme is already in the poem, don't do anything
            if themes_in_poem[theme_idx]: continue

            new_sentence = None
            selected_sentence_num = 0

            # if there are sentences without any theme, prioritize changing 
            # them to add themes
            if len(sentences_with_no_theme) > 0:
                selected_sentence_num = choice(sentences_with_no_theme)
                root, sentence, token_list = self.get_sentence_template\
                                                        (self.templates)
                new_sentence = self.generate_sentence_from_root(root, theme, \
                                                         sentence, token_list)
                sentences_with_no_theme.remove(selected_sentence_num)

            # if all sentences already have at least one theme
            else:
                # select a sentence to be modified
                selected_sentence = choice(sentence_list)
                selected_sentence_num = sentence_list.index(selected_sentence)
                theme_doc = self.nlp(theme)
                theme_tag = ""
                for token in theme_doc:
                    theme_tag = token.tag_
                # keep the sentence but replace one word with the new theme
                new_sentence = self.add_theme_to_sentence(theme, theme_tag, \
                                                    themes, selected_sentence)
            
            # replace selected sentence in poem with new sentence
            sentence_list[selected_sentence_num] = new_sentence
        
        poem.sentence_list = sentence_list
        poem.text = "\n".join([sentence.text for sentence in poem.sentence_list])

        return poem
    
    
    def evaluate_sentiment(self, poem):
        """
        Calculates the average polarity and subjectivity of the poem.
        """
        sum_polarity = 0
        sum_subjectivitiy = 0
        for sentence_obj in poem.sentence_list:
            sentence = sentence_obj.text
            sentence_blob = TextBlob(sentence)
            sent_doc = self.nlp(sentence)
            sum_pol = 0
            for token in sent_doc:
                token_blob = TextBlob(token.text)
                token_pol = token_blob.polarity
                sum_pol += token_pol
            sum_polarity += sentence_blob.polarity
            sum_subjectivitiy += sentence_blob.subjectivity
        avg_polarity = sum_polarity / poem.num_sentences
        avg_subjectivity = sum_subjectivitiy / poem.num_sentences
        return avg_polarity, avg_subjectivity


    def improve_word_sentiment(self, token_list, sentiment_dict, curr_avg):
        """
        Takes a sentence and selects a new replacement word with a higher 
        sentiment value than that of the current word. Could be used for 
        polarity or subjectivity depending on which sentiment dictionary is 
        given.
        """
        # stores whether overall sentiment is positive or negative
        positive = True
        if curr_avg < 0:
            positive = False

        word_chosen = False
        while not word_chosen:
            idx = randint(0, len(token_list)-1)
            curr_word = token_list[idx]

            doc = self.nlp(curr_word)
            tag = ""
            for token in doc:
                tag = token.tag_

            # only choose the word if its tag is in the POS tag dictionary
            if tag in self.word_categories.keys():
                word_chosen = True
        
        words_with_tag = self.word_categories[tag]

        if positive:
            # new word choices only include those with higher sentiment value
            try:
                word_choices = [word for word in words_with_tag if \
                            sentiment_dict[word] > sentiment_dict[curr_word]]
            except KeyError:
                word_choices = [curr_word]
        else:
            # new word choices only include those with lower sentiment value
            try:
                word_choices = [word for word in words_with_tag if \
                            sentiment_dict[word] < sentiment_dict[curr_word]]
            except KeyError:
                word_choices = [curr_word]

        # if no word choice has better sentiment value, don't update sentence
        if len(word_choices) == 0:
            return token_list

        new_word = choice(word_choices)
        
        token_list[idx] = new_word

        return token_list


    def improve_poem_sentiment(self, poem, goal_pol, goal_sub):
        """
        Revises the poem so that the polarity and subjectivity of the poem
        reach the given goals.
        """
        new_sentence_list = poem.sentence_list.copy()

        avg_pol, avg_sub = self.evaluate_sentiment(poem)

        counter = 0

        # max 10 times to avoid infinite loop
        while (abs(avg_pol) < abs(goal_pol) or abs(avg_sub) < abs(goal_sub)) \
                and counter < 10:
            counter += 1

            # choose a sentence to revise to increase polarity
            pol_sentence = choice(new_sentence_list)
            pol_idx = new_sentence_list.index(pol_sentence)
            new_pol_token_list = self.improve_word_sentiment\
                            (pol_sentence.token_list, self.polarities, avg_pol)
            new_pol_sentence = Sentence(" ".join(new_pol_token_list), \
                            new_pol_token_list, pol_sentence.original_template)
            new_sentence_list[pol_idx] = new_pol_sentence

            # choose a sentence to revise to increase subjectivity
            sub_sentence = choice(new_sentence_list)
            sub_idx = new_sentence_list.index(sub_sentence)
            new_sub_token_list = self.improve_word_sentiment\
                        (sub_sentence.token_list, self.subjectivities, avg_sub)
            new_sub_sentence = Sentence(" ".join(new_sub_token_list), \
                            new_sub_token_list, sub_sentence.original_template)
            new_sentence_list[sub_idx] = new_sub_sentence

            poem.sentence_list = new_sentence_list
            poem.join_list_to_text()

            # calculate new average sentiment values
            avg_pol, avg_sub = self.evaluate_sentiment(poem)

        return poem