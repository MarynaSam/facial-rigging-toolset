from genericpath import exists
from importlib import reload

import maya.cmds as mc
from maya import OpenMaya as om

from facial_rig_toolset import structure
reload(structure)

from facial_rig_toolset import model_check
reload(model_check)


ROOT_GUIDE = "Jaw_guide"
GUIDES = [ROOT_GUIDE, "Jaw_Bt_guide", "Jaw_Tp_guide", "Jaw_Lf_guide", "Jaw_Rt_guide"]
GUIDE_POSITIONS = {
    ROOT_GUIDE: [0, 0, 0],
    GUIDES[1]: [0, -0.3, 5],
    GUIDES[2]: [0, 0.3, 5],
    GUIDES[3]: [3, 0, 5],
    GUIDES[4]: [-3, 0, 5]   
}

JAW_MAIN_GROUP = "Jaw_grp"
JAW_CONTROL_GROUP = "Jaw_sdk"
JAW_CONTROL = "Jaw_ctl"

ROOT_JOINT = "Jaw_jnt"
JAW_JOINTS = [ROOT_JOINT, "Jaw_Bt_jnt", "Jaw_Tp_jnt", "Jaw_Lf_jnt", "Jaw_Rt_jnt"]
JAW_NO_JOINTS = ["Jaw_No_jnt", "Jaw_Bt_Base_jnt", "Jaw_Tp_Base_jnt", "Jaw_Lf_Base_jnt", "Jaw_Rt_Base_jnt"]

ATTR_NAMES = ["jawOpen", "chew", "chewHeight", "cornerPinLf", "cornerPinRt"]
ATTR_RANGES = {
    ATTR_NAMES[0]: "none",
    ATTR_NAMES[1]: [0,1],
    ATTR_NAMES[2]: [-1, 1],
    ATTR_NAMES[3]: [-1, 1],
    ATTR_NAMES[4]: [-1, 1]
}

REMAP_VALUE_NODE = "remapValue"
BLEND_COLORS_NODE = "blendColors"
REMAP_VALUE_SUFFIX = "_RMVN"
BLEND_COLORS_SUFFIX = "_BLNDC"

BLEND_COLORS_NODES = [f"Jaw_TpBt{BLEND_COLORS_SUFFIX}", f"Jaw_LfRt{BLEND_COLORS_SUFFIX}"]
REMAP_VALUE_NODES = [f"{ATTR_NAMES[2]}{REMAP_VALUE_SUFFIX}", f"{ATTR_NAMES[3]}{REMAP_VALUE_SUFFIX}", f"{ATTR_NAMES[4]}{REMAP_VALUE_SUFFIX}"]


def create_guides():
    '''
        axis Z is a front axis
        axis Y is a top axis
        axis X is a side axis
    '''
    if mc.objExists(ROOT_GUIDE):
        button = mc.confirmDialog(
            title="Guides Exist",
            message="The Guides already exist in the scene. Are you sure you want to re-create it?",
            button=["Yes", "No"],
            defaultButton="No",
            cancelButton="No",
            dismissString="No"
        )
        if button == "No":
            return

        mc.delete(ROOT_GUIDE)

    for guide, pos in GUIDE_POSITIONS.items():

        mc.spaceLocator(position=pos, name=guide)
        mc.xform(centerPivots=True)

        mc.setAttr(f"{guide}Shape.localScale", 0.3, 0.3, 0.3)

        if guide != ROOT_GUIDE:
            mc.parent(guide, ROOT_GUIDE)

    mc.select(ROOT_GUIDE)


def build():
    if not mc.objExists(ROOT_GUIDE):
        mc.confirmDialog(
            title="Guides Don't Exist",
            message="Please create a Guide Rig to continue.",
            button=["Ok"]
        )            
        return

    if mc.objExists(JAW_MAIN_GROUP):
        button = mc.confirmDialog(
            title="The Jaw Rig Already Exists",
            message="The Jaw Rig already exists in the scene. Are you sure you want to re-create it?",
            button=["Yes", "No"],
            defaultButton="No",
            cancelButton="No",
            dismissString="No"
        )
        if button == "No":
            return

        mc.delete(JAW_MAIN_GROUP)
        model_check.delete_unused_nodes()


    # create main control and sdk group above it
    _create_control(JAW_CONTROL_GROUP, JAW_CONTROL, 14)
    
    # create main group above sdk group
    mc.group(JAW_CONTROL_GROUP, n=JAW_MAIN_GROUP)

    _create_joints_from_guides()

    # hide guides
    mc.hide(ROOT_GUIDE)

    _build_hierarchy()

    mc.select(JAW_CONTROL)

    constraints = _constraint_base_joints()
    _set_attrs_to_jaw_control(constraints)

    _parent_jaw_to_motion_group()


