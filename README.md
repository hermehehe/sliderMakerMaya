# Slider Control Maker Maya Tool

This tool automates the slider control creation process in Maya. It generates NURBs polygon UI and uses driven keys to connect the slider translation to the selected controls.

I created this tool as some people like the option to have rig controls as sliders off to the side for easier access, especially for facial controls. It can also be used on props and other objects. I tested and applied this tool to the Morpheus Rig created by Josh Burton, downloaded from his website http://www.joshburton.com/projects/morpheus.asp


![image](https://github.com/user-attachments/assets/fb95495c-723d-488d-bbc4-56f2e8c3d7ca)

# How to Use
1. Start Maya with a scene containing a referrenced rig. Users must type in a name for the slider.
2. Select and save the controls you want to be driven by the slider. Saving the selection creates a dictionary stored in a .json file of each attribute as keys and a list containing min, default and max values. 3. Move the rig into desired start and end poses (in any order), saving each of them by pressing 'Set Min' and 'Set Max' buttons. This updates the affected dictionaries items min and max values.
4. Finally, select the rig(s) you want to connect to a slider, click 'Apply' which will generate the sliders UI and set all driven keys. The user can select one or multiple rigs and it will create a separate slider to each of them.
Warnings have been added so users must complete each step in order before proceeding to the next.

![image](https://github.com/user-attachments/assets/70095c4f-9bae-4be6-88a7-6a9d152b2ad2)


# Optional Features:
This are features that are only enable when the user checks its box.
Mirroring: Applies keys to other side of rig. E.g select and set poses for the left eye and the tool will apply it to the right eye aswell.
Set Zero as Default: Sets all driven attributes and slider translation to zero in the middle of the slider. This allows users to easily set all influenced attributes back to zero by zeroing out the slider. If this option is not selected, the slider's zero value is moved to the bottom of the slider and is keyed to the min value. 


This tool not only saves time by generating control UI and automating setting driven keys for attribute, it also allows users to set min and max poses in any order, it ensures keys are always set properly and users can set them as many times as they want before hitting apply. This is more flexible than setting driven keys manually, as the order the keys are set matters. It also does not key any unused attributes, so user could selected the entire rig and the result is the same as selecting only the in use controls.

I chose to store the attribute dictionary in a .json file to allow different functions to access and update the dictionary without the use of global variables in ui.py module. As cleanup, after hitting 'Apply' the .json file is deleted.
