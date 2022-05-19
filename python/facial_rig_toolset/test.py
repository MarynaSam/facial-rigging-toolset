import maya.cmds as mc
from maya import OpenMaya as om

HEAD_JNT = "_head_jnt"
BODY_GEOMETRY = "body_geo"
HEAD_GEOMETRY = "head_geo"
SKIN_CLUSTER_BODY = "body_skinCluster"
SKIN_CLUSTER_HEAD = "head_skinCluster"
BLEND_SHAPE_HEAD_AND_BODY_NAME = "head_body_blendShape"



def connect_the_head_and_the_body(body_joints, head_joints):
    '''
        connect shared body joints to the head joints (parent and scale constraint)
        create blend shape between the head and body
        set the blen shape to 1
        hide the head_geo 
    '''
    for index in range(len(body_joints)):
        mc.parentConstraint(body_joints[index], head_joints[index], maintainOffset=True, weight=1)
        mc.scaleConstraint(body_joints[index], head_joints[index], offset=[1,1,1], weight=1)
        
    
    mc.blendShape(HEAD_GEOMETRY, BODY_GEOMETRY, topologyCheck=False, w=(0,1), name=BLEND_SHAPE_HEAD_AND_BODY_NAME)
    mc.hide(HEAD_GEOMETRY)
    

def transfer_weights_from_body_to_head():
    '''
        body skin cluster should be named body_skinCluster
        copy body skin weights to the shared part of the head skin cluster 
    '''

    if not mc.objExists(SKIN_CLUSTER_BODY):
        om.MGlobal.displayError(f"'{SKIN_CLUSTER_BODY}' doesn't exist")
        return
    
    mc.copySkinWeights(ss=SKIN_CLUSTER_BODY, ds=SKIN_CLUSTER_HEAD, noMirror=True, ia="label")
    
    
    
def bind_skin_cluster_to_head_geometry(selected_head_joints):
    '''
        create skin cluster head_skinCluster
        head_geo will be bound to the selected joints
    '''
    if not mc.objExists(HEAD_GEOMETRY):
        om.MGlobal.displayError(f"'{HEAD_GEOMETRY}' doesn't exist")
        return
    
    #adding head_geo to selection
    mc.select(HEAD_GEOMETRY, add=True)
    selected_head_joints_and_geo = mc.ls(selection=True)
    
    print(selected_head_joints_and_geo)
    
    #create and mane the skin cluster
    mc.skinCluster(selected_head_joints_and_geo, tsb=True, name=SKIN_CLUSTER_HEAD)
    
    

def body_head_blend():
    '''
        body rig does not contain any joints for the face, including the eye joints
        the joints must be labeled
        naming convention for the rig is "jointName_number_jnt", exmp. "neck_00_jnt"
    '''

    joints_to_duplicate = mc.ls(selection=True)

    if not joints_to_duplicate:
        om.MGlobal.displayError("Please select the joints you'd like to duplicate.")
        return
        
    
    head_shared_joints = mc.duplicate(joints_to_duplicate, rc=True)
    
    mc.parent(head_shared_joints[0], w=True)
    
    head_joints = []
    
    for joint_index, head_shared_joint in enumerate(head_shared_joints):
        
        joint_old_name = head_shared_joint
        
        #split _jnt from the joint name on the right
        joint_splited_name = joint_old_name.rsplit("_", 1)[0]
        joint_new_name = f"{joint_splited_name}{HEAD_JNT}"
        
        mc.rename(head_shared_joint, joint_new_name)
        head_joints.append(joint_new_name)
      
    print(head_joints)  
    
    for index in range(len(head_joints)):
        mc.select(head_joints[index], add=True)
    
    head_joints_selected = mc.ls(selection=True)
    
    print(head_joints_selected)
    
    bind_skin_cluster_to_head_geometry(head_joints)
    transfer_weights_from_body_to_head()   
    connect_the_head_and_the_body(joints_to_duplicate, head_joints_selected)