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
from facial_rig_toolset import structure
reload(model_check)
reload(head_cut)
reload(structure)


MOUTH_CORNER = "mouth_corner"
CLEAN_MODEL_MOUTH_CORNER = f"{MOUTH_CORNER}_cluster_geo"
CLEAN_MODEL = "clean_head_geo"
MOUTH_CLUSTER_GROUP = f"WIP_{MOUTH_CORNER}_grp"
MOUTH_CORNER_CLUSTER_NAME = f"{MOUTH_CORNER}_cluster_geo_clsHandle"
MOUTH_MASK_NAMES = [f"{MOUTH_CORNER}_eye_mask_geo", f"{MOUTH_CORNER}_nose_mask_geo", f"{MOUTH_CORNER}_chin_mask_geo", f"{MOUTH_CORNER}_half_face_mask_geo"]
MOUTH_CORNER_LF_NAMES = ["smileLf", "smileWideLf", "wideLf", "frownWideLf", "frownLf", "frownNarrowLf", "narrowLf", "smileNarrowLf"]
MOUTH_CORNER_RT_NAMES = ["smileRt", "smileWideRt", "wideRt", "frownWideRt", "frownRt", "frownNarrowRt", "narrowRt", "smileNarrowRt"]
CORNER_SHAPE_LOCATION = [1, 3, 5, 7]
MOUTH_CORNER_LF_COMBO_NAMES = ["smileWideLf_combo", "frownWideLf_combo", "frownNarrowLf_combo", "smileNarrowLf_combo"]
MOUTH_CORNER_RT_COMBO_NAMES = ["smileWideRt_combo", "frownWideRt_combo", "frownNarrowRt_combo", "smileNarrowRt_combo"]
MOUTH_CORNER_CONTROL_NAMES = ["MouthLf_Corner_ctl", "MouthRt_Corner_ctl"]
MOUTH_CONTROL_GROUPS = ["_neg", "_sdk", "_grp"]

BLEND_SHAPE = "_blendShape"
CTL = "_ctl"

HEIGHT_MULTIPLIER = 1
WIDTH_MULTIPLIER = 2
ANNOTATION_HEIGHT_MULTIPLIER = 2
KEYFRAME_COUNT = 9
MIRROR_SIZE_BBOX_MULTIPLIER = 45


