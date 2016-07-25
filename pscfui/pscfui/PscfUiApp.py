'''
Created on Jul 21, 2016

@author: tprather
'''

import kivy
kivy.require('1.9.1')

from kivy.app             import App
from kivy.lang            import Builder
from kivy.properties      import StringProperty
from kivy.uix.button      import Button
from kivy.uix.boxlayout   import BoxLayout
from kivy.uix.gridlayout  import GridLayout
from kivy.uix.label       import Label
from kivy.uix.modalview   import ModalView
from kivy.uix.scrollview  import ScrollView
'from kivy.uix.popup       import Popup'
from kivy.utils           import platform
from os.path              import sep, expanduser, isdir, dirname

import io
import os
import subprocess
import sys
import threading

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

<ScrollableLabel>:
    Label:
        size_hint_y: None
        height:      self.texture_size[1]
        text_size:   self.width, None
        text:        root.text

''')

#==================================================================================================
def find_child_by_id(widget,idval):
    for w in widget.walk():
        if (w.id == idval):
            return w
    return None
    
#==================================================================================================
class FileSelectModalView(ModalView):
    
    m_selected_file = ''

    def __init__(self, **kwargs):
        super(FileSelectModalView,self).__init__(**kwargs)

        #-----Determine users document path to add to file selection "Favorites"-------------------
        if platform == 'win':
            user_path = os.path.expanduser('~') + sep + 'Documents'
        else:
            user_path = os.path.expanduser('~')

        #-----Create a FileBrowser instance with suggested "Favorites" directories-----------------
        file_browser = FileBrowser.FileBrowser(
            select_string='Select',
            favorites=[
                (user_path                                               , 'Documents'),
                (user_path+sep+'Projects'+sep+'DMREF'+sep+'pscf-examples', 'Examples' )
            ]
        )
        file_browser.bind(on_success=self.note_file)
        self.add_widget(file_browser)

    def note_file(self,instance):
        #-----Note the selected file for external use---------------------------------------------- 
        try:
            self.m_selected_file = instance.selection[0]
        except:
            pass
        self.dismiss()
    
#==================================================================================================
class ScrollableLabel(ScrollView):
    text = StringProperty('')
    
    def __init__(self,**kwargs):
        super(ScrollableLabel,self).__init__(**kwargs)
        self.bar_inactive_color = [.7,.7,.7,.9]
    
    def append_text(self,t):
        self.text += t
        self.scroll_y = 0

'''        
class ScrollableTextBox(ScrollView):
    
    m_text_label = None
    
    def __init__(self,**kwargs):
        super(ScrollableTextBox,self).__init__(size_hint_y=None,**kwargs)
        layout = BoxLayout(size_hint_y=None)
        #layout.bind(minimum_height=layout.setter('height'))
        self.m_text_label = Label(size_hint_y=None)
        layout.add_widget(self.m_text_label)
        self.add_widget(layout)
        
    def append_text(self,t):
        self.m_text_label.text += t;
'''
    
#==================================================================================================
class PscfUi(BoxLayout):

    #.....Internal Instance Members................................................................
    __m_fs_dialog   = FileSelectModalView()
    __m_input_file  = None
    __m_output_text = None
    
    def __init__(self,**kwargs):
        super(PscfUi,self).__init__(orientation='vertical',**kwargs)
        #-----When file select completes, note the input file selected-----------------------------
        self.__m_fs_dialog.bind(on_dismiss=self.note_input_file)

        #-----UI Row 1: Selected input file and button for dialog to select it.--------------------
        fs_box = BoxLayout(orientation='horizontal',height=50,size_hint=(1.0,None))
        fs_box.add_widget(Button(text='Select Input File',size_hint=(0.2,1.0),on_press=self.__m_fs_dialog.open))
        fs_box.add_widget(Label (id='input_file'         ,size_hint=(0.8,1.0)))
        self.add_widget(fs_box)

        #-----UI Row 2: Button to call pscf with input file and capture output---------------------
        ex_box = BoxLayout(orientation='horizontal',height=50,size_hint=(1.0,None))
        ex_box.add_widget(Button(text='Execute',size_hint=(1.0,1.0),on_press=self.process_input_file))
        self.add_widget(ex_box)

        #-----UI Row 3: Scrolling view of pscf output----------------------------------------------
        #self.add_widget(ScrollableTextBox(id='output_text',size_hint=(1.0,1.0),scroll_type=['bars']))
        self.add_widget(ScrollableLabel(id='output_text',scroll_type=['bars'],bar_width=10))
        
        #-----Note references to important widgets-------------------------------------------------
        self.__m_input_file  = find_child_by_id(self,'input_file')
        self.__m_output_text = find_child_by_id(self,'output_text')

        #-----Temporary: default input file for easy testing---------------------------------------
        self.__m_input_file.text = 'C:\\Users\\tprather\\Documents\\Projects\\DMREF\\pscf-examples\\diblock\\bcc\\iterate\\param'

    def note_input_file(self,*args):
        #-----Note the selected input file---------------------------------------------------------
        self.__m_input_file.text = self.__m_fs_dialog.m_selected_file;
    
    def pscf_thread(self,input_file,output_text):
        #-----Execute pscf with the __m_input_file opened for stdin and capture stdout---------------
        with io.open(input_file,'r') as ifile:
            try:
                # Assume that pscf/bin directory is in the path.
                # poutput = subprocess.check_output(["C:\\Users\\tprather\\Documents\\Projects\\DMREF\\pscf\\bin\\pscf.exe"], stdin=param, stderr=subprocess.STDOUT)
                p = subprocess.Popen(["pscf.exe"],cwd=os.path.dirname(input_file),stdin=ifile,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                for c in iter(lambda: p.stdout.read(1),''):
                    sys.stdout.write(c)
                    output_text.append_text(c);
            except subprocess.CalledProcessError, e:
                print(e.output)
    
    def process_input_file(self,instance):
        threading.Thread(target=self.pscf_thread,args=(self.__m_input_file.text,self.__m_output_text)).start()
        
#==================================================================================================
class PscfUiApp(App):
    
    def build(self):
        return PscfUi()
    
#==================================================================================================
if __name__ == '__main__':
    PscfUiApp().run()
