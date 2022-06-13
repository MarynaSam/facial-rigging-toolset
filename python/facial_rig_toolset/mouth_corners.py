from importlib import reload
from functools import reduce
import math
import os

import maya.cmds as mc
import math
from maya import OpenMaya as om
from maya import mel

from facial_rig_toolset import model_check
from facial_rig_toolset import head_cut
reload(model_check)
reload(head_cut)


CLEAN_MODEL_MOUTH_CORNER = "mouth_cluster_geo"
CLEAN_MODEL = "clean_head_geo"
MOUTH_CLUSTER_GROUP = "WIP_mouth_corner_grp"
MOUTH_CORNER_CLUSTER_NAME = "mouth_cluster_geo_clsHandle"
MOUTH_MASK_NAMES = ["mouth_corner_eye_mask", "mouth_corner_nose_mask", "mouth_corner_chin_mask", "mouth_corner_half_face_mask"]
MOUTH_CORNER_LF_NAMES = ["smileLf", "smileWideLf", "wideLf", "frownWideLf", "frownLf", "frownNarrowLf", "narrowLf", "smileNarrowLf"]
MOUTH_CORNER_RT_NAMES = ["smileRt", "smileWideRt", "wideRt", "frownWideRt", "frownRt", "frownNarrowRt", "narrowRt", "smileNarrowRt"]
CORNER_SHAPE_LOCATION = [1, 3, 5, 7]
MOUTH_CORNER_LF_COMBO_NAMES = ["smileWideLf_combo", "frownWideLf_combo", "frownNarrowLf_combo", "smileNarrowLf_combo"]
MOUTH_CORNER_RT_COMBO_NAMES = ["smileWideRt_combo", "frownWideRt_combo", "frownNarrowRt_combo", "smileNarrowRt_combo"]
MOUTH_CORNER_CONTROL_NAMES = ["MouthLf_Corner_ctl", "MouthRt_Corner_ctl"]
BLEND_SHAPE = "_blendShape"

HEIGHT_MULTIPLIER = 1
WIDTH_MULTIPLIER = 2
KEYFRAME_COUNT = 9
MIRROR_SIZE_BBOX_MULTIPLIER = 45


def _get_head_bbox():
    return mc.exactWorldBoundingBox(head_cut.HEAD_GEOMETRY)


def _set_locked(obj, locked):
    '''
    lock/unlock the attributes
    '''
    attrs = mc.listAttr(obj)
    attrs.remove('visibility')

    mc.setAttr(f"{obj}.visibility", 1)

    for attr in attrs:
        try:
            if mc.getAttr(f"{obj}.{attr}", lock=True) != locked:
                mc.setAttr(f"{obj}.{attr}", lock=locked)
        except ValueError:
            print (f"Couldn't get locked-state of {obj}.{attr}")


def get_clean_model():
    '''
    makes a clean copy of the head
    rename it as 'clean_model_geo' and delete the history
    select the model
    '''

    if not mc.objExists(head_cut.HEAD_GEOMETRY):
        om.MGlobal.displayError(f"The object '{head_cut.HEAD_GEOMETRY}' doesn't exist. Please, rename your head geometry as '{head_cut.HEAD_GEOMETRY}'")
        return

    clean_mouth_model = mc.duplicate(head_cut.HEAD_GEOMETRY, n=CLEAN_MODEL)
    _set_locked(CLEAN_MODEL, False)
    # delete construction history
    mc.delete(clean_mouth_model, ch=True)

    root_parent = mc.listRelatives(head_cut.HEAD_GEOMETRY, parent=True)
    
    if root_parent:
        mc.parent(clean_mouth_model, world=True)

    # getting the width of the model
    model_width_bbox = math.ceil(_get_head_bbox()[5])

    # calculating the Tx of the duplicate
    clean_mouth_model_pos_x = mc.xform(head_cut.HEAD_GEOMETRY, ws=True, q=True, rp=1)[1] - model_width_bbox*WIDTH_MULTIPLIER

    mc.xform(clean_mouth_model, ws=True, t=[clean_mouth_model_pos_x, 0, 0])

    mc.select(clean_mouth_model)