def _annotate_model(model_name, model_position):
    '''
    annotate the model 
    name the annotation and position it
    '''
    # get the name for annotation
    ann_name_label = model_name.rsplit('_', 1)[0]
    ann_name = f"{ann_name_label}_ann"

    if mc.objExists(ann_name):
        button = mc.confirmDialog(
            title=f"The Annotation '{ann_name}' Exists",
            message=f"The Annotation '{ann_name} already exists in the scene. Are you sure you want to re-create it?",
            button=["Yes", "No"],
            defaultButton="No",
            cancelButton="No",
            dismissString="No"
        )
        if button == "No":
            return
        
        mc.delete(ann_name)


    # get the height of the annotation
    ann_pos_y = model_position[1] * ANNOTATION_HEIGHT_MULTIPLIER
    annotation_position = model_position
    annotation_position[1]=ann_pos_y
   
    # create annoation
    ann = mc.annotate(model_name, tx=ann_name_label, p=annotation_position)
    ann_transform = mc.listRelatives(ann, parent=True)

    # rename annotation in the Outliner
    ann = mc.rename(ann_transform, ann_name)


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

    cluster_mouth_model = mc.duplicate(head_cut.HEAD_GEOMETRY, n=CLEAN_MODEL_MOUTH_CORNER)
    _set_locked(CLEAN_MODEL_MOUTH_CORNER, False)
    # delete construction history
    mc.delete(cluster_mouth_model, ch=True)

    root_parent = mc.listRelatives(head_cut.HEAD_GEOMETRY, parent=True)
    
    if root_parent:
        mc.parent(cluster_mouth_model, world=True)

    # getting the height of the model
    model_height_bbox = math.ceil(_get_head_bbox()[4])

    # calculating the Ty of the duplicate
    clean_mouth_model_pos_y = mc.xform(head_cut.HEAD_GEOMETRY, ws=True, q=True, rp=1)[1] + model_height_bbox*HEIGHT_MULTIPLIER
    
    clean_mouth_model_position = [0, clean_mouth_model_pos_y, 0]

    mc.xform(cluster_mouth_model, ws=True, t=clean_mouth_model_position)

    _annotate_model(cluster_mouth_model[0], clean_mouth_model_position)

    mc.select(cluster_mouth_model)


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
    masks_obj = []

    for mask_name in MOUTH_MASK_NAMES:
        if mc.objExists(mask_name):
            mask_exists = True
            masks_obj.append(mask_name)

    if mask_exists > 0:
        button = mc.confirmDialog(
            title="The Mask(s) Exist",
            message=f"It seems, there are shapes for masking: {masks_obj}. Are you sure you want to re-create them? The modification will be lost.",
            button=["Yes", "No"],
            defaultButton="No",
            cancelButton="No",
            dismissString="No"
        )
        if button == "No":
            return
        
        for mask_obj in masks_obj:
            mc.delete(mask_obj)
            ann_name_label = mask_obj.rsplit('_', 1)[0]
            ann_node = f"{ann_name_label}_ann"
            if mc.objExists(ann_node):
                mc.delete(ann_node)



    # getting the width of the model 
    model_width_bbox = math.ceil(_get_head_bbox()[5]) 

    previous_model = CLEAN_MODEL_MOUTH_CORNER

    for model_name in MOUTH_MASK_NAMES:

        new_model = ""

        #getting the name of the annotaion node
        ann_name_label = previous_model.rsplit('_', 1)[0]
        ann_node = f"{ann_name_label}_ann"

        # we need to disconnect the annotation node then duplicate the model and then connect it again
        if mc.objExists(ann_node):
            mc.disconnectAttr(f"{previous_model}Shape.worldMatrix[0]", f"{ann_node}Shape.dagObjectMatrix[0]")

            if mc.objExists(new_model):
                mc.delete(new_model)

            new_model = mc.duplicate(previous_model, n = model_name)
            print(new_model)
            mc.connectAttr(f"{previous_model}Shape.worldMatrix[0]", f"{ann_node}Shape.dagObjectMatrix[0]")
                    

        if not mc.objExists(new_model[0]):
            print("dupl one more")
            new_model = mc.duplicate(previous_model, n = model_name)
  
        previous_model_position = mc.xform(previous_model, ws=True, q=True, rp=1)
        new_model_pos_x = previous_model_position[0] + model_width_bbox*WIDTH_MULTIPLIER
        new_model_position = [new_model_pos_x, previous_model_position[1], previous_model_position[2]]

        mc.xform(new_model, ws=True, t=new_model_position)
        mc.blendShape(previous_model, new_model, topologyCheck=True, w=(0,1), name=f"{model_name}{BLEND_SHAPE}")

        _annotate_model(new_model[0], new_model_position)
        
        previous_model = new_model[0]



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

        #my edit to delete Shape from the name of the cluster, because of annotation it takes the Shape
        if selectionVrts[0].find("Shape"):
            selectionVrts[0] = selectionVrts[0].replace("Shape", "")
            print(selectionVrts[0])

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
    

def _delete_control(ctl, side):
    '''
    delete control if the user pressed 'Yes'
    '''

    if side.lower().startswith("l"):
        side = "Left"
    else:
        side = "Right"

    button = mc.confirmDialog(
        title="The Mouth Control(s) Exist",
        message=f"It seems, the {side} Mouth Corner Control(s) exist(s). Are you sure you want to re-create them?",
        button=["Yes", "No"],
        defaultButton="No",
        cancelButton="No",
        dismissString="No"
    )

    if button == "No":
        return False
    
    current_node = ctl
    while True:
        parent_node = mc.listRelatives(current_node, parent=True)
        if parent_node is None:
            break
        current_node = parent_node[0]

    mc.delete(current_node)
    return True


