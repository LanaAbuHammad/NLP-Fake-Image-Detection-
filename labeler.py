import io
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:\\Users\\ThinkPad\\Desktop\\COURSE PROJECT\\DETECTOR\\GoogleCloudKey.json"
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
#Imports the Google Cloud client library
from google.cloud import vision
classes = [
        'real',
        'fake'
    ]
cm =[]
report = ""
#Imports the Google Translate Library
from google.cloud import translate_v2 as translate
translate_client = translate.Client()
from sklearn.naive_bayes import MultinomialNB
nb = MultinomialNB() #build a NB classifier
stop_words = []
count_vect = CountVectorizer(stop_words=["in", "the", "a", "an"]) #remove stop words
tfidf_transformer = TfidfTransformer() #reduce the weightage of more common words

#Translate Caption to English
def translate(text):
    target = "en" #target language is english
    translated = translate_client.translate(
        text, target_language=target)
    print(translated)
    return translated

#Get Labels of Selected Image by User
def label_image(image_path):
    client = vision.ImageAnnotatorClient()
    Labels1 = []
    str = ""
    # Loads the image into memory
    with io.open(image_path, 'rb') as image_file:
        print("---------------------------------------")
        content = image_file.read()
        image = vision.Image(content=content)
        # Performs label detection on the image file
        response = client.label_detection(image=image)
        labels = response.label_annotations

        for label in labels:
            str = str +"\n" + label.description
        Labels1.append(str[2:])
        print(str)
        return str


def classification(image, caption):

    labels = label_image(image)
    #print(labels)
    translated_caption = translate(caption)
    X_test = [labels +" "+translated_caption['translatedText']]

    # transform X_text for prediction
    X_test_tfidf = count_vect.transform(X_test)

    # prediction
    y_pred = nb.predict(X_test_tfidf)
    #print("DECISION IS: "+ y_pred[0] +" WITH ~85% CONFIDENCE")

    return str(y_pred[0])

def print_cm(cm, labels, hide_zeroes=False, hide_diagonal=False, hide_threshold=None):
    """pretty print for confusion matrixes"""
    columnwidth = max([len(x) for x in labels] + [5])  # 5 is value length
    empty_cell = " " * columnwidth
    # Print header
    #print("    " + empty_cell, end=" ")
    str = "    " + empty_cell + " "
    for label in labels:
        #print("%{0}s".format(columnwidth) % label, end=" ")
        str = str + "%{0}s".format(columnwidth) % label + " "
    #print()
    str = str + "\n"
    # Print rows
    for i, label1 in enumerate(labels):
        #print("    %{0}s".format(columnwidth) % label1, end=" ")
        str = str + "    %{0}s".format(columnwidth) % label1 + " "
        for j in range(len(labels)):
            cell = "%{0}.1f".format(columnwidth) % cm[i, j]
            if hide_zeroes:
                cell = cell if float(cm[i, j]) != 0 else empty_cell
            if hide_diagonal:
                cell = cell if i != j else empty_cell
            if hide_threshold:
                cell = cell if cm[i, j] > hide_threshold else empty_cell
         #   print(cell, end=" ")
            str = str + cell + " "
        #print()
        str = str + "\n"
    return str

def trainingPhase(csvfilePath):
    global cm, report
    col = ['Labels', 'Translation', 'Decision']
    dataset = pd.read_csv(csvfilePath)
    dataset = dataset.dropna() #drop rows or col with null values
    dataset = dataset.reset_index(drop=True) #drops the current index of the Datasey and replaces it with an index of increasing integers.

    x = pd.concat([dataset.iloc[:, 0],dataset.iloc[:, 1]], axis=1).T.to_dict('l')
    y = dataset.iloc[:, 2]
    ycopy = []
    for i in y:
      ycopy.append(i.strip())
    ycopy = np.asarray(ycopy)
    X = []
    str = ""
    for k, v in x.items():
        X.append(str.join(i.lower() for i in v))

    test_size = 4;
    train_size = 10 - test_size
    X_train, X_test, y_train, y_test = train_test_split(X, ycopy , test_size=test_size / 10, train_size= train_size / 10, random_state=4)

    X_train_counts = count_vect.fit_transform(X_train)
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
    X_train_tfidf.toarray()

    nb.fit(X_train_tfidf, y_train)
    nb.score(X_train_tfidf, y_train)

    # transform X_text for prediction
    X_test_tfidf = count_vect.transform(X_test)

    # prediction
    y_pred = nb.predict(X_test_tfidf)

    classes = [
        'real',
        'fake'
    ]

    from sklearn.metrics import classification_report
    #print(classification_report(y_test, y_pred))
    report = classification_report(y_test, y_pred)
    from sklearn.metrics import confusion_matrix, accuracy_score
    cm = confusion_matrix(y_test, y_pred)
    print_cm(cm,classes)
    Accuracy_Score = accuracy_score(y_test, y_pred)
    return round(Accuracy_Score * 100,2)


#translate("صور | فضولين في محل بقالة ... شاهدوا ما أظرفهم جريدة_القدس غزال")
#label_image("C:\\Users\\ThinkPad\\Desktop\\pic.jpg")