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


# change this, need to create a dictionary of selection names.attributes and min. medium, max values of all attributes
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
    """ create dictionary of all attributes from selected controls and contains their previous & current values

    Args:
        selection: list of selected controls

    Returns:
        attr_dict: dictionary of attribute names as keys and list of previous and current values

    """
    attr_dict = {}
    for ctrl in selection:
        attr_list = cmds.listAttr(ctrl, k=True, u=True)
        for attr in attr_list:
            ctrl_attr_full = '{}.{}'.format(ctrl, attr)
            value = cmds.getAttr(ctrl_attr_full)
            attr_dict[ctrl_attr_full] = [value, value, value]    # [min value, default value, max value]

    return attr_dict


def create_slider_attr(controls):
    """ Add driver attribute to the circle polygon to drive keys
    Args:
        controls: list, 0 = ctrl group name, 1 = circle ctrl name

    Returns:
        dict: circle control's Slider and Translate Y min, default and max values
    """
    slider_attr_name = controls[0]
    slider_full_name = '{}.{}'.format(controls[1], slider_attr_name)
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

# TEST THIS FUNCTION
def update_attr_dict(attr_dict, slider_val):
    """ Updates attribute values in dictionary
    Args:
        attr_dict: dictionary of selected control attribute names and list of previous and current values
        slider_val: setting of slider (min, default, max)
    """
    # setDrivenKeyframe -currentDriver Eyes_Slider1|Eyes_slider_ctrl.Eyes_Slider severus:eyeIK_right_anim.translateY;
    # ['severus:eyeFK_right_anim', 'severus:sideHead_left_mover_ctrl_anim', 'severus:eye_masterIK_anim']

    for attr, value_list in attr_dict.items():
        # compare and update value list
        current_val = cmds.getAttr(attr)
        if current_val == value_list[0] and current_val == value_list[1] and current_val == value_list[2]:
            continue
        elif slider_val == 'min' and current_val is not value_list[0]:
            attr_dict[attr] = [current_val, value_list[1], value_list[2]]
        elif slider_val == 'default' and current_val is not value_list[1]:
            attr_dict[attr] = [value_list[0], current_val, value_list[2]]
        else:
            attr_dict[attr] = [value_list[0], value_list[1], current_val]

    return attr_dict


#def set_driven_keys():
