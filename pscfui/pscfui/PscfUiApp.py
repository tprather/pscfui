'''
Created on Jul 21, 2016

@author: tprather
'''

import kivy
kivy.require('1.9.1')

from kivy.app             import App
from kivy.lang            import Builder
from kivy.uix.button      import Button
from kivy.uix.boxlayout   import BoxLayout
'from kivy.uix.filechooser import FileChooserIconView'
from kivy.uix.label       import Label
from kivy.uix.modalview   import ModalView
'from kivy.uix.popup       import Popup'
from kivy.utils           import platform
from os.path              import sep, expanduser, isdir, dirname

import subprocess

from pscfui               import FileBrowser

'''
<Label>:
    halign:    'left'
    valign:    'top'
    text_size: self.size

<Widget>:
    halign:    'left'
    valign:    'top'

<BoxLayout>
    orientation: 'vertical'
    
<Button>:
    size: self.texture_size
    
PfscUi:
    BoxLayout:
        Button:
            id: select_input_file_button
            text: "Select Input File"
        Label:
            id: selected_input_file_name
        
<FileSelect>:
    ModalView:
        FileChooserIconView:
            on_selection: root.note_input_file(*args)
    
'''
Builder.load_string('''

<Button>:
    size: self.texture_size

''')

class FileSelectModalView(ModalView):
    
    selectedFile = ''

    def __init__(self, **kwargs):
        super(FileSelectModalView,self).__init__(**kwargs)
        if platform == 'win':
            user_path = dirname(expanduser('~')) + sep + 'Documents'
        else:
            user_path = expanduser('~') + sep + 'Documents'
        fileBrowser = FileBrowser.FileBrowser(
            select_string='Select',
            favorites=[
                (user_path                                           , 'Documents'),
                (user_path+"Projects"+sep+"DMREF"+sep+"pscf_examples", 'Examples' )
            ]
        )
        fileBrowser.bind(on_success=self.note_file)
        self.add_widget(fileBrowser)

    def note_file(self,instance):
        try:
            self.selectedFile = instance.selection[0]
        except:
            pass
        self.dismiss()
    
class PscfUi(BoxLayout):

    fsDialog  = FileSelectModalView()
    inputFile = Label()
    
    def __init__(self, **kwargs):
        super(PscfUi,self).__init__(orientation='vertical',**kwargs)
        self.fsDialog.bind(on_dismiss=self.note_input_file)
        bSelect = Button(text="Select Input File")
        bSelect.bind(on_press=self.fsDialog.open)
        fsBox = BoxLayout(orientation='horizontal',height=100)
        fsBox.add_widget(bSelect)
        fsBox.add_widget(self.inputFile)
        self.add_widget(fsBox)
        bProcess = Button(text="Execute")
        bProcess.bind(on_press=self.process_input_file)
        self.add_widget(bProcess)
        self.inputFile = 'C:\\Users\\tprather\\Documents\\Projects\\DMREF\\pscf-examples\\diblock\\bcc\\iterate\\param'

    def note_input_file(self,*args):
        self.inputFile.text = self.fsDialog.selectedFile;
        print(self.inputFile.text)
    
    def process_input_file(self,instance):
        param = open(self.inputFile,'r')
        try:
            poutput = subprocess.check_output(["C:\\Users\\tprather\\Documents\\Projects\\DMREF\\pscf\\bin\\pscf.exe"], stdin=param, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            poutput = e.output
        print(poutput)
        
class PscfUiApp(App):
    
    def build(self):
        return PscfUi()
    
if __name__ == '__main__':
    PscfUiApp().run()