def get_cluster_model():
    '''
    makes a copy of the head
    rename it as 'mouth_cluster_geo' and delete the history
    position the duplicate above the head considering the height of the model
    select the model
    '''

    if not mc.objExists(head_cut.HEAD_GEOMETRY):
        om.MGlobal.displayError(f"The object '{head_cut.HEAD_GEOMETRY}' doesn't exist. Please, rename your head geometry as '{head_cut.HEAD_GEOMETRY}'")
        return

    if mc.objExists(CLEAN_MODEL_MOUTH_CORNER):
        button = mc.confirmDialog(
            title="The Cluster Mouth Model Exists",
            message="The Cluster Mouth Model already exists in the scene. Are you sure you want to re-create it?",
            button=["Yes", "No"],
            defaultButton="No",
            cancelButton="No",
            dismissString="No"
        )
        if button == "No":
            return

        mc.delete(CLEAN_MODEL_MOUTH_CORNER)
        model_check.delete_unused_nodes()

    clean_mouth_model = mc.duplicate(head_cut.HEAD_GEOMETRY, n=CLEAN_MODEL_MOUTH_CORNER)
    _set_locked(CLEAN_MODEL_MOUTH_CORNER, False)
    # delete construction history
    mc.delete(clean_mouth_model, ch=True)

    root_parent = mc.listRelatives(head_cut.HEAD_GEOMETRY, parent=True)
    
    if root_parent:
        mc.parent(clean_mouth_model, world=True)

    # getting the height of the model
    model_height_bbox = math.ceil(_get_head_bbox()[4])

    # calculating the Ty of the duplicate
    clean_mouth_model_pos_y = mc.xform(head_cut.HEAD_GEOMETRY, ws=True, q=True, rp=1)[1] + model_height_bbox*HEIGHT_MULTIPLIER

    mc.xform(clean_mouth_model, ws=True, t=[0, clean_mouth_model_pos_y, 0])

    mc.select(clean_mouth_model)


def call_ss_buddy():
    '''
    call ssBuddy
    '''
    ss_buddy_script_path = os.path.join(
        os.path.dirname(__file__), 'mel', 'ssBuddy.mel')

    ss_buddy_script_path = os.path.normpath(ss_buddy_script_path)
    ss_buddy_script_path = ss_buddy_script_path.replace('\\', '\\\\')

    print(ss_buddy_script_path)

    mel.eval(f'source "{ss_buddy_script_path}"')


def set_soft_cluster_shapes():
    '''
    select the soft cluster handle
    set 8 frames on the timeline
    position the cluster with step 1
    '''

    soft_cluster_position = {
        0: {
            'tx':0,
            'ty':0,
            'tz':0
        },
        10:{
            'tx':0,
            'ty':1,
            'tz':0  
        },
        20:{
            'tx':1,
            'ty':1,
            'tz':-1
        },
        30:{
            'tx':1,
            'ty':0,
            'tz':-1 
        },
        40:{
            'tx':1,
            'ty':-1,
            'tz':-1 
        },
        50:{
            'tx':0,
            'ty':-1,
            'tz':0
        },
        60:{
            'tx':-1,
            'ty':-1,
            'tz':0
        },
        70:{
            'tx':-1,
            'ty':0,
            'tz':0
        },
        80:{
            'tx':-1,
            'ty':1,
            'tz':0
        }

    }

    if not mc.objExists(MOUTH_CORNER_CLUSTER_NAME):
        om.MGlobal.displayError(f"The cluster '{MOUTH_CORNER_CLUSTER_NAME}' doesn't exist. Please, rename the cluster handle as '{MOUTH_CORNER_CLUSTER_NAME}'")
        return

    mc.select(MOUTH_CORNER_CLUSTER_NAME)
    
    # identify if there are any keyframes on the cluster
    if_keyframes = mc.keyframe(MOUTH_CORNER_CLUSTER_NAME, q=True, kc=True)

    if if_keyframes > 0:
        button = mc.confirmDialog(
            title="The Keyframes Exist",
            message="It seems, there are keyframes on the soft cluster. Are you sure you want to re-create them? The modification will be lost.",
            button=["Yes", "No"],
            defaultButton="No",
            cancelButton="No",
            dismissString="No"
        )
        if button == "No":
            return

    # keyframe the cluster hamdle each 10th frame 8 times
    for key_frame_number in range(0, KEYFRAME_COUNT*10, 10):
        mc.currentTime(key_frame_number, edit=True)
        coords = soft_cluster_position[key_frame_number]
        mc.xform(
            MOUTH_CORNER_CLUSTER_NAME,
            t=[
                coords['tx'], 
                coords['ty'], 
                coords['tz']
            ]
        )
        mc.setKeyframe(MOUTH_CORNER_CLUSTER_NAME, t=[key_frame_number])
        
    mc.keyTangent(MOUTH_CORNER_CLUSTER_NAME,inTangentType="linear", outTangentType="linear")
    mc.currentTime(0, edit=True)


