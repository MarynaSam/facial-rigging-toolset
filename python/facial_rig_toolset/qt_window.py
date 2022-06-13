import maya.cmds as mc
from maya import OpenMayaUI as omui
from maya import OpenMaya as om

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *
from shiboken2 import wrapInstance

from importlib import reload

from facial_rig_toolset import model_check
from facial_rig_toolset import head_cut
from facial_rig_toolset import body_head_blend
from facial_rig_toolset import structure
from facial_rig_toolset import jaw_rig
from facial_rig_toolset import mouth_corners

reload(model_check)
reload(head_cut)
reload(body_head_blend)
reload(structure)
reload(jaw_rig)
reload(mouth_corners)


mayaMainWindowPtr = omui.MQtUtil.mainWindow()
MAYA_MAIN_WINDOW = wrapInstance(int(mayaMainWindowPtr), QWidget)

WIN_TITLE = "Facial Rig Toolset"

class MainWindow(QWidget):
    """
    Overall window, responsible for scrolling
    """
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setParent(MAYA_MAIN_WINDOW)
        self.setWindowTitle(WIN_TITLE)
        self.setWindowFlags(Qt.Window)
        self.initUI()

    def initUI(self):
        self.layout = QGridLayout(self)
        self.initScrollArea()

        self.subWindow = SubWindow(self)
        self.scrollLayout.addWidget(self.subWindow)

        self.show()

    def initScrollArea(self):
        self.scrollWidget = QWidget()
        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.scrollWidget.setLayout(self.scrollLayout)
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidget(self.scrollWidget)
        self.layout.addWidget(self.scroll)

