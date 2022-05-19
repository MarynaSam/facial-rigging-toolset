from functools import partial
from importlib import reload

import pymel.core as pm
import maya.cmds as mc
from maya import OpenMaya as om


from facial_rig_toolset import model_check
reload(model_check)



HEAD_GEOMETRY = "head_geo"
BODY_GEOMETRY = "body_geo"



def clean_up():
    
    model_check.delete_history()
    model_check.freeze_tranfsorm()
    model_check.zero_out_pivots()
    
    

def head_cut():
    '''
    Make the head cut
    It should be done before applying the skin cluster
    the part that has the head should be named "body_geo".
    '''
    
    #get selected faces
    head_faces  = mc.filterExpand(sm=34)

    if not head_faces:
        om.MGlobal.displayError("Please select the faces you'd like to extract.")
        return
    
    mc.polyChipOff(head_faces, dup=False)
    
    #to get faces for the body
    mc.InvertSelection()
    body_faces = mc.filterExpand(sm=34)
    
    mc.duplicate(BODY_GEOMETRY, n=HEAD_GEOMETRY)
    
    # delete faces for body
    mc.delete(head_faces)

    # for head
    mc.delete([item.replace(BODY_GEOMETRY, HEAD_GEOMETRY) for item in body_faces])
    
    head_name_dupl = "head_dupl_geo"
    
    mc.duplicate(HEAD_GEOMETRY, n=head_name_dupl)
    
    new_body = mc.polyUnite(head_name_dupl, BODY_GEOMETRY, name=BODY_GEOMETRY)
    mc.polyMergeVertex(d=0.00005)
    
    clean_up()

    mc.delete(head_name_dupl)
    
    root_parent = mc.listRelatives(HEAD_GEOMETRY, parent=True)
    
    if root_parent:
        pm.parent(BODY_GEOMETRY, root_parent)

    pm.parent(HEAD_GEOMETRY, world=True)
    
    clean_up()