def make_claster_mask_shapes():
    '''
    Makes the shapes for the masking
    Names the masks
    '''
    mc.currentTime(0, edit=True)

    if not mc.objExists(CLEAN_MODEL_MOUTH_CORNER):
        om.MGlobal.displayError(f"The object '{CLEAN_MODEL_MOUTH_CORNER}' doesn't exist. Please, rename the model as '{CLEAN_MODEL_MOUTH_CORNER}'")
        return 

    mask_exists = False
    mask_obj = []

    for mask_name in MOUTH_MASK_NAMES:
        if mc.objExists(mask_name):
            mask_exists = True
            mask_obj.append(mask_name)

    if mask_exists > 0:
        button = mc.confirmDialog(
            title="The Mask(s) Exist",
            message=f"It seems, there are shapes for masking: {mask_obj}. Are you sure you want to re-create them? The modification will be lost.",
            button=["Yes", "No"],
            defaultButton="No",
            cancelButton="No",
            dismissString="No"
        )
        if button == "No":
            return
        else:
            mc.delete(mask_obj)

    # getting the width of the model 
    model_width_bbox = math.ceil(_get_head_bbox()[5]) 

    previous_model = CLEAN_MODEL_MOUTH_CORNER

    for model_name in MOUTH_MASK_NAMES:

        new_model = mc.duplicate(previous_model, n = model_name)
        previous_model_position = mc.xform(previous_model, ws=True, q=True, rp=1)
        new_model_pos_x = previous_model_position[0] + model_width_bbox*WIDTH_MULTIPLIER
        mc.xform(new_model, ws=True, t=[new_model_pos_x, previous_model_position[1], previous_model_position[2]])
        mc.blendShape(previous_model, new_model, topologyCheck=True, w=(0,1), name=f"{model_name}{BLEND_SHAPE}")
        previous_model = new_model