class SubWindow(QWidget):

    def __init__(self, parent=None):
        super(SubWindow, self).__init__(parent)
        self.setParent(parent)
        self.initUI()


    def initUI(self):

        self.structure_exists = mc.objExists("|Face|Dont|Eyelid_Setup_grp|Eyelid_Locators_grp")
        #self.structure_exists = mc.objExists("|Face")
        self.jaw_rig_exists = mc.objExists(jaw_rig.JAW_MAIN_GROUP)
        self.jaw_guides_exists = mc.objExists(jaw_rig.ROOT_GUIDE)
        
        self._init_widgets()
        self._init_layout()
        self._init_signals()


    def _init_widgets(self):
        self.group_box_model_check = QGroupBox("Model Check")
        self.group_box_assign_material = QGroupBox("Assign Material")
        self.group_box_head_cut = QGroupBox("Head Cut")
        self.group_box_body_head_blend = QGroupBox("Body Head Blend")
        self.group_box_structure = QGroupBox("Structure")
        self.group_box_jaw_rig = QGroupBox("Jaw Rig")
        self.group_box_mouth = QGroupBox("Mouth")
        self.group_box_lips = QGroupBox("Lips")


        self.checkbox_set_current_units_to_cm = QCheckBox("Set Units To Cm")
        self.checkbox_pivots_zero_out = QCheckBox("Zero Out Pivots")
        self.checkbox_fix_character_scale = QCheckBox("Fix Character Height")
        self.checkbox_freeze_transform = QCheckBox("Freeze Transform")

        self.input_height = QDoubleSpinBox()
        self.input_height.setRange(0, 400)
        self.input_height.setValue(175)

        self.checkbox_auto_uvs = QCheckBox("Auto UVs")
        self.checkbox_soften_edges = QCheckBox("Soften Edges")

        self.checkbox_delete_history = QCheckBox("Delete History")
        self.checkbox_delete_intermediate_objects = QCheckBox("Delete Intermediate Objects")
        self.checkbox_delete_layers = QCheckBox("Delete Display And Render Layers")
        self.checkbox_delete_unknow_nodes = QCheckBox("Delete Unknown Nodes")
        self.checkbox_delete_unused_nodes = QCheckBox("Delete Unused Nodes")  

        self.combo_box_assing_material = QComboBox()
        combo_box_items = model_check.MATERIAL_PARMS.keys()
        for box_item in combo_box_items:
            self.combo_box_assing_material.addItem(box_item.title())
        self.combo_box_assing_material.setToolTip("Materials to assign")

        self.button_model_check = QPushButton("Model Check")
        self.button_model_check.setToolTip("Select the model and check the parameters")

        self.button_check_symmetry = QPushButton("Check Symmetry")
        self.button_check_symmetry.setToolTip("Select the model to check if it is symmetrical")

        self.button_assign_material = QPushButton("Assign Material")
        self.button_assign_material.setToolTip("Select the faces to assign the material")

        self.button_head_cut = QPushButton("Head Cut")
        self.button_head_cut.setToolTip(
            '<div>1) Name the geomentry <b>"body_geo"</b></div>'
            '<div>2) Select the faces of the head to perform the cutting</div>'
            '<div><b>!IMPORTANT!</b> Make sure the model is facing Tz positive</div>')
        self.button_head_cut.setStyleSheet('QToolTip { min-width: 300px; }')

        self.button_joint_label = QPushButton("Label Joints")
        self.button_joint_label.setToolTip(
            "<div>Select the body rig joint(s) to label them</div>"
            "<div><b>!IMPORTANT!</b> The joints must be labeled for better skin cluster transfer</div>")
        self.button_joint_label.setStyleSheet('QToolTip { min-width: 300px; }')

        self.button_duplicate_joints = QPushButton("Duplicate Joints")
        self.button_duplicate_joints.setToolTip(
            "<div>Select the body rig joint(s) to duplicate</div>"
            "<div><b>!IMPORTANT!</b> The joints must be labeled for better skin cluster transfer</div>")
        self.button_duplicate_joints.setStyleSheet('QToolTip { min-width: 300px; }')

        self.button_body_head_transfer_skinweight = QPushButton("Body Head Skin Transfer")
        self.button_body_head_transfer_skinweight.setToolTip(
            '<div>1) Rename skin cluster as <b>"body_skinCluster"</b></div>'
            '<div>2) Select the <b>head</b> joints</div>')
        self.button_body_head_transfer_skinweight.setStyleSheet('QToolTip { min-width: 300px; }')

        self.button_body_head_blend = QPushButton("Body Head Blend")
        self.button_body_head_blend.setToolTip(
            '<div>1) Select the shared joints one by one following the hierarchy, first the body rig joints then the head joints</div>')
        self.button_body_head_blend.setStyleSheet('QToolTip { min-width: 300px; }')

        self.button_build_structure = QPushButton("Build Structure")
        self.button_build_structure.setDisabled(self.structure_exists)
        self.button_build_structure.setToolTip(
            "<div>Build the structure of the scene</div>"
            "<div>Disabled if the structure already exists</div>")
        self.button_build_structure.setStyleSheet('QToolTip { min-width: 300px; }')
        
        self.button_parent_mesh = QPushButton("Put Under Model Group")
        self.button_parent_mesh.setEnabled(self.structure_exists)
        self.button_parent_mesh.setToolTip(
            "<div>Select the geo(s) to parent under 'Model Group'</div>"
            "<div>Disabled if the structure of the scene doesn't exist</div>")
        self.button_parent_mesh.setStyleSheet('QToolTip { min-width: 300px; }')

        self.button_parent_joints = QPushButton("Put Under Motion Group")
        self.button_parent_joints.setEnabled(self.structure_exists)
        self.button_parent_joints.setToolTip(
            "<div>Select the joint(s) or control(s) to parent under 'Motion Group'</div>"
            "<div>Disabled if the structure of the scene doesn't exist</div>")
        self.button_parent_joints.setStyleSheet('QToolTip { min-width: 300px; }')
        
        self.button_build_guides = QPushButton("Build Guides")
        self.button_build_guides.setToolTip(
            "<div>Create guides to position the jaw joints</div>"
            "<div>Press <b>'Build Jaw'</b> button once the guides are placed</div>")
        self.button_build_guides.setStyleSheet('QToolTip { min-width: 300px; }')

        self.button_build_jaw_rig = QPushButton("Build Jaw")
        self.button_build_jaw_rig.setEnabled(self.jaw_guides_exists)
        self.button_build_jaw_rig.setToolTip(
            "<div>Placing the jaw joint(s) on the guides place</div>"
            "<div>Press <b>'Update Jaw Open'</b> button to set the mouth openning</div>")
        self.button_build_jaw_rig.setStyleSheet('QToolTip { min-width: 300px; }')    

        self.button_update_jaw_range = QPushButton("Update Jaw Open")
        self.button_update_jaw_range.setEnabled(self.jaw_rig_exists)
        self.button_update_jaw_range.setToolTip(
            "<div>1) Select the <b>'Jaw_ctl'</b></div>"
            "<div>2) Set <b>'Jaw Open'</b> to 0</div>"
            "<div>3) Set <b>'Rotate X'</b> of the <b>'Jaw Control'</b> to a desiered value</div>"
            "<div>4) Press the button</div>"
            "<div>Process can be repeated</div>")
        self.button_update_jaw_range.setStyleSheet('QToolTip { min-width: 300px; }')

        self.button_clean_model = QPushButton("Clean Model")
        self.button_clean_model.setToolTip("Create a clean model and position it to the side of the head")

        self.button_cluster_model = QPushButton("Cluster Model")
        self.button_cluster_model.setToolTip("Create a cluster model and position it above the head")

        self.button_ss_buddy = QPushButton("SS Buddy")
        self.button_ss_buddy.setToolTip(
            "<div>Call ssBuddy to shape the soft selection</div>"
            "<div>1) Select <b>ONE</b> vert on the <b>'mouth_cluster_geo'</b> mouth's <b>LEFT</b> corner</div>"
            "<div>2) Check <b>'Soft Select'</b></div>"
            "<div>3) Falloff mode is <b>'Volume'</b></div>"
            "<div>4) Shape the curve. For mouth corners the curve looks like <b>'('</b> turned to the left around 45 deg</div>"
            "<div>5) Increase or decrease the soft select diameter by moving the slider in <b>'Falloff radius'</b> or by holding <b>'B'+MMCK</b></div>")
        self.button_ss_buddy.setStyleSheet('QToolTip { min-width: 300px; }')

        self.button_soft_cluster = QPushButton("Soft Cluster")
        self.button_soft_cluster.setToolTip("Create a Soft Cluster according to the soft selection made in ssBuddy")

        self.button_shapes_for_cluster = QPushButton("Soft Cluster Shapes")
        self.button_shapes_for_cluster.setToolTip(
            "<div>Create 9 shapes (every 10 frames) for the cluster handle with step for Tx, Ty, Tz = 1</div>"
            "<div><b>!IMPORTANT!</b> Make sure the model is facing Tz positive</div>"
            "<div>At the moment, works with only one soft cluster</div>")
        self.button_shapes_for_cluster.setStyleSheet('QToolTip { min-width: 300px; }')

        self.button_cluster_mask_shapes = QPushButton("Cluster Mask Shapes")
        self.button_cluster_mask_shapes.setToolTip(
            "<div>Create several shapes for masking</div>"
            "<div>Position and rename the shapes</div>")
        self.button_cluster_mask_shapes.setStyleSheet('QToolTip { min-width: 200px; }')

        self.button_shapes_for_mouth = QPushButton("Mouth Shapes")
        self.button_shapes_for_mouth.setToolTip(
            "<div>1) Select the final mask model</div>"
            "<div>2) Makes 8 mouth models and rename them</div>")
        self.button_shapes_for_cluster.setStyleSheet('QToolTip { min-width: 300px; }')

        self.button_combo_shapes = QPushButton("Combo Shapes")
        self.button_combo_shapes.setToolTip(
            "<div>Make Combo Shapes for the mouth shapes on the left side</div>")
        self.button_combo_shapes.setStyleSheet('QToolTip { min-width: 300px; }')

        self.button_right_side_shapes = QPushButton("Right Side Shapes")
        self.button_right_side_shapes.setToolTip(
            "<div>Make Combo Shapes for the mouth shapes on the left side</div>")
        self.button_right_side_shapes.setStyleSheet('QToolTip { min-width: 300px; }')

        self.button_flip_shapes = QPushButton("Flip Selected Shapes")
        self.button_flip_shapes.setToolTip(
            "<div>Flip selected mouth shapes on the left side</div>"
            "<div><b>!IMPORTANT!</b> Don't select <b>combo</b> shapes</div>")
        self.button_flip_shapes.setStyleSheet('QToolTip { min-width: 300px; }')

        self.button_create_mouth_corner_control = QPushButton("Create Mouth Corner Control")
        self.button_connect_control_to_face = QPushButton("Connect Control To Face")
        self.button_wip_group_mouth_corner = QPushButton("Make WIP Mouth Corner Group")
        self.button_clean_unused_shapes = QPushButton("Delete Unused Shapes")


    def _init_layout(self):
        layout = QVBoxLayout()        
        
        layout.addWidget(self.group_box_model_check)
        layout.addWidget(self.group_box_assign_material)
        layout.addWidget(self.group_box_head_cut)
        layout.addWidget(self.group_box_body_head_blend)
        layout.addWidget(self.group_box_structure)
        layout.addWidget(self.group_box_jaw_rig)
        layout.addWidget(self.group_box_mouth)
        
        layout.addWidget(self.group_box_lips)
        
        
        self.setLayout(layout)

        layout = QVBoxLayout(self.group_box_model_check)

        layout.addWidget(self.checkbox_set_current_units_to_cm)
        
        sublayout = QHBoxLayout()
        sublayout.addWidget(self.checkbox_fix_character_scale)
        sublayout.addWidget(self.input_height)
        layout.addLayout(sublayout)

        layout.addWidget(self.checkbox_pivots_zero_out)
        layout.addWidget(self.checkbox_freeze_transform)
        layout.addWidget(self.checkbox_delete_history)
        layout.addWidget(self.checkbox_auto_uvs)
        layout.addWidget(self.checkbox_soften_edges)
        layout.addWidget(self.checkbox_delete_intermediate_objects)
        layout.addWidget(self.checkbox_delete_layers)
        layout.addWidget(self.checkbox_delete_unknow_nodes)
        layout.addWidget(self.checkbox_delete_unused_nodes)

        layout.addWidget(self.button_model_check)
        layout.addWidget(self.button_check_symmetry)

        layout = QVBoxLayout(self.group_box_assign_material)
        layout.addWidget(self.combo_box_assing_material)
        layout.addWidget(self.button_assign_material)

        layout = QVBoxLayout(self.group_box_head_cut)
        layout.addWidget(self.button_head_cut)

        layout = QVBoxLayout(self.group_box_body_head_blend)
        layout.addWidget(self.button_joint_label)
        layout.addWidget(self.button_duplicate_joints) 
        layout.addWidget(self.button_body_head_transfer_skinweight)
        layout.addWidget(self.button_body_head_blend)

        layout = QVBoxLayout(self.group_box_structure)
        layout.addWidget(self.button_build_structure)
        layout.addWidget(self.button_parent_mesh)
        layout.addWidget(self.button_parent_joints)

        layout = QVBoxLayout(self.group_box_jaw_rig)
        layout.addWidget(self.button_build_guides)
        layout.addWidget(self.button_build_jaw_rig)       
        layout.addWidget(self.button_update_jaw_range)

        
        layout = QVBoxLayout(self.group_box_mouth)
        layout.addWidget(self.button_clean_model)
        layout.addWidget(self.button_cluster_model)
        layout.addWidget(self.button_ss_buddy)
        layout.addWidget(self.button_soft_cluster)
        layout.addWidget(self.button_shapes_for_cluster)
        layout.addWidget(self.button_cluster_mask_shapes)
        layout.addWidget(self.button_shapes_for_mouth)
        layout.addWidget(self.button_combo_shapes)
        layout.addWidget(self.button_right_side_shapes)
        layout.addWidget(self.button_flip_shapes)
        layout.addWidget(self.button_create_mouth_corner_control)
        layout.addWidget(self.button_connect_control_to_face)
        layout.addWidget(self.button_wip_group_mouth_corner)
        layout.addWidget(self.button_clean_unused_shapes)

        layout = QVBoxLayout(self.group_box_lips)


    def _init_signals(self):
        self.button_model_check.clicked.connect(self._on_button_model_check_clicked)
        self.button_check_symmetry.clicked.connect(self._on_button_check_symmetry_clicked)

        self.button_assign_material.clicked.connect(self._on_button_assign_material_clicked)

        self.button_head_cut.clicked.connect(self._on_button_head_cut_clicked)

        self.button_joint_label.clicked.connect(self._on_button_joint_label_clicked)
        self.button_duplicate_joints.clicked.connect(self._on_button_duplicate_joints_clicked)
        self.button_body_head_transfer_skinweight.clicked.connect(self._on_button_body_head_transfer_skinweight_clicked)
        self.button_body_head_blend.clicked.connect(self._on_button_body_head_blend_clicked)

        self.button_build_structure.clicked.connect(self._on_button_build_structure_clicked)
        self.button_parent_mesh.clicked.connect(self._on_button_parent_mesh_clicked)
        self.button_parent_joints.clicked.connect(self._on_button_parent_joints_clicked)

        self.button_build_guides.clicked.connect(self._on_button_build_guide_clicked)
        self.button_build_jaw_rig.clicked.connect(self._on_button_build_jaw_rig_clicked)
        self.button_update_jaw_range.clicked.connect(self._on_button_update_jaw_range_clicked)

        self.button_clean_model.clicked.connect(self._on_button_clean_model_clicked)
        self.button_cluster_model.clicked.connect(self._on_button_cluster_model_clicked)
        self.button_ss_buddy.clicked.connect(self._on_button_ss_buddy_clicked)
        self.button_soft_cluster.clicked.connect(self._on_button_soft_cluster_clicked)
        self.button_shapes_for_cluster.clicked.connect(self._on_button_shapes_for_cluster_clicked)
        self.button_cluster_mask_shapes.clicked.connect(self._on_button_cluster_mask_shapes_clicked)
        self.button_shapes_for_mouth.clicked.connect(self._on_button_shapes_for_mouth_clicked)
        self.button_combo_shapes.clicked.connect(self._on_button_combo_shapes_clicked)
        self.button_right_side_shapes.clicked.connect(self._on_button_right_side_shapes_clicked)
        self.button_flip_shapes.clicked.connect(self._on_button_flip_shapes_clicked)
        self.button_clean_unused_shapes.clicked.connect(self._on_button_clean_unused_shapes_clicked)
        self.button_create_mouth_corner_control.clicked.connect(self._on_button_create_mouth_corner_control_clicked)
        self.button_connect_control_to_face.clicked.connect(self._on_button_connect_control_to_face_clicked)
        self.button_wip_group_mouth_corner.clicked.connect(self._on_button_wip_group_mouth_corner_clicked)


    def _on_button_clean_model_clicked(self):
        try:
            mouth_corners.get_clean_model()

        except RuntimeError as e:
           om.MGlobal.displayError(str(e)) 

        
    def _on_button_cluster_model_clicked(self):
        try:
            mouth_corners.get_cluster_model()

        except RuntimeError as e:
           om.MGlobal.displayError(str(e)) 
        

    def _on_button_ss_buddy_clicked(self):
        try:
            mouth_corners.call_ss_buddy()

        except RuntimeError as e:
            om.MGlobal.displayError(str(e))


    def _on_button_soft_cluster_clicked(self):
        try:
            mouth_corners.make_soft_cluster()

        except RuntimeError as e:
            om.MGlobal.displayError(str(e))


    def _on_button_shapes_for_cluster_clicked(self):
        try:
            mouth_corners.set_soft_cluster_shapes()

        except RuntimeError as e:
            om.MGlobal.displayError(str(e))


    def _on_button_cluster_mask_shapes_clicked(self):
        try:
            mouth_corners.make_claster_mask_shapes()

        except RuntimeError as e:
            om.MGlobal.displayError(str(e))


    def _on_button_shapes_for_mouth_clicked(self):
        try:
            mouth_corners.make_mouth_corner_shape()

        except RuntimeError as e:
            om.MGlobal.displayError(str(e))


    def _on_button_combo_shapes_clicked(self):
        try:
            mouth_corners.make_combo_shapes()

        except RuntimeError as e:
            om.MGlobal.displayError(str(e))


    def _on_button_right_side_shapes_clicked(self):
        try:
            mouth_corners.mirror_mouth_corner_shapes()

        except RuntimeError as e:
            om.MGlobal.displayError(str(e))


    def _on_button_flip_shapes_clicked(self):
        try:
            mouth_corners.flip_shapes()

        except RuntimeError as e:
            om.MGlobal.displayError(str(e))


    def _on_button_clean_unused_shapes_clicked(self):
        pass


    def _on_button_create_mouth_corner_control_clicked(self):
        pass


    def _on_button_connect_control_to_face_clicked(self):
        pass
    

    def _on_button_wip_group_mouth_corner_clicked(self):
        pass


    def _on_button_model_check_clicked(self):
        try:
            if self.checkbox_set_current_units_to_cm.isChecked():
                model_check.check_current_unit()

            if self.checkbox_pivots_zero_out.isChecked():
                model_check.zero_out_pivots()

            if self.checkbox_fix_character_scale.isChecked():
                model_check.fix_character_scale_and_zero_out_pivots(self.input_height.value())

            if self.checkbox_auto_uvs.isChecked():
                model_check.auto_uvs()

            if self.checkbox_soften_edges.isChecked():
                model_check.soften_edges()

            if self.checkbox_freeze_transform.isChecked():
                model_check.freeze_transform()

            if self.checkbox_delete_history.isChecked():
                model_check.delete_history()    

            if self.checkbox_delete_intermediate_objects.isChecked():
                model_check.delete_intermediate_objects()  

            if self.checkbox_delete_layers.isChecked():
                model_check.delete_display_and_render_layers()  

            if self.checkbox_delete_unknow_nodes.isChecked():
                model_check.delete_unknown_nodes()  

            if self.checkbox_delete_unused_nodes.isChecked():
                model_check.delete_unused_nodes()

        except RuntimeError as e:
            om.MGlobal.displayError(str(e))


    def _on_button_check_symmetry_clicked(self):
        try:
            model_check.check_symmetry()

        except RuntimeError as e:
            om.MGlobal.displayError(str(e))


    def _on_button_assign_material_clicked(self):
        try:
            face_part = self.combo_box_assing_material.currentText().lower()
            model_check.set_material(face_part, model_check.MATERIAL_PARMS[face_part])

        except RuntimeError as e:
           om.MGlobal.displayError(str(e)) 


    def _on_button_head_cut_clicked(self):
        try:
            head_cut.head_cut()

        except RuntimeError as e:
           om.MGlobal.displayError(str(e)) 


    def _on_button_joint_label_clicked(self):
        try: 
            body_head_blend.label_joints() 

        except RuntimeError as e:
            om.MGlobal.displayError(str(e))


    def _on_button_duplicate_joints_clicked(self):
        try: 
            body_head_blend.duplicate_joints() 

        except RuntimeError as e:
            om.MGlobal.displayError(str(e))     


    def _on_button_body_head_transfer_skinweight_clicked(self):
        try:
            body_head_blend.transfer_body_skinweight_to_head()

        except RuntimeError as e:
            om.MGlobal.displayError(str(e))


    def _on_button_body_head_blend_clicked(self):
        try:
            body_head_blend.connect_the_head_and_the_body()

        except RuntimeError as e:
            om.MGlobal.displayError(str(e))


    def _on_button_build_structure_clicked(self):
        try:
            structure.build_structure()
            self.button_build_structure.setDisabled(True)
            self.button_parent_mesh.setDisabled(False)
            self.button_parent_joints.setDisabled(False)

        except RuntimeError as e:
            om.MGlobal.displayError(str(e))


    def _on_button_parent_mesh_clicked(self):
        try:
            structure.parent_mesh_under_model_group()

        except RuntimeError as e:
            om.MGlobal.displayError(str(e))


    def _on_button_parent_joints_clicked(self):
        try:
            structure.parent_joints_under_motion_group()
        
        except RuntimeError as e:
            om.MGlobal.displayError(str(e))


    def _on_button_build_guide_clicked(self):
        try:
            jaw_rig.create_guides()
            self.button_build_jaw_rig.setDisabled(False)

        except RuntimeError as e:
            om.MGlobal.displayError(str(e))
   

    def _on_button_build_jaw_rig_clicked(self):
        try:
            jaw_rig.build()
            self.button_update_jaw_range.setDisabled(False)

        except RuntimeError as e:
            om.MGlobal.displayError(str(e))

    
    def _on_button_update_jaw_range_clicked(self):
        try:
            jaw_rig.set_jaw_ranges()

        except RuntimeError as e:
            om.MGlobal.displayError(str(e))


def main():
    window = MainWindow()
    window.show()