def set_jaw_ranges():

    if not mc.objExists(JAW_CONTROL):
        mc.confirmDialog(
            title="Jaw Control Doesn't Exist",
            message="Please run the 'create_guides' and 'build' functions first.",
            button=["Ok"]
        )            
        return

    open_jaw_angle = mc.getAttr(f"{JAW_CONTROL}.rx")

    if open_jaw_angle < 0.001:
        mc.confirmDialog(
            title="Jaw control's rotation is not updated",
            message=(
                "Jaw control's rotation X is not updated. "
                "Please set it to the angle you'd like to use for a fully open mouth."),
            button=["Ok"]
        )            
        return

    driver = JAW_CONTROL
    driven = JAW_CONTROL_GROUP

    for attr in ('jawOpen', 'rx', 'ty', 'tz'):
        mc.setAttr(f"{driver}.{attr}", 0)

    mc.setDrivenKeyframe(
        [f"{driven}.ty", f"{driven}.tz", f"{driven}.rx"], 
        currentDriver=f"{driver}.jawOpen", itt="clamped", ott="clamped"
    )

    mc.setAttr(f"{driver}.jawOpen", 1) 

    mc.setAttr(f"{driven}.ty", 0)
    mc.setAttr(f"{driven}.tz", 0)
    mc.setAttr(f"{driven}.rx", open_jaw_angle)

    mc.setDrivenKeyframe([f"{driven}.ty", f"{driven}.tz", f"{driven}.rx"], currentDriver=f"{driver}.jawOpen", itt="clamped", ott="clamped")

    mc.setAttr(f"{driver}.jawOpen", 0)
    
    mc.select(driven)

    # for this command to work on all the attributes
    # we've just pre-selected the object itself
    mc.setInfinity(pri="linear", poi="linear")

    _set_closed_jaw_movement()

    mc.select(driver)


def _parent_jaw_to_motion_group():
    motion_group = structure.FACE_GROUP[1]

    if mc.objExists(motion_group):
        mc.parent(JAW_MAIN_GROUP, motion_group)
        mc.select(JAW_CONTROL)


def _create_joints_from_guides():
    guide_positions = _get_guide_positions()

    # create and rename jaw joints
    for index in range(len(JAW_JOINTS)):

        joint_name = JAW_JOINTS[index]
        joint_no_name = JAW_NO_JOINTS[index]

        # if the joint is on the right side
        if '_Rt_' in joint_name:
            # get left guide position and mirror it
            position = guide_positions[index-1]
            position[0] = -position[0]                
        else:
            position = guide_positions[index]

        mc.select(clear=True)

        mc.joint(p=position, n=joint_name, rad=0.5)
        mc.duplicate(joint_name, n=joint_no_name)
        
    mc.select(clear=True)


def _build_hierarchy():
    # get root joint position
    root_joint_pos = mc.xform(ROOT_JOINT, ws=True, q=True, rp=1)

    # move Jaw_grp to the root joint position
    mc.xform(JAW_MAIN_GROUP, t=root_joint_pos)

    # parent jaw_base joints under jaw_jnt
    for index in range(1, len(JAW_NO_JOINTS)):
        jaw_no_joint = JAW_NO_JOINTS[index]
        mc.parent(jaw_no_joint, JAW_JOINTS[0])
        mc.xform(jaw_no_joint, t=(0,0,0))

    # parent jaw joints under base jointd
    for index in range(1, len(JAW_JOINTS)):
        mc.parent(JAW_JOINTS[index], JAW_NO_JOINTS[index])

    # parent jaw joint under the control
    mc.parent(JAW_JOINTS[0], JAW_CONTROL)

    # parent jaw no control and the jaw group
    mc.parent(JAW_NO_JOINTS[0], JAW_MAIN_GROUP)


def _constraint_base_joints():

    constraints = []
    attr_name = "Switch"
    node_type = "reverse"
    node_name_suffix = "_RVS"

    for index in range(1, len(JAW_NO_JOINTS)):
        jaw_no_jnt = JAW_NO_JOINTS[0]
        jaw_jnt = JAW_JOINTS[0]
        jaw_base_joint = JAW_NO_JOINTS[index]
        node_name = f"{jaw_base_joint}{node_name_suffix}"

        parent_constraint = mc.parentConstraint(jaw_no_jnt, jaw_jnt, jaw_base_joint)
        mc.addAttr(f"{parent_constraint[0]}", longName=attr_name, minValue=0, maxValue=1, k=True)
        constraints.append(parent_constraint[0])

        mc.createNode(node_type, n=node_name)

        mc.connectAttr(f"{parent_constraint[0]}.{attr_name}", f"{parent_constraint[0]}.{jaw_no_jnt}W0")

        mc.connectAttr(f"{parent_constraint[0]}.{attr_name}", f"{node_name}.input.inputX")
        mc.connectAttr(f"{node_name}.output.outputX", f"{parent_constraint[0]}.{jaw_jnt}W1")

    return constraints


def _create_control(group_name, control_name, color):
    # create control
    mc.circle(n=control_name)

    # apply color
    mc.setAttr(f"{control_name}Shape.overrideEnabled", 1)
    mc.setAttr(f"{control_name}Shape.overrideColor", color)

    # delete construction history
    mc.delete(control_name, ch=True)

    # orient
    mc.xform(control_name, ro=(-90,0,0))   
    
    # freeze transforms
    mc.makeIdentity(control_name, apply=True, t=1, r=1, s=1, n=0, pn=1)

    mc.group(control_name, n=group_name)

    mc.select(clear=True)


def _get_guide_positions():
    guide_positions = []

    # get the world space positions of the guides
    for guide in GUIDES:
        position = mc.xform(guide, ws=True, q=True, rp=1)
        guide_positions.append(position)

    return guide_positions


def _set_attrs_to_jaw_control(constraints):
    remap_values_nodes = []

    #add attrs to the jaw control and create the remapValue node
    for attr_name, val_range in ATTR_RANGES.items():
        node_name = f"{attr_name}{REMAP_VALUE_SUFFIX}"

        # checking the type of the object
        if not isinstance(val_range, list):
            mc.addAttr(JAW_CONTROL, longName=attr_name, k=True)
        else:
            mc.addAttr(JAW_CONTROL, longName=attr_name, minValue=val_range[0], maxValue=val_range[1], k=True)

            if val_range[0] == -1:
                mc.createNode(REMAP_VALUE_NODE, n=node_name)
                mc.setAttr(f"{node_name}.inputMin", val_range[0])

                mc.connectAttr(f"{JAW_CONTROL}.{attr_name}", f"{node_name}.inputValue")

                remap_values_nodes.append(node_name)

    blend_colors_nodes = []
    
    # create two the blendColors node
    for node_name in BLEND_COLORS_NODES:

        mc.createNode(BLEND_COLORS_NODE, n=node_name)
        mc.connectAttr(f"{JAW_CONTROL}.{ATTR_NAMES[1]}", f"{node_name}.blender")

        blend_colors_nodes.append(node_name)

    # create connection between the remapValue nodes and blendColors nodes
    for blend_colors_node in blend_colors_nodes: 

        for remap_value_node in remap_values_nodes:

            if remap_value_node == REMAP_VALUE_NODES[0]:
                mc.connectAttr(f"{remap_value_node}.outValue", f"{blend_colors_node}.color1.color1R")
                mc.connectAttr(f"{remap_value_node}.outValue", f"{blend_colors_node}.color1.color1G")

            if blend_colors_node == BLEND_COLORS_NODES[0]:
                mc.setAttr(f"{blend_colors_node}.color2", *[1,0,0], type="double3")
        
            if blend_colors_node == BLEND_COLORS_NODES[1] and \
                    (remap_value_node == REMAP_VALUE_NODES[1] or \
                        remap_value_node == REMAP_VALUE_NODES[2]):

                if remap_value_node == REMAP_VALUE_NODES[1]:
                    mc.connectAttr(f"{remap_value_node}.outValue", f"{blend_colors_node}.color2.color2R")

                if remap_value_node == REMAP_VALUE_NODES[2]:
                    mc.connectAttr(f"{remap_value_node}.outValue", f"{blend_colors_node}.color2.color2G")

                mc.setAttr(f"{blend_colors_node}.color2.color2B", 0)
    
    # connect blendColors to the joints' constraints
    for blend_colors_node in blend_colors_nodes:

        if blend_colors_node == BLEND_COLORS_NODES[0]:
            mc.connectAttr(f"{blend_colors_node}.output.outputR", f"{constraints[1]}.Switch")
            mc.connectAttr(f"{blend_colors_node}.output.outputG", f"{constraints[0]}.Switch") 

        if blend_colors_node == BLEND_COLORS_NODES[1]:
            mc.connectAttr(f"{blend_colors_node}.output.outputR", f"{constraints[2]}.Switch")
            mc.connectAttr(f"{blend_colors_node}.output.outputG", f"{constraints[3]}.Switch")


def _set_closed_jaw_movement():

    name = "jawOpen"
    node_type = "condition"
    node_name_suffix = "_COND"
    node_name = f"{name}{node_name_suffix}"
    node_existing_flag = False

    if mc.objExists(node_name):
        model_check.delete_unused_nodes()
        mc.delete(node_name)
        node_existing_flag = True 

    mc.createNode(node_type, n=node_name)
    mc.setAttr(f"{node_name}.operation", 3)

    mc.connectAttr(f"{JAW_CONTROL}.{ATTR_NAMES[0]}", f"{node_name}.firstTerm")
    mc.connectAttr(f"{JAW_CONTROL}.{ATTR_NAMES[1]}", f"{node_name}.colorIfTrue.colorIfTrueR")

    for blend_colors_node in BLEND_COLORS_NODES:
        if not node_existing_flag:
            mc.disconnectAttr(f"{JAW_CONTROL}.{ATTR_NAMES[1]}", f"{blend_colors_node}.blender")

        mc.connectAttr(f"{node_name}.outColor.outColorR", f"{blend_colors_node}.blender")