def make_mouth_corner_shape():
    '''
    makes 8 mouth corners shapes that should be cleaned by the rigger
    posiotn this 8 shapes in a square manner
    '''
    model_selected = mc.ls(selection=True, type='transform')

    # checking if the model selected
    if not model_selected:
        om.MGlobal.displayError("Please select one model")
        return
    
    # checking if only one model selected
    if len(model_selected) > 1:
        om.MGlobal.displayError("Please select only ONE model")
        return

    # checking if the mouth corner shapes already in the scene
    shapes_exist = []
    for mouth_shape in MOUTH_CORNER_LF_NAMES:
        if mc.objExists(mouth_shape):
            shapes_exist.append(mouth_shape)

    if len(shapes_exist) > 0:
        button = mc.confirmDialog(
            title="The Mouth Shape(s) Exist",
            message=f"It seems, the mouth corner shapes exist. Are you sure you want to re-create them? The modification will be lost.",
            button=["Yes", "No"],
            defaultButton="No",
            cancelButton="No",
            dismissString="No"
        )
        if button == "No":
            return
        else:
            for mouth_shape in MOUTH_CORNER_LF_NAMES:
                mc.delete(mouth_shape)

    # getting the bounding box of the model
    model_width_bbox = math.ceil(_get_head_bbox()[5])
    model_height_bbox = math.ceil(_get_head_bbox()[4])
    model_position = mc.xform(model_selected, ws=True, q=True, rp=1)

    # multiplier to move the model on Tx
    left_multiplier = 20

    model_pos_x = model_position[0] + model_width_bbox*left_multiplier
    model_pos_y = model_position[1] # - model_height_bbox*HEIGHT_MULTIPLIER/2
    model_pos_z = model_position[2]
    
    mouth_corner_lf_models_pos = {
        10: [model_pos_x, model_pos_y, model_pos_z],
        20: [model_pos_x + model_width_bbox*2, model_pos_y, model_pos_z],
        30: [model_pos_x + model_width_bbox*2, model_pos_y - model_height_bbox*HEIGHT_MULTIPLIER/2, model_pos_z],
        40: [model_pos_x + model_width_bbox*2, model_pos_y - model_height_bbox*HEIGHT_MULTIPLIER, model_pos_z],
        50: [model_pos_x, model_pos_y - model_height_bbox*HEIGHT_MULTIPLIER, model_pos_z],
        60: [model_pos_x - model_width_bbox*2, model_pos_y - model_height_bbox*HEIGHT_MULTIPLIER, model_pos_z],
        70: [model_pos_x - model_width_bbox*2, model_pos_y - model_height_bbox*HEIGHT_MULTIPLIER/2, model_pos_z],
        80: [model_pos_x - model_width_bbox*2, model_pos_y, model_pos_z]
    }

    frame_number = 1
    for model_name in MOUTH_CORNER_LF_NAMES:

        if frame_number < KEYFRAME_COUNT:
            
            current_time = frame_number*10
            mc.currentTime(current_time, edit=True)

            new_model = mc.duplicate(model_selected, n = model_name)

            position = mouth_corner_lf_models_pos[current_time]
            mc.xform(new_model, ws=True, t=position)

            frame_number += 1

    mc.currentTime(0, edit=True)


def _get_combo_shapes(side):
    '''
    connect the combo shapes with the mouth shapes 
    depending on the side
    '''
    i = 0

    combo_shapes = []
    mouth_shapes = []

    if side.lower().startswith("l"):
        mouth_shapes = MOUTH_CORNER_LF_NAMES
        combo_shapes = MOUTH_CORNER_LF_COMBO_NAMES
    else:
        mouth_shapes = MOUTH_CORNER_RT_NAMES
        combo_shapes = MOUTH_CORNER_RT_COMBO_NAMES

    for combo_shape in combo_shapes:

        corner_shape_ind = CORNER_SHAPE_LOCATION[i]
        if corner_shape_ind == 7:
            a_shape_ind = 0
            b_shape_ind = corner_shape_ind - 1
        else:
            a_shape_ind = corner_shape_ind - 1
            b_shape_ind = corner_shape_ind + 1

        shapes_to_blend = [mouth_shapes[a_shape_ind], mouth_shapes[b_shape_ind], mouth_shapes[corner_shape_ind]]

        mc.blendShape(shapes_to_blend, combo_shape, topologyCheck=False, w=[(0,-1), (1, -1), (2, 1)], name=f"{combo_shape}{BLEND_SHAPE}")
        i += 1


