import _pickle

import matplotlib.pyplot as plt
from mtcnn.mtcnn import MTCNN
from PIL import Image
import numpy as np
import os
import pickle
from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
from scipy.spatial.distance import cosine

filepath = os.path.dirname(__file__)


class Detector:
    def __init__(self, model_path, source_path, dest_path, hist_bool) -> None:
        self.required_size = (224, 224)
        self.is_history = hist_bool
        self.extentions = ['jpg', 'png', 'jpeg']

        self.face_detector = MTCNN()

        self.model = VGGFace(model='resnet50', include_top=False, input_shape=(224, 224, 3), pooling='avg')

        # listy plików zdjęciowych - scieżek
        if self.is_history is False:
            self.model_filespath_list = self.get_files_path(model_path)

        if self.is_history is True:
            self.history_filespath = model_path

        self.destination_path = dest_path

        # dodanie ścieżek zdjęć testowych do pola source_filespath_list
        self.source_filespath_list = []
        for directory in source_path:
            dir_files = self.get_files_path(directory)
            for d in dir_files:
                ext = d.split('.')[-1]
                if ext in self.extentions:
                    self.source_filespath_list.append(d)

        # lista embedding dla modelu
        self.model_embedding = []
        self.source_embedding = []

        # finalna lista zdjęć do wyselekcjonowanych plików
        self.final_files_list = []
        self.dirlabel = os.path.split(model_path)[1].split('.')[0]
        # self.dirlabel = self.dirlabel.split('.')[0]
        # lista pliku modelowego do zapisania w historii

        self.counter = 0

    def get_files_path(self, path):
        files_path_array = [os.path.join(path, l) for l in os.listdir(path) if l.split('.')[-1] in self.extentions]
        return files_path_array

    # -----------------------------------------------------------------
    # dla MODEL
    def extract_face_model(self, filename):
        # load image from file
        image = plt.imread(filename)
        # create the detector, using default weights
        # face_detector = MTCNN()
        # detect faces in the image
        results = self.face_detector.detect_faces(image)
        # extract the bounding box from the first face
        x1, y1, width, height = results[0]['box']
        x2, y2 = x1 + width, y1 + height
        # extract the face
        face = image[y1:y2, x1:x2]
        # resize pixels to the model size
        image = Image.fromarray(face)
        image = image.resize(self.required_size)
        face_array = np.asarray(image)
        return face_array

    def get_embeddings_model(self, filenames):
        # extract faces
        faces = [self.extract_face_model(f) for f in filenames]
        # convert into an array of samples
        samples = np.asarray(faces, 'float32')
        # prepare the face for the model, e.g. center pixels
        try:
            samples = preprocess_input(samples)
        except IndexError:
            return -1
        pred_embeddings = self.model.predict(samples)
        return pred_embeddings

    # -----------------------------------------------------------------
    # dla funkcji SOURCE
    def extract_face_source(self, filepath, required_size=(224, 224)):
        pixels = plt.imread(filepath)
        faces = self.face_detector.detect_faces(pixels)
        faces_array = []

        for face in faces:
            x1, y1, width, height = face['box']
            x2, y2 = x1 + width, y1 + height
            # extract the face
            face_box = pixels[y1:y2, x1:x2]
            # plt.imshow(face_box)
            # plt.show()

            # resize image to the model size
            image = Image.fromarray(face_box)
            # print(image)
            image = image.resize(required_size)
            face_array = np.asarray(image)
            # print(face_array)
            faces_array.append(face_array)

        # face_array = np.array(faces_array)
        # print(len(faces_array))
        return faces_array

    def get_embeddings_source_one_photo(self, filename):
        # extract faces
        faces = self.extract_face_source(filename)
        # convert into an array of samples
        samples = np.asarray(faces, 'float32')
        # prepare the face for the model, e.g. center pixels
        try:
            samples = preprocess_input(samples)
        except IndexError:
            return -1
        embed = self.model.predict(samples)
        return embed

    # -----------------------------------------------------------------

    def set_model_embedding(self, emb):
        self.model_embedding = emb

    def load_embeddings_from_history(self):
        with open(self.history_filespath, "rb") as f:
            try:
                model_emb = pickle.load(f)
                # print("pickle: ", type(model_emb))
                self.model_embedding = model_emb
            # print(type(self.model_embedding))
            except _pickle.UnpicklingError:
                return -1
            return self.model_embedding

    def write_history(self):
        write_path = os.path.join(filepath, "models/")
        face_label_filename = write_path + self.dirlabel
        with open(face_label_filename, 'wb') as f:
            pickle.dump(self.model_embedding, f)

    def write_final_selection(self):
        # self.destination_path = self.destination_path + '/' + dirname
        for img in self.final_files_list:
            # print('img ', img)
            img_name = os.path.split(img)[1]
            print('img_name ', img_name)
            destination_file_path = self.destination_path + '/' + 'symlink_' + img_name
            # print('dest file ', destination_file_path)
            try:
                os.symlink(img, destination_file_path)
            except FileExistsError:
                pass
        return True

    def select_faces(self):
        if self.is_history is True:
            emb = self.load_embeddings_from_history()
            if emb == -1:
                print("Zły plik Pickle")
                return "Zły plik Pickle"
            self.set_model_embedding(emb)

        if self.is_history is False:
            try:
                model_embedds = self.get_embeddings_model(self.model_filespath_list)
                print(model_embedds)
                # if model_embedds==-1:
                #     print("Błąd w folderze")
                #     return "Błąd w folderze zawierającym model"

                self.set_model_embedding(model_embedds)
            except ValueError:
                return "Błąd w folderze zawierającym model"

        # if not self.model_embedding:
        #     return "Pusty model"

        for image_path in self.source_filespath_list:
            print(image_path)
            try:
                embeddings_one_photo = self.get_embeddings_source_one_photo(image_path)
                # print("len ", len(embeddings_one_photo))

                for emb in embeddings_one_photo:
                    try:
                        dist = 1
                        for mod in self.model_embedding:
                            dist_mod = cosine(mod, emb)

                            if dist_mod < dist:
                                dist = dist_mod
                                # print("dist ", dist)
                        if dist < 0.5:
                            print("dist<0.5", dist)
                            self.final_files_list.append(image_path)
                            self.counter = self.counter + 1
                            # embeddings_array.append(embeddings_one_photo)
                    except TypeError:
                        print("TypeError")
                        return "TypeError"

            except (IndexError, TypeError) as error:
                print(error)
                pass
        if self.is_history is False:
            self.write_history()

        is_written = self.write_final_selection()

        if is_written is not True:
            self.model_embedding = []
            return "Błąd w zapisie wyselekcjonowanych danych"

        self.model_embedding = []
        print("Zakończone sukcesem")
        print("COUNTER: ", self.counter)
        return True
