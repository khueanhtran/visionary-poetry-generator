import torch
from PIL import Image
from torchvision.models.detection import fasterrcnn_resnet50_fpn 
from torchvision.models.detection import FasterRCNN_ResNet50_FPN_Weights
import glob
from textblob import TextBlob

def detect_objects_in_images():
    """
    Processes image files from the images folder and enters them as inputs
    for a Faster-RCNN network for object detection. Processes the detected
    labels and returns as a list of themes.
    """

    device = 'cpu'

    # load images into PIL files

    PIL_images = []
    for filename in glob.glob("flaskr/images/*"): 
        img = Image.open(filename)
        PIL_images.append(img)
    
    # if no files in the images folder
    if len(PIL_images) == 0:
        return None
        
    # load Faster RCNN model

    weights_rcnn = FasterRCNN_ResNet50_FPN_Weights.DEFAULT
    model_rcnn = fasterrcnn_resnet50_fpn(weights=weights_rcnn)
    model_rcnn.to(device)

    # preprocess images for Faster RCNN

    transforms_rcnn = weights_rcnn.transforms()
    input_list_rcnn = []
    for img in PIL_images:
        transformed_img = transforms_rcnn(img)
        input_list_rcnn.append(transformed_img)
        
    # run images through Faster RCNN model

    model_rcnn.eval()
    results_rcnn = model_rcnn(input_list_rcnn)

    score_threshold = 0.5

    weights = FasterRCNN_ResNet50_FPN_Weights.DEFAULT

    # get all the possible object classes from the model
    classes_rcnn = weights.meta['categories']

    label_tensors = []
    score_tensors = []

    # extract labels and scores from the network's outputs
    for i in range(len(results_rcnn)):
        result = results_rcnn[i]
        scores = result['scores']
        labels_idx = result['labels'][scores > score_threshold]
        label_tensors.append(labels_idx)
        scores = result['scores'][scores > score_threshold]
        score_tensors.append(scores)

    all_labels = []

    # transform label tensors into numpy arrays
    for labels_idx in label_tensors:
        if torch.is_tensor(labels_idx):
            labels_idx = labels_idx.detach().numpy()
            for idx in labels_idx:
                all_labels.append(classes_rcnn[idx])

    all_scores = []

    # transform score tensors into numpy arrays
    for scores in score_tensors:
        if torch.is_tensor(scores):
            scores = scores.detach().numpy()
            for score in scores:
                all_scores.append(float(score))

    labels_set = set(all_labels.copy())

    label_to_score = dict()

    # parse all distinct labels
    for label in labels_set:

        # find highest corresponding score for a certain label

        label_score = 0
        # parse all instances of current label
        for instance in all_labels:
            if instance == label:
                idx = all_labels.index(instance)
                if all_scores[idx] > label_score:
                    label_score = all_scores[idx]

        # pluralize the label if more than one instance

        if all_labels.count(label) > 1:
            blob = TextBlob(label)
            label_list = blob.words.pluralize()
            pluralized_token = label_list[0]
            pluralized_label = ""
            for char in pluralized_token:
                pluralized_label += char
            label_to_score[pluralized_label] = label_score
            
        else: # if only one instance of label
            label_to_score[str(label)] = label_score

    final_labels = list(label_to_score.keys())
    max_num_themes = 5

    # if more themes than max number
    if len(final_labels) > max_num_themes:
        # sort labels by descending order of corresponding scores
        sorted_dict = {k: v for k, v in sorted(label_to_score.items(), \
                                    key=lambda item: item[1], reverse=True)}
        # pick the highest scoring labels as the themes
        final_labels = list(sorted_dict.keys())[:max_num_themes]
    
    return final_labels