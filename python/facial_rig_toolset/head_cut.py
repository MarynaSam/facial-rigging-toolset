from functools import partial
from importlib import reload

import maya.cmds as mc
from maya import OpenMaya as om

from facial_rig_toolset import model_check
reload(model_check)


HEAD_GEOMETRY = "head_geo"
BODY_GEOMETRY = "body_geo"


def _clean_up():
    
    model_check.delete_history()
    model_check.zero_out_pivots()
    model_check.freeze_transform()
    

def _set_locked(obj, locked):
    '''
    lock/unlock the attributes
    '''
    attrs = mc.listAttr(obj)
    attrs.remove('visibility')


    for attr in attrs:
        try:
            if mc.getAttr(f"{obj}.{attr}", lock=True) != locked:
                mc.setAttr(f"{obj}.{attr}", lock=locked)
        except ValueError:
            print (f"Couldn't get locked-state of {obj}.{attr}")


def head_cut():
    '''
    Make the head cut
    It should be done before applying the skin cluster
    the part that has the head should be named "body_geo".
    '''

    if not mc.objExists(BODY_GEOMETRY):
        om.MGlobal.displayError(f"The object '{BODY_GEOMETRY}' doesn't exist. Please, rename the model as '{BODY_GEOMETRY}'")
        return 

    #body geo attributes unlock
    _set_locked(BODY_GEOMETRY, False)

    #get selected faces
    head_faces  = mc.filterExpand(sm=34)

    if not head_faces:
        om.MGlobal.displayError("Please select the faces you'd like to extract.")
        return

    mc.polyChipOff(head_faces, dup=False)
    
    # to get faces for the body
    mc.InvertSelection()
    body_faces = mc.filterExpand(sm=34)
    
    mc.duplicate(BODY_GEOMETRY, n=HEAD_GEOMETRY)
    
    # delete faces for body
    mc.delete(head_faces)

    # for head
    mc.delete([item.replace(BODY_GEOMETRY, HEAD_GEOMETRY) for item in body_faces])

    temp_body_name = "body_temp_name"

    mc.rename(BODY_GEOMETRY, temp_body_name)
    
    head_name_dupl = "head_dupl_geo"
    
    mc.duplicate(HEAD_GEOMETRY, n=head_name_dupl)
    
    # new body
    mc.polyUnite(head_name_dupl, temp_body_name, name=BODY_GEOMETRY)
    mc.polyMergeVertex(d=0.00005)
    
    _clean_up()

    mc.delete(head_name_dupl)

    root_parent = mc.listRelatives(HEAD_GEOMETRY, parent=True)
    
    if root_parent:
        mc.parent(BODY_GEOMETRY, root_parent)
        mc.parent(HEAD_GEOMETRY, world=True)

    _clean_up()
    
    _set_locked(BODY_GEOMETRY, True)

    _set_locked(HEAD_GEOMETRY, True)

    mc.select(HEAD_GEOMETRY)