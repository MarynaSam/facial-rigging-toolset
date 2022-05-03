from functools import partial
from importlib import reload

import pymel.core as pm
import maya.cmds as mc
from maya import OpenMaya as om

from facial_rig_toolset import model_check
reload(model_check)

HEAD_MESH_NAME = "head_geo"
BODY_MESH_NAME = "body_geo"


def extract_faces(faces):
    mc.ExtractFace(faces)



def head_cut():
    '''
    Make the head cut
    the part that has the head should be named "body_geo".

    Steps:
    1. Extract the selected faces
    2. Duplicate the cutted head
    3. Rename the duplicate as "head_geo"
    4. Unparent the "head_geo" 
    5. Delete the history
    6. Freeze transform
    7. Zero out the pivot

    8. Combine the old head with the body again
    9. Name is as "body_geo" parented uder world
    10. Delete the history to delete the previous "body_geo" group
    11. Merge the verts of the newly created "body_geo"
    12. Soften the edges
    13. Delete history
    14. Put it under the group where the old "body_geo" was
    '''

    # keep only selected faces
    faces = mc.filterExpand(sm=34)

    if not faces:
        om.MGlobal.displayError("Please select the faces you'd like to extract.")
        return

    extract_faces(faces)

    selected_body_parts = mc.ls(selection=True)

    root_parent = mc.listRelatives(
        mc.listRelatives(selected_body_parts[0], parent=True), 
        parent=True
    )

    mc.select(selected_body_parts[1], replace=True)

    head = mc.ls(selection=True)

    head_duplicate = mc.duplicate(head, n=HEAD_MESH_NAME)

    pm.parent(head_duplicate, world=True)

    model_check.delete_history()
    model_check.freeze_tranfsorm()
    model_check.zero_out_pivots()

    body_parts = [selected_body_parts[1], selected_body_parts[0]]

    new_body = mc.polyUnite(body_parts, name=BODY_MESH_NAME)

    new_body_selected = mc.ls(selection=True)

    model_check.delete_history()

    mc.polyMergeVertex(d=0.00005)

    model_check.soften_edges()
    model_check.delete_history()

    new_body_selected = mc.ls(selection=True, transforms=True)

    if root_parent:
        pm.parent(new_body_selected, root_parent)

    mc.select(head_duplicate, replace=True)