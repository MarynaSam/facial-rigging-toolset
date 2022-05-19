from genericpath import exists
from importlib import reload

import maya.cmds as mc
from maya import OpenMaya as om

from facial_rig_toolset import file_structure
reload(file_structure)


GUIDES_NAME = ["Jaw_loc", "Jaw_Bt_loc", "Jaw_Tp_loc", "Jaw_Lf_loc", "Jaw_Rt_loc"]
JAW_LOCATORS = {
    GUIDES_NAME[0]: [0, 0, 0],
    GUIDES_NAME[1]: [0, -0.3, 5],
    GUIDES_NAME[2]: [0, 0.3, 5],
    GUIDES_NAME[3]: [3, 0, 5],
    GUIDES_NAME[4]: [-3, 0, 5]   
    }

JAW_MAIN_GROUP_NAME = "Jaw_grp"
JAW_CONTROL_GROUP = "Jaw_sdk"
JAW_CONTROL_NAME = "Jaw_ctl"
JAW_JOINTS_NAME = ["Jaw_jnt", "Jaw_Bt_jnt", "Jaw_Tp_jnt", "Jaw_Lf_jnt", "Jaw_Rt_jnt"]
JAW_NO_JOINTS_NAME = ["Jaw_No_jnt", "Jaw_Bt_Base_jnt", "Jaw_Tp_Base_jnt", "Jaw_Lf_Base_jnt", "Jaw_Rt_Base_jnt"]


def create_locator_guides():
    '''
        axis Z is a front axis
        axis Y is a top axis
        axis X is a side axis
    '''
    for attr, value in JAW_LOCATORS.items():
        mc.spaceLocator(position=value, name=attr)
        mc.xform(centerPivots=True)

        mc.setAttr(f"{attr}.s", 0.3, 0.3, 0.3)
        #mc.makeIdentity(attr, apply=True, t=1, r=1, s=1, n=0, pn=1)

        if attr != GUIDES_NAME[0]:
            mc.parent(attr, GUIDES_NAME[0])

    mc.select(GUIDES_NAME[0])


def create_control(group_name, control_name, color):

    mc.circle(n=control_name)
    mc.setAttr(f"{control_name}Shape.overrideEnabled", 1)
    mc.setAttr(f"{control_name}Shape.overrideColor", color)
    mc.xform(control_name, ro=(-90,0,0))
    mc.delete(control_name, ch=True)
    mc.makeIdentity(control_name, apply=True, t=1, r=1, s=1, n=0, pn=1)
    mc.group(n=group_name)


def create_jaw_joints():

    locators_position = []
    #get the world space locators position
    for index in range(len(GUIDES_NAME)):
        loc = mc.xform(GUIDES_NAME[index], ws=True, q=True, rp=1)
        locators_position.append(loc)
        mc.select(clear=True)

    #delete the locators
    mc.delete(GUIDES_NAME[0])

    #create the corntrol and the groups
    create_control(JAW_CONTROL_GROUP, JAW_CONTROL_NAME, 14)
    mc.group(n=JAW_MAIN_GROUP_NAME)
    mc.select(clear=True)

    #create and rename jaw joints
    for index in range(len(JAW_JOINTS_NAME)):
        joint_name = JAW_JOINTS_NAME[index]
        joint_no_name = JAW_NO_JOINTS_NAME[index]
        if joint_name != JAW_JOINTS_NAME[4]:
            mc.joint(p=locators_position[index], n=joint_name, rad=0.5)
            mc.duplicate(joint_name, n=joint_no_name)

        else:
            position = locators_position[index-1]
            position[0] = -position[0]
            mc.joint(p=position, n=joint_name, rad=0.5)
            mc.duplicate(joint_name, n=joint_no_name)
        mc.select(clear=True)

    #position Jaw_grp where the jaw_jnt is
    mc.xform(JAW_MAIN_GROUP_NAME, t=locators_position[0])

    #parent jaw_base joints under jaw_jnt
    for index in range(1,len(JAW_NO_JOINTS_NAME)):
        mc.parent(JAW_NO_JOINTS_NAME[index], JAW_JOINTS_NAME[0])
        mc.xform(JAW_NO_JOINTS_NAME[index], t=(0,0,0))

    #parent jaw joints under base jointd
    for index in range(1,len(JAW_JOINTS_NAME)):
        mc.parent(JAW_JOINTS_NAME[index], JAW_NO_JOINTS_NAME[index])

    #parent jaw joint under the control
    mc.parent(JAW_JOINTS_NAME[0], JAW_CONTROL_NAME)

    #parent jaw no control and the jaw group
    mc.parent(JAW_NO_JOINTS_NAME[0], JAW_MAIN_GROUP_NAME)

    mc.select(JAW_CONTROL_NAME) 
    

def parent_jaw_under_motion():
    mc.parent(JAW_MAIN_GROUP_NAME, file_structure.FACE_GROUP[1])
    mc.select(JAW_CONTROL_NAME)


def remap_node(node_type, node_name, minInp=1, maxInp=1):

    mc.createNode(node_type, n=node_name)
    mc.setAttr(f"{node_name}.inputMin", minInp)

def add_attr_to_control():

    attrs = {
        "jawOpen": "none",
        "chew": [0,1],
        "chewHeight": [-1, 1],
        "cornerPinLf": [-1, 1],
        "cornerPinRt": [-1, 1]
    }

    for attr_name, value in attrs.items():

        node_name_short = "_RMVN"
        node_name = f"{attr_name}_{node_name_short}"

        # checking the type of the object
        if not isinstance(value, list):
            mc.addAttr(JAW_CONTROL_NAME, longName=attr_name, k=True)
        else:
            mc.addAttr(JAW_CONTROL_NAME, longName=attr_name, minValue=value[0], maxValue=value[1], k=True)

            if value[0] == -1:
                remap_node("remapValue", node_name, value[0])

                mc.connectAttr(f"{JAW_CONTROL_NAME}.{attr_name}", f"{node_name}.inputValue")


def constrain_jaw_base_joints():

    constraints = []
    attr_name = "Switch"
    node_type = "reverse"
    node_name_short = "_RVS"

    for index in range(1, len(JAW_NO_JOINTS_NAME)):
        jaw_no_jnt = JAW_NO_JOINTS_NAME[0]
        jaw_jnt = JAW_JOINTS_NAME[0]
        jaw_base_joint = JAW_NO_JOINTS_NAME[index]
        node_name = f"{jaw_base_joint}_{node_name_short}"

        parent_constraint = mc.parentConstraint(jaw_no_jnt, jaw_jnt, jaw_base_joint)
        mc.addAttr(f"{parent_constraint[0]}", longName=attr_name, minValue=0, maxValue=1, k=True)
        constraints.append(parent_constraint[0])

        mc.createNode(node_type, n=node_name)

        mc.connectAttr(f"{parent_constraint[0]}.{attr_name}", f"{parent_constraint[0]}.{jaw_no_jnt}W0")

        mc.connectAttr(f"{parent_constraint[0]}.{attr_name}", f"{node_name}.input.inputX")
        mc.connectAttr(f"{node_name}.output.outputX", f"{parent_constraint[0]}.{jaw_jnt}W1")


