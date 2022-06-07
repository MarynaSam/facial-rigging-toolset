import maya.cmds as mc
from maya import OpenMaya as om

MAIN_GROUP = "Face"
FACE_GROUP = ["Model", "Motion", "Dont"] 
DONT_GROUP = ["Fascia_grp", "Shapes_grp", "Infs_grp", "Deformers_grp", "Follicles_grp", "Eyelid_Setup_grp", "Clusters_grp"]
FASCIA_GROUP = ["Shapes_geo", "Infs_Local_geo", "Infs_Broad_geo", "Clusters_geo", "Joints_geo", "Deformers_geo", "Follicles_geo", "Wrap_geo"]
EYELID_SETUP_GROUP = ["Eyelid_Curves_grp","Eyelid_Locators_grp"]
HEAD_JNT = "_head_jnt"



def parent_mesh_under_model_group():

    meshes_to_parent = mc.ls(selection=True)

    if not meshes_to_parent:
        om.MGlobal.displayError("Please select the meshes you'd like to parent under 'Model'.")
        return

    mc.parent(meshes_to_parent, FACE_GROUP[0])


def parent_joints_under_motion_group():

    joints_to_parent = mc.ls(selection=True)

    if not joints_to_parent:
        om.MGlobal.displayError("Please select the joints you'd like to parent under 'Motion'.")
        return   

    mc.parent(joints_to_parent[0], FACE_GROUP[1])


def _name_and_parent_groups(list_of_names, grp_to_parent):
    
    for index in range(len(list_of_names)):
        mc.group(em=True, name=list_of_names[index])
        mc.parent(list_of_names[index], grp_to_parent)    

    mc.select(clear=True)


def build_structure():
    
    mc.group(em=True, name=MAIN_GROUP)
    
    _name_and_parent_groups(FACE_GROUP, MAIN_GROUP)
    _name_and_parent_groups(DONT_GROUP, FACE_GROUP[2])
    _name_and_parent_groups(FASCIA_GROUP, DONT_GROUP[0])
    _name_and_parent_groups(EYELID_SETUP_GROUP, DONT_GROUP[5])