def _create_combo_shapes(side):
    '''
    makes combo shapes
    '''
    combo_shapes = []
    mouth_shapes = []

    if side.lower().startswith("l"):
        mouth_shapes = MOUTH_CORNER_LF_NAMES
        combo_shapes = MOUTH_CORNER_LF_COMBO_NAMES
    else:
        mouth_shapes = MOUTH_CORNER_RT_NAMES
        combo_shapes = MOUTH_CORNER_RT_COMBO_NAMES

    # check if the mouth corner shapes exist
    shapes_dont_exist = []
    for mouth_shape in mouth_shapes:
        if not mc.objExists(mouth_shape):
            shapes_dont_exist.append(mouth_shape)

    if len(shapes_dont_exist) > 0:
        om.MGlobal.displayError(f"The following shapes '{shapes_dont_exist}' don't exist. Please, rename the them accordingly or run mouth shapes again")
        return 

    # check if the combo shapes exist
    if any(map(mc.objExists, combo_shapes)):
        button = mc.confirmDialog(
            title="The Conbo Mouth Shape(s) Exist",
            message=f"It seems, the combo mouth shapes exist. Are you sure you want to re-create them? The modification will be lost.",
            button=["Yes", "No"],
            defaultButton="No",
            cancelButton="No",
            dismissString="No"
        )
        if button == "No":
            return
        else:
            for combo_shape in combo_shapes:
                mc.delete(combo_shape)

    # get the position for the combo shapes
    combo_position = []
    i = 0
    for combo_shape in combo_shapes:
        corner_shape = mouth_shapes[CORNER_SHAPE_LOCATION[i]]

        print(corner_shape)

        corner_shape_positoin = mc.xform(corner_shape, ws=True, q=True, rp=1)

        sign = 1 if side.lower().startswith("l") else -1

        if i == 0:
            combo_model_x = corner_shape_positoin[0] + sign * math.ceil(_get_head_bbox()[5])
            combo_model_y = corner_shape_positoin[1] + math.ceil(_get_head_bbox()[4])/3
            combo_model_z = corner_shape_positoin[2]
        elif i == 1:
            combo_model_x = corner_shape_positoin[0] + sign * math.ceil(_get_head_bbox()[5])
            combo_model_y = corner_shape_positoin[1] - math.ceil(_get_head_bbox()[4])/3
            combo_model_z = corner_shape_positoin[2]
        elif i == 2:
            combo_model_x = corner_shape_positoin[0] - sign * math.ceil(_get_head_bbox()[5])
            combo_model_y = corner_shape_positoin[1] - math.ceil(_get_head_bbox()[4])/3
            combo_model_z = corner_shape_positoin[2]
        elif i == 3: 
            combo_model_x = corner_shape_positoin[0] - sign * math.ceil(_get_head_bbox()[5])
            combo_model_y = corner_shape_positoin[1] + math.ceil(_get_head_bbox()[4])/3
            combo_model_z = corner_shape_positoin[2] 


        combo_position.append([combo_model_x, combo_model_y, combo_model_z])
        
        i += 1

    # making combo shapes and position them
    i = 0
    for combo_shape in combo_shapes:

        if not mc.objExists(CLEAN_MODEL):
            get_clean_model()

        mc.rename(CLEAN_MODEL, combo_shape)
        mc.xform(combo_shape, ws=True, t=combo_position[i])
        i += 1

    # get combo shapes
    _get_combo_shapes(side)


def make_combo_shapes():

    _create_combo_shapes("Left")



def mirror_mouth_corner_shapes():

    # check if the mouth corner shapes exist
    if not all(map(mc.objExists, MOUTH_CORNER_LF_NAMES)):
        om.MGlobal.displayError(f"The objects '{MOUTH_CORNER_LF_NAMES}' doesn't exist. Please, rename the model as '{MOUTH_CORNER_LF_NAMES}'")
        return

    if not all(map(mc.objExists, MOUTH_CORNER_LF_COMBO_NAMES)):
        om.MGlobal.displayError(f"The objects '{MOUTH_CORNER_LF_COMBO_NAMES}' doesn't exist. Please, rename the model as '{MOUTH_CORNER_LF_COMBO_NAMES}'")
        return

    # checking if the mouth corner shapes already in the scene
    if any(map(mc.objExists, MOUTH_CORNER_RT_NAMES)):
        button = mc.confirmDialog(
            title="The Mouth Shape(s) Exist",
            message=f"It seems, the mouth corner shapes for right side exist. Are you sure you want to re-create them? The modification will be lost.",
            button=["Yes", "No"],
            defaultButton="No",
            cancelButton="No",
            dismissString="No"
        )
        if button == "No":
            return
        else:
            for mouth_shape in MOUTH_CORNER_RT_NAMES:
                mc.delete(mouth_shape)

    model_width_bbox = math.ceil(_get_head_bbox()[5])

    for i, shape_to_mirror in enumerate(reversed(MOUTH_CORNER_LF_NAMES)):

        shape_position = mc.xform(shape_to_mirror, ws=True, q=True, rp=1)
        mirrored_shape = mc.duplicate(shape_to_mirror, n=MOUTH_CORNER_RT_NAMES[-(i+1)])

        mirrored_shape_x = -shape_position[0] + (model_width_bbox*MIRROR_SIZE_BBOX_MULTIPLIER)
        mirrored_shape_y = shape_position[1]
        mirrored_shape_z = shape_position[2]

        mc.xform(mirrored_shape, ws=True, t=[mirrored_shape_x, mirrored_shape_y, mirrored_shape_z])

    _create_combo_shapes("Right")


