from maya import cmds
import math
import os
import json

ROOT_DIR = r'C:\Users\herme\python_projects\slider_maker'
EXT = 'json'


def create_slider_ctrl(name, size):
    """ Create slider control polygons (rectangle and circle).
        Groups polygons and freezes transforms
        Args:
           name: User input name of slider
           size: User selected size of slider (small, medium, large)
        Return:
            list: control group name, circle control name
    """
    slider_name = '{}_Slider'.format(name)
    ctrl_box_name = 'box'
    ctrl_circle_name = '{}_slider_ctrl'.format(name)

    if size == 'small':
        box_len = 10
        box_width = 5
        radius = 1
    elif size == 'medium':
        box_len = 15
        box_width = 6
        radius = 2
    else:
        box_len = 20
        box_width = 7
        radius = 3

    # create NURBS text label
    label = cmds.textCurves(f='Times-Roman', t=name)
    cmds.move(-box_width/2.0 - 2.0, box_len / 2.0 + 5, 0, label)
    cmds.scale(5, 5, 5, label)

    # create slider control polygons
    circle_ctrl = cmds.circle(name=ctrl_circle_name, normal=[0, 0, 1], r=radius)
    box_ctrl = cmds.nurbsSquare(name=ctrl_box_name, normal=[0, 0, 1], d=3, sl1=box_len, sl2=box_width)
    circle_node = circle_ctrl[0]
    box_node = box_ctrl[0]
    # group polygons
    ctrl_group = cmds.group(box_node, circle_node, label, name=slider_name)

    # construct full name of polygon nodes
    circle_node = ctrl_group + '|' + circle_node
    box_node = ctrl_group + '|' + box_node

    # edit box to have curved ends
    z_loc = math.sqrt(((box_width/2.0)**2 + (box_width/4.0)**2))  # pythagoras theorem to find z points for curve
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
    cmds.transformLimits(circle_node, ty=[-((box_len/2.0)-2), (box_len/2.0)-2], ety=[True, True])

    controls = [ctrl_group, circle_node]
    return controls


def create_slider_attr(controls, size):
    """ Add driver attribute to the circle polygon to drive keys

    Args:
        controls: list containing ctrl group name (0) and circle ctrl name (1)
        size: User selected size of slider (small, medium, large)

    Returns:
        limit_dict: circle control's Slider and Translate Y min, default and max values

    """
    slider_attr_name = controls[0]
    slider_full_name = '{}.{}'.format(controls[1], slider_attr_name)

    if size == 'small':
        drv_min = -1
        drv_max = 1
    elif size == 'medium':
        drv_min = -5
        drv_max = 5
    else:
        drv_min = -10
        drv_max = 10

    # Add slider attribute to circle control
    cmds.addAttr(controls[1], longName=slider_attr_name, defaultValue=0, minValue=drv_min, maxValue=drv_max)
    cmds.setAttr(slider_full_name, keyable=True)

    # Set circle ctrl translateY as the driver for the slider attr
    # Get y transform limits
    y_lims = cmds.transformLimits(controls[1], query=True, ty=True)
    limit_dict = {y_lims[0]: drv_min, 0: 0, y_lims[1]: drv_max}

    # set keys for min, default and max values of translate Y and slider attributes
    for i, j in limit_dict.items():
        cmds.setAttr('{}.translateY'.format(controls[1]), i)
        cmds.setAttr(slider_full_name, j)
        cmds.setDrivenKeyframe(slider_full_name, cd='{}.translateY'.format(controls[1]))

    return limit_dict


def get_selection():
    """ Get names of all selected controls that will be driven by the slider

    Returns: List of selected controls

    """
    selection = cmds.ls(selection=True)
    if len(selection) == 0:
        return []  # empty list
    # check if each item is a control
    for name in selection:
        suffix = name.split('_')[-1]
        if suffix != 'anim':
            selection.remove(name)
    return selection


def create_attr_dict(selection):
    """ create dictionary of all attributes from selected controls that contains their previous & current values

    Args:
        selection: list of selected controls

    Returns:
        attr_dict: dictionary of attribute names as keys and a list of attribute values

    """
    attr_dict = {}
    for ctrl in selection:
        attr_list = cmds.listAttr(ctrl, k=True, u=True)
        for attr in attr_list:
            ctrl_attr_full = '{}.{}'.format(ctrl, attr)
            attr_dict[ctrl_attr_full] = [0, 0, 0]    # [min value, default value, max value]

    return attr_dict


def write_attrs_to_file(name, attr_dict):
    """Write attribute dictionary to json file

    Args:
        name: User input name of slider
        attr_dict: dictionary of selected controls attributes and there key values


    """
    slider_name = '{}_slider'.format(name)
    file_name = '{}.{}'.format(slider_name, EXT)
    file_path = os.path.join(ROOT_DIR, file_name)

    with open(file_path, 'w') as f:
        json.dump(attr_dict, f, indent=4)


def read_attrs_from_file(file_path):
    """Read attribute data from json file

    Args:
        file_path: full path name of file

    Returns: attribute dictionary

    """
    with open(file_path, 'r') as f:
        attr_dict = json.load(f)
        return attr_dict


def update_attr_dict(attr_dict, slider_val):
    """ Updates attribute values in dictionary
    Args:
        attr_dict: dictionary of selected control attribute names and list of previous and current values
        slider_val: setting of slider (min or max)
    """

    for attr, value_list in attr_dict.items():
        # compare and update value list
        current_val = cmds.getAttr(attr)
        if slider_val == 'min':
            attr_dict[attr][0] = current_val
        elif slider_val == 'max':
            attr_dict[attr][2] = current_val

    return attr_dict


def set_driven_keys(attr_dict, limit_dict, controls):
    """ Set attribute values and key min, default and max slider values to each

    Args:
        attr_dict: attribute names and their min, default and max values
        limit_dict: circle control's Slider and Translate Y min, default and max values
        controls: names of control group and circle node

    """
    slider_full_name = '{}.{}'.format(controls[1], controls[0])

    for attr, value_list in attr_dict.items():
        # if min and max key values are the same, skip keying (unused attribute)
        if value_list[0] == value_list[2] and value_list[0] == 0:
            continue

        cmds.setAttr(attr, keyable=True)
        i = 0
        for lim in limit_dict.keys():
            # set attribute and slider values
            cmds.setAttr(attr, value_list[0+i])
            cmds.setAttr('{}.translateY'.format(controls[1]), lim)
            cmds.setAttr(attr, limit_dict[lim])
            # set driven key with slider as driver for all attributes
            cmds.setDrivenKeyframe(attr, cd=slider_full_name)
            i = i+1


