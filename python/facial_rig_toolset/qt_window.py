import maya.cmds as mc
from maya import OpenMayaUI as omui

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

reload(model_check)
reload(head_cut)
reload(body_head_blend)
reload(structure)
reload(jaw_rig)



mayaMainWindowPtr = omui.MQtUtil.mainWindow()
MAYA_MAIN_WINDOW = wrapInstance(int(mayaMainWindowPtr), QWidget)

WIN_TITLE = "Facial Rigging Toolset"


class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow,self).__init__(MAYA_MAIN_WINDOW)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(WIN_TITLE)

        self.structure_exists = mc.objExists("|Face|Dont|Eyelid_Setup_grp|Eyelid_Locators_grp")
        self.jaw_rig_exists = mc.objExists(jaw_rig.JAW_MAIN_GROUP)
        
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


        self.checkbox_set_current_units_to_cm = QCheckBox("Set Units To Cm")
        self.checkbox_pivots_zero_out = QCheckBox("Zero Out Pivots")
        self.checkbox_fix_character_scale = QCheckBox("Fix Character Height")

        self.input_height = QDoubleSpinBox()
        self.input_height.setRange(0, 400)
        self.input_height.setValue(175)

        self.checkbox_auto_uvs = QCheckBox("Auto UVs")
        self.checkbox_soften_edges = QCheckBox("Soften Edges")
        self.checkbox_freeze_transform = QCheckBox("Freeze Transform")
        self.checkbox_delete_history = QCheckBox("Delete History")
        self.checkbox_delete_intermediate_objects = QCheckBox("Delete Intermediate Objects")
        self.checkbox_delete_layers = QCheckBox("Delete Display And Render Layers")
        self.checkbox_delete_unknow_nodes = QCheckBox("Delete Unknown Nodes")
        self.checkbox_delete_unused_nodes = QCheckBox("Delete Unused Nodes")
        self.checkbox_check_symmetry = QCheckBox("Check Symmetry")
        

        self.combo_box_assing_material = QComboBox()
        self.combo_box_assing_material.addItem("Skin")
        self.combo_box_assing_material.addItem("Hair")
        self.combo_box_assing_material.addItem("Lips")
        self.combo_box_assing_material.addItem("Brows")
        self.combo_box_assing_material.addItem("Mustache")
        self.combo_box_assing_material.addItem("Tongue")
        self.combo_box_assing_material.addItem("Teeth")
        self.combo_box_assing_material.addItem("Gums")
        self.combo_box_assing_material.addItem("Inner_Mouth")
        self.combo_box_assing_material.addItem("Lashes")
        self.combo_box_assing_material.addItem("Eyeball")
        self.combo_box_assing_material.addItem("Sclera")
        self.combo_box_assing_material.addItem("Pupil")
        self.combo_box_assing_material.addItem("Inner_Iris")
        self.combo_box_assing_material.addItem("Iris")
        self.combo_box_assing_material.addItem("Outer_Iris")



        self.button_model_check = QPushButton("Model Check")
        self.button_assign_material = QPushButton("Assign Material")
        self.button_head_cut = QPushButton("Head Cut")
        self.button_duplicate_joints = QPushButton("Duplicate Joints")
        self.button_body_head_blend = QPushButton("Body Head Blend")

        self.button_build_structure = QPushButton("Build Structure")
        self.button_build_structure.setDisabled(self.structure_exists)
        
        self.button_parent_mesh = QPushButton("Put Model(s) Under Model Group")
        self.button_parent_mesh.setEnabled(self.structure_exists)

        self.button_parent_joints = QPushButton("Put Joints(s) Under Motion Group")
        self.button_parent_joints.setEnabled(self.structure_exists)
        
        self.button_build_guides = QPushButton("Build Guides")

        self.checkbox_check_guides_ready = QCheckBox("Guides Ready")

        self.button_build_jaw_rig = QPushButton("Build Jaw Rig")
        self.button_build_jaw_rig.setDisabled(True)

        self.button_update_jaw_range = QPushButton("Update Jaw Range To Open")
        self.button_update_jaw_range.setEnabled(self.jaw_rig_exists)

    def _init_layout(self):
        layout = QVBoxLayout()        
        
        layout.addWidget(self.group_box_model_check)
        layout.addWidget(self.group_box_assign_material)
        layout.addWidget(self.group_box_head_cut)
        layout.addWidget(self.group_box_body_head_blend)
        layout.addWidget(self.group_box_structure)
        layout.addWidget(self.group_box_jaw_rig)
        
        self.setLayout(layout)

        layout = QVBoxLayout(self.group_box_model_check)

        layout.addWidget(self.checkbox_set_current_units_to_cm)
        
        sublayout = QHBoxLayout()
        sublayout.addWidget(self.checkbox_fix_character_scale)
        sublayout.addWidget(self.input_height)
        layout.addLayout(sublayout)

        layout.addWidget(self.checkbox_pivots_zero_out)
        layout.addWidget(self.checkbox_auto_uvs)
        layout.addWidget(self.checkbox_soften_edges)
        layout.addWidget(self.checkbox_freeze_transform)
        layout.addWidget(self.checkbox_delete_history)
        layout.addWidget(self.checkbox_delete_intermediate_objects)
        layout.addWidget(self.checkbox_delete_layers)
        layout.addWidget(self.checkbox_delete_unknow_nodes)
        layout.addWidget(self.checkbox_delete_unused_nodes)
        layout.addWidget(self.checkbox_check_symmetry)

        layout.addWidget(self.button_model_check)

        layout = QVBoxLayout(self.group_box_assign_material)
        layout.addWidget(self.combo_box_assing_material)
        layout.addWidget(self.button_assign_material)

        layout = QVBoxLayout(self.group_box_head_cut)
        layout.addWidget(self.button_head_cut)

        layout = QVBoxLayout(self.group_box_body_head_blend)
        layout.addWidget(self.button_duplicate_joints)
        layout.addWidget(self.button_body_head_blend)

        layout = QVBoxLayout(self.group_box_structure)
        layout.addWidget(self.button_build_structure)
        layout.addWidget(self.button_parent_mesh)
        layout.addWidget(self.button_parent_joints)

        layout = QVBoxLayout(self.group_box_jaw_rig)
        layout.addWidget(self.button_build_guides)

        sublayout = QHBoxLayout()
        layout.addWidget(self.checkbox_check_guides_ready)
        layout.addWidget(self.button_build_jaw_rig)    
        layout.addLayout(sublayout)
        
        layout.addWidget(self.button_update_jaw_range)



    def _init_signals(self):
        self.button_model_check.clicked.connect(self._on_button_model_check_clicked)
        self.button_assign_material.clicked.connect(self._on_button_assign_material_clicked)
        self.button_head_cut.clicked.connect(self._on_button_head_cut_clicked)
        self.button_duplicate_joints.clicked.connect(self._on_button_duplicate_joints_clicked)
        self.button_body_head_blend.clicked.connect(self._on_button_body_head_blend_clicked)
        self.button_build_structure.clicked.connect(self._on_button_build_structure_clicked)
        self.button_parent_mesh.clicked.connect(self._on_button_parent_mesh_clicked)
        self.button_parent_joints.clicked.connect(self._on_button_parent_joints_clicked)
        self.button_build_guides.clicked.connect(self._on_button_build_guide_clicked)
        self.button_build_jaw_rig.clicked.connect(self._on_button_build_jaw_rig_clicked)
        self.button_update_jaw_range.clicked.connect(self._on_button_update_jaw_range_clicked)

        self.checkbox_check_guides_ready.stateChanged.connect(self._on_check_guides_ready_state_changed)


    def _on_check_guides_ready_state_changed(self, state):
        if state == Qt.CheckState.Checked:
            self.button_build_jaw_rig.setEnabled(True)
        elif state == Qt.CheckState.Unchecked:
            self.button_build_jaw_rig.setEnabled(False)


    def _on_button_model_check_clicked(self):
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

        if self.checkbox_check_symmetry.isChecked():
            model_check.check_symmetry()


    def _on_button_assign_material_clicked(self):
        face_part = self.combo_box_assing_material.currentText().lower()
        model_check.set_material(face_part, model_check.MATERIAL_PARMS[face_part])


    def _on_button_head_cut_clicked(self):
        head_cut.head_cut()


    def _on_button_duplicate_joints_clicked(self):
        body_head_blend.duplicate_joints()      


    def _on_button_body_head_blend_clicked(self):
        body_head_blend.body_head_blend()


    def _on_button_build_structure_clicked(self):
        structure.build_structure()
        self.button_build_structure.setDisabled(True)
        self.button_parent_mesh.setDisabled(False)
        self.button_parent_joints.setDisabled(False)


    def _on_button_parent_mesh_clicked(self):
        structure.parent_mesh_under_model_group()


    def _on_button_parent_joints_clicked(self):
        structure.parent_joints_under_motion_group()


    def _on_button_build_guide_clicked(self):
        jaw_rig.create_guides()

    

    def _on_button_build_jaw_rig_clicked(self):
        jaw_rig.build()
        self.button_update_jaw_range.setDisabled(False)

    
    def _on_button_update_jaw_range_clicked(self):
        jaw_rig.set_jaw_ranges()


def main():
    window = MainWindow()
    window.show()