def flip_shapes():
    '''
    flip the shapes
    '''
    symmetry_script_path = os.path.join(
        os.path.dirname(__file__), 'mel', 'symmetry.mel')

    symmetry_script_path = os.path.normpath(symmetry_script_path)
    symmetry_script_path = symmetry_script_path.replace('\\', '\\\\')

    mel.eval(f'source "{symmetry_script_path}"')


def make_soft_cluster():

    selectionVrts = mc.ls(selection = True, flatten = True)

    if selectionVrts:

        posVtx = _get_average(selectionVrts)
        mc.softSelect(sse=True)
        softElementData = _soft_selection()
        selection = ["%s.vtx[%d]" % (el[0], el[1])for el in softElementData ] 
        model = selectionVrts[0].split('.')[0]
        mc.select(model, r=True)
        cluster = mc.cluster(name = '%s_cls' % model, relative=False, bindState = True)
        clusterGrp = mc.createNode('transform', name = '%s_grp' % cluster[1])
        mc.xform(cluster, rotatePivot = posVtx, scalePivot = posVtx, objectSpace = True)
        mc.xform(clusterGrp, rotatePivot = posVtx, scalePivot = posVtx, objectSpace = True)
        mc.parent(cluster[1], clusterGrp)
        mc.connectAttr('%s.worldInverseMatrix' % clusterGrp, '%s.bindPreMatrix' % cluster[0])
        weight = [0.0]
        zero = 0.0
        VertexNb = mc.polyEvaluate(model, v=1) - 1

        for x in range(VertexNb):
            weight.append(zero)

        mc.setAttr('{0}.weightList[0].weights[0:{1}]'.format(cluster[0], VertexNb), *weight, size=len(weight))
        shape = mc.listRelatives(cluster[1], shapes = True)[0]
        mc.setAttr('%s.originX' % shape, posVtx[0])
        mc.setAttr('%s.originY' % shape, posVtx[1])
        mc.setAttr('%s.originZ' % shape, posVtx[2])

        for i in range(len(softElementData)):
            mc.percent(cluster[0], selection[i], v=softElementData[i][2])

        mc.select(cluster[1], r=True)

def _soft_selection():

    selection = om.MSelectionList()
    softSelection = om.MRichSelection()
    om.MGlobal.getRichSelection(softSelection)
    softSelection.getSelection(selection)
    dagPath = om.MDagPath()
    component = om.MObject()
    iter = om.MItSelectionList( selection,om.MFn.kMeshVertComponent )
    elements = []

    while not iter.isDone():

        iter.getDagPath( dagPath, component )
        dagPath.pop()
        node = dagPath.fullPathName()
        fnComp = om.MFnSingleIndexedComponent(component)

        for i in range(fnComp.elementCount()):
            elements.append([node, fnComp.element(i), fnComp.weight(i).influence()] )

        iter.next()

    return elements

def _get_average(selection):

    average = []
    listX = []
    listY = []
    listZ = []

    for item in selection:

        pos = mc.xform(item, query = True, translation = True, worldSpace = True)
        listX.append(pos[0])
        listY.append(pos[1])
        listZ.append(pos[2])

    aveX = reduce(lambda x, y: x + y, listX) / len(listX)
    aveY = reduce(lambda x, y: x + y, listY) / len(listY)
    aveZ = reduce(lambda x, y: x + y, listZ) / len(listZ)
    average.append(aveX)
    average.append(aveY)
    average.append(aveZ)

    return average
    