from maya import cmds
from slider_maker import core

WINDOW_NAME = 'slider_maker_ui'
TEXT_FIELD_NAME = 'slider_name'


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
    cmds.checkBox(label='Mirror', ann='Will apply keys to controls opposite from selected as well')
    cmds.checkBox(label='Zero as Default', ann='Sets 0 as midpoint for slider controller')

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
    if not selection:
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
    slider_name = get_name()
    if slider_name is None:
        return

    attr_dict = get_attr_dict()
    if attr_dict is None:
        return

    selected_namespace_list = core.get_selected_namespace()
    if len(selected_namespace_list) == 0:
        cmds.warning("Please select at least one rig!")
        return

    for namespace in selected_namespace_list:
        # rename attributes in dictionary to match selected namespace
        renamed_attr_dict = {}
        renamed_attr_dict = core.rename_attr_dict(namespace, attr_dict)
        if not renamed_attr_dict:
            cmds.warning('Cannot apply {} slider to {}'.format(slider_name, namespace))
            continue
        # create NURBS polygons slider
        controls = core.create_slider_ctrl(slider_name, namespace)
        # move slider to rig location
        selected = list(renamed_attr_dict.keys())[0]
        core.slider_position(controls, selected)
        # set driven keys
        limit_dict = core.create_slider_attr(controls)
        core.set_driven_keys(renamed_attr_dict, limit_dict, controls)

    # cleanup removing attr dict json file
    file_name = '{}_slider.{}'.format(slider_name, core.EXT)
    file_path = core.os.path.join(core.ROOT_DIR, file_name)

    core.remove_json(file_path)
