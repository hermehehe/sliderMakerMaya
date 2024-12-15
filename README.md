# Slider Control Maker Maya Tool

This tool automates the slider control creation process in Maya. It generates NURBs polygon UI and uses driven keys to connect the slider translation to the selected controls.
I created this tool as some people like the option to have rig controls as sliders off to the side for easier access especially for facial controls. I tested and applied this tool to the Morpheus Rig created by Josh Burton, downloaded from his website http://www.joshburton.com/projects/morpheus.asp

![image](https://github.com/user-attachments/assets/fb95495c-723d-488d-bbc4-56f2e8c3d7ca)

Start with a scene containing a referrenced rig. Users must type in a name for the slider. Then select and save the controls they would like to be driven by the slider. Saving the selection creates a dictionary stored in a .json file of each attribute as keys and a list containing min, default and max values. The user then moves the controls into their desired min and max poses and saves each of them by pressing 'Set Min' and 'Set Max' buttons. This updates the dictionaries min and max values. Finally, clicking 'Apply' will generate the sliders UI and set all driven keys. The user can select one or multiple rigs and apply the slider to each of them.
![image](https://github.com/user-attachments/assets/70095c4f-9bae-4be6-88a7-6a9d152b2ad2)

Optional Features:
Mirroring: Applies keys to other side of rig. For example, select and set poses for the left eye and the tool will apply it to the right eye aswell.
Set Zero as Default: This sets all driven attributes and slider translation to zero in the middle of the slider. This allows users to easily set all attributes back to zero by zeroing out the slider. If this option is not selected, the slider's zero value is moved to the bottom of the slider and is keyed to the min value. 


This tool not only saves time by generating control UI and automating setting driven keys for attribute, it also allows users to set min and max poses in any order, it ensures keys are always set properly and users can set them as many times as they want before hitting apply. This is more flexible than setting driven keys manually, as the order the keys are set matters.

I chose to store the attribute dictionary in a .json file to allow different functions to access and update the dictionary without the use of global variables in ui.py module.
