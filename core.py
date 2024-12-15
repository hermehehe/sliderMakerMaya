from maya import cmds
import math
import os
import json

ROOT_DIR = r'C:\Users\herme\python_projects\slider_maker'
EXT = 'json'


def create_slider_ctrl(name, selected_namespace):
    """ Create slider control polygons (rectangle and circle).
        Groups polygons and freezes transforms
        Args:
           name: User input name of slider
           selected_namespace: name of a selected rig
        Return:
            list: control group name, circle control name
    """
    slider_name = '{}_Slider'.format(name)
    ctrl_box_name = 'box'
    ctrl_circle_name = '{}_slider_ctrl'.format(name)

    box_len = 20
    box_width = 7
    radius = 3

    # create NURBS text label
    label = cmds.textCurves(f='Times-Roman', t=name)
    cmds.move(-box_width/2.0 - len(name)/2.0, box_len / 2.0 + 5, 0, label)  # centre text
    cmds.scale(5, 5, 5, label)

    # create slider control polygons
    circle_ctrl = cmds.circle(name=ctrl_circle_name, normal=[0, 0, 1], r=radius)
    box_ctrl = cmds.nurbsSquare(name=ctrl_box_name, normal=[0, 0, 1], d=3, sl1=box_len, sl2=box_width)
    circle_node = circle_ctrl[0]
    box_node = box_ctrl[0]

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

    # parent under rig
    rig_name = selected_namespace + ':all_anim'
    ctrl_group = cmds.group(box_node, circle_node, label, name=slider_name)
    ctrl_full_group = cmds.parent(ctrl_group, rig_name)[0]

    # construct full name of polygon nodes
    circle_full_node = ctrl_full_group + '|' + circle_node.split('|')[-1]
    box_full_node = ctrl_full_group + '|' + box_node.split('|')[-1]

    # set min/max values for circle y translation
    cmds.transformLimits(circle_full_node, ty=[-((box_len/2.0)-2), (box_len/2.0)-2], ety=[True, True])

    controls = [ctrl_full_group, circle_full_node, box_full_node]

    return controls


def slider_position(controls, attr_dict):
    """ Rotate and move slider. Lock unused transforms either horizontal or vertical

    Args:
        controls: (list) slider ctrl group name, slider circle node name, slider box node name
        attr_dict: dictionary of attributes' full names as keys and list of values

    """

    # move group from origin closer to selection
    selected = list(attr_dict.keys())[0]
    selected_ctrl = selected.split('.')[0]
    location = cmds.xform(selected_ctrl, q=True, ws=True, t=True)
    cmds.move(location[0], location[1], location[2], controls[0])

    # freeze transforms
    cmds.makeIdentity(controls[0], apply=True, rotate=True, translate=True, scale=True)

    # lock rotations and translations
    for node in controls:
        cmds.setAttr('{}.r'.format(node, lock=True))
        if node == controls[0]:
            continue
        cmds.setAttr('{}.translateX'.format(node), lock=True)
        cmds.setAttr('{}.translateZ'.format(node), lock=True)
        if node == controls[2]:
            cmds.setAttr('{}.translateY'.format(node), lock=True)


def create_slider_attr(controls, zero_as_default):
    """ Add driver attribute to the circle polygon to drive keys

    Args:
         controls: list containing ctrl group name (0) and circle ctrl name (1)
         zero_as_default: bool value of Set Zero as default box

    Returns:
         limit_dict: circle control's Slider and Translate Y min, default and max values

    """
    slider_attr_name = controls[0].split('|')[-1]
    slider_full_name = '{}.{}'.format(controls[1], slider_attr_name)

    drv_min = -10
    drv_max = 10

    if not zero_as_default:
        drv_min = 0

    # Add slider attribute to circle control
    cmds.addAttr(controls[1], longName=slider_attr_name, defaultValue=0, minValue=drv_min, maxValue=drv_max)
    cmds.setAttr(slider_full_name, keyable=True)

    # Get y transform limits
    y_lims = cmds.transformLimits(controls[1], query=True, ty=True)
    limit_dict = {y_lims[0]: drv_min, 0: 0, y_lims[1]: drv_max}
    # Set circle ctrl translateY as the driver for the slider attr
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
        attr_list = cmds.listAttr(ctrl, k=True, u=True, r=True, w=True)
        if attr_list is None:
            continue
        for attr in attr_list:
            ctrl_attr_full = '{}.{}'.format(ctrl, attr)
            value = cmds.getAttr(ctrl_attr_full)

            attr_dict[ctrl_attr_full] = [value, 0, value]   # min, default, max values

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