def create_mouth_lf_corner_controls():
    '''
    create left mouth cornen control
    '''
    control_lf = MOUTH_CORNER_CONTROL_NAMES[0]

    if mc.objExists(control_lf) and not _delete_control(control_lf, "Left"):
        return

    #makes the circle nurbe for the cotnrol
    mc.circle(n=control_lf)
    mc.setAttr(f"{control_lf}Shape.overrideEnabled", 1)
    mc.setAttr(f"{control_lf}Shape.overrideColor", 17)
    #delete history
    mc.delete(control_lf, ch=True)
    #freeze transform
    mc.makeIdentity(control_lf, apply=True, t=1, r=1, s=1, n=0, pn=1)

    group_name = control_lf.replace(CTL, "")

    #make hierarchy for the face control
    for grp_end in MOUTH_CONTROL_GROUPS:
        mc.group(n=f"{group_name}{grp_end}")


def create_mouth_rt_corner_controls():
    '''
    create the right mouth corner control
    put the left control group into another group
    duplicate the newly created group
    changes Scale X on negative(-X) to position the duplicate for the right side
    rename for the right side
    ungroup both controls' hierarchy
    '''
    control_rt = MOUTH_CORNER_CONTROL_NAMES[1]
    control_lf = MOUTH_CORNER_CONTROL_NAMES[0]

    if mc.objExists(control_rt) and not _delete_control(control_rt, "Right"):
        return

    if not mc.objExists(control_lf):
        om.MGlobal.displayError(f"The '{control_lf}' don't exist. Please, recreate the left control again.")
        return

    temp_grp_1 = "grp_1"
    temp_grp_2 = "grp_2"

    #identify the top group of the left mouth corner control
    current_node = control_lf
    while True:
        parent_node = mc.listRelatives(current_node, parent=True)
        if parent_node is None:
            break
        current_node = parent_node[0]    

    mc.group(current_node, n=temp_grp_1)
    mc.xform(temp_grp_1, piv=(0, 0, 0), ws=True)
    mc.duplicate(temp_grp_1, n=temp_grp_2)

    mc.setAttr(f"{temp_grp_2}.scaleX", -1)

    #rename the hierarchy for the right side
    parent_node = temp_grp_2
    while True:
        child_node = mc.listRelatives(parent_node, children=True, fullPath=True)
        if child_node is None:
            break
        child_node = child_node[0]
        parent_node = mc.rename(child_node, child_node.rsplit('|', 1)[-1].replace("Lf", "Rt"))

    mc.ungroup(temp_grp_1)
    mc.ungroup(temp_grp_2)


def connect_control_to_face():
    '''
    connect the controls to the face
    '''
    obj_selected = mc.ls(selection=True)
    
    if not obj_selected:
        om.MGlobal.displayError("Please select the vert then the control for the left and then for the right side")
        return 

    verts = mc.filterExpand(sm=31)
    nurbs = mc.filterExpand(sm=9)

    if not verts or not nurbs:
        om.MGlobal.displayError("Please select the verts and the controls ONLY")
        return

    if len(obj_selected) != 4:
        om.MGlobal.displayError("Please select 2 verts and 2 controls ONLY")
        return

    for vert in verts:

        fascia_name = vert.rsplit('.', 1)[0]
        follicle_fascia = ""

        if fascia_name != structure.FASCIA_GROUP[6]:
            follicle_fascia = structure.FASCIA_GROUP[6]

        vert = vert.replace(fascia_name, follicle_fascia)


    vert_lf = obj_selected[0]
    ctl_lf = obj_selected[1]
    vert_rt = obj_selected[2]
    ctl_rt = obj_selected[3]

    fascia_name = vert_lf.rsplit('.', 1)[0]
    follicle_fascia = ""

    if fascia_name != structure.FASCIA_GROUP[6]:
        follicle_fascia = structure.FASCIA_GROUP[6]

    vert_lf = obj_selected[0].replace(fascia_name, follicle_fascia)
    vert_rt = obj_selected[2].replace(fascia_name, follicle_fascia)

    obj_selected[0] = vert_lf
    obj_selected[2] = vert_rt

    _glueControl(obj_selected[:2])
    _glueControl(obj_selected[2:])

    _put_control_under_motion(ctl_lf)
    _put_control_under_motion(ctl_rt)


