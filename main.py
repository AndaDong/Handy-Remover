#Import UI
import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

#Import Utils
import os
import json
import shutil
import datetime
import numpy as np
#from kivy.logger import Logger
#Logger.setLevel(logging.TRACE)

#Import Image Porcessing
import cv2
import PIL
from skimage import measure, morphology
from skimage.measure import regionprops

#Linked list
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
 
    # Method to add a node at begin of LL
    def insertAtBegin(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            return
        else:
            new_node.next = self.head
            self.head = new_node
 
    # Method to add a node at any index
    def insertAtIndex(self, data, index):
        new_node = Node(data)
        current_node = self.head
        position = 0
        if position == index:
            self.insertAtBegin(data)
        else:
            while(current_node != None and position+1 != index):
                position = position+1
                current_node = current_node.next
 
            if current_node != None:
                new_node.next = current_node.next
                current_node.next = new_node
            else:
                print("Index not present")
 
    # Method to add a node at the end of LL
    def insertAtEnd(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            return
 
        current_node = self.head
        while(current_node.next):
            current_node = current_node.next
 
        current_node.next = new_node
 
    # Update node of a linked list at given position
    def updateNode(self, val, index):
        current_node = self.head
        position = 0
        if position == index:
            current_node.data = val
        else:
            while(current_node != None and position != index):
                position = position+1
                current_node = current_node.next
 
            if current_node != None:
                current_node.data = val
            else:
                print("Index not present")
 
    # Method to remove first node of linked list
    def remove_first_node(self):
        if(self.head == None):
            return
        self.head = self.head.next
 
    # Method to remove last node of linked list
    def remove_last_node(self):
        if self.head is None:
            return
        current_node = self.head
        while(current_node.next.next):
            current_node = current_node.next
        current_node.next = None
 
    # Method to remove at given index
    def remove_at_index(self, index):
        if self.head == None:
            return
        current_node = self.head
        position = 0
        if position == index:
            self.remove_first_node()
        else:
            while(current_node != None and position+1 != index):
                position = position+1
                current_node = current_node.next
 
            if current_node != None:
                current_node.next = current_node.next.next
            else:
                print("Index not present")
 
    # Print the size of linked list
    def sizeOfLL(self):
        size = 0
        if(self.head):
            current_node = self.head
            while(current_node):
                size = size+1
                current_node = current_node.next
            return size
        else:
            return 0

    def getData(self, index):
        current_node = self.head
        for i in range(index):
            current_node = current_node.next
        return current_node.data

#Initialize user data
with open('userData.json', 'r') as openfile:
    # Reading from json file
    json_object = json.load(openfile)
    
num_scans = json_object["num_scans"]
dir_list = json_object["dir_list"]
len_list = json_object["len_list"]

#initialize directories
storage_dir = "Scans/"
temp_dir = "Temp/"
# External storage (exported files directory)
ext_storage_dir = os.path.join(os.environ['EXTERNAL_STORAGE'])
ext_storage_dir = os.path.join(ext_storage_dir, 'Handy Remover')
os.makedirs(ext_storage_dir, exist_ok=True)
# # Album directory
# alb_storage_dir = "/storage/emulated/0/DCIM"

# Instentiate linked list for scan image directories
tempLList = LinkedList()
currImageIndex = 0

#Create Screens for Kivy
class MainWindow(Screen):
    pass

#Camera        
class CameraWindow(Screen):
    pass

class CameraClick(BoxLayout):
    def capture(self):
        global currImageIndex
        camera = self.ids["camera"]
        # using the current time to ensure that file name does not conflict
        nowDate = datetime.datetime.now()
        destStr = temp_dir + str(nowDate.min) + str(nowDate.second) + str(nowDate.microsecond) + ".jpg"
        camera.export_to_png(destStr)
        #empty scan, insert at end
        if (currImageIndex==0): 
            tempLList.insertAtEnd(destStr)
        else: #add function used, insert after current image
            tempLList.insertAtIndex(destStr, currImageIndex+1)
            currImageIndex+=1

#Select from Album
class AlbumWindow(Screen):
    def selectionDone(self):
        selection = self.ids.file_chooser.selection
        for i in range(len(selection)):
            filePath = selection[i]
            shutil.copy(filePath, temp_dir+str(i)+".jpg")         
            tempLList.insertAtEnd(temp_dir+str(i)+".jpg")         
        
#Edit the scan
class EditScanWindow(Screen):
    #show the previous image
    def prevImage(self):
        global currImageIndex
        if (currImageIndex>0):
            currImageIndex-=1
            self.ids.scanImageView.source = tempLList.getData(currImageIndex)
            self.ids.currImageNum.text = str(currImageIndex+1)
    
    #show the next image
    def nextImage(self):
        global currImageIndex
        if (currImageIndex<tempLList.sizeOfLL()-1):
            currImageIndex+=1
            self.ids.scanImageView.source = tempLList.getData(currImageIndex)
            self.ids.currImageNum.text = str(currImageIndex+1)          
    
    #reset index when moving to next screen
    def resetIndex(self):
        global currImageIndex
        currImageIndex=0
    
    #reload to first image
    def reloadImage(self):
        global currImageIndex
        currImageIndex = 0
        self.ids.scanImageView.source = tempLList.getData(currImageIndex)
        self.ids.currImageNum.text = str(currImageIndex+1)           

    #remove image at index
    def removeImage(self):
        global currImageIndex
        tempLList.remove_at_index(currImageIndex)
        if (currImageIndex==tempLList.sizeOfLL()):
            currImageIndex-=1
        self.ids.scanImageView.source = tempLList.getData(currImageIndex)
        self.ids.currImageNum.text = str(currImageIndex+1)         

#Edit the photo filters
class EditPhotoWindow(Screen):
    #show the previous image
    def prevImage(self):
        global currImageIndex
        if (currImageIndex>0):
            currImageIndex-=1
            self.ids.scanPhotoView.source = tempLList.getData(currImageIndex)
            self.ids.currPhotoNum.text = str(currImageIndex+1)
    
    #show the next image
    def nextImage(self):
        global currImageIndex
        if (currImageIndex<tempLList.sizeOfLL()-1):
            currImageIndex+=1
            self.ids.scanPhotoView.source = tempLList.getData(currImageIndex)
            self.ids.currPhotoNum.text = str(currImageIndex+1)          
    
    #reset index when moving to next screen
    def resetIndex(self):
        global currImageIndex
        currImageIndex=0
        
    
    #relaod to first image
    def reloadImage(self):
        global currImageIndex
        currImageIndex = 0
        self.ids.scanPhotoView.source = tempLList.getData(currImageIndex)
        self.ids.currPhotoNum.text = str(currImageIndex+1)    

    #remove shadow of all images
    def shadowButtonFunction(self):
        currentNode = tempLList.head
        for i in range(tempLList.sizeOfLL()):
            removeShadows(currentNode.data, i)
            currentNode = currentNode.next
    
    #remove handwriting of all images
    def handButtonFunction(self):
        currentNode = tempLList.head
        for i in range(tempLList.sizeOfLL()):
            removeHandWriting(currentNode.data, i)
            currentNode = currentNode.next

#Image Processing
def removeShadows(imgDir, index):
    nowDate = datetime.datetime.now()
    #read the image
    img = cv2.imread(imgDir)
    
    #split into 3 color channels
    rgb_planes = cv2.split(img)
    
    result_planes = []
    result_norm_planes = []
    #loop through 3 color channels
    for plane in rgb_planes:
        #expands the image so details can be spotted
        dilated_img = cv2.dilate(plane, np.ones((7,7), np.uint8))
        #apply median blur to create background image
        bg_img = cv2.medianBlur(dilated_img, 21)
        #create the diffrence between image and background
        diff_img = 255 - cv2.absdiff(plane, bg_img)
        #enhance the contrast of the highlighted region by normalization
        norm_img = cv2.normalize(diff_img,None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
        #append to respective lists
        result_planes.append(diff_img)
        result_norm_planes.append(norm_img)
    
    # merge color channels back
    result_norm = cv2.merge(result_norm_planes)
    
    
    # save as new image in Temp
    destStr = temp_dir + str(nowDate.min) + str(nowDate.second) + str(nowDate.microsecond) + ".jpg"
    cv2.imwrite(destStr,result_norm)
    # replace the element in the LL to the processed image (prev image not deleted)
    tempLList.updateNode(destStr, index)

def removeHandWriting(imgDir, index):
    nowDate = datetime.datetime.now()
    img = cv2.imread(imgDir, 0)
    #create binary image intensity>127 is white, < is black
    img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)[1] 

    #grab the handwriting into blobs using image pixel mean
    blobs = img > img.mean()
    blobs_labels = measure.label(blobs, background=1)

    the_biggest_component = 0
    total_area = 0
    counter = 0
    average = 0.0
    #calculate area distribution and not counting small blobs
    for region in regionprops(blobs_labels):
        if (region.area > 10):
            total_area = total_area + region.area
            counter = counter + 1
        if (region.area >= 250):
            if (region.area > the_biggest_component):
                the_biggest_component = region.area
    #adjust threshold constant using average blob size
    average = (total_area/counter)
    a4_constant = ((average/84.0)*250.0)+100
    #remove Noise
    b = morphology.remove_small_objects(blobs_labels, a4_constant)
    cv2.imwrite('temp.png', b)
    # ensure binary by thresholding again
    img2 = cv2.imread('temp.png', 0)
    img2 = cv2.threshold(img2, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    
    #invert image to make handwriting stand out
    diff = cv2.bitwise_xor(img,img2)
    #subtract out the hand writing
    diff = cv2.bitwise_not(diff)

    destStr = temp_dir + str(nowDate.min) + str(nowDate.second) + str(nowDate.microsecond) + ".jpg"
    cv2.imwrite(destStr,diff)
    tempLList.updateNode(destStr, index)
           
class ExportWindow(Screen):
    #update file index
    def on_pre_enter(self):
        self.ids.file_index_label.text = "File index: " + str(num_scans)

    def exportDone(self):
        global num_scans
        global dir_list
        global len_list

        #make new directory for new scan
        nowDate = datetime.datetime.now()
        #directory named as scan index and date
        dayDir = str(num_scans)+"_"+str(nowDate.month)+"-"+str(nowDate.day)
        seriesDir = storage_dir + dayDir
        os.mkdir(seriesDir)
        currentNode = tempLList.head
        #save images to new directory
        for i in range(tempLList.sizeOfLL()):
            #Images named in order
            imageName = str(i)+".jpg"
            targetPath = os.path.join(seriesDir, imageName)
            shutil.copy(currentNode.data, targetPath)
            currentNode=currentNode.next

        #update user data
        num_scans+=1
        dir_list.append(dayDir)
        len_list.append(tempLList.sizeOfLL())
        dictionary = {
            "num_scans": num_scans,
            "dir_list": dir_list,
            "len_list": len_list
        }
        with open("userData.json", "w") as outfile:
            json.dump(dictionary, outfile)
        
        #clear LL and Temp
        tempLList.head = None
        shutil.rmtree(temp_dir)
        os.mkdir(temp_dir)


    #export images to pdf
    def toPDF(self):
        #load images to list
        myImages = []
        currentNode = tempLList.head
        for i in range(tempLList.sizeOfLL()):
            myImages.append(PIL.Image.open(currentNode.data))
            currentNode=currentNode.next
        #configure pdf size
        width, height = myImages[0].size
        pdf = PIL.Image.new("RGB", (width, height*len(myImages)), "white")
        for i, image in enumerate(myImages):
            pdf.paste(image, (0, i*height))
        #export and save pdf to external storage
        pdfDir = os.path.join(ext_storage_dir, "Scan"+str(num_scans)+".pdf")
        # pdfDir = "myPDF.pdf"
        pdf.save(pdfDir)

    #export images to images
    def toImage(self):
        seriesDir = os.path.join(ext_storage_dir, "Scan"+str(num_scans))
        # seriesDir = "test series"
        os.mkdir(seriesDir)
        currentNode = tempLList.head
        for i in range(tempLList.sizeOfLL()):
            #copy image from Temp to new dirctory
            imageName = str(i)+".jpg"
            targetPath = os.path.join(seriesDir, imageName)
            shutil.copy(currentNode.data, targetPath)
            currentNode=currentNode.next

#View previous scans
class PrevScansWindow(Screen):
    #updaate the scans
    def updatePrevScans(self):
        #clear widgets
        self.ids.scans_scroll_view.clear_widgets()
        #add buttons corresponding to each scan
        for i in range(len(dir_list)):
                button = Button(text=dir_list[i])
                button.bind(on_release=lambda instance: self.scansButtonFunction(i))
                self.ids.scans_scroll_view.add_widget(button)            

    #button functions for acessing scans
    def scansButtonFunction(self, myIndex):
        for i in range(len_list[myIndex]):
            #copy image to Temp, and append to LL
            shutil.copy(storage_dir+dir_list[myIndex]+"/"+str(i)+".jpg", temp_dir+str(i)+".jpg")         
            tempLList.insertAtEnd(temp_dir+str(i)+".jpg")
        #move to next screen
        app=App.get_running_app()
        app.root.current="edit scan"


#App Run and Compile
class WindowManager(ScreenManager):
    pass

kv = Builder.load_file("my.kv")
class MyApp(App):
    def build(self):
        return kv

if __name__ == "__main__":
    MyApp().run()
