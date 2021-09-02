# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy
from bpy.types import (
    PropertyGroup,
)
from bpy.app.handlers import persistent


### Landmarks.
@persistent
def vr_ensure_default_landmark(context: bpy.context):
    # Ensure there's a default landmark (scene camera by default).
    landmarks = bpy.context.scene.vr_landmarks
    if not landmarks:
        landmarks.add()
        landmarks[0].type = 'SCENE_CAMERA'


def vr_landmark_active_type_update(self, context):
    wm = context.window_manager
    session_settings = wm.xr_session_settings
    landmark_active = VRLandmark.get_active_landmark(context)

    # Update session's base pose type to the matching type.
    if landmark_active.type == 'SCENE_CAMERA':
        session_settings.base_pose_type = 'SCENE_CAMERA'
    elif landmark_active.type == 'OBJECT':
        session_settings.base_pose_type = 'OBJECT'
    elif landmark_active.type == 'CUSTOM':
        session_settings.base_pose_type = 'CUSTOM'


def vr_landmark_active_base_pose_object_update(self, context):
    session_settings = context.window_manager.xr_session_settings
    landmark_active = VRLandmark.get_active_landmark(context)

    # Update the anchor object to the (new) camera of this landmark.
    session_settings.base_pose_object = landmark_active.base_pose_object


def vr_landmark_active_base_pose_location_update(self, context):
    session_settings = context.window_manager.xr_session_settings
    landmark_active = VRLandmark.get_active_landmark(context)

    session_settings.base_pose_location = landmark_active.base_pose_location


def vr_landmark_active_base_pose_angle_update(self, context):
    session_settings = context.window_manager.xr_session_settings
    landmark_active = VRLandmark.get_active_landmark(context)

    session_settings.base_pose_angle = landmark_active.base_pose_angle


def vr_landmark_active_base_scale_update(self, context):
    session_settings = context.window_manager.xr_session_settings
    landmark_active = VRLandmark.get_active_landmark(context)

    session_settings.base_scale = landmark_active.base_scale


def vr_landmark_type_update(self, context):
    landmark_selected = VRLandmark.get_selected_landmark(context)
    landmark_active = VRLandmark.get_active_landmark(context)

    # Only update session settings data if the changed landmark is actually
    # the active one.
    if landmark_active == landmark_selected:
        vr_landmark_active_type_update(self, context)


def vr_landmark_base_pose_object_update(self, context):
    landmark_selected = VRLandmark.get_selected_landmark(context)
    landmark_active = VRLandmark.get_active_landmark(context)

    # Only update session settings data if the changed landmark is actually
    # the active one.
    if landmark_active == landmark_selected:
        vr_landmark_active_base_pose_object_update(self, context)


def vr_landmark_base_pose_location_update(self, context):
    landmark_selected = VRLandmark.get_selected_landmark(context)
    landmark_active = VRLandmark.get_active_landmark(context)

    # Only update session settings data if the changed landmark is actually
    # the active one.
    if landmark_active == landmark_selected:
        vr_landmark_active_base_pose_location_update(self, context)


def vr_landmark_base_pose_angle_update(self, context):
    landmark_selected = VRLandmark.get_selected_landmark(context)
    landmark_active = VRLandmark.get_active_landmark(context)

    # Only update session settings data if the changed landmark is actually
    # the active one.
    if landmark_active == landmark_selected:
        vr_landmark_active_base_pose_angle_update(self, context)


def vr_landmark_base_scale_update(self, context):
    landmark_selected = VRLandmark.get_selected_landmark(context)
    landmark_active = VRLandmark.get_active_landmark(context)

    # Only update session settings data if the changed landmark is actually
    # the active one.
    if landmark_active == landmark_selected:
        vr_landmark_active_base_scale_update(self, context)


def vr_landmark_active_update(self, context):
    wm = context.window_manager

    vr_landmark_active_type_update(self, context)
    vr_landmark_active_base_pose_object_update(self, context)
    vr_landmark_active_base_pose_location_update(self, context)
    vr_landmark_active_base_pose_angle_update(self, context)
    vr_landmark_active_base_scale_update(self, context)

    if wm.xr_session_state:
        wm.xr_session_state.reset_to_base_pose(context)


