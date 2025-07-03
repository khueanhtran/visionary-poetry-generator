# Vision-ary Poetry Generator!

## Description
This is a poetry generator system that takes in image files, detects objects from the images, and uses these as themes to generate poetry. The system is inspired by the human approach of using observations of real life to create poetry and art in general. Through combining computer vision and poetry generation, the system aims to emulate how humans are influenced by our surroundings and experiences, which is integral to human creativity.

Object detection is done using a pre-trained Faster-RCNN network. Poetry generation uses inspiring poems from a Poetry Foundation database to parse the dependency structures of sentences, which are used as templates to generate new sentences. The evaluation of the system takes place via an editing approach, in which the system revises the original generated poem to improve it. The two modes of evaluation that the system uses are theme-based analysis, in which it attempts to include all the identified themes from the images in the poem, and sentiment analysis, in which it maximizes the polarity and subjectivity of the poem to reflect the personal and emotional aspect of human-made poetry. The system is experienced via a website, which prompts the user to input image files as inspiration for the poem, displays the generated poem, offers the option of voicing the poem, and also allows the user to view previously generated poems. 

## Running the Code

To run the system, first download this project directory and navigate to the directory in the terminal. Make sure Python is installed on your computer.

Next, run the following commands to install the necessary modules:

```
pip install spacy
pip install textblob
pip install contractions
pip install numpy
pip install pandas
pip install flask
pip install werkzeug
pip install torch
pip install PIL
pip install torchvision
```

Once all the modules have been installed, run the following command to start the local server:

```
flask --app flaskr run
```

Once the server has started, in a browser, open the URL that the server is running on. This will be in the format of ```localhost:yourPort/```. For example,

*Running on http://127.0.0.1:5000*

The website should appear and allow you to navigate the poetry generator! 


## Challenges

There were multiple challenges that I faced as a programmer during this project. First of all, I incorporated an element that has not been thoroughly discussed during our class, which is computer vision. This is something that has briefly come up as a possible feature to be implemented in computational creativity, which has piqued my curiosity since I am currently enrolled in a class on Computer Vision. Therefore, I wanted to bring this aspect into my project, even if this is surely not the most complex implementation possible of computer vision in computational creativity,

Furthermore, this project is my first time using Flask, HTML, and Javascript for a program (with the exception of the small Explore exercises we have done in class). There were thus quite big learning curves for me working on this project, as I had to essentially learn from scratch how to code what I wanted my program to do. While aesthetically speaking, my website is not very developed, it was quite time-intensive for me to implement all the functionalities. Some functionalities were particularly challenging to incorporate in my website, such as the file upload feature to allow users to upload images that they want to inspire their poems. 

In terms of the poetry generation aspect, it was a non-trivial task to generate sentences by parsing the dependency trees of sentences. I had to understand how `spaCy` works and how words within a sentence are related to each other through dependency structures. This method of generation allowed me to have a better understanding of what was going on in my system, as opposed to something like using a neural network to generate sentences. At the same time, following the dependency structures but allowing randomness/creativity in terms of word choices resulted in sentences that were different from the original templates that they may have been based on, which is more novel than an approach such as n-grams.


## Scholarly Inspiration

In my research, I encountered three scholarly articles that informed the approach I wanted to take with my system:

1. Anna Kantosalo - *Human-Computer Co-Creativity : Designing, Evaluating and Modelling Computational Collaborators for Poetry Writing* (https://helda.helsinki.fi/items/73f429d8-49ae-4ba0-b4ee-de22a3ac5764): This paper discussed the approach of having human users inform the creative production of the system, which touches upon the Producer aspect of the PPPPerspectives. From this, I thought of the idea to have users submit their own images to inform what the poems in my system were based on. On a high level, we can understand this as having human users influence what perspective/understanding of the world the computer system has, which would then affect the way that it generates poetry.
2. Pablo Gervás - *Computational Modelling of Poetry Generation* (https://www.researchgate.net/publication/288288388_Computational_modelling_of_poetry_generation): This paper proposes a framework model for poetry generation that involves modules inspired by human roles. The role of *revisers* that is mentioned in the article was highly influential to my decision of having the evaluative feature directly edit on the original generated poem instead of merely generating new poems. This implementation makes the evaluation take on a form that more closely resembles a human approach to poetry creating.
3. Hannu Toinoven and Oskar Gross - *Data mining and machine learning in computational creativity* (https://wires.onlinelibrary.wiley.com/doi/full/10.1002/widm.1170): This paper discusses the use of data mining and machine learning for transformational creativity in the way that Wiggins defines it (as we have talked about in class). This opens up the possibility for these two tools to go beyond mere generation and beyond the uses that they usually have in computational creativity, such as to generalize an evaluation function for the generated artifacts. I did not specifically implement something from this paper, but I thought it was relevant to my general approach of combining deep learning (though that is not 100% the same as machine learning) with poetry generation. Again, my use of deep learning in the project is not quite integral to the process of poetry generation itself, but I still found that this paper points towards the interest of incorporating machine learning into computational creativity in general.
4. (Bonus) Eitan Wilf - *“I randomize, therefore I think”: Computational indeterminacy and the tensions of liberal subjectivity among writers of computer-generated poetry in the United States* (https://anthrosource.onlinelibrary.wiley.com/doi/full/10.1111/amet.13115): This is more of an Anthropology paper than a Computer Science one, and I did not necessarily implement something specific from this, but I found it really interesting in how it combines ideas of randomization/indeterminacy in computational creativity with understandings and notions of social justice, specifically the idea that computers' randomness is still deeply informed by our cultural landscape and the implicit dominant belief system that lies beneath it. I thought this was a fascinating combination of computer science/computational creativity with more humanities-based analysis and study, which is like the intersection of my two majors (Computer Science and GSWS).
