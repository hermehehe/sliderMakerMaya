from maya import cmds
import math


def create_slider_ctrl(name):
    """ Create slider control polygons (rectangle and circle).
        Groups polygons and freezes transforms
        Args: User input name of slider
        Return:
            list: control group name, circle control name
    """
    slider_name = name+"_Slider"
    ctrl_box_name = 'box'
    ctrl_circle_name = name+'_slider_ctrl'
    box_len = 20
    box_width = 7
    # create slider control polygons
    circle_ctrl = cmds.circle(name=ctrl_circle_name, normal=[0, 0, 1], r=3)
    box_ctrl = cmds.nurbsSquare(name=ctrl_box_name, normal=[0, 0, 1], d=3, sl1=box_len, sl2=box_width)
    circle_node = circle_ctrl[0]
    box_node = box_ctrl[0]

    # group polygons
    ctrl_group = cmds.group(box_node, circle_node, name=slider_name)
    if circle_node[0] == '|':
        circle_node = ctrl_group + circle_node
        box_node = ctrl_group + box_node

    # edit box to have curved ends
    z_loc = math.sqrt(((box_width/2.0)**2 + (box_width/4.0)**2))
    left_curve = cmds.curve(d=3, p=[(box_width/2.0, 0, 0), (box_width/4.0, 0, z_loc), (-box_width/4.0, 0, z_loc),
                                    (-box_width/2.0, 0, 0)])
    right_curve = cmds.curve(d=3, p=[(box_width/2, 0, 0), (box_width/4.0, 0, -z_loc), (-box_width/4.0, 0, -z_loc),
                                     (-box_width/2, 0, 0)])

    cmds.rotate('90deg', 0, 0, left_curve, right_curve)
    cmds.move(0, -box_len/2.0, 0, left_curve)
    cmds.move(0, box_len/2.0, 0, right_curve)

    cmds.parent(right_curve, left_curve, box_node)
    cmds.delete(box_node+'|right'+ctrl_box_name, box_node+'|left'+ctrl_box_name)

    # move group from origin
    cmds.move(50, 150, 0, ctrl_group)

    # freeze transforms
    cmds.makeIdentity(ctrl_group, apply=True, rotate=True, translate=True, scale=True)

    # lock rotations
    cmds.setAttr('{}.r'.format(ctrl_group), lock=True)
    cmds.setAttr('{}.r'.format(circle_node), lock=True)
    cmds.setAttr('{}.r'.format(box_node), lock=True)

    # lock circle x, z translations
    cmds.setAttr('{}.translateX'.format(circle_node), lock=True)
    cmds.setAttr('{}.translateZ'.format(circle_node), lock=True)

    # set min/max values for circle y translation
    cmds.transformLimits(circle_node, ty=[-8, 8], ety=[True, True])

    controls = [ctrl_group, circle_node]
    return controls


def get_selection():
    """ Get names of all selected controls that will be driven by the slider

    Returns: List of names

    """
    selection = cmds.ls(selection=True)
    if len(selection) == 0:
        return []  # empty list

    return selection


def create_key_attr(name, controls):
    """ Add attribute to the circle polygon to drive keys
    Args:
        name: User input name of slider
        controls: group ctrl and circle ctrl names from Maya
    """
    attr_name = name+"_Slider"
    # Add slider Attribute to circle control
    cmds.addAttr(controls[1], longName=attr_name, defaultValue=0, minValue=-10, maxValue=10)
    cmds.setAttr('{}.{}'.format(controls[1], attr_name), keyable=True)



