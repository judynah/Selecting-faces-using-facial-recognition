# from tkinter import tk, filedialog, font
from tkinter import *
from tkinter import filedialog
import os
import detection

filepath = os.path.dirname(__file__)


def btn_clicked():
    print("Button Clicked")


class Interface:
    def __init__(self):

        self.text = ""
        self.model_path = ""
        self.source_path = []
        self.destination_path = ""
        self.is_history = False

        self.window = Tk()

        self.window.geometry("1500x850")
        self.window.configure(bg="#ffffff")
        self.canvas = Canvas(
            self.window,
            bg="#ffffff",
            height=850,
            width=1500,
            bd=0,
            highlightthickness=0,
            relief="ridge")
        self.canvas.place(x=0, y=0)

        background_file = os.path.join(filepath, "images/background.png")
        background_img = PhotoImage(file=background_file)
        background = self.canvas.create_image(
            752.5, 427.5,
            image=background_img)

        img_path0 = os.path.join(filepath, "images/img0.png" )
        img0 = PhotoImage(file=img_path0)
        self.canvas.pack(fill=BOTH)
        button0 = self.canvas.create_image(224, 97, anchor='nw', image=img0)
        self.canvas.tag_bind(button0, '<Button-1>', lambda e: self.choose_model_folder())

        img_path1 = os.path.join(filepath, "images/img1.png")
        img1 = PhotoImage(file=img_path1)
        self.canvas.pack(fill=BOTH)
        button1 = self.canvas.create_image(224, 198, anchor='nw', image=img1)
        self.canvas.tag_bind(button1, '<Button-1>', lambda e: self.choose_source_folder())

        img_path2 = os.path.join(filepath, "images/img2.png")
        img2 = PhotoImage(file=img_path2)
        self.canvas.pack(fill=BOTH)
        button2 = self.canvas.create_image(224, 308, anchor='nw', image=img2)
        self.canvas.tag_bind(button2, '<Button-1>', lambda e: self.choose_dest_folder())

        img_path3 = os.path.join(filepath, "images/img3.png")
        img3 = PhotoImage(file=img_path3)
        self.canvas.pack(fill=BOTH)
        button3 = self.canvas.create_image(224, 418, anchor='nw', image=img3)
        self.canvas.tag_bind(button3, '<Button-1>', lambda e: self.choose_from_history())

        img_path4 = os.path.join(filepath, "images/img4.png")
        img4 = PhotoImage(file=img_path4)
        self.canvas.pack(fill=BOTH)
        button4 = self.canvas.create_image(224, 537, anchor='nw', image=img4)
        self.canvas.tag_bind(button4, '<Button-1>', lambda e: self.start())


        img_path5 = os.path.join(filepath, "images/img5.png")
        img5 = PhotoImage(file=img_path5)
        self.canvas.pack(fill=BOTH)
        button5 = self.canvas.create_image(224, 663, anchor='nw', image=img5)
        self.canvas.tag_bind(button5, '<Button-1>', lambda e: self.clear())

        img_path6 = os.path.join(filepath, "images/img6.png")
        img6 = PhotoImage(file=img_path6)
        self.canvas.pack(fill=BOTH)
        button6 = self.canvas.create_image(465, 663, anchor='nw', image=img6)
        self.canvas.tag_bind(button6, '<Button-1>', lambda e: self.close())

        # self.canvas.create_text(
        #     1165.0, 435.5,
        #     anchor='nw',
        #     text="Witaj!\n\nWybierz folder z danymi wzorcowymi",
        #     fill="#ffffff",
        #     font=("Inter", int(22.0)))

        # self.font = font.Font(family='Purisa', size=12, weight='bold')
        self.text_id = self.canvas.create_text(1165.0, 435.5, anchor="center", font=("Inter", int(20.0)), fill="#ffffff",
                                               text="Witaj!\n\nWybierz folder z danymi wzorcowymi", width=450)

        self.window.resizable(False, False)

        self.window.mainloop()

    def choose_model_folder(self):
        self.text = "Wybierz folder wzorcowy"
        self.change_text()
        self.model_path = filedialog.askdirectory(title="Wybierz folder wzorcowy")
        self.text = "Wybrany folder wzorcowy:\n\n" + self.model_path
        self.change_text(("Inter", int(14.0)))

    def choose_source_folder(self):
        self.text = "Wybierz folder źródłowy"
        self.change_text()
        path = filedialog.askdirectory(title="Wybierz folder źródłowy")
        self.source_path.append(path)

        self.text = "Wybrane foldery źródłowe:\n\n"
        for path in self.source_path:
            self.text += str(path) + "\n"
        self.change_text(("Inter", int(14.0)))

    def choose_dest_folder(self):
        self.text = "Wybierz folder docelowy"
        self.change_text()
        self.destination_path = filedialog.askdirectory(title="Wybierz folder docelowy")
        self.text = "Wybrany folder docelowy:\n\n" + self.destination_path
        self.change_text(("Inter", int(14.0)))

    def choose_from_history(self):
        self.text = "Wybierz plik z historii"
        self.change_text()
        self.model_path = filedialog.askopenfilename(title="Wybierz plik z historii")
        self.is_history = True
        self.text = "Wybrany plik z historii:\n\n" + self.model_path
        self.change_text(("Inter", int(14.0)))

    def start(self):
        self.text = "Rozpoczęcie selekcji"
        self.change_text()

        if not self.is_ready():
            self.text = "Wprowadź wszystkie dane"
            self.change_text()
        else:
            print("Rozpoczęcie selekcji")
            self.change_text()

            if self.is_history == False:
                d = detection.Detector(self.model_path, self.source_path, self.destination_path, False)
            if self.is_history:
                d = detection.Detector(self.model_path, self.source_path, self.destination_path, True)
            text_return = d.select_faces()
            if text_return is True:
                self.text = "Selekcja zakończona\n\nPliki znajdziesz w folderze: \n" + self.destination_path
                self.change_text(("Inter", int(14.0)))
                self.clear_data()
            else:
                self.text = "Selekcja zakończona niepowodzeniem\n\n" + str(text_return)
                self.change_text()
                self.clear_data()

    def clear(self):
        self.model_path = ""
        self.source_path = []
        self.destination_path = ""
        self.is_history = False

        self.text = "Dane wyczyszczone\n\nRozpocznij od początku"
        self.change_text()

    def clear_data(self):
        self.model_path = ""
        self.source_path = []
        self.destination_path = ""
        self.is_history = False

    def close(self):
        self.canvas.delete(self.text_id)  # delete the text
        self.window.destroy()

    def change_text(self, font=("Inter", int(20.0))):
        self.canvas.itemconfig(self.text_id, text=self.text, font=font)

    def is_ready(self):
        if self.model_path != " " and self.source_path != [] and self.destination_path != " ":
            return True
        else:
            return False