def set_driven_keys(attr_dict, limit_dict, controls, zero_as_default):
    """ Set attribute values and key min, default and max slider values

    Args:
        attr_dict: attribute names and their min, default and max values
        limit_dict: circle control's Slider and Translate Y min, default and max values
        controls: names of control group and circle node

    """
    ctrl_slider_attr = '{}.{}'.format(controls[1], controls[0].split('|')[-1])
    ctrl_y_attr = '{}.translateY'.format(controls[1])
    lwr_bound = False
    upr_bound = False

    for attr, value_list in attr_dict.items():
        # if min and max key values are the same, skip keying (unused attribute)
        if value_list[0] == value_list[-1]:
            continue
        # Check upper and lower bounds if they are in use (any attr going above or below 0)
        if value_list[0] != 0 and zero_as_default:
            lwr_bound = True
        if value_list[-1] != 0 and zero_as_default:
            upr_bound = True

        # go through each attribute and key min, default and max values to the driver attribute
        i = 0
        for y_lim in limit_dict.keys():
            # if user does not select set zero as default skip keying default
            if not zero_as_default and i == 1:
                i += 1
                continue
            # if min or max value equals default, skip keying (duplicate key)
            elif value_list[i] == 0 and y_lim != 0 and zero_as_default:
                i += 1
                continue

            # set attribute and slider values
            cmds.setAttr(ctrl_y_attr, y_lim)  # must move driver before moving driven attribute
            cmds.setAttr(attr, value_list[i])

            # set driven key with slider as driver for all attributes
            cmds.setDrivenKeyframe(attr, cd=ctrl_slider_attr)
            i += 1

        # if lower or upper bound range not in use, restrict y translation value
        if not lwr_bound and zero_as_default:
            lims = cmds.transformLimits(controls[1], query=True, ty=True)
            cmds.transformLimits(controls[1], ty=[0, lims[1]], ety=[True, True])

        if not upr_bound and zero_as_default:
            lims = cmds.transformLimits(controls[1], query=True, ty=True)
            cmds.transformLimits(controls[1], ty=[lims[0], 0], ety=[True, True])


def get_selected_namespace():
    """ Extracts list of namespaces from a selection

        Returns: list of unique namespaces
    """

    selected = cmds.ls(selection=True)
    namespaces = []
    for item in selected:
        # isolate namespace from full name
        name = item.split(':')[0]
        if name not in namespaces:
            namespaces.append(name)

    return namespaces


def mirror_attrs(attr_dict):
    """Construct mirrored attribute names and add them to attribute dictionary
        Args:
            attr_dict: dictionary of attribute names and values
        Returns: updated attr_dict with new attributes
    """
    l_r_dict = {':r_': ':l_', '_r_': '_l_', 'right': 'left', 'Right': 'Left'}
    mirrors_dict = {}
    for attr, value_list in attr_dict.items():
        new_attr = ''
        for r_label, l_label in l_r_dict.items():
            # construct mirrored name
            if r_label in attr:
                new_attr = '{}{}{}'.format(attr.split(r_label)[0], l_label, attr.split(r_label)[-1])
                break
            elif l_label in attr:
                new_attr = '{}{}{}'.format(attr.split(l_label)[0], r_label, attr.split(l_label)[-1])
                break
        # check if attribute exists and is keyable
        if new_attr == '':
            continue
        node_name = new_attr.split('.')[0]
        attr_short_name = new_attr.split('.')[-1]
        if not cmds.objExists(node_name) or not cmds.attributeQuery(attr_short_name, node=node_name, exists=True):
            print("New Attr: {} does not exist".format(new_attr))
            continue
        # add new attribute to dictionary
        mirrors_dict.update({new_attr: value_list})

    # add mirror dictionary to attr dict
    for mirror_attr, value_list in mirrors_dict.items():
        attr_dict.update({mirror_attr: value_list})

    return attr_dict


def rename_attr_dict(namespace, attr_dict):
    """ Rename attributes in dictionary with selected namespace

    Args:
        namespace: string selected name of rig
        attr_dict: dictionary containing list of attribute names and values

    Returns: attribute dictionary renamed to include selected namespace

    """
    # get namespace from attribute dictionary key
    cur_namespace = (list(attr_dict.keys())[0]).split(':')[0]
    # check if namespace already matches
    if cur_namespace == namespace:
        return attr_dict
    # if different copy renamed keys and values to new dict
    renamed_attr_dict = {}
    for name, value in attr_dict.items():
        new_name = '{}:{}'.format(namespace, name.split(':')[-1])
        node = new_name.split('.')[0]
        attr = new_name.split('.')[-1]
        # if object and attribute exists add it to new dictionary
        if not cmds.objExists(node):
            continue
        if cmds.attributeQuery(attr, node=node, exists=True):
            renamed_attr_dict[new_name] = value

    return renamed_attr_dict


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


def remove_json(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

