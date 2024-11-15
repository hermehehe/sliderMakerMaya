from maya import cmds
from slider_maker import core

WINDOW_NAME = 'slider_maker_ui'
TEXT_FIELD_NAME = 'slider_name'


def show_ui():
    """Show Slider Maker UI"""
    if cmds.window(WINDOW_NAME, query=True, exists=True):
        cmds.deleteUI(WINDOW_NAME)

    cmds.window(WINDOW_NAME, title='Slider Maker')
    # name slider
    cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.text(label='Slider Name')
    cmds.textField(TEXT_FIELD_NAME)

    # save selection
    cmds.setParent('..')
    cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
    cmds.text(label='Select animation controllers to create slider')
    cmds.button(label='Save Selection', command=save_selection)
    # set driven keys
    cmds.setParent('..')
    cmds.rowLayout(numberOfColumns=2)
    cmds.button(label='Set Min', height=25, command=set_min_key)
    cmds.button(label='Set Max', height=25, command=set_max_key)

    # apply keys
    cmds.setParent('..')
    cmds.button(label='Apply', height=30, command=apply_attr_dict)

    cmds.showWindow(WINDOW_NAME)


def get_name():
    """Get name from textbox and validate string
        Returns: name as string
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
    # validate selection
    if not selection:
        cmds.warning("Please select at least one controller!")
        return
    name = get_name()
    attr_dict = core.create_attr_dict(selection)

    # write attribute dict to a file
    core.write_attrs_to_file(name, attr_dict)


def get_attr_dict():
    """ Constructs file path and reads attribute dictionary

    Returns: attribute dictionary

    """
    name = get_name()
    slider_name = '{}_slider'.format(name)
    file_name = '{}.{}'.format(slider_name, core.EXT)
    file_path = core.os.path.join(core.ROOT_DIR, file_name)
    attr_dict = core.read_attrs_from_file(file_path)

    return attr_dict


def set_min_key(*args):
    """ Updates min attributes to file """
    attr_dict = get_attr_dict()

    attr_dict = core.update_attr_dict(attr_dict, 'min')
    core.write_attrs_to_file(get_name(), attr_dict)


def set_max_key(*args):
    """ Updates max attributes to file """
    attr_dict = get_attr_dict()

    attr_dict = core.update_attr_dict(attr_dict, 'max')
    core.write_attrs_to_file(get_name(), attr_dict)


def apply_attr_dict(*args):
    """ Creates slider controller and sets driven keys from attribute dictionary"""
    size = ' ' # MAKE THE SIZE WORK LATER
    name = get_name()
    controls = core.create_slider_ctrl(name, size)
    attr_dict = get_attr_dict()

    limit_dict = core.create_slider_attr(controls, size)
    core.set_driven_keys(attr_dict, limit_dict, controls)