def _put_control_under_motion(ctl):

    top_parent = ctl
    while True:
        parent_node = mc.listRelatives(top_parent, parent=True)
        if parent_node is None:
            break
        top_parent = parent_node[0]

    mc.parent(top_parent, structure.CONTROLS_GROUP[0])


def _glueControl(selection):
    
    if len(selection) == 2:
        
        #virables
        vertex = selection[0]
        vertex_id = int(selection[0].split('[')[1][:-1])
        mesh = selection[0].split('.')[0]
        name = selection[1][:-4]
        
        #snap the control to the right location
        vert_pos = mc.xform(vertex, q=True, t=True, ws=True)
        mc.xform('%s_grp' % name, t = vert_pos, ws = True)
        
        #create follicle
        fol = _createFollicle('%s_fol' % name, mesh, vertex_id, parent = None)

        #put follicle under Follicle_grp and make it hidden
        mc.parent(fol[0], structure.DONT_GROUP[4])
        mc.setAttr(f"{fol[0]}.visibility", 0)
        
        #attach the control to the follcle
        mc.pointConstraint(fol[0], '%s_sdk' % name)
        
        
        #negate control
        _negateControl('%s_ctl' % name)


def _createFollicle(name, mesh, vertex, parent = None):
    follicle = name
    follicleShape = mc.createNode('follicle', n='%sShape' % name)
    mc.connectAttr('%s.outMesh' % mesh, '%s.inputMesh' % follicleShape)
    mc.connectAttr('%s.worldMatrix[0]' % mesh, '%s.inputWorldMatrix' % follicleShape)
    mc.connectAttr('%s.outRotate' % follicleShape, '%s.rotate' % follicle)
    mc.connectAttr('%s.outTranslate' % follicleShape, '%s.translate' % follicle)
    uv = _getUVFromVertexIndex(mesh, vertex)
    mc.setAttr('%s.parameterU' % follicleShape, uv[0])
    mc.setAttr('%s.parameterV' % follicleShape, uv[1])
    if parent:
        mc.parent(follicle, parent)
    return follicle, follicleShape
    

def _getUVFromVertexIndex(mesh, vertex):
    mc.select('%s.vtx[%s]' % (mesh, vertex), r = True)
    mc.ConvertSelectionToUVs()
    uvs = mc.polyEditUV(q=True)
    mc.select(clear = True)
    return uvs[0], uvs[1]


def _negateControl(ctrl):
    parentNode = mc.listRelatives(ctrl, p = True)
    if parentNode:
        trnMultiplyDivide = mc.createNode('multiplyDivide', name = '%s_neg_md' % ctrl)
        for letter in ['X','Y','Z']:
            mc.connectAttr('%s.translate%s' % (ctrl, letter), '%s.input1%s' % (trnMultiplyDivide, letter))
            mc.connectAttr('%s.output%s' % (trnMultiplyDivide, letter), '%s.translate%s' % (parentNode[0], letter))
            mc.setAttr('%s.input2%s' % (trnMultiplyDivide, letter), -1)


def put_ready_shapes_under_shapes_group():
    pass

def make_wip_mouth_corners_group():

    mouth_corner_grp = mc.ls(f"{MOUTH_CORNER}*", transforms=True)

    for i in range(len(mouth_corner_grp)-1, -1, -1):
            mouth_corner = mouth_corner_grp[i]
            parent = mc.listRelatives(mouth_corner, parent=True)
            if parent:
                del mouth_corner_grp[i]

    if not mc.objExists(MOUTH_CLUSTER_GROUP):
        mc.group(mouth_corner_grp, n=MOUTH_CLUSTER_GROUP)
        mc.setAttr(f"{MOUTH_CLUSTER_GROUP}.visibility", 0)
    else:
        for mouth_corner in mouth_corner_grp:
            parent = mc.listRelatives(mouth_corner, parent=True)
            if parent:
                if MOUTH_CLUSTER_GROUP not in parent:
                    mc.parent(mouth_corner, MOUTH_CLUSTER_GROUP)
            else: 
                mc.parent(mouth_corner, MOUTH_CLUSTER_GROUP)


    