from maya import cmds
from slider_maker import core

WINDOW_NAME = 'slider_maker_ui'
TEXT_FIELD_NAME = 'slider_name'
MIRROR_BOX = False
DEFAULT_BOX = True


def show_ui():
    """Show Slider Maker UI"""
    if cmds.window(WINDOW_NAME, query=True, exists=True):
        cmds.deleteUI(WINDOW_NAME)

    cmds.window(WINDOW_NAME, title='Slider Maker', width=150)
    # name slider
    cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.text(label='Slider Name')
    cmds.textField(TEXT_FIELD_NAME)

    # save selection
    cmds.setParent('..')
    cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
    cmds.text(label='Select animation controllers to create slider', font="boldLabelFont", height=30)
    cmds.button(label='Save Selection', command=save_selection)
    # set driven keys
    cmds.setParent('..')
    cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
    cmds.text(label='Move selected controls then save pose', font="boldLabelFont", height=30)
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=[1, 2])
    cmds.button(label='Set Min', height=30, ann='Save slider start key after moving controls', command=set_min_key)
    cmds.button(label='Set Max', height=30, ann='Save slider end key after moving controls', command=set_max_key)
    # check boxes
    cmds.setParent('..')
    cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=[1, 2])
    cmds.checkBox(MIRROR_BOX, label='Mirror', ann='Will apply keys to controls opposite from selected as well')
    cmds.checkBox(DEFAULT_BOX, label='Zero as Default', value=True, ann='Sets 0 as midpoint for slider controller')

    # apply keys
    cmds.setParent('..')
    cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
    cmds.text(label='Select one or multiple rigs then apply slider', font="boldLabelFont", height=30)
    cmds.button(label='Apply', height=60, ann='Create slider and set driven keys onto selected controls',
                bgc=[0.55, 0.19, 0.60], command=apply_attr_dict)

    cmds.showWindow(WINDOW_NAME)


def get_name():
    """Get name from textfield and validate
    Returns: name(str)
    """
    name = cmds.textField(TEXT_FIELD_NAME, query=True, text=True)
    # validate name
    if name == '':
        cmds.warning("Please type a slider name!")
        return
    return name


def save_selection(*args):
    """Saves animation controller selection"""
    selection = core.get_selection()
    name = get_name()
    if name == '':
        return
    # validate selection
    if selection is None:
        cmds.warning("Please select at least one controller!")
        return

    attr_dict = core.create_attr_dict(selection)

    # write attribute dict to a file
    core.write_attrs_to_file(name, attr_dict)


def get_attr_dict():
    """ Constructs file path and reads attribute dictionary

    Returns: attribute dictionary

    """
    name = get_name()
    if name is None:
        return
    file_name = '{}_slider.{}'.format(name, core.EXT)
    file_path = core.os.path.join(core.ROOT_DIR, file_name)

    if not core.os.path.exists(file_path):
        cmds.warning("Please save controller selection first!")
        return

    attr_dict = core.read_attrs_from_file(file_path)

    return attr_dict


def set_min_key(*args):
    """ Updates min attributes to file """
    attr_dict = get_attr_dict()
    name = get_name()
    if name is None:
        return

    if attr_dict is None:
        return
    attr_dict = core.update_attr_dict(attr_dict, 'min')
    core.write_attrs_to_file(name, attr_dict)


def set_max_key(*args):
    """ Updates max attributes to file """
    name = get_name()
    if name is None:
        return
    attr_dict = get_attr_dict()
    if attr_dict is None:
        return

    attr_dict = core.update_attr_dict(attr_dict, 'max')
    core.write_attrs_to_file(name, attr_dict)


def apply_attr_dict(*args):
    """ Creates slider controller NURBS polygon group and sets all driven keys from attribute dictionary"""
    zero_as_default_value = cmds.checkBox(DEFAULT_BOX, query=True, value=True)

    slider_name = get_name()
    if slider_name is None:
        return

    attr_dict = get_attr_dict()
    if attr_dict is None:
        return

    # added mirror attributes if box checked
    updated_attr_dict = add_mirror_attrs(slider_name, attr_dict)
    print("Mirror Attr Dict: ")
    print(updated_attr_dict)

    # get all selected rig namespaces
    selected_namespace_list = core.get_selected_namespace()
    if len(selected_namespace_list) == 0:
        cmds.warning("Please select at least one rig!")
        return
    # loop to set keys for all namespaces
    for namespace in selected_namespace_list:
        # rename attributes in dictionary to match selected namespace
        renamed_attr_dict = core.rename_attr_dict(namespace, updated_attr_dict)
        if not renamed_attr_dict:
            cmds.warning('Cannot apply {} slider to {}'.format(slider_name, namespace))
            continue

        # create NURBS polygons slider
        controls = core.create_slider_ctrl(slider_name, namespace)
        # move slider to rig location
        core.slider_position(controls, renamed_attr_dict)

        # set driven keys
        limit_dict = core.create_slider_attr(controls, zero_as_default_value)
        core.set_driven_keys(renamed_attr_dict, limit_dict, controls, zero_as_default_value)
        
    file_cleanup()


def add_mirror_attrs(name, attr_dict):
    """And mirror attributes to attribute dictionary if mirror box checked"""
    mirror_value = cmds.checkBox(MIRROR_BOX, query=True, value=True)

    if mirror_value:
        mirror_attr_dict = core.mirror_attrs(attr_dict)
        core.write_attrs_to_file(name, mirror_attr_dict)
        return mirror_attr_dict
    else:
        return attr_dict


def file_cleanup():
    """Remove json file storing attribute dictionary"""
    slider_name = get_name()
    file_name = '{}_slider.{}'.format(slider_name, core.EXT)
    file_path = core.os.path.join(core.ROOT_DIR, file_name)

    core.remove_json(file_path)






