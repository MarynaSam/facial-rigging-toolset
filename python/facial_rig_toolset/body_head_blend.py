from genericpath import exists
import maya.cmds as mc
from maya import OpenMaya as om

HEAD_JNT = "_head_jnt"
BODY_GEOMETRY = "body_geo"
HEAD_GEOMETRY = "head_geo"
SKIN_CLUSTER_BODY = "body_skinCluster"
SKIN_CLUSTER_HEAD = "head_skinCluster"
BLEND_SHAPE_HEAD_AND_BODY_NAME = "head_body_blendShape"
JOINT = "_jnt"
LEFT_SIDE = "_lf"
RIGHT_SIDE = "_rt"

LABEL_SIDE_DICT = {  
       'Center':0,   
       'Left':1,   
       'Right':2,  
       'None':3  
       }


def _object_exists(object_name):
    '''
        check if the object with a specific name exists
    '''
    if not mc.objExists(object_name):
        om.MGlobal.displayError(f"'{object_name}' doesn't exist")
        return False
    
    return True


def connect_the_head_and_the_body():
    '''
        connect shared body joints to the head joints (parent and scale constraint)
        create blend shape between the head and body
        set the blen shape to 1
        hide the head_geo 
    '''
    selected_joints = mc.ls(selection=True)

    if not selected_joints:
        om.MGlobal.displayError("Please select the joints you'd like to connect, first the body joints then the head joints.")
        return

    body_joints = selected_joints[:int(len(selected_joints)/2)]
    head_joints = selected_joints[int(len(selected_joints)/2):]

    for index in range(len(body_joints)):
        mc.parentConstraint(body_joints[index], head_joints[index], maintainOffset=True, weight=1)
        mc.scaleConstraint(body_joints[index], head_joints[index], offset=[1,1,1], weight=1)
        
    
    mc.blendShape(HEAD_GEOMETRY, BODY_GEOMETRY, topologyCheck=False, w=(0,1), name=BLEND_SHAPE_HEAD_AND_BODY_NAME)
    mc.hide(HEAD_GEOMETRY)
    

def _transfer_weights_from_body_to_head():
    '''
        copy body skin weights to the shared part of the head skin cluster 
    ''' 

    if not _object_exists(SKIN_CLUSTER_BODY):
        return 

    mc.copySkinWeights(ss=SKIN_CLUSTER_BODY, ds=SKIN_CLUSTER_HEAD, noMirror=True, ia="label")
    
      
def _bind_skin_cluster_to_head_geometry(selected_head_joints_and_geo):
    '''
        create skin cluster head_skinCluster
        head_geo will be bound to the selected joints
    '''
    if not _object_exists(HEAD_GEOMETRY):
        return
    
    #adding head_geo to selection
    mc.select(HEAD_GEOMETRY, add=True)
    selected_head_joints_and_geo = mc.ls(selection=True)
    
    #create and mane the skin cluster
    mc.skinCluster(selected_head_joints_and_geo, tsb=True, name=SKIN_CLUSTER_HEAD)


def label_joints():
    '''
    lable joints
    name convention is as follows for center joints: 'name_00_jnt'
    name convention is as follows for the sides: 'name_00_lf_jnt', 'name_00_rt_jnt'
    '''

    joints_to_label_selected = mc.ls(selection=True)

    if not joints_to_label_selected:
        om.MGlobal.displayError("Please select the joints to label them.")
        return 
   
    for joint_to_label in joints_to_label_selected:

        label_name = joint_to_label
        if LEFT_SIDE in joint_to_label:
            mc.setAttr(f"{joint_to_label}.side", LABEL_SIDE_DICT['Left'])
            label_name = label_name.replace(f"{LEFT_SIDE}{JOINT}", "")
        elif RIGHT_SIDE in joint_to_label:
            mc.setAttr(f"{joint_to_label}.side", LABEL_SIDE_DICT['Right'])
            label_name = label_name.replace(f"{RIGHT_SIDE}{JOINT}", "")
        else:
            mc.setAttr(f"{joint_to_label}.side", LABEL_SIDE_DICT['Center'])
            label_name = label_name.replace(f"{JOINT}", "")   

        #type 18 goes for Other in 'jointName.type'
        mc.setAttr(f"{joint_to_label}.type", 18)
        #name the label
        mc.setAttr (f"{joint_to_label}.otherType", label_name, type ='string')
        #draw thw label
        mc.setAttr (f"{joint_to_label}.drawLabel", 1)


def duplicate_joints():
    '''
        body rig does not contain any joints for the face, including the eye joints
        the joints must be labeled
        naming convention for the rig is 'jointName_number_jnt', exmp. 'neck_00_jnt'
    '''

    joints_to_duplicate = mc.ls(selection=True)

    if not joints_to_duplicate:
        om.MGlobal.displayError("Please select the joints you'd like to duplicate.")
        return

    head_shared_joints = mc.duplicate(joints_to_duplicate, rc=True)
    
    root_parent = mc.listRelatives(joints_to_duplicate, parent=True)

    if root_parent:
        mc.parent(head_shared_joints[0], w=True)
    
    for joint_index, head_shared_joint in enumerate(head_shared_joints):
        
        joint_old_name = head_shared_joint
        
        #split _jnt from the joint name on the right
        joint_splited_name = joint_old_name.rsplit("_", 1)[0]
        joint_new_name = f"{joint_splited_name}{HEAD_JNT}"
        
        mc.rename(head_shared_joint, joint_new_name)
    

def transfer_body_skinweight_to_head():
    ''' 
        body skin cluster should be named as 'body_skinCluster'
        mesh where there is head should be named as 'body_geo'
        the cut head should be named as 'head_geo'

    '''
    if not _object_exists(SKIN_CLUSTER_BODY) or not _object_exists(BODY_GEOMETRY) or not _object_exists(HEAD_GEOMETRY):
        return

    head_joints_selected = mc.ls(selection=True)

    if not head_joints_selected:
        om.MGlobal.displayError("Please select the head joints.")
        return
  
    _bind_skin_cluster_to_head_geometry(head_joints_selected)
    _transfer_weights_from_body_to_head()   









   

  
