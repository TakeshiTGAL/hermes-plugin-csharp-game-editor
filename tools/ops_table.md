# Upstream operations

Upstream 10.3.0. Tools 49. Ops 388. Ask 295. Read 93. Unknown 13.

Blocked menu paths taken from the editor handler: File/Quit

| bundle | op | flags | ask | evidence |
| --- | --- | --- | --- | --- |
| unity_generate | batch_execute | runs_code | True | MCPForUnity/Editor/Tools/BatchExecute.cs |
| unity_generate | blender_bridge.status | sends | True | MCPForUnity/Editor/Tools/Blender/BlenderBridgeTool.cs:55 |
| unity_generate | blender_bridge.scene_info | sends | True | MCPForUnity/Editor/Tools/Blender/BlenderBridgeTool.cs:56 |
| unity_generate | blender_bridge.object_info | sends | True | MCPForUnity/Editor/Tools/Blender/BlenderBridgeTool.cs:59 |
| unity_generate | blender_bridge.screenshot | runs_code, sends, writes | True | MCPForUnity/Editor/Tools/Blender/BlenderBridgeTool.cs:68 |
| unity_generate | blender_bridge.run_python | sends | True | MCPForUnity/Editor/Tools/Blender/BlenderBridgeTool.cs:69 |
| unity_generate | blender_bridge.import_model | runs_code, sends, writes | True | MCPForUnity/Editor/Tools/Blender/BlenderBridgeTool.cs:76 |
| unity_generate | blender_bridge.compare_screenshot | deletes, runs_code, sends, writes | True | MCPForUnity/Editor/Tools/Blender/BlenderBridgeTool.cs:77 |
| unity_generate | blender_bridge.setup_bloom | runs_code, writes | True | MCPForUnity/Editor/Tools/Blender/BlenderBridgeTool.cs:78 |
| unity_generate | blender_bridge.check_updates | sends | True | MCPForUnity/Editor/Tools/Blender/BlenderBridgeTool.cs:79 |
| unity_generate | blender_bridge.sync_addon | writes | True | MCPForUnity/Editor/Tools/Blender/BlenderBridgeTool.cs:80 |
| unity_generate | generate_audio.generate | sends | True | MCPForUnity/Editor/Tools/AssetGen/GenerateAudio.cs:29 |
| unity_generate | generate_audio.status | - | False | MCPForUnity/Editor/Tools/AssetGen/GenerateAudio.cs:30 |
| unity_generate | generate_audio.cancel | - | False | MCPForUnity/Editor/Tools/AssetGen/GenerateAudio.cs:31 |
| unity_generate | generate_audio.list_providers | - | False | MCPForUnity/Editor/Tools/AssetGen/GenerateAudio.cs:32 |
| unity_generate | generate_audio.list_models | sends | True | MCPForUnity/Editor/Tools/AssetGen/GenerateAudio.cs:33 |
| unity_generate | generate_audio.refresh_models | sends | True | MCPForUnity/Editor/Tools/AssetGen/GenerateAudio.cs:34 |
| unity_generate | generate_image.generate | runs_code, sends, writes | True | MCPForUnity/Editor/Tools/AssetGen/GenerateImage.cs:28 |
| unity_generate | generate_image.remove_background | - | False | MCPForUnity/Editor/Tools/AssetGen/GenerateImage.cs:29 |
| unity_generate | generate_image.status | - | False | MCPForUnity/Editor/Tools/AssetGen/GenerateImage.cs:31 |
| unity_generate | generate_image.cancel | - | False | MCPForUnity/Editor/Tools/AssetGen/GenerateImage.cs:32 |
| unity_generate | generate_image.list_providers | - | False | MCPForUnity/Editor/Tools/AssetGen/GenerateImage.cs:33 |
| unity_generate | generate_image.list_models | sends | True | MCPForUnity/Editor/Tools/AssetGen/GenerateImage.cs:34 |
| unity_generate | generate_image.refresh_models | sends | True | MCPForUnity/Editor/Tools/AssetGen/GenerateImage.cs:35 |
| unity_generate | generate_model.generate | sends | True | MCPForUnity/Editor/Tools/AssetGen/GenerateModel.cs:29 |
| unity_generate | generate_model.status | - | False | MCPForUnity/Editor/Tools/AssetGen/GenerateModel.cs:30 |
| unity_generate | generate_model.cancel | - | False | MCPForUnity/Editor/Tools/AssetGen/GenerateModel.cs:31 |
| unity_generate | generate_model.list_providers | - | False | MCPForUnity/Editor/Tools/AssetGen/GenerateModel.cs:32 |
| unity_generate | generate_model.list_models | sends | True | MCPForUnity/Editor/Tools/AssetGen/GenerateModel.cs:33 |
| unity_generate | generate_model.refresh_models | sends | True | MCPForUnity/Editor/Tools/AssetGen/GenerateModel.cs:34 |
| unity_generate | import_model.search | - | False | MCPForUnity/Editor/Tools/AssetGen/ImportModel.cs:41 |
| unity_generate | import_model.preview | - | False | MCPForUnity/Editor/Tools/AssetGen/ImportModel.cs:42 |
| unity_generate | import_model.import | sends | True | MCPForUnity/Editor/Tools/AssetGen/ImportModel.cs:43 |
| unity_generate | import_model.status | - | False | MCPForUnity/Editor/Tools/AssetGen/ImportModel.cs:44 |
| unity_generate | import_model.cancel | - | False | MCPForUnity/Editor/Tools/AssetGen/ImportModel.cs:45 |
| unity_generate | import_model.list_providers | - | False | MCPForUnity/Editor/Tools/AssetGen/ImportModel.cs:46 |
| unity_generate | import_model_file | runs_code, writes | True | MCPForUnity/Editor/Tools/AssetGen/ImportModelFile.cs |
| unity_editor | debug_request_context | - | True | Server/src/services/tools/debug_request_context.py |
| unity_editor | execute_menu_item | runs_code | True | MCPForUnity/Editor/Tools/ExecuteMenuItem.cs |
| unity_editor | manage_editor.telemetry_status | - | True | MCPForUnity/Editor/Tools/ManageEditor.cs has no case telemetry_status; description read-only |
| unity_editor | manage_editor.telemetry_ping | - | True | MCPForUnity/Editor/Tools/ManageEditor.cs has no case telemetry_ping; description read-only |
| unity_editor | manage_editor.play | runs_code | True | MCPForUnity/Editor/Tools/ManageEditor.cs:53; description modifying |
| unity_editor | manage_editor.pause | - | True | MCPForUnity/Editor/Tools/ManageEditor.cs:67; description modifying |
| unity_editor | manage_editor.stop | - | True | MCPForUnity/Editor/Tools/ManageEditor.cs:83; description modifying |
| unity_editor | manage_editor.set_active_tool | - | True | MCPForUnity/Editor/Tools/ManageEditor.cs:99; description modifying |
| unity_editor | manage_editor.add_tag | writes | True | MCPForUnity/Editor/Tools/ManageEditor.cs:106; description modifying |
| unity_editor | manage_editor.remove_tag | writes | True | MCPForUnity/Editor/Tools/ManageEditor.cs:111; description modifying |
| unity_editor | manage_editor.add_layer | writes | True | MCPForUnity/Editor/Tools/ManageEditor.cs:117; description modifying |
| unity_editor | manage_editor.remove_layer | writes | True | MCPForUnity/Editor/Tools/ManageEditor.cs:122; description modifying |
| unity_editor | manage_editor.deploy_package | - | True | MCPForUnity/Editor/Tools/ManageEditor.cs:138; description modifying |
| unity_editor | manage_editor.restore_package | - | True | MCPForUnity/Editor/Tools/ManageEditor.cs:140; description modifying |
| unity_editor | manage_editor.undo | - | True | MCPForUnity/Editor/Tools/ManageEditor.cs:144; description modifying |
| unity_editor | manage_editor.redo | - | True | MCPForUnity/Editor/Tools/ManageEditor.cs:159; description modifying |
| unity_editor | manage_tools.list_groups | - | True | Server/src/services/tools/manage_tools.py |
| unity_editor | manage_tools.activate | - | True | Server/src/services/tools/manage_tools.py |
| unity_editor | manage_tools.deactivate | - | True | Server/src/services/tools/manage_tools.py |
| unity_editor | manage_tools.sync | - | True | Server/src/services/tools/manage_tools.py |
| unity_editor | manage_tools.reset | - | True | Server/src/services/tools/manage_tools.py |
| unity_editor | read_console.get | - | False | MCPForUnity/Editor/Tools/ReadConsole.cs:183; description read-only |
| unity_editor | read_console.clear | - | True | MCPForUnity/Editor/Tools/ReadConsole.cs:179; description modifying |
| unity_editor | refresh_unity | runs_code | True | MCPForUnity/Editor/Tools/RefreshUnity.cs |
| unity_editor | set_active_instance | - | True | Server/src/services/tools/set_active_instance.py |
| unity_code | execute_code.execute | deletes, runs_code | True | MCPForUnity/Editor/Tools/ExecuteCode.cs:94 |
| unity_code | execute_code.get_history | - | False | MCPForUnity/Editor/Tools/ExecuteCode.cs:96 |
| unity_code | execute_code.replay | runs_code | True | MCPForUnity/Editor/Tools/ExecuteCode.cs:100 |
| unity_code | execute_code.clear_history | deletes | True | MCPForUnity/Editor/Tools/ExecuteCode.cs:98 |
| unity_code | execute_custom_tool | - | True | Server/src/services/tools/execute_custom_tool.py |
| unity_code | unity_reflect.get_member | - | False | MCPForUnity/Editor/Tools/UnityReflect.cs:123 |
| unity_code | unity_reflect.get_type | - | False | MCPForUnity/Editor/Tools/UnityReflect.cs:121 |
| unity_code | unity_reflect.search | - | False | MCPForUnity/Editor/Tools/UnityReflect.cs:125 |
| unity_object | find_gameobjects | - | False | MCPForUnity/Editor/Tools/FindGameObjects.cs |
| unity_object | manage_components.add | writes | True | MCPForUnity/Editor/Tools/ManageComponents.cs:55 |
| unity_object | manage_components.remove | deletes, writes | True | MCPForUnity/Editor/Tools/ManageComponents.cs:56 |
| unity_object | manage_components.set_property | writes | True | MCPForUnity/Editor/Tools/ManageComponents.cs:57 |
| unity_object | manage_gameobject.create | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/GameObjects/ManageGameObject.cs:93 |
| unity_object | manage_gameobject.modify | deletes, writes | True | MCPForUnity/Editor/Tools/GameObjects/ManageGameObject.cs:95 |
| unity_object | manage_gameobject.delete | deletes | True | MCPForUnity/Editor/Tools/GameObjects/ManageGameObject.cs:97 |
| unity_object | manage_gameobject.duplicate | writes | True | MCPForUnity/Editor/Tools/GameObjects/ManageGameObject.cs:99 |
| unity_object | manage_gameobject.move_relative | writes | True | MCPForUnity/Editor/Tools/GameObjects/ManageGameObject.cs:101 |
| unity_object | manage_gameobject.look_at | writes | True | MCPForUnity/Editor/Tools/GameObjects/ManageGameObject.cs:103 |
| unity_script | find_in_file.read | - | False | MCPForUnity/Editor/Tools/ManageScript.cs:224 |
| unity_script | apply_text_edits.read | - | False | MCPForUnity/Editor/Tools/ManageScript.cs:224 |
| unity_script | apply_text_edits.apply_text_edits | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageScript.cs:232 |
| unity_script | create_script.create | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageScript.cs:198 |
| unity_script | delete_script.delete | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageScript.cs:230 |
| unity_script | validate_script.validate | runs_code | True | MCPForUnity/Editor/Tools/ManageScript.cs:242 |
| unity_script | manage_script.create | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageScript.cs:198; description modifying |
| unity_script | manage_script.read | - | False | MCPForUnity/Editor/Tools/ManageScript.cs:224 |
| unity_script | manage_script.delete | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageScript.cs:230; description modifying |
| unity_script | manage_script_capabilities | - | True | Server/src/services/tools/manage_script.py |
| unity_script | get_sha.get_sha | - | False | MCPForUnity/Editor/Tools/ManageScript.cs:281 |
| unity_script | manage_scriptable_object.create | - | True | - |
| unity_script | manage_scriptable_object.modify | - | True | - |
| unity_script | script_apply_edits.get_sha | - | False | MCPForUnity/Editor/Tools/ManageScript.cs:281 |
| unity_script | script_apply_edits.edit | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageScript.cs:276 |
| unity_script | script_apply_edits.read | - | False | MCPForUnity/Editor/Tools/ManageScript.cs:224 |
| unity_script | script_apply_edits.apply_text_edits | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageScript.cs:232 |
| unity_animation | manage_animation.add_blend_tree_child | runs_code, writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:229 |
| unity_animation | manage_animation.add_curve | runs_code, writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:241 |
| unity_animation | manage_animation.add_event | runs_code, writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:246 |
| unity_animation | manage_animation.add_layer | runs_code, writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:224 |
| unity_animation | manage_animation.add_parameter | runs_code, writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:221 |
| unity_animation | manage_animation.add_state | runs_code, writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:219 |
| unity_animation | manage_animation.add_transition | runs_code, writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:220 |
| unity_animation | manage_animation.assign | runs_code, writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:223 |
| unity_animation | manage_animation.create | runs_code, writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:218 |
| unity_animation | manage_animation.create_blend_tree_1d | runs_code, writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:227 |
| unity_animation | manage_animation.create_blend_tree_2d | runs_code, writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:228 |
| unity_animation | manage_animation.create_preset | runs_code, writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:244 |
| unity_animation | manage_animation.crossfade | writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:205 |
| unity_animation | manage_animation.get_info | runs_code | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:202 |
| unity_animation | manage_animation.get_parameter | - | False | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:203 |
| unity_animation | manage_animation.play | writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:204 |
| unity_animation | manage_animation.remove_event | runs_code, writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:247 |
| unity_animation | manage_animation.remove_layer | runs_code, writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:225 |
| unity_animation | manage_animation.set_curve | runs_code, writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:242 |
| unity_animation | manage_animation.set_enabled | writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:208 |
| unity_animation | manage_animation.set_layer_weight | runs_code, writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:226 |
| unity_animation | manage_animation.set_parameter | writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:206 |
| unity_animation | manage_animation.set_speed | writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:207 |
| unity_animation | manage_animation.set_vector_curve | runs_code, writes | True | MCPForUnity/Editor/Tools/Animation/ManageAnimation.cs:243 |
| unity_asset | manage_asset.import | deletes, runs_code | True | MCPForUnity/Editor/Tools/ManageAsset.cs:86 |
| unity_asset | manage_asset.create | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageAsset.cs:89 |
| unity_asset | manage_asset.modify | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageAsset.cs:91 |
| unity_asset | manage_asset.delete | deletes, runs_code | True | MCPForUnity/Editor/Tools/ManageAsset.cs:94 |
| unity_asset | manage_asset.duplicate | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageAsset.cs:96 |
| unity_asset | manage_asset.move | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageAsset.cs:98 |
| unity_asset | manage_asset.rename | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageAsset.cs:99 |
| unity_asset | manage_asset.search | deletes, runs_code | True | MCPForUnity/Editor/Tools/ManageAsset.cs:101 |
| unity_asset | manage_asset.get_info | deletes, runs_code | True | MCPForUnity/Editor/Tools/ManageAsset.cs:103 |
| unity_asset | manage_asset.create_folder | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageAsset.cs:108 |
| unity_asset | manage_asset.get_components | runs_code | True | MCPForUnity/Editor/Tools/ManageAsset.cs:110 |
| unity_asset | manage_prefabs.create_from_gameobject | runs_code, writes | True | MCPForUnity/Editor/Tools/Prefabs/ManagePrefabs.cs:49 |
| unity_asset | manage_prefabs.get_info | runs_code | True | MCPForUnity/Editor/Tools/Prefabs/ManagePrefabs.cs:51 |
| unity_asset | manage_prefabs.get_hierarchy | runs_code | True | MCPForUnity/Editor/Tools/Prefabs/ManagePrefabs.cs:53 |
| unity_asset | manage_prefabs.modify_contents | runs_code | True | MCPForUnity/Editor/Tools/Prefabs/ManagePrefabs.cs:55 |
| unity_asset | manage_prefabs.open_prefab_stage | runs_code | True | MCPForUnity/Editor/Tools/Prefabs/ManagePrefabs.cs:57 |
| unity_asset | manage_prefabs.save_prefab_stage | runs_code, writes | True | MCPForUnity/Editor/Tools/Prefabs/ManagePrefabs.cs:62 |
| unity_asset | manage_prefabs.close_prefab_stage | runs_code, writes | True | MCPForUnity/Editor/Tools/Prefabs/ManagePrefabs.cs:64 |
| unity_build | manage_build.batch | runs_code, writes | True | MCPForUnity/Editor/Tools/ManageBuild.cs:46 |
| unity_build | manage_build.build | runs_code, writes | True | MCPForUnity/Editor/Tools/ManageBuild.cs:40 |
| unity_build | manage_build.cancel | - | False | MCPForUnity/Editor/Tools/ManageBuild.cs:47 |
| unity_build | manage_build.platform | writes | True | MCPForUnity/Editor/Tools/ManageBuild.cs:42 |
| unity_build | manage_build.profiles | runs_code | True | MCPForUnity/Editor/Tools/ManageBuild.cs:45 |
| unity_build | manage_build.scenes | - | False | MCPForUnity/Editor/Tools/ManageBuild.cs:44 |
| unity_build | manage_build.settings | writes | True | MCPForUnity/Editor/Tools/ManageBuild.cs:43 |
| unity_build | manage_build.status | - | False | MCPForUnity/Editor/Tools/ManageBuild.cs:41 |
| unity_look | manage_camera.add_extension | writes | True | MCPForUnity/Editor/Tools/Cameras/ManageCamera.cs:103 |
| unity_look | manage_camera.create_camera | writes | True | MCPForUnity/Editor/Tools/Cameras/ManageCamera.cs:40 |
| unity_look | manage_camera.ensure_brain | writes | True | MCPForUnity/Editor/Tools/Cameras/ManageCamera.cs:88 |
| unity_look | manage_camera.force_camera | - | False | MCPForUnity/Editor/Tools/Cameras/ManageCamera.cs:112 |
| unity_look | manage_camera.get_brain_status | - | False | MCPForUnity/Editor/Tools/Cameras/ManageCamera.cs:91 |
| unity_look | manage_camera.list_cameras | - | False | MCPForUnity/Editor/Tools/Cameras/ManageCamera.cs:60 |
| unity_look | manage_camera.ping | - | False | MCPForUnity/Editor/Tools/Cameras/ManageCamera.cs:26 |
| unity_look | manage_camera.release_override | - | False | MCPForUnity/Editor/Tools/Cameras/ManageCamera.cs:115 |
| unity_look | manage_camera.remove_extension | deletes, writes | True | MCPForUnity/Editor/Tools/Cameras/ManageCamera.cs:106 |
| unity_look | manage_camera.screenshot | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/Cameras/ManageCamera.cs:63 |
| unity_look | manage_camera.screenshot_multiview | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/Cameras/ManageCamera.cs:64 |
| unity_look | manage_camera.set_aim | deletes, writes | True | MCPForUnity/Editor/Tools/Cameras/ManageCamera.cs:97 |
| unity_look | manage_camera.set_blend | writes | True | MCPForUnity/Editor/Tools/Cameras/ManageCamera.cs:109 |
| unity_look | manage_camera.set_body | deletes, writes | True | MCPForUnity/Editor/Tools/Cameras/ManageCamera.cs:94 |
| unity_look | manage_camera.set_lens | writes | True | MCPForUnity/Editor/Tools/Cameras/ManageCamera.cs:50 |
| unity_look | manage_camera.set_noise | writes | True | MCPForUnity/Editor/Tools/Cameras/ManageCamera.cs:100 |
| unity_look | manage_camera.set_priority | writes | True | MCPForUnity/Editor/Tools/Cameras/ManageCamera.cs:55 |
| unity_look | manage_camera.set_target | writes | True | MCPForUnity/Editor/Tools/Cameras/ManageCamera.cs:45 |
| unity_look | manage_material.ping | - | False | MCPForUnity/Editor/Tools/ManageMaterial.cs:27; description read-only |
| unity_look | manage_material.create | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageMaterial.cs:30; description modifying |
| unity_look | manage_material.set_material_shader_property | runs_code, writes | True | MCPForUnity/Editor/Tools/ManageMaterial.cs:33; description modifying |
| unity_look | manage_material.set_material_color | runs_code, writes | True | MCPForUnity/Editor/Tools/ManageMaterial.cs:36; description modifying |
| unity_look | manage_material.assign_material_to_renderer | runs_code, writes | True | MCPForUnity/Editor/Tools/ManageMaterial.cs:39; description modifying |
| unity_look | manage_material.set_renderer_color | runs_code, writes | True | MCPForUnity/Editor/Tools/ManageMaterial.cs:42; description modifying |
| unity_look | manage_material.get_material_info | runs_code | True | MCPForUnity/Editor/Tools/ManageMaterial.cs:45; description read-only |
| unity_look | manage_shader.create | runs_code, writes | True | MCPForUnity/Editor/Tools/ManageShader.cs:94; description modifying |
| unity_look | manage_shader.read | - | False | MCPForUnity/Editor/Tools/ManageShader.cs:118 |
| unity_look | manage_shader.update | runs_code, writes | True | MCPForUnity/Editor/Tools/ManageShader.cs:94; description modifying |
| unity_look | manage_shader.delete | deletes | True | MCPForUnity/Editor/Tools/ManageShader.cs:122; description modifying |
| unity_look | manage_texture.create | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageTexture.cs:69 |
| unity_look | manage_texture.modify | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageTexture.cs:72 |
| unity_look | manage_texture.delete | deletes | True | MCPForUnity/Editor/Tools/ManageTexture.cs:74 |
| unity_look | manage_texture.create_sprite | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageTexture.cs:70 |
| unity_look | manage_texture.apply_pattern | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageTexture.cs:76 |
| unity_look | manage_texture.apply_gradient | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageTexture.cs:78 |
| unity_look | manage_texture.apply_noise | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageTexture.cs:80 |
| unity_look | manage_texture.set_import_settings | writes | True | MCPForUnity/Editor/Tools/ManageTexture.cs:82 |
| unity_graphics | manage_graphics.bake_cancel | runs_code | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:75 |
| unity_graphics | manage_graphics.bake_clear | deletes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:79 |
| unity_graphics | manage_graphics.bake_create_light_probe_group | writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:87 |
| unity_graphics | manage_graphics.bake_create_reflection_probe | writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:89 |
| unity_graphics | manage_graphics.bake_get_settings | - | False | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:83 |
| unity_graphics | manage_graphics.bake_reflection_probe | runs_code, writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:81 |
| unity_graphics | manage_graphics.bake_set_probe_positions | writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:91 |
| unity_graphics | manage_graphics.bake_set_settings | writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:85 |
| unity_graphics | manage_graphics.bake_start | runs_code | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:73 |
| unity_graphics | manage_graphics.bake_status | - | False | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:77 |
| unity_graphics | manage_graphics.feature_add | runs_code, writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:116 |
| unity_graphics | manage_graphics.feature_configure | runs_code, writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:118 |
| unity_graphics | manage_graphics.feature_list | runs_code, writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:115 |
| unity_graphics | manage_graphics.feature_remove | runs_code, writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:117 |
| unity_graphics | manage_graphics.feature_reorder | runs_code, writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:120 |
| unity_graphics | manage_graphics.feature_toggle | runs_code, writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:119 |
| unity_graphics | manage_graphics.ping | - | False | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:26 |
| unity_graphics | manage_graphics.pipeline_get_info | - | False | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:105 |
| unity_graphics | manage_graphics.pipeline_get_settings | - | False | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:109 |
| unity_graphics | manage_graphics.pipeline_set_quality | writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:107 |
| unity_graphics | manage_graphics.pipeline_set_settings | runs_code, writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:111 |
| unity_graphics | manage_graphics.skybox_get | - | False | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:138 |
| unity_graphics | manage_graphics.skybox_set_ambient | writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:144 |
| unity_graphics | manage_graphics.skybox_set_fog | writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:146 |
| unity_graphics | manage_graphics.skybox_set_material | runs_code, writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:140 |
| unity_graphics | manage_graphics.skybox_set_properties | runs_code, writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:142 |
| unity_graphics | manage_graphics.skybox_set_reflection | runs_code, writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:148 |
| unity_graphics | manage_graphics.skybox_set_sun | writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:150 |
| unity_graphics | manage_graphics.stats_get | - | False | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:95 |
| unity_graphics | manage_graphics.stats_get_memory | - | False | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:101 |
| unity_graphics | manage_graphics.stats_list_counters | - | False | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:97 |
| unity_graphics | manage_graphics.stats_set_scene_debug | - | False | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:99 |
| unity_graphics | manage_graphics.volume_add_effect | runs_code, writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:46 |
| unity_graphics | manage_graphics.volume_create | runs_code, writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:45 |
| unity_graphics | manage_graphics.volume_create_profile | runs_code, writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:52 |
| unity_graphics | manage_graphics.volume_get_info | runs_code, writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:49 |
| unity_graphics | manage_graphics.volume_list_effects | runs_code, writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:51 |
| unity_graphics | manage_graphics.volume_remove_effect | runs_code, writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:48 |
| unity_graphics | manage_graphics.volume_set_effect | runs_code, writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:47 |
| unity_graphics | manage_graphics.volume_set_properties | runs_code, writes | True | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:50 |
| unity_packages | manage_packages.add_package | sends | True | MCPForUnity/Editor/Tools/ManagePackages.cs:45 |
| unity_packages | manage_packages.add_registry | writes | True | MCPForUnity/Editor/Tools/ManagePackages.cs:59 |
| unity_packages | manage_packages.embed_package | - | False | MCPForUnity/Editor/Tools/ManagePackages.cs:63 |
| unity_packages | manage_packages.get_package_info | - | False | MCPForUnity/Editor/Tools/ManagePackages.cs:55 |
| unity_packages | manage_packages.list_packages | - | False | MCPForUnity/Editor/Tools/ManagePackages.cs:51 |
| unity_packages | manage_packages.list_registries | - | False | MCPForUnity/Editor/Tools/ManagePackages.cs:57 |
| unity_packages | manage_packages.ping | - | False | MCPForUnity/Editor/Tools/ManagePackages.cs:67 |
| unity_packages | manage_packages.remove_package | sends | True | MCPForUnity/Editor/Tools/ManagePackages.cs:47 |
| unity_packages | manage_packages.remove_registry | writes | True | MCPForUnity/Editor/Tools/ManagePackages.cs:61 |
| unity_packages | manage_packages.resolve_packages | - | False | MCPForUnity/Editor/Tools/ManagePackages.cs:65 |
| unity_packages | manage_packages.search_packages | sends | True | MCPForUnity/Editor/Tools/ManagePackages.cs:53 |
| unity_packages | manage_packages.status | - | False | MCPForUnity/Editor/Tools/ManagePackages.cs:49 |
| unity_physics | manage_physics.add_joint | writes | True | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:50 |
| unity_physics | manage_physics.apply_force | writes | True | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:70 |
| unity_physics | manage_physics.assign_physics_material | runs_code, writes | True | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:46 |
| unity_physics | manage_physics.configure_joint | writes | True | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:52 |
| unity_physics | manage_physics.configure_physics_material | runs_code, writes | True | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:44 |
| unity_physics | manage_physics.configure_rigidbody | writes | True | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:76 |
| unity_physics | manage_physics.create_physics_material | runs_code, writes | True | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:42 |
| unity_physics | manage_physics.get_collision_matrix | - | False | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:36 |
| unity_physics | manage_physics.get_rigidbody | - | False | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:74 |
| unity_physics | manage_physics.get_settings | - | False | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:30 |
| unity_physics | manage_physics.linecast | - | False | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:62 |
| unity_physics | manage_physics.overlap | - | False | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:66 |
| unity_physics | manage_physics.ping | - | False | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:26 |
| unity_physics | manage_physics.raycast | - | False | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:58 |
| unity_physics | manage_physics.raycast_all | - | False | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:60 |
| unity_physics | manage_physics.remove_joint | deletes, writes | True | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:54 |
| unity_physics | manage_physics.set_collision_matrix | writes | True | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:38 |
| unity_physics | manage_physics.set_settings | writes | True | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:32 |
| unity_physics | manage_physics.shapecast | - | False | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:64 |
| unity_physics | manage_physics.simulate_step | - | False | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:84 |
| unity_physics | manage_physics.validate | - | False | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:80 |
| unity_probuilder | manage_probuilder.append_vertices_to_edge | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:227 |
| unity_probuilder | manage_probuilder.auto_smooth | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:243 |
| unity_probuilder | manage_probuilder.bevel_edges | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:208 |
| unity_probuilder | manage_probuilder.bridge_edges | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:211 |
| unity_probuilder | manage_probuilder.center_pivot | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:246 |
| unity_probuilder | manage_probuilder.combine_meshes | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:216 |
| unity_probuilder | manage_probuilder.connect_elements | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:212 |
| unity_probuilder | manage_probuilder.convert_to_probuilder | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:239 |
| unity_probuilder | manage_probuilder.create_poly_shape | deletes, writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:203 |
| unity_probuilder | manage_probuilder.create_polygon | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:219 |
| unity_probuilder | manage_probuilder.create_shape | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:202 |
| unity_probuilder | manage_probuilder.delete_faces | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:210 |
| unity_probuilder | manage_probuilder.detach_faces | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:213 |
| unity_probuilder | manage_probuilder.duplicate_and_flip | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:218 |
| unity_probuilder | manage_probuilder.extrude_edges | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:207 |
| unity_probuilder | manage_probuilder.extrude_faces | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:206 |
| unity_probuilder | manage_probuilder.flip_normals | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:214 |
| unity_probuilder | manage_probuilder.freeze_transform | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:247 |
| unity_probuilder | manage_probuilder.get_mesh_info | - | False | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:238 |
| unity_probuilder | manage_probuilder.insert_vertex | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:226 |
| unity_probuilder | manage_probuilder.merge_faces | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:215 |
| unity_probuilder | manage_probuilder.merge_objects | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:217 |
| unity_probuilder | manage_probuilder.merge_vertices | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:222 |
| unity_probuilder | manage_probuilder.move_vertices | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:225 |
| unity_probuilder | manage_probuilder.ping | - | False | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:198 |
| unity_probuilder | manage_probuilder.repair_mesh | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:250 |
| unity_probuilder | manage_probuilder.select_faces | - | False | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:230 |
| unity_probuilder | manage_probuilder.set_face_color | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:234 |
| unity_probuilder | manage_probuilder.set_face_material | runs_code, writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:233 |
| unity_probuilder | manage_probuilder.set_face_uvs | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:235 |
| unity_probuilder | manage_probuilder.set_pivot | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:248 |
| unity_probuilder | manage_probuilder.set_smoothing | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:242 |
| unity_probuilder | manage_probuilder.split_vertices | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:224 |
| unity_probuilder | manage_probuilder.subdivide | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:209 |
| unity_probuilder | manage_probuilder.validate_mesh | - | False | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:249 |
| unity_probuilder | manage_probuilder.weld_vertices | writes | True | MCPForUnity/Editor/Tools/ProBuilder/ManageProBuilder.cs:223 |
| unity_profiler | manage_profiler.frame_debugger_disable | - | False | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:55 |
| unity_profiler | manage_profiler.frame_debugger_enable | runs_code | True | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:53 |
| unity_profiler | manage_profiler.frame_debugger_get_events | - | False | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:57 |
| unity_profiler | manage_profiler.get_counters | - | False | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:39 |
| unity_profiler | manage_profiler.get_frame_timing | - | False | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:37 |
| unity_profiler | manage_profiler.get_object_memory | runs_code | True | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:41 |
| unity_profiler | manage_profiler.memory_compare_snapshots | - | False | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:49 |
| unity_profiler | manage_profiler.memory_list_snapshots | - | False | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:47 |
| unity_profiler | manage_profiler.memory_take_snapshot | - | False | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:45 |
| unity_profiler | manage_profiler.ping | - | False | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:61 |
| unity_profiler | manage_profiler.profiler_set_areas | writes | True | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:33 |
| unity_profiler | manage_profiler.profiler_start | - | False | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:27 |
| unity_profiler | manage_profiler.profiler_status | - | False | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:31 |
| unity_profiler | manage_profiler.profiler_stop | - | False | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:29 |
| unity_scene | manage_scene.create | runs_code, writes | True | MCPForUnity/Editor/Tools/ManageScene.cs:201 |
| unity_scene | manage_scene.load | runs_code | True | MCPForUnity/Editor/Tools/ManageScene.cs:251 |
| unity_scene | manage_scene.save | runs_code, writes | True | MCPForUnity/Editor/Tools/ManageScene.cs:270; description modifying |
| unity_scene | manage_scene.get_hierarchy | - | False | MCPForUnity/Editor/Tools/ManageScene.cs:273; description read-only |
| unity_scene | manage_scene.get_active | - | False | MCPForUnity/Editor/Tools/ManageScene.cs:278; description read-only |
| unity_scene | manage_scene.get_build_settings | - | False | MCPForUnity/Editor/Tools/ManageScene.cs:283; description read-only |
| unity_scene | manage_scene.scene_view_frame | - | False | MCPForUnity/Editor/Tools/ManageScene.cs:287; description read-only |
| unity_scene | manage_scene.close_scene | deletes | True | MCPForUnity/Editor/Tools/ManageScene.cs:291; description modifying |
| unity_scene | manage_scene.set_active_scene | - | True | MCPForUnity/Editor/Tools/ManageScene.cs:293; description modifying |
| unity_scene | manage_scene.get_loaded_scenes | - | False | MCPForUnity/Editor/Tools/ManageScene.cs:295; description read-only |
| unity_scene | manage_scene.move_to_scene | - | True | MCPForUnity/Editor/Tools/ManageScene.cs:297; description modifying |
| unity_scene | manage_scene.validate | writes | True | MCPForUnity/Editor/Tools/ManageScene.cs:305 |
| unity_ui | manage_ui.ping | - | False | MCPForUnity/Editor/Tools/ManageUI.cs:60; description read-only |
| unity_ui | manage_ui.create | runs_code, writes | True | MCPForUnity/Editor/Tools/ManageUI.cs:63; description modifying |
| unity_ui | manage_ui.read | - | False | MCPForUnity/Editor/Tools/ManageUI.cs:66; description read-only |
| unity_ui | manage_ui.update | runs_code, writes | True | MCPForUnity/Editor/Tools/ManageUI.cs:69; description modifying |
| unity_ui | manage_ui.delete | deletes | True | MCPForUnity/Editor/Tools/ManageUI.cs:90; description modifying |
| unity_ui | manage_ui.attach_ui_document | runs_code, writes | True | MCPForUnity/Editor/Tools/ManageUI.cs:72; description modifying |
| unity_ui | manage_ui.detach_ui_document | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageUI.cs:96; description modifying |
| unity_ui | manage_ui.create_panel_settings | runs_code, writes | True | MCPForUnity/Editor/Tools/ManageUI.cs:75; description modifying |
| unity_ui | manage_ui.update_panel_settings | runs_code, writes | True | MCPForUnity/Editor/Tools/ManageUI.cs:78; description modifying |
| unity_ui | manage_ui.get_visual_tree | runs_code | True | MCPForUnity/Editor/Tools/ManageUI.cs:81; description read-only |
| unity_ui | manage_ui.render_ui | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/ManageUI.cs:84 |
| unity_ui | manage_ui.link_stylesheet | runs_code, writes | True | MCPForUnity/Editor/Tools/ManageUI.cs:87 |
| unity_ui | manage_ui.list | - | False | MCPForUnity/Editor/Tools/ManageUI.cs:93; description read-only |
| unity_ui | manage_ui.modify_visual_element | runs_code | True | MCPForUnity/Editor/Tools/ManageUI.cs:99; description modifying |
| unity_vfx | manage_vfx.add_burst | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:323 |
| unity_vfx | manage_vfx.add_position | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:381 |
| unity_vfx | manage_vfx.assign_asset | runs_code, writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:342 |
| unity_vfx | manage_vfx.clear | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:322 |
| unity_vfx | manage_vfx.clear_bursts | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:324 |
| unity_vfx | manage_vfx.create | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:307 |
| unity_vfx | manage_vfx.create_arc | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:390 |
| unity_vfx | manage_vfx.create_asset | deletes, runs_code, writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:341 |
| unity_vfx | manage_vfx.create_bezier | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:391 |
| unity_vfx | manage_vfx.create_circle | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:389 |
| unity_vfx | manage_vfx.create_line | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:388 |
| unity_vfx | manage_vfx.emit | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:408 |
| unity_vfx | manage_vfx.enable_module | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:317 |
| unity_vfx | manage_vfx.get_info | - | False | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:308 |
| unity_vfx | manage_vfx.list_assets | runs_code | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:344 |
| unity_vfx | manage_vfx.list_templates | - | False | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:343 |
| unity_vfx | manage_vfx.pause | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:320 |
| unity_vfx | manage_vfx.play | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:318 |
| unity_vfx | manage_vfx.reinit | - | False | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:363 |
| unity_vfx | manage_vfx.restart | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:321 |
| unity_vfx | manage_vfx.send_event | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:359 |
| unity_vfx | manage_vfx.set_bool | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:350 |
| unity_vfx | manage_vfx.set_color | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:354 |
| unity_vfx | manage_vfx.set_color_over_lifetime | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:312 |
| unity_vfx | manage_vfx.set_curve | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:358 |
| unity_vfx | manage_vfx.set_emission | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:310 |
| unity_vfx | manage_vfx.set_float | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:348 |
| unity_vfx | manage_vfx.set_gradient | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:355 |
| unity_vfx | manage_vfx.set_int | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:349 |
| unity_vfx | manage_vfx.set_main | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:309 |
| unity_vfx | manage_vfx.set_material | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:385 |
| unity_vfx | manage_vfx.set_mesh | runs_code, writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:357 |
| unity_vfx | manage_vfx.set_noise | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:315 |
| unity_vfx | manage_vfx.set_playback_speed | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:364 |
| unity_vfx | manage_vfx.set_position | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:382 |
| unity_vfx | manage_vfx.set_positions | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:380 |
| unity_vfx | manage_vfx.set_properties | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:386 |
| unity_vfx | manage_vfx.set_renderer | runs_code, writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:316 |
| unity_vfx | manage_vfx.set_seed | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:365 |
| unity_vfx | manage_vfx.set_shape | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:311 |
| unity_vfx | manage_vfx.set_size_over_lifetime | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:313 |
| unity_vfx | manage_vfx.set_texture | runs_code, writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:356 |
| unity_vfx | manage_vfx.set_time | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:402 |
| unity_vfx | manage_vfx.set_vector2 | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:351 |
| unity_vfx | manage_vfx.set_vector3 | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:352 |
| unity_vfx | manage_vfx.set_vector4 | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:353 |
| unity_vfx | manage_vfx.set_velocity_over_lifetime | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:314 |
| unity_vfx | manage_vfx.set_width | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:383 |
| unity_vfx | manage_vfx.stop | writes | True | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:319 |
| unity_tests | run_tests | runs_code | True | MCPForUnity/Editor/Tools/RunTests.cs |
| unity_tests | get_test_job | - | False | MCPForUnity/Editor/Tools/GetTestJob.cs |
| unity_docs | unity_docs.get_doc | sends | True | Server/src/services/tools/unity_docs.py |
| unity_docs | unity_docs.get_manual | sends | True | Server/src/services/tools/unity_docs.py |
| unity_docs | unity_docs.get_package_doc | sends | True | Server/src/services/tools/unity_docs.py |
| unity_docs | unity_docs.lookup | sends | True | Server/src/services/tools/unity_docs.py |

Guards listed: 168. Resources listed: 30.

plan_batch and apply_plan are not upstream tools. plan_batch returns the text. apply_plan runs that plan once.