class VRLandmark(PropertyGroup):
    name: bpy.props.StringProperty(
        name="VR Landmark",
        default="Landmark"
    )
    type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ('SCENE_CAMERA', "Scene Camera",
             "Use scene's currently active camera to define the VR view base "
             "location and rotation"),
            ('OBJECT', "Custom Object",
             "Use an existing object to define the VR view base location and "
             "rotation"),
            ('CUSTOM', "Custom Pose",
             "Allow a manually defined position and rotation to be used as "
             "the VR view base pose"),
        ],
        default='SCENE_CAMERA',
        update=vr_landmark_type_update,
    )
    base_pose_object: bpy.props.PointerProperty(
        name="Object",
        type=bpy.types.Object,
        update=vr_landmark_base_pose_object_update,
    )
    base_pose_location: bpy.props.FloatVectorProperty(
        name="Base Pose Location",
        subtype='TRANSLATION',
        update=vr_landmark_base_pose_location_update,
    )
    base_pose_angle: bpy.props.FloatProperty(
        name="Base Pose Angle",
        subtype='ANGLE',
        update=vr_landmark_base_pose_angle_update,
    )
    base_scale: bpy.props.FloatProperty(
        name="Base Scale",
        default=1.0,
        min=0.001,
        max=1000.0,
        soft_min=0.001,
        soft_max=1000.0,
        update=vr_landmark_base_scale_update,
    )

    @staticmethod
    def get_selected_landmark(context):
        scene = context.scene
        landmarks = scene.vr_landmarks

        return (
            None if (len(landmarks) <
                     1) else landmarks[scene.vr_landmarks_selected]
        )

    @staticmethod
    def get_active_landmark(context):
        scene = context.scene
        landmarks = scene.vr_landmarks

        return (
            None if (len(landmarks) <
                     1) else landmarks[scene.vr_landmarks_active]
        )


### Motion capture.
def vr_mocap_object_selected_get(session_settings):
    mocap_objects = session_settings.mocap_objects
    return (
        None if (len(mocap_objects) <
                 1) else mocap_objects[session_settings.selected_mocap_object]
    )


def vr_scene_mocap_object_selected_get(scene, session_settings):
    mocap_objects = scene.vr_mocap_objects
    return (
        None if (len(mocap_objects) <
                 1) else mocap_objects[session_settings.selected_mocap_object]
    )


def vr_scene_mocap_object_update(self, context):
    session_settings = context.window_manager.xr_session_settings
    mocap_ob = vr_mocap_object_selected_get(session_settings)
    if not mocap_ob:
        return

    scene = context.scene
    scene_mocap_ob = vr_scene_mocap_object_selected_get(scene, session_settings)
    if not scene_mocap_ob:
        return

    # Check for duplicate object.
    if scene_mocap_ob.object and session_settings.mocap_objects.find(scene_mocap_ob.object):
        scene_mocap_ob.object = None
        return

    mocap_ob.object = scene_mocap_ob.object


class VRMotionCaptureObject(PropertyGroup):
    object: bpy.props.PointerProperty(
        name="Object",
        type=bpy.types.Object,
        update=vr_scene_mocap_object_update,
    )


classes = (
    VRLandmark,
    VRMotionCaptureObject,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.vr_landmarks = bpy.props.CollectionProperty(
        name="Landmark",
        type=VRLandmark,
    )
    bpy.types.Scene.vr_landmarks_selected = bpy.props.IntProperty(
        name="Selected Landmark"
    )
    bpy.types.Scene.vr_landmarks_active = bpy.props.IntProperty(
        update=vr_landmark_active_update,
    )
    # This scene collection property is needed instead of directly accessing
    # XrSessionSettings.mocap_objects in the UI to avoid invalid pointers when
    # deleting objects.
    bpy.types.Scene.vr_mocap_objects = bpy.props.CollectionProperty(
        name="Motion Capture Object",
        type=VRMotionCaptureObject,
    )

    bpy.app.handlers.load_post.append(vr_ensure_default_landmark)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.vr_landmarks
    del bpy.types.Scene.vr_landmarks_selected
    del bpy.types.Scene.vr_landmarks_active
    del bpy.types.Scene.vr_mocap_objects

    bpy.app.handlers.load_post.remove(vr_ensure_default_landmark)
