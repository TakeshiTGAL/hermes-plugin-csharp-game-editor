# What each operation does inside (upstream 10.3.0)

Made by tools/extract_side_effects.py from the MCPForUnity C# source. One row per effect site: the Unity call, where it is, the chain from the operation to it, and the arguments that gate it. The bridge decides the plan text, the second question, and the state fingerprint from these rows.

| op | effect | call | at | gated by | via |
| --- | --- | --- | --- | --- | --- |
| batch_execute | editor_prefs | `EditorPrefs.SetBool` | Editor/Services/ToolDiscoveryService.cs:254 | - | BatchExecute.HandleCommand > … > ToolDiscoveryService.DiscoverAllTools > ToolDiscoveryService.EnsurePreferenceInitialized |
| blender_bridge.status | send | `TcpClient` | Editor/Services/Blender/BlenderSocketClient.cs:46 | - | case status > … > BlenderSocketClient.SendAsync > BlenderSocketClient.Send |
| blender_bridge.scene_info | send | `TcpClient` | Editor/Services/Blender/BlenderSocketClient.cs:46 | - | case scene_info > BlenderSocketClient.SendAsync > BlenderSocketClient.Send |
| blender_bridge.object_info | send | `TcpClient` | Editor/Services/Blender/BlenderSocketClient.cs:46 | - | case object_info > BlenderSocketClient.SendAsync > BlenderSocketClient.Send |
| blender_bridge.screenshot | write_file | `File.Copy` | Editor/Tools/Blender/BlenderBridgeTool.cs:171 | - | case screenshot > BlenderBridgeTool.ScreenshotAsync |
| blender_bridge.screenshot | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/Blender/BlenderBridgeTool.cs:172 | - | case screenshot > BlenderBridgeTool.ScreenshotAsync |
| blender_bridge.screenshot | send | `TcpClient` | Editor/Services/Blender/BlenderSocketClient.cs:46 | - | case screenshot > … > BlenderSocketClient.SendAsync > BlenderSocketClient.Send |
| blender_bridge.run_python | send | `TcpClient` | Editor/Services/Blender/BlenderSocketClient.cs:46 | - | case run_python > … > BlenderSocketClient.RunPython > BlenderSocketClient.Send |
| blender_bridge.import_model | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ControllerCreate.cs:99 | auto_animate | case import_model > … > BlenderBridgeTool.SetupAnimation > ControllerCreate.AddState |
| blender_bridge.import_model | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Blender/BlenderBridgeTool.cs:443 | auto_animate | case import_model > BlenderBridgeTool.ImportModelAsync > BlenderBridgeTool.SetupAnimation |
| blender_bridge.import_model | write_file | `File.Copy` | Editor/Tools/AssetGen/ImportModelFile.cs:97 | - | case import_model > … > ImportModelFile.HandleCommand > ImportModelFile.StageUnderAssets |
| blender_bridge.import_model | write_file | `PrefabUtility.SaveAsPrefabAssetAndConnect` | Editor/Tools/Blender/BlenderBridgeTool.cs:460 | save_prefab | case import_model > BlenderBridgeTool.ImportModelAsync > BlenderBridgeTool.SavePrefab |
| blender_bridge.import_model | write_file | `File.Create` | Editor/Services/AssetGen/Import/SafeZipExtractor.cs:66 | - | case import_model > … > ModelImportPipeline.ImportArchive > SafeZipExtractor.ExtractTo |
| blender_bridge.import_model | import_compile | `AssetDatabase.ImportAsset` | Editor/Services/AssetGen/Import/ModelImportPipeline.cs:62 | - | case import_model > … > ModelImportPipeline.ImportInto > ModelImportPipeline.ImportModelFile |
| blender_bridge.import_model | import_compile | `AssetDatabase.Refresh` | Editor/Tools/AssetGen/ImportModelFile.cs:47 | - | case import_model > BlenderBridgeTool.ImportModelAsync > ImportModelFile.HandleCommand |
| blender_bridge.import_model | import_compile | `AssetDatabase.ImportAsset` | Editor/Services/AssetGen/Import/ModelImportPipeline.cs:111 | - | case import_model > … > ModelImportPipeline.ImportInto > ModelImportPipeline.ImportArchive |
| blender_bridge.import_model | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Blender/BlenderBridgeTool.cs:252 | - | case import_model > BlenderBridgeTool.ImportModelAsync |
| blender_bridge.import_model | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ControllerCreate.cs:435 | auto_animate | case import_model > … > ControllerCreate.AddState > ControllerCreate.LoadController |
| blender_bridge.import_model | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Services/AssetGen/Import/ModelImportPipeline.cs:193 | - | case import_model > … > ModelImportPipeline.ApplyModelImporterSettings > ModelImportPipeline.ComputeMaxDimension |
| blender_bridge.import_model | instantiate | `PrefabUtility.InstantiatePrefab` | Editor/Tools/Blender/BlenderBridgeTool.cs:259 | - | case import_model > BlenderBridgeTool.ImportModelAsync |
| blender_bridge.import_model | instantiate | `.AddComponent` | Editor/Tools/Blender/BlenderBridgeTool.cs:423 | auto_animate | case import_model > BlenderBridgeTool.ImportModelAsync > BlenderBridgeTool.SetupAnimation |
| blender_bridge.import_model | instantiate | `.AddComponent` | Editor/Tools/Blender/BlenderBridgeTool.cs:498 | ensure_bloom | case import_model > BlenderBridgeTool.ImportModelAsync > BlenderBridgeTool.SetupBloomAsync |
| blender_bridge.import_model | scene_edit | `.position =` | Editor/Tools/Blender/BlenderBridgeTool.cs:262 | - | case import_model > BlenderBridgeTool.ImportModelAsync |
| blender_bridge.import_model | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Animation/ControllerCreate.cs:98 | auto_animate | case import_model > … > BlenderBridgeTool.SetupAnimation > ControllerCreate.AddState |
| blender_bridge.import_model | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Blender/BlenderBridgeTool.cs:503 | ensure_bloom | case import_model > BlenderBridgeTool.ImportModelAsync > BlenderBridgeTool.SetupBloomAsync |
| blender_bridge.import_model | send | `TcpClient` | Editor/Services/Blender/BlenderSocketClient.cs:46 | - | case import_model > … > BlenderSocketClient.SendAsync > BlenderSocketClient.Send |
| blender_bridge.compare_screenshot | delete_file | `AssetDatabase.DeleteAsset` | Editor/Tools/Blender/BlenderBridgeTool.cs:603 | - | case compare_screenshot > BlenderBridgeTool.CompareScreenshotAsync |
| blender_bridge.compare_screenshot | write_file | `File.Copy` | Editor/Tools/Blender/BlenderBridgeTool.cs:611 | - | case compare_screenshot > BlenderBridgeTool.CompareScreenshotAsync |
| blender_bridge.compare_screenshot | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/Blender/BlenderBridgeTool.cs:612 | - | case compare_screenshot > BlenderBridgeTool.CompareScreenshotAsync |
| blender_bridge.compare_screenshot | send | `TcpClient` | Editor/Services/Blender/BlenderSocketClient.cs:46 | - | case compare_screenshot > … > BlenderSocketClient.SendAsync > BlenderSocketClient.Send |
| blender_bridge.setup_bloom | instantiate | `.AddComponent` | Editor/Tools/Blender/BlenderBridgeTool.cs:498 | - | case setup_bloom > BlenderBridgeTool.SetupBloomAsync |
| blender_bridge.setup_bloom | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Blender/BlenderBridgeTool.cs:503 | - | case setup_bloom > BlenderBridgeTool.SetupBloomAsync |
| blender_bridge.check_updates | send | `Process.Start` | Editor/Tools/Blender/BlenderBridgeTool.cs:817 | - | case check_updates > … > BlenderBridgeTool.CheckUpdatesBlocking > BlenderBridgeTool.TryGit |
| blender_bridge.sync_addon | write_file | `File.Copy` | Editor/Tools/Blender/BlenderBridgeTool.cs:790 | - | case sync_addon > BlenderBridgeTool.SyncAddon |
| blender_bridge.sync_addon | write_file | `File.Copy` | Editor/Tools/Blender/BlenderBridgeTool.cs:788 | - | case sync_addon > BlenderBridgeTool.SyncAddon |
| generate_audio.generate | write_file | `File.WriteAllBytes` | Editor/Services/AssetGen/AssetGenJobManager.cs:533 | - | case generate > … > AssetGenJobManager.Advance > AssetGenJobManager.WriteFile |
| generate_audio.generate | write_file | `File.WriteAllText` | Editor/Services/AssetGen/FalModelCatalog.cs:365 | - | case generate > … > FalModelCatalog.VerifyForGeneration > FalModelCatalog.Save |
| generate_audio.generate | write_file | `File.Replace` | Editor/Services/AssetGen/FalModelCatalog.cs:366 | - | case generate > … > FalModelCatalog.VerifyForGeneration > FalModelCatalog.Save |
| generate_audio.generate | import_compile | `AssetDatabase.Refresh` | Editor/Services/AssetGen/AssetGenJobManager.cs:451 | - | case generate > … > AssetGenJobManager.Tick > AssetGenJobManager.Advance |
| generate_audio.generate | send | `UnityWebRequest` | Editor/Services/AssetGen/Http/UnityWebRequestTransport.cs:22 | - | case generate > … > TripoAdapter.SubmitAsync > UnityWebRequestTransport.SendAsync |
| generate_audio.generate | send | `UnityWebRequest` | Editor/Services/AssetGen/Http/UnityWebRequestTransport.cs:66 | - | case generate > … > TripoAdapter.SubmitAsync > UnityWebRequestTransport.SendAsync |
| generate_audio.status | none found | - | - | - | MCPForUnity/Editor/Tools/AssetGen/GenerateAudio.cs:30 |
| generate_audio.cancel | none found | - | - | - | MCPForUnity/Editor/Tools/AssetGen/GenerateAudio.cs:31 |
| generate_audio.list_providers | none found | - | - | - | MCPForUnity/Editor/Tools/AssetGen/GenerateAudio.cs:32 |
| generate_audio.list_models | write_file | `File.WriteAllText` | Editor/Services/AssetGen/FalModelCatalog.cs:365 | - | case list_models > … > FalModelCatalog.RefreshCore > FalModelCatalog.Save |
| generate_audio.list_models | write_file | `File.WriteAllText` | Editor/Services/AssetGen/OpenRouterModelCatalog.cs:184 | - | case list_models > … > OpenRouterModelCatalog.RefreshCore > OpenRouterModelCatalog.Save |
| generate_audio.list_models | write_file | `File.Replace` | Editor/Services/AssetGen/FalModelCatalog.cs:366 | - | case list_models > … > FalModelCatalog.RefreshCore > FalModelCatalog.Save |
| generate_audio.refresh_models | write_file | `File.WriteAllText` | Editor/Services/AssetGen/FalModelCatalog.cs:365 | - | case refresh_models > … > FalModelCatalog.RefreshCore > FalModelCatalog.Save |
| generate_audio.refresh_models | write_file | `File.WriteAllText` | Editor/Services/AssetGen/OpenRouterModelCatalog.cs:184 | - | case refresh_models > … > OpenRouterModelCatalog.RefreshCore > OpenRouterModelCatalog.Save |
| generate_audio.refresh_models | write_file | `File.Replace` | Editor/Services/AssetGen/FalModelCatalog.cs:366 | - | case refresh_models > … > FalModelCatalog.RefreshCore > FalModelCatalog.Save |
| generate_image.generate | write_file | `File.WriteAllBytes` | Editor/Services/AssetGen/AssetGenJobManager.cs:533 | - | case generate > … > AssetGenJobManager.Advance > AssetGenJobManager.WriteFile |
| generate_image.generate | write_file | `File.WriteAllText` | Editor/Services/AssetGen/FalModelCatalog.cs:365 | provider | case generate > … > FalModelCatalog.VerifyForGeneration > FalModelCatalog.Save |
| generate_image.generate | write_file | `File.WriteAllText` | Editor/Services/AssetGen/OpenRouterModelCatalog.cs:184 | provider | case generate > … > OpenRouterModelCatalog.VerifyForGeneration > OpenRouterModelCatalog.Save |
| generate_image.generate | import_compile | `AssetDatabase.ImportAsset` | Editor/Services/AssetGen/Import/ImageImportPipeline.cs:30 | - | case generate > … > AssetGenJobManager.StartImageGeneration > ImageImportPipeline.ImportInto |
| generate_image.generate | import_compile | `AssetDatabase.Refresh` | Editor/Services/AssetGen/AssetGenJobManager.cs:451 | - | case generate > … > AssetGenJobManager.Tick > AssetGenJobManager.Advance |
| generate_image.generate | send | `UnityWebRequest` | Editor/Services/AssetGen/Http/UnityWebRequestTransport.cs:22 | - | case generate > … > TripoAdapter.SubmitAsync > UnityWebRequestTransport.SendAsync |
| generate_image.generate | send | `UnityWebRequest` | Editor/Services/AssetGen/Http/UnityWebRequestTransport.cs:66 | - | case generate > … > TripoAdapter.SubmitAsync > UnityWebRequestTransport.SendAsync |
| generate_image.remove_background | none found | - | - | - | MCPForUnity/Editor/Tools/AssetGen/GenerateImage.cs:29 |
| generate_image.status | none found | - | - | - | MCPForUnity/Editor/Tools/AssetGen/GenerateImage.cs:31 |
| generate_image.cancel | none found | - | - | - | MCPForUnity/Editor/Tools/AssetGen/GenerateImage.cs:32 |
| generate_image.list_providers | none found | - | - | - | MCPForUnity/Editor/Tools/AssetGen/GenerateImage.cs:33 |
| generate_image.list_models | write_file | `File.WriteAllText` | Editor/Services/AssetGen/FalModelCatalog.cs:365 | - | case list_models > … > FalModelCatalog.RefreshCore > FalModelCatalog.Save |
| generate_image.list_models | write_file | `File.WriteAllText` | Editor/Services/AssetGen/OpenRouterModelCatalog.cs:184 | - | case list_models > … > OpenRouterModelCatalog.RefreshCore > OpenRouterModelCatalog.Save |
| generate_image.list_models | write_file | `File.Replace` | Editor/Services/AssetGen/FalModelCatalog.cs:366 | - | case list_models > … > FalModelCatalog.RefreshCore > FalModelCatalog.Save |
| generate_image.refresh_models | write_file | `File.WriteAllText` | Editor/Services/AssetGen/FalModelCatalog.cs:365 | - | case refresh_models > … > FalModelCatalog.RefreshCore > FalModelCatalog.Save |
| generate_image.refresh_models | write_file | `File.WriteAllText` | Editor/Services/AssetGen/OpenRouterModelCatalog.cs:184 | - | case refresh_models > … > OpenRouterModelCatalog.RefreshCore > OpenRouterModelCatalog.Save |
| generate_image.refresh_models | write_file | `File.Replace` | Editor/Services/AssetGen/FalModelCatalog.cs:366 | - | case refresh_models > … > FalModelCatalog.RefreshCore > FalModelCatalog.Save |
| generate_model.generate | write_file | `File.WriteAllBytes` | Editor/Services/AssetGen/AssetGenJobManager.cs:533 | - | case generate > … > AssetGenJobManager.Advance > AssetGenJobManager.WriteFile |
| generate_model.generate | write_file | `File.WriteAllText` | Editor/Services/AssetGen/FalModelCatalog.cs:365 | provider | case generate > … > FalModelCatalog.VerifyForGeneration > FalModelCatalog.Save |
| generate_model.generate | write_file | `File.Replace` | Editor/Services/AssetGen/FalModelCatalog.cs:366 | provider | case generate > … > FalModelCatalog.VerifyForGeneration > FalModelCatalog.Save |
| generate_model.generate | import_compile | `AssetDatabase.Refresh` | Editor/Services/AssetGen/AssetGenJobManager.cs:451 | - | case generate > … > AssetGenJobManager.Tick > AssetGenJobManager.Advance |
| generate_model.generate | send | `UnityWebRequest` | Editor/Services/AssetGen/Http/UnityWebRequestTransport.cs:22 | - | case generate > … > TripoAdapter.SubmitAsync > UnityWebRequestTransport.SendAsync |
| generate_model.generate | send | `UnityWebRequest` | Editor/Services/AssetGen/Http/UnityWebRequestTransport.cs:66 | - | case generate > … > TripoAdapter.SubmitAsync > UnityWebRequestTransport.SendAsync |
| generate_model.status | none found | - | - | - | MCPForUnity/Editor/Tools/AssetGen/GenerateModel.cs:30 |
| generate_model.cancel | none found | - | - | - | MCPForUnity/Editor/Tools/AssetGen/GenerateModel.cs:31 |
| generate_model.list_providers | none found | - | - | - | MCPForUnity/Editor/Tools/AssetGen/GenerateModel.cs:32 |
| generate_model.list_models | write_file | `File.WriteAllText` | Editor/Services/AssetGen/FalModelCatalog.cs:365 | - | case list_models > … > FalModelCatalog.RefreshCore > FalModelCatalog.Save |
| generate_model.list_models | write_file | `File.WriteAllText` | Editor/Services/AssetGen/OpenRouterModelCatalog.cs:184 | - | case list_models > … > OpenRouterModelCatalog.RefreshCore > OpenRouterModelCatalog.Save |
| generate_model.list_models | write_file | `File.Replace` | Editor/Services/AssetGen/FalModelCatalog.cs:366 | - | case list_models > … > FalModelCatalog.RefreshCore > FalModelCatalog.Save |
| generate_model.refresh_models | write_file | `File.WriteAllText` | Editor/Services/AssetGen/FalModelCatalog.cs:365 | - | case refresh_models > … > FalModelCatalog.RefreshCore > FalModelCatalog.Save |
| generate_model.refresh_models | write_file | `File.WriteAllText` | Editor/Services/AssetGen/OpenRouterModelCatalog.cs:184 | - | case refresh_models > … > OpenRouterModelCatalog.RefreshCore > OpenRouterModelCatalog.Save |
| generate_model.refresh_models | write_file | `File.Replace` | Editor/Services/AssetGen/FalModelCatalog.cs:366 | - | case refresh_models > … > FalModelCatalog.RefreshCore > FalModelCatalog.Save |
| import_model.search | send | `UnityWebRequest` | Editor/Services/AssetGen/Http/UnityWebRequestTransport.cs:22 | - | case search > … > SketchfabAdapter.SearchAsync > UnityWebRequestTransport.SendAsync |
| import_model.search | send | `UnityWebRequest` | Editor/Services/AssetGen/Http/UnityWebRequestTransport.cs:66 | - | case search > … > SketchfabAdapter.SearchAsync > UnityWebRequestTransport.SendAsync |
| import_model.preview | send | `UnityWebRequest` | Editor/Services/AssetGen/Http/UnityWebRequestTransport.cs:22 | - | case preview > … > SketchfabAdapter.PreviewAsync > UnityWebRequestTransport.SendAsync |
| import_model.preview | send | `UnityWebRequest` | Editor/Services/AssetGen/Http/UnityWebRequestTransport.cs:66 | - | case preview > … > SketchfabAdapter.PreviewAsync > UnityWebRequestTransport.SendAsync |
| import_model.import | write_file | `File.WriteAllBytes` | Editor/Services/AssetGen/AssetGenJobManager.cs:533 | - | case import > … > AssetGenJobManager.Advance > AssetGenJobManager.WriteFile |
| import_model.import | import_compile | `AssetDatabase.Refresh` | Editor/Services/AssetGen/AssetGenJobManager.cs:451 | - | case import > … > AssetGenJobManager.Tick > AssetGenJobManager.Advance |
| import_model.import | send | `UnityWebRequest` | Editor/Services/AssetGen/Http/UnityWebRequestTransport.cs:22 | - | case import > … > SketchfabAdapter.ResolveDownloadUrlAsync > UnityWebRequestTransport.SendAsync |
| import_model.import | send | `UnityWebRequest` | Editor/Services/AssetGen/Http/UnityWebRequestTransport.cs:66 | - | case import > … > SketchfabAdapter.ResolveDownloadUrlAsync > UnityWebRequestTransport.SendAsync |
| import_model.status | none found | - | - | - | MCPForUnity/Editor/Tools/AssetGen/ImportModel.cs:44 |
| import_model.cancel | none found | - | - | - | MCPForUnity/Editor/Tools/AssetGen/ImportModel.cs:45 |
| import_model.list_providers | none found | - | - | - | MCPForUnity/Editor/Tools/AssetGen/ImportModel.cs:46 |
| import_model_file | write_file | `File.Copy` | Editor/Tools/AssetGen/ImportModelFile.cs:97 | - | ImportModelFile.HandleCommand > ImportModelFile.StageUnderAssets |
| import_model_file | write_file | `File.Create` | Editor/Services/AssetGen/Import/SafeZipExtractor.cs:66 | - | ImportModelFile.HandleCommand > … > ModelImportPipeline.ImportArchive > SafeZipExtractor.ExtractTo |
| import_model_file | import_compile | `AssetDatabase.ImportAsset` | Editor/Services/AssetGen/Import/ModelImportPipeline.cs:62 | - | ImportModelFile.HandleCommand > ModelImportPipeline.ImportInto > ModelImportPipeline.ImportModelFile |
| import_model_file | import_compile | `AssetDatabase.Refresh` | Editor/Tools/AssetGen/ImportModelFile.cs:47 | - | ImportModelFile.HandleCommand |
| import_model_file | import_compile | `AssetDatabase.ImportAsset` | Editor/Services/AssetGen/Import/ModelImportPipeline.cs:111 | - | ImportModelFile.HandleCommand > ModelImportPipeline.ImportInto > ModelImportPipeline.ImportArchive |
| import_model_file | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Services/AssetGen/Import/ModelImportPipeline.cs:193 | - | ImportModelFile.HandleCommand > … > ModelImportPipeline.ApplyModelImporterSettings > ModelImportPipeline.ComputeMaxDimension |
| debug_request_context | none found | - | - | - | no C# handler |
| execute_menu_item | menu_item | `EditorApplication.ExecuteMenuItem` | Editor/Tools/ExecuteMenuItem.cs:38 | - | ExecuteMenuItem.HandleCommand |
| manage_editor.telemetry_status | none found | - | - | - | unresolved |
| manage_editor.telemetry_ping | none found | - | - | - | unresolved |
| manage_editor.play | enter_play | `EditorApplication.isPlaying = true` | Editor/Tools/ManageEditor.cs:58 | - | case play |
| manage_editor.pause | none found | - | - | - | MCPForUnity/Editor/Tools/ManageEditor.cs:67 |
| manage_editor.stop | exit_play | `EditorApplication.isPlaying = false` | Editor/Tools/ManageEditor.cs:88 | - | case stop |
| manage_editor.set_active_tool | none found | - | - | - | MCPForUnity/Editor/Tools/ManageEditor.cs:99 |
| manage_editor.add_tag | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/ManageEditor.cs:234 | - | case add_tag > ManageEditor.AddTag |
| manage_editor.add_tag | project_settings | `InternalEditorUtility.AddTag` | Editor/Tools/ManageEditor.cs:232 | - | case add_tag > ManageEditor.AddTag |
| manage_editor.remove_tag | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/ManageEditor.cs:261 | - | case remove_tag > ManageEditor.RemoveTag |
| manage_editor.remove_tag | project_settings | `InternalEditorUtility.RemoveTag` | Editor/Tools/ManageEditor.cs:259 | - | case remove_tag > ManageEditor.RemoveTag |
| manage_editor.add_layer | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/ManageEditor.cs:327 | - | case add_layer > ManageEditor.AddLayer |
| manage_editor.add_layer | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Tools/ManageEditor.cs:447 | - | case add_layer > ManageEditor.AddLayer > ManageEditor.GetTagManager |
| manage_editor.add_layer | set_values | `.ApplyModifiedProperties` | Editor/Tools/ManageEditor.cs:325 | - | case add_layer > ManageEditor.AddLayer |
| manage_editor.add_layer | project_settings | `tagManager` | Editor/Tools/ManageEditor.cs:279 | - | case add_layer > ManageEditor.AddLayer |
| manage_editor.add_layer | project_settings | `tagManager` | Editor/Tools/ManageEditor.cs:280 | - | case add_layer > ManageEditor.AddLayer |
| manage_editor.add_layer | project_settings | `tagManager` | Editor/Tools/ManageEditor.cs:283 | - | case add_layer > ManageEditor.AddLayer |
| manage_editor.remove_layer | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/ManageEditor.cs:383 | - | case remove_layer > ManageEditor.RemoveLayer |
| manage_editor.remove_layer | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Tools/ManageEditor.cs:447 | - | case remove_layer > ManageEditor.RemoveLayer > ManageEditor.GetTagManager |
| manage_editor.remove_layer | set_values | `.ApplyModifiedProperties` | Editor/Tools/ManageEditor.cs:381 | - | case remove_layer > ManageEditor.RemoveLayer |
| manage_editor.remove_layer | project_settings | `tagManager` | Editor/Tools/ManageEditor.cs:344 | - | case remove_layer > ManageEditor.RemoveLayer |
| manage_editor.remove_layer | project_settings | `tagManager` | Editor/Tools/ManageEditor.cs:345 | - | case remove_layer > ManageEditor.RemoveLayer |
| manage_editor.remove_layer | project_settings | `tagManager` | Editor/Tools/ManageEditor.cs:348 | - | case remove_layer > ManageEditor.RemoveLayer |
| manage_editor.deploy_package | delete_file | `FileUtil.DeleteFileOrDirectory` | Editor/Services/PackageDeploymentService.cs:192 | - | case deploy_package > … > PackageDeploymentService.CopyCoreFolders > PackageDeploymentService.ReplaceDirectory |
| manage_editor.deploy_package | delete_file | `FileUtil.DeleteFileOrDirectory` | Editor/Services/PackageDeploymentService.cs:208 | - | case deploy_package > … > PackageDeploymentService.DeployFromStoredSource > PackageDeploymentService.CreateBackup |
| manage_editor.deploy_package | import_compile | `AssetDatabase.Refresh` | Editor/Services/PackageDeploymentService.cs:126 | - | case deploy_package > ManageEditor.DeployPackage > PackageDeploymentService.DeployFromStoredSource |
| manage_editor.deploy_package | editor_prefs | `EditorPrefs.SetString` | Editor/Services/PackageDeploymentService.cs:122 | - | case deploy_package > ManageEditor.DeployPackage > PackageDeploymentService.DeployFromStoredSource |
| manage_editor.deploy_package | editor_prefs | `EditorPrefs.SetString` | Editor/Services/PackageDeploymentService.cs:123 | - | case deploy_package > ManageEditor.DeployPackage > PackageDeploymentService.DeployFromStoredSource |
| manage_editor.deploy_package | editor_prefs | `EditorPrefs.SetString` | Editor/Services/PackageDeploymentService.cs:124 | - | case deploy_package > ManageEditor.DeployPackage > PackageDeploymentService.DeployFromStoredSource |
| manage_editor.restore_package | delete_file | `FileUtil.DeleteFileOrDirectory` | Editor/Services/PackageDeploymentService.cs:192 | - | case restore_package > … > PackageDeploymentService.RestoreLastBackup > PackageDeploymentService.ReplaceDirectory |
| manage_editor.restore_package | import_compile | `AssetDatabase.Refresh` | Editor/Services/PackageDeploymentService.cs:165 | - | case restore_package > ManageEditor.RestorePackage > PackageDeploymentService.RestoreLastBackup |
| manage_editor.undo | undo_redo | `Undo.PerformUndo` | Editor/Tools/ManageEditor.cs:147 | - | case undo |
| manage_editor.redo | undo_redo | `Undo.PerformRedo` | Editor/Tools/ManageEditor.cs:161 | - | case redo |
| manage_tools.list_groups | none found | - | - | - | no C# handler |
| manage_tools.activate | none found | - | - | - | no C# handler |
| manage_tools.deactivate | none found | - | - | - | no C# handler |
| manage_tools.sync | none found | - | - | - | no C# handler |
| manage_tools.reset | none found | - | - | - | no C# handler |
| read_console.get | reflection | `Activator.CreateInstance` | Editor/Tools/ReadConsole.cs:393 | - | case get > ReadConsole.GetConsoleEntries |
| read_console.clear | none found | - | - | - | MCPForUnity/Editor/Tools/ReadConsole.cs:179 |
| refresh_unity | import_compile | `CompilationPipeline.RequestScriptCompilation` | Editor/Tools/RefreshUnity.cs:75 | compile | RefreshUnity.HandleCommand |
| refresh_unity | import_compile | `AssetDatabase.Refresh` | Editor/Tools/RefreshUnity.cs:84 | scope | RefreshUnity.HandleCommand |
| refresh_unity | import_compile | `AssetDatabase.Refresh` | Editor/Tools/RefreshUnity.cs:68 | not scope | RefreshUnity.HandleCommand |
| set_active_instance | none found | - | - | - | no C# handler |
| execute_code.execute | delete_file | `File.Delete` | Editor/Tools/ExecuteCode.cs:380 | - | case execute > … > ExecuteCode.CompileAndExecute > ExecuteCode.CodeDomCompile |
| execute_code.execute | delete_file | `File.Delete` | Editor/Tools/ExecuteCode.cs:387 | - | case execute > … > ExecuteCode.CompileAndExecute > ExecuteCode.CodeDomCompile |
| execute_code.execute | compile_run | `CompileAndExecute` | Editor/Tools/ExecuteCode.cs:130 | - | case execute > ExecuteCode.HandleExecute |
| execute_code.execute | compile_run | `RoslynCompiler` | Editor/Tools/ExecuteCode.cs:218 | - | case execute > ExecuteCode.HandleExecute > ExecuteCode.CompileAndExecute |
| execute_code.execute | compile_run | `RoslynCompiler` | Editor/Tools/ExecuteCode.cs:220 | - | case execute > ExecuteCode.HandleExecute > ExecuteCode.CompileAndExecute |
| execute_code.execute | reflection | `Activator.CreateInstance` | Editor/Tools/ExecuteCode.cs:767 | - | case execute > … > ExecuteCode.CompileAndExecute > RoslynCompiler.Compile |
| execute_code.execute | reflection | `method.Invoke` | Editor/Tools/ExecuteCode.cs:275 | - | case execute > … > ExecuteCode.CompileAndExecute > ExecuteCode.InvokeCompiled |
| execute_code.execute | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case execute > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| execute_code.get_history | none found | - | - | - | MCPForUnity/Editor/Tools/ExecuteCode.cs:96 |
| execute_code.replay | delete_file | `File.Delete` | Editor/Tools/ExecuteCode.cs:380 | - | case replay > … > ExecuteCode.CompileAndExecute > ExecuteCode.CodeDomCompile |
| execute_code.replay | delete_file | `File.Delete` | Editor/Tools/ExecuteCode.cs:387 | - | case replay > … > ExecuteCode.CompileAndExecute > ExecuteCode.CodeDomCompile |
| execute_code.replay | compile_run | `CompileAndExecute` | Editor/Tools/ExecuteCode.cs:130 | - | case replay > ExecuteCode.HandleReplay > ExecuteCode.HandleExecute |
| execute_code.replay | compile_run | `RoslynCompiler` | Editor/Tools/ExecuteCode.cs:218 | - | case replay > … > ExecuteCode.HandleExecute > ExecuteCode.CompileAndExecute |
| execute_code.replay | compile_run | `RoslynCompiler` | Editor/Tools/ExecuteCode.cs:220 | - | case replay > … > ExecuteCode.HandleExecute > ExecuteCode.CompileAndExecute |
| execute_code.replay | reflection | `Activator.CreateInstance` | Editor/Tools/ExecuteCode.cs:767 | - | case replay > … > ExecuteCode.CompileAndExecute > RoslynCompiler.Compile |
| execute_code.replay | reflection | `method.Invoke` | Editor/Tools/ExecuteCode.cs:275 | - | case replay > … > ExecuteCode.CompileAndExecute > ExecuteCode.InvokeCompiled |
| execute_code.replay | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case replay > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| execute_code.clear_history | none found | - | - | - | MCPForUnity/Editor/Tools/ExecuteCode.cs:98 |
| execute_custom_tool | none found | - | - | - | no C# handler |
| unity_reflect.get_member | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case get_member > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| unity_reflect.get_type | reflection | `Activator.CreateInstance` | Editor/Tools/Profiler/Operations/FrameDebuggerOps.cs:181 | - | case get_type > UnityReflect.GetTypeInfo > FrameDebuggerOps.GetEvents |
| unity_reflect.get_type | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case get_type > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| unity_reflect.search | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case search > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| find_gameobjects | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | FindGameObjects.HandleCommand > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_components.add | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case add > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_components.add | reflection | `Activator.CreateInstance` | Editor/Helpers/PropertyConversion.cs:29 | properties | case add > … > ComponentOps.TrySetViaReflection > PropertyConversion.ConvertToType |
| manage_components.add | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Helpers/ComponentOps.cs:650 | properties | case add > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_components.add | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Helpers/ComponentOps.cs:676 | properties | case add > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_components.add | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ComponentOps.cs:700 | properties | case add > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_components.add | instantiate | `Undo.AddComponent` | Editor/Helpers/ComponentOps.cs:66 | - | case add > ManageComponents.AddComponent > ComponentOps.AddComponent |
| manage_components.add | instantiate | `.AddComponent` | Editor/Tools/ManageComponents.cs:92 | - | case add > ManageComponents.AddComponent |
| manage_components.add | set_values | `propInfo.SetValue` | Editor/Helpers/ComponentOps.cs:224 | properties | case add > … > ComponentOps.SetProperty > ComponentOps.TrySetViaReflection |
| manage_components.add | set_values | `.ApplyModifiedProperties` | Editor/Helpers/ComponentOps.cs:469 | properties | case add > … > ComponentOps.SetProperty > ComponentOps.SetViaSerializedProperty |
| manage_components.add | set_values | `.ApplyModifiedProperties` | Editor/Helpers/ComponentOps.cs:508 | properties | case add > … > ComponentOps.SetViaSerializedProperty > ComponentOps.SetSerializedPropertyRecursive |
| manage_components.add | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/ManageComponents.cs:113 | - | case add > ManageComponents.AddComponent |
| manage_components.add | scene_edit | `Undo.RecordObject` | Editor/Tools/ManageComponents.cs:109 | properties | case add > ManageComponents.AddComponent |
| manage_components.add | scene_edit | `EditorSceneManager.MarkSceneDirty` | Editor/Tools/ManageComponents.cs:350 | - | case add > ManageComponents.AddComponent > ManageComponents.MarkOwningSceneDirty |
| manage_components.remove | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case remove > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_components.remove | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/ManageComponents.cs:176 | - | case remove > ManageComponents.RemoveComponent |
| manage_components.remove | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/ManageComponents.cs:159 | component_index | case remove > ManageComponents.RemoveComponent |
| manage_components.remove | scene_edit | `EditorSceneManager.MarkSceneDirty` | Editor/Tools/ManageComponents.cs:350 | component_index | case remove > ManageComponents.RemoveComponent > ManageComponents.MarkOwningSceneDirty |
| manage_components.remove | destroy_object | `Undo.DestroyObjectImmediate` | Editor/Helpers/ComponentOps.cs:131 | - | case remove > ManageComponents.RemoveComponent > ComponentOps.RemoveComponent |
| manage_components.remove | destroy_object | `Undo.DestroyObjectImmediate` | Editor/Tools/ManageComponents.cs:158 | component_index | case remove > ManageComponents.RemoveComponent |
| manage_components.set_property | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case set_property > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_components.set_property | reflection | `Activator.CreateInstance` | Editor/Helpers/PropertyConversion.cs:29 | - | case set_property > … > ComponentOps.TrySetViaReflection > PropertyConversion.ConvertToType |
| manage_components.set_property | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Helpers/ComponentOps.cs:650 | - | case set_property > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_components.set_property | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Helpers/ComponentOps.cs:676 | - | case set_property > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_components.set_property | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ComponentOps.cs:700 | - | case set_property > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_components.set_property | set_values | `propInfo.SetValue` | Editor/Helpers/ComponentOps.cs:224 | - | case set_property > … > ComponentOps.SetProperty > ComponentOps.TrySetViaReflection |
| manage_components.set_property | set_values | `.ApplyModifiedProperties` | Editor/Helpers/ComponentOps.cs:469 | - | case set_property > … > ComponentOps.SetProperty > ComponentOps.SetViaSerializedProperty |
| manage_components.set_property | set_values | `.ApplyModifiedProperties` | Editor/Helpers/ComponentOps.cs:508 | - | case set_property > … > ComponentOps.SetViaSerializedProperty > ComponentOps.SetSerializedPropertyRecursive |
| manage_components.set_property | scene_edit | `Undo.RecordObject` | Editor/Tools/ManageComponents.cs:245 | - | case set_property > ManageComponents.SetProperty |
| manage_components.set_property | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/ManageComponents.cs:270 | - | case set_property > ManageComponents.SetProperty |
| manage_components.set_property | scene_edit | `EditorSceneManager.MarkSceneDirty` | Editor/Tools/ManageComponents.cs:350 | - | case set_property > ManageComponents.SetProperty > ManageComponents.MarkOwningSceneDirty |
| manage_gameobject.create | write_file | `PrefabUtility.SaveAsPrefabAssetAndConnect` | Editor/Tools/GameObjects/GameObjectCreate.cs:308 | save_as_prefab | case create > GameObjectCreate.Handle |
| manage_gameobject.create | import_compile | `AssetDatabase.Refresh` | Editor/Tools/GameObjects/GameObjectCreate.cs:304 | save_as_prefab | case create > GameObjectCreate.Handle |
| manage_gameobject.create | reflection | `Activator.CreateInstance` | Editor/Helpers/PropertyConversion.cs:29 | components_to_add | case create > … > GameObjectComponentHelpers.ConvertJTokenToType > PropertyConversion.ConvertToType |
| manage_gameobject.create | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | components_to_add | case create > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_gameobject.create | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Helpers/ComponentOps.cs:650 | components_to_add | case create > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_gameobject.create | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/GameObjects/GameObjectCreate.cs:89 | not save_as_prefab, prefab_path | case create > GameObjectCreate.Handle |
| manage_gameobject.create | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Helpers/ComponentOps.cs:676 | components_to_add | case create > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_gameobject.create | instantiate | `Undo.AddComponent` | Editor/Tools/GameObjects/GameObjectComponentHelpers.cs:63 | components_to_add | case create > GameObjectCreate.Handle > GameObjectComponentHelpers.AddComponentInternal |
| manage_gameobject.create | instantiate | `GameObject.CreatePrimitive` | Editor/Tools/GameObjects/GameObjectCreate.cs:128 | primitive_type | case create > GameObjectCreate.Handle |
| manage_gameobject.create | instantiate | `PrefabUtility.InstantiatePrefab` | Editor/Tools/GameObjects/GameObjectCreate.cs:94 | not save_as_prefab, prefab_path | case create > GameObjectCreate.Handle |
| manage_gameobject.create | set_values | `propInfo.SetValue` | Editor/Helpers/ComponentOps.cs:224 | components_to_add | case create > … > ComponentOps.SetProperty > ComponentOps.TrySetViaReflection |
| manage_gameobject.create | set_values | `.ApplyModifiedProperties` | Editor/Helpers/ComponentOps.cs:469 | components_to_add | case create > … > ComponentOps.SetProperty > ComponentOps.SetViaSerializedProperty |
| manage_gameobject.create | set_values | `.ApplyModifiedProperties` | Editor/Helpers/ComponentOps.cs:508 | components_to_add | case create > … > ComponentOps.SetViaSerializedProperty > ComponentOps.SetSerializedPropertyRecursive |
| manage_gameobject.create | scene_edit | `Undo.RecordObject` | Editor/Tools/GameObjects/GameObjectCreate.cs:170 | - | case create > GameObjectCreate.Handle |
| manage_gameobject.create | scene_edit | `.SetParent` | Editor/Tools/GameObjects/GameObjectCreate.cs:183 | parent | case create > GameObjectCreate.Handle |
| manage_gameobject.create | scene_edit | `.localPosition =` | Editor/Tools/GameObjects/GameObjectCreate.cs:191 | position | case create > GameObjectCreate.Handle |
| manage_gameobject.create | scene_edit | `.localEulerAngles =` | Editor/Tools/GameObjects/GameObjectCreate.cs:192 | rotation | case create > GameObjectCreate.Handle |
| manage_gameobject.create | scene_edit | `.localScale =` | Editor/Tools/GameObjects/GameObjectCreate.cs:193 | scale | case create > GameObjectCreate.Handle |
| manage_gameobject.create | scene_edit | `Undo.RecordObject` | Editor/Tools/GameObjects/GameObjectComponentHelpers.cs:238 | components_to_add | case create > … > GameObjectComponentHelpers.AddComponentInternal > GameObjectComponentHelpers.SetComponentPropertiesInternal |
| manage_gameobject.create | destroy_object | `Object.DestroyImmediate` | Editor/Tools/GameObjects/GameObjectCreate.cs:278 | - | case create > GameObjectCreate.Handle |
| manage_gameobject.create | destroy_object | `Object.DestroyImmediate` | Editor/Tools/GameObjects/GameObjectCreate.cs:218 | tag | case create > GameObjectCreate.Handle |
| manage_gameobject.create | destroy_object | `Object.DestroyImmediate` | Editor/Tools/GameObjects/GameObjectCreate.cs:319 | save_as_prefab | case create > GameObjectCreate.Handle |
| manage_gameobject.create | destroy_object | `Undo.DestroyObjectImmediate` | Editor/Tools/GameObjects/GameObjectComponentHelpers.cs:88 | components_to_add | case create > GameObjectCreate.Handle > GameObjectComponentHelpers.AddComponentInternal |
| manage_gameobject.create | destroy_object | `Object.DestroyImmediate` | Editor/Tools/GameObjects/GameObjectCreate.cs:180 | parent | case create > GameObjectCreate.Handle |
| manage_gameobject.create | destroy_object | `Object.DestroyImmediate` | Editor/Tools/GameObjects/GameObjectCreate.cs:135 | primitive_type, not name | case create > GameObjectCreate.Handle |
| manage_gameobject.create | destroy_object | `Object.DestroyImmediate` | Editor/Tools/GameObjects/GameObjectCreate.cs:207 | tag, tag | case create > GameObjectCreate.Handle |
| manage_gameobject.create | project_settings | `InternalEditorUtility.AddTag` | Editor/Tools/GameObjects/GameObjectCreate.cs:203 | tag, tag | case create > GameObjectCreate.Handle |
| manage_gameobject.modify | write_file | `AssetDatabase.RenameAsset` | Editor/Tools/GameObjects/GameObjectModify.cs:65 | name | case modify > GameObjectModify.Handle |
| manage_gameobject.modify | reflection | `Activator.CreateInstance` | Editor/Helpers/PropertyConversion.cs:29 | components_to_add | case modify > … > GameObjectComponentHelpers.ConvertJTokenToType > PropertyConversion.ConvertToType |
| manage_gameobject.modify | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | components_to_remove | case modify > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_gameobject.modify | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Helpers/ComponentOps.cs:650 | components_to_add | case modify > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_gameobject.modify | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Helpers/ComponentOps.cs:676 | components_to_add | case modify > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_gameobject.modify | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ComponentOps.cs:700 | components_to_add | case modify > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_gameobject.modify | instantiate | `Undo.AddComponent` | Editor/Tools/GameObjects/GameObjectComponentHelpers.cs:63 | components_to_add | case modify > GameObjectModify.Handle > GameObjectComponentHelpers.AddComponentInternal |
| manage_gameobject.modify | set_values | `propInfo.SetValue` | Editor/Helpers/ComponentOps.cs:224 | components_to_add | case modify > … > ComponentOps.SetProperty > ComponentOps.TrySetViaReflection |
| manage_gameobject.modify | set_values | `.ApplyModifiedProperties` | Editor/Helpers/ComponentOps.cs:469 | components_to_add | case modify > … > ComponentOps.SetProperty > ComponentOps.SetViaSerializedProperty |
| manage_gameobject.modify | set_values | `.ApplyModifiedProperties` | Editor/Helpers/ComponentOps.cs:508 | components_to_add | case modify > … > ComponentOps.SetViaSerializedProperty > ComponentOps.SetSerializedPropertyRecursive |
| manage_gameobject.modify | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/GameObjects/GameObjectModify.cs:244 | - | case modify > GameObjectModify.Handle |
| manage_gameobject.modify | scene_edit | `.SetActive` | Editor/Tools/GameObjects/GameObjectModify.cs:105 | set_active | case modify > GameObjectModify.Handle |
| manage_gameobject.modify | scene_edit | `.localPosition =` | Editor/Tools/GameObjects/GameObjectModify.cs:172 | position | case modify > GameObjectModify.Handle |
| manage_gameobject.modify | scene_edit | `.localEulerAngles =` | Editor/Tools/GameObjects/GameObjectModify.cs:177 | rotation | case modify > GameObjectModify.Handle |
| manage_gameobject.modify | scene_edit | `.localScale =` | Editor/Tools/GameObjects/GameObjectModify.cs:182 | scale | case modify > GameObjectModify.Handle |
| manage_gameobject.modify | scene_edit | `Undo.RecordObject` | Editor/Tools/GameObjects/GameObjectComponentHelpers.cs:238 | components_to_add | case modify > … > GameObjectComponentHelpers.AddComponentInternal > GameObjectComponentHelpers.SetComponentPropertiesInternal |
| manage_gameobject.modify | scene_edit | `.SetParent` | Editor/Tools/GameObjects/GameObjectModify.cs:97 | parent | case modify > GameObjectModify.Handle |
| manage_gameobject.modify | destroy_object | `Undo.DestroyObjectImmediate` | Editor/Tools/GameObjects/GameObjectComponentHelpers.cs:137 | components_to_remove | case modify > GameObjectModify.Handle > GameObjectComponentHelpers.RemoveComponentInternal |
| manage_gameobject.modify | destroy_object | `Undo.DestroyObjectImmediate` | Editor/Tools/GameObjects/GameObjectComponentHelpers.cs:88 | components_to_add | case modify > GameObjectModify.Handle > GameObjectComponentHelpers.AddComponentInternal |
| manage_gameobject.modify | project_settings | `InternalEditorUtility.AddTag` | Editor/Tools/GameObjects/GameObjectModify.cs:119 | tag | case modify > GameObjectModify.Handle |
| manage_gameobject.delete | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case delete > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_gameobject.delete | destroy_object | `Object.DestroyImmediate` | Editor/Tools/GameObjects/GameObjectDelete.cs:32 | - | case delete > GameObjectDelete.Handle |
| manage_gameobject.duplicate | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case duplicate > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_gameobject.duplicate | instantiate | `Object.Instantiate` | Editor/Tools/GameObjects/GameObjectDuplicate.cs:26 | - | case duplicate > GameObjectDuplicate.Handle |
| manage_gameobject.duplicate | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/GameObjects/GameObjectDuplicate.cs:71 | - | case duplicate > GameObjectDuplicate.Handle |
| manage_gameobject.duplicate | scene_edit | `.position =` | Editor/Tools/GameObjects/GameObjectDuplicate.cs:40 | position | case duplicate > GameObjectDuplicate.Handle |
| manage_gameobject.duplicate | scene_edit | `.position =` | Editor/Tools/GameObjects/GameObjectDuplicate.cs:44 | offset | case duplicate > GameObjectDuplicate.Handle |
| manage_gameobject.duplicate | scene_edit | `.SetParent` | Editor/Tools/GameObjects/GameObjectDuplicate.cs:68 | not parent | case duplicate > GameObjectDuplicate.Handle |
| manage_gameobject.duplicate | scene_edit | `.SetParent` | Editor/Tools/GameObjects/GameObjectDuplicate.cs:51 | parent | case duplicate > GameObjectDuplicate.Handle |
| manage_gameobject.move_relative | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case move_relative > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_gameobject.move_relative | scene_edit | `Undo.RecordObject` | Editor/Tools/GameObjects/GameObjectMoveRelative.cs:37 | - | case move_relative > GameObjectMoveRelative.Handle |
| manage_gameobject.move_relative | scene_edit | `.position =` | Editor/Tools/GameObjects/GameObjectMoveRelative.cs:62 | - | case move_relative > GameObjectMoveRelative.Handle |
| manage_gameobject.move_relative | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/GameObjects/GameObjectMoveRelative.cs:64 | - | case move_relative > GameObjectMoveRelative.Handle |
| manage_gameobject.look_at | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case look_at > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_gameobject.look_at | scene_edit | `Undo.RecordObject` | Editor/Tools/GameObjects/GameObjectLookAt.cs:48 | - | case look_at > GameObjectLookAt.Handle |
| find_in_file.read | none found | - | - | - | MCPForUnity/Editor/Tools/ManageScript.cs:224 |
| apply_text_edits.read | none found | - | - | - | MCPForUnity/Editor/Tools/ManageScript.cs:224 |
| apply_text_edits.apply_text_edits | delete_file | `File.Delete` | Editor/Tools/ManageScript.cs:762 | - | case apply_text_edits > ManageScript.ApplyTextEdits |
| apply_text_edits.apply_text_edits | delete_file | `File.Delete` | Editor/Tools/ManageScript.cs:768 | - | case apply_text_edits > ManageScript.ApplyTextEdits |
| apply_text_edits.apply_text_edits | delete_file | `File.Delete` | Editor/Tools/ManageScript.cs:757 | - | case apply_text_edits > ManageScript.ApplyTextEdits |
| apply_text_edits.apply_text_edits | write_file | `File.WriteAllText` | Editor/Tools/ManageScript.cs:752 | - | case apply_text_edits > ManageScript.ApplyTextEdits |
| apply_text_edits.apply_text_edits | write_file | `File.Replace` | Editor/Tools/ManageScript.cs:756 | - | case apply_text_edits > ManageScript.ApplyTextEdits |
| apply_text_edits.apply_text_edits | write_file | `File.Copy` | Editor/Tools/ManageScript.cs:761 | - | case apply_text_edits > ManageScript.ApplyTextEdits |
| apply_text_edits.apply_text_edits | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageScript.cs:778 | - | case apply_text_edits > ManageScript.ApplyTextEdits |
| apply_text_edits.apply_text_edits | import_compile | `CompilationPipeline.RequestScriptCompilation` | Editor/Tools/ManageScript.cs:783 | - | case apply_text_edits > ManageScript.ApplyTextEdits |
| apply_text_edits.apply_text_edits | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageScript.cs:2981 | - | case apply_text_edits > … > RefreshDebounce.Schedule > RefreshDebounce.Tick |
| create_script.create | delete_file | `File.Delete` | Editor/Tools/ManageScript.cs:383 | - | case create > ManageScript.CreateScript |
| create_script.create | write_file | `File.WriteAllText` | Editor/Tools/ManageScript.cs:375 | - | case create > ManageScript.CreateScript |
| create_script.create | write_file | `File.Move` | Editor/Tools/ManageScript.cs:378 | - | case create > ManageScript.CreateScript |
| create_script.create | write_file | `File.Copy` | Editor/Tools/ManageScript.cs:382 | - | case create > ManageScript.CreateScript |
| create_script.create | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageScript.cs:3018 | - | case create > ManageScript.CreateScript > ManageScriptRefreshHelpers.ImportAndRequestCompile |
| create_script.create | import_compile | `CompilationPipeline.RequestScriptCompilation` | Editor/Tools/ManageScript.cs:3020 | - | case create > ManageScript.CreateScript > ManageScriptRefreshHelpers.ImportAndRequestCompile |
| delete_script.delete | delete_file | `AssetDatabase.MoveAssetToTrash` | Editor/Tools/ManageScript.cs:1211 | - | case delete > ManageScript.DeleteScript |
| delete_script.delete | import_compile | `AssetDatabase.Refresh` | Editor/Tools/ManageScript.cs:1214 | - | case delete > ManageScript.DeleteScript |
| validate_script.validate | none found | - | - | - | MCPForUnity/Editor/Tools/ManageScript.cs:242 |
| manage_script.create | delete_file | `File.Delete` | Editor/Tools/ManageScript.cs:383 | - | case create > ManageScript.CreateScript |
| manage_script.create | write_file | `File.WriteAllText` | Editor/Tools/ManageScript.cs:375 | - | case create > ManageScript.CreateScript |
| manage_script.create | write_file | `File.Move` | Editor/Tools/ManageScript.cs:378 | - | case create > ManageScript.CreateScript |
| manage_script.create | write_file | `File.Copy` | Editor/Tools/ManageScript.cs:382 | - | case create > ManageScript.CreateScript |
| manage_script.create | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageScript.cs:3018 | - | case create > ManageScript.CreateScript > ManageScriptRefreshHelpers.ImportAndRequestCompile |
| manage_script.create | import_compile | `CompilationPipeline.RequestScriptCompilation` | Editor/Tools/ManageScript.cs:3020 | - | case create > ManageScript.CreateScript > ManageScriptRefreshHelpers.ImportAndRequestCompile |
| manage_script.read | none found | - | - | - | MCPForUnity/Editor/Tools/ManageScript.cs:224 |
| manage_script.delete | delete_file | `AssetDatabase.MoveAssetToTrash` | Editor/Tools/ManageScript.cs:1211 | - | case delete > ManageScript.DeleteScript |
| manage_script.delete | import_compile | `AssetDatabase.Refresh` | Editor/Tools/ManageScript.cs:1214 | - | case delete > ManageScript.DeleteScript |
| manage_script_capabilities | none found | - | - | - | no C# handler |
| get_sha.get_sha | none found | - | - | - | MCPForUnity/Editor/Tools/ManageScript.cs:281 |
| manage_scriptable_object.create | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/ManageScriptableObject.cs:198 | - | if IsCreateAction > ManageScriptableObject.HandleCreate |
| manage_scriptable_object.create | delete_file | `AssetDatabase.DeleteAsset` | Editor/Tools/ManageScriptableObject.cs:169 | overwrite | if IsCreateAction > ManageScriptableObject.HandleCreate |
| manage_scriptable_object.create | write_file | `AssetDatabase.CreateFolder` | Editor/Tools/ManageScriptableObject.cs:1404 | - | if IsCreateAction > ManageScriptableObject.HandleCreate > ManageScriptableObject.EnsureFolderExists |
| manage_scriptable_object.create | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/ManageScriptableObject.cs:177 | - | if IsCreateAction > ManageScriptableObject.HandleCreate |
| manage_scriptable_object.create | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageScriptableObject.cs:147 | overwrite | if IsCreateAction > ManageScriptableObject.HandleCreate |
| manage_scriptable_object.create | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/ManageScriptableObject.cs:197 | - | if IsCreateAction > ManageScriptableObject.HandleCreate |
| manage_scriptable_object.create | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/ManageScriptableObject.cs:163 | overwrite | if IsCreateAction > ManageScriptableObject.HandleCreate |
| manage_scriptable_object.create | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageScriptableObject.cs:158 | overwrite | if IsCreateAction > ManageScriptableObject.HandleCreate |
| manage_scriptable_object.modify | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageScriptableObject.cs:1327 | - | ManageScriptableObject.HandleModify > ManageScriptableObject.TryResolveTarget |
| script_apply_edits.get_sha | none found | - | - | - | MCPForUnity/Editor/Tools/ManageScript.cs:281 |
| script_apply_edits.edit | delete_file | `File.Delete` | Editor/Tools/ManageScript.cs:1667 | - | case edit > ManageScript.EditScript |
| script_apply_edits.edit | delete_file | `File.Delete` | Editor/Tools/ManageScript.cs:1673 | - | case edit > ManageScript.EditScript |
| script_apply_edits.edit | delete_file | `File.Delete` | Editor/Tools/ManageScript.cs:1662 | - | case edit > ManageScript.EditScript |
| script_apply_edits.edit | write_file | `File.WriteAllText` | Editor/Tools/ManageScript.cs:1657 | - | case edit > ManageScript.EditScript |
| script_apply_edits.edit | write_file | `File.Replace` | Editor/Tools/ManageScript.cs:1661 | - | case edit > ManageScript.EditScript |
| script_apply_edits.edit | write_file | `File.Copy` | Editor/Tools/ManageScript.cs:1666 | - | case edit > ManageScript.EditScript |
| script_apply_edits.edit | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageScript.cs:3018 | - | case edit > ManageScript.EditScript > ManageScriptRefreshHelpers.ImportAndRequestCompile |
| script_apply_edits.edit | import_compile | `CompilationPipeline.RequestScriptCompilation` | Editor/Tools/ManageScript.cs:3020 | - | case edit > ManageScript.EditScript > ManageScriptRefreshHelpers.ImportAndRequestCompile |
| script_apply_edits.edit | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageScript.cs:2981 | - | case edit > … > RefreshDebounce.Schedule > RefreshDebounce.Tick |
| script_apply_edits.read | none found | - | - | - | MCPForUnity/Editor/Tools/ManageScript.cs:224 |
| script_apply_edits.apply_text_edits | delete_file | `File.Delete` | Editor/Tools/ManageScript.cs:762 | - | case apply_text_edits > ManageScript.ApplyTextEdits |
| script_apply_edits.apply_text_edits | delete_file | `File.Delete` | Editor/Tools/ManageScript.cs:768 | - | case apply_text_edits > ManageScript.ApplyTextEdits |
| script_apply_edits.apply_text_edits | delete_file | `File.Delete` | Editor/Tools/ManageScript.cs:757 | - | case apply_text_edits > ManageScript.ApplyTextEdits |
| script_apply_edits.apply_text_edits | write_file | `File.WriteAllText` | Editor/Tools/ManageScript.cs:752 | - | case apply_text_edits > ManageScript.ApplyTextEdits |
| script_apply_edits.apply_text_edits | write_file | `File.Replace` | Editor/Tools/ManageScript.cs:756 | - | case apply_text_edits > ManageScript.ApplyTextEdits |
| script_apply_edits.apply_text_edits | write_file | `File.Copy` | Editor/Tools/ManageScript.cs:761 | - | case apply_text_edits > ManageScript.ApplyTextEdits |
| script_apply_edits.apply_text_edits | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageScript.cs:778 | - | case apply_text_edits > ManageScript.ApplyTextEdits |
| script_apply_edits.apply_text_edits | import_compile | `CompilationPipeline.RequestScriptCompilation` | Editor/Tools/ManageScript.cs:783 | - | case apply_text_edits > ManageScript.ApplyTextEdits |
| script_apply_edits.apply_text_edits | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageScript.cs:2981 | - | case apply_text_edits > … > RefreshDebounce.Schedule > RefreshDebounce.Tick |
| manage_animation.add_blend_tree_child | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ControllerBlendTrees.cs:207 | - | case add_blend_tree_child > ControllerBlendTrees.AddBlendTreeChild |
| manage_animation.add_blend_tree_child | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ControllerBlendTrees.cs:237 | - | case add_blend_tree_child > ControllerBlendTrees.AddBlendTreeChild |
| manage_animation.add_blend_tree_child | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ControllerBlendTrees.cs:155 | - | case add_blend_tree_child > ControllerBlendTrees.AddBlendTreeChild |
| manage_animation.add_blend_tree_child | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ControllerBlendTrees.cs:168 | - | case add_blend_tree_child > ControllerBlendTrees.AddBlendTreeChild |
| manage_animation.add_blend_tree_child | scene_edit | `Undo.RecordObject` | Editor/Tools/Animation/ControllerBlendTrees.cs:195 | - | case add_blend_tree_child > ControllerBlendTrees.AddBlendTreeChild |
| manage_animation.add_blend_tree_child | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Animation/ControllerBlendTrees.cs:205 | - | case add_blend_tree_child > ControllerBlendTrees.AddBlendTreeChild |
| manage_animation.add_blend_tree_child | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Animation/ControllerBlendTrees.cs:206 | - | case add_blend_tree_child > ControllerBlendTrees.AddBlendTreeChild |
| manage_animation.add_curve | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ClipCreate.cs:210 | - | case add_curve > ClipCreate.AddCurve > ClipCreate.SetOrAddCurve |
| manage_animation.add_curve | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case add_curve > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_animation.add_curve | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ClipCreate.cs:166 | - | case add_curve > ClipCreate.AddCurve > ClipCreate.SetOrAddCurve |
| manage_animation.add_curve | scene_edit | `Undo.RecordObject` | Editor/Tools/Animation/ClipCreate.cs:207 | - | case add_curve > ClipCreate.AddCurve > ClipCreate.SetOrAddCurve |
| manage_animation.add_curve | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Animation/ClipCreate.cs:209 | - | case add_curve > ClipCreate.AddCurve > ClipCreate.SetOrAddCurve |
| manage_animation.add_event | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ClipCreate.cs:540 | - | case add_event > ClipCreate.AddEvent |
| manage_animation.add_event | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ClipCreate.cs:517 | - | case add_event > ClipCreate.AddEvent |
| manage_animation.add_event | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Animation/ClipCreate.cs:539 | - | case add_event > ClipCreate.AddEvent |
| manage_animation.add_layer | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ControllerLayers.cs:47 | - | case add_layer > ControllerLayers.AddLayer |
| manage_animation.add_layer | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/ManageEditor.cs:327 | - | case add_layer > ControllerLayers.AddLayer > ManageEditor.AddLayer |
| manage_animation.add_layer | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ControllerLayers.cs:21 | - | case add_layer > ControllerLayers.AddLayer |
| manage_animation.add_layer | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Tools/ManageEditor.cs:447 | - | case add_layer > … > ManageEditor.AddLayer > ManageEditor.GetTagManager |
| manage_animation.add_layer | set_values | `.ApplyModifiedProperties` | Editor/Tools/ManageEditor.cs:325 | - | case add_layer > ControllerLayers.AddLayer > ManageEditor.AddLayer |
| manage_animation.add_layer | scene_edit | `Undo.RecordObject` | Editor/Tools/Animation/ControllerLayers.cs:36 | - | case add_layer > ControllerLayers.AddLayer |
| manage_animation.add_layer | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Animation/ControllerLayers.cs:46 | - | case add_layer > ControllerLayers.AddLayer |
| manage_animation.add_layer | project_settings | `tagManager` | Editor/Tools/ManageEditor.cs:279 | - | case add_layer > ControllerLayers.AddLayer > ManageEditor.AddLayer |
| manage_animation.add_layer | project_settings | `tagManager` | Editor/Tools/ManageEditor.cs:280 | - | case add_layer > ControllerLayers.AddLayer > ManageEditor.AddLayer |
| manage_animation.add_layer | project_settings | `tagManager` | Editor/Tools/ManageEditor.cs:283 | - | case add_layer > ControllerLayers.AddLayer > ManageEditor.AddLayer |
| manage_animation.add_parameter | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ControllerCreate.cs:288 | - | case add_parameter > ControllerCreate.AddParameter |
| manage_animation.add_parameter | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ControllerCreate.cs:435 | - | case add_parameter > ControllerCreate.AddParameter > ControllerCreate.LoadController |
| manage_animation.add_parameter | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Animation/ControllerCreate.cs:287 | - | case add_parameter > ControllerCreate.AddParameter |
| manage_animation.add_state | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ControllerCreate.cs:99 | - | case add_state > ControllerCreate.AddState |
| manage_animation.add_state | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ControllerCreate.cs:435 | - | case add_state > ControllerCreate.AddState > ControllerCreate.LoadController |
| manage_animation.add_state | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ControllerCreate.cs:85 | clip_path, clip_path | case add_state > ControllerCreate.AddState |
| manage_animation.add_state | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Animation/ControllerCreate.cs:98 | - | case add_state > ControllerCreate.AddState |
| manage_animation.add_transition | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ControllerCreate.cs:213 | - | case add_transition > ControllerCreate.AddTransition |
| manage_animation.add_transition | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ControllerCreate.cs:435 | - | case add_transition > ControllerCreate.AddTransition > ControllerCreate.LoadController |
| manage_animation.add_transition | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Animation/ControllerCreate.cs:212 | - | case add_transition > ControllerCreate.AddTransition |
| manage_animation.assign | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ControllerCreate.cs:410 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > ManageAnimation.HandleControllerAction > ControllerCreate.AssignToGameObject |
| manage_animation.assign | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ClipCreate.cs:357 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > ManageAnimation.HandleClipAction > ClipCreate.Assign |
| manage_animation.assign | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ClipCreate.cs:389 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > ManageAnimation.HandleClipAction > ClipCreate.Assign |
| manage_animation.assign | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_animation.assign | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ClipCreate.cs:342 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > ManageAnimation.HandleClipAction > ClipCreate.Assign |
| manage_animation.assign | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ControllerCreate.cs:435 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > … > ControllerCreate.AssignToGameObject > ControllerCreate.LoadController |
| manage_animation.assign | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.assign | instantiate | `Undo.AddComponent` | Editor/Tools/Animation/ClipCreate.cs:384 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > ManageAnimation.HandleClipAction > ClipCreate.Assign |
| manage_animation.assign | instantiate | `Undo.AddComponent` | Editor/Tools/Animation/ControllerCreate.cs:404 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > ManageAnimation.HandleControllerAction > ControllerCreate.AssignToGameObject |
| manage_animation.assign | set_values | `.ApplyModifiedProperties` | Editor/Tools/Animation/ClipCreate.cs:431 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > … > ClipCreate.Assign > ClipCreate.SetupLegacyClip |
| manage_animation.assign | scene_edit | `Undo.RecordObject` | Editor/Tools/Animation/ControllerCreate.cs:407 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > ManageAnimation.HandleControllerAction > ControllerCreate.AssignToGameObject |
| manage_animation.assign | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Animation/ControllerCreate.cs:409 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > ManageAnimation.HandleControllerAction > ControllerCreate.AssignToGameObject |
| manage_animation.assign | scene_edit | `Undo.RecordObject` | Editor/Tools/Animation/ClipCreate.cs:352 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > ManageAnimation.HandleClipAction > ClipCreate.Assign |
| manage_animation.create | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ClipCreate.cs:70 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > ManageAnimation.HandleClipAction > ClipCreate.Create |
| manage_animation.create | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ControllerCreate.cs:37 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > ManageAnimation.HandleControllerAction > ControllerCreate.Create |
| manage_animation.create | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/Animation/ClipCreate.cs:55 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > ManageAnimation.HandleClipAction > ClipCreate.Create |
| manage_animation.create | write_file | `AssetDatabase.CreateFolder` | Editor/Tools/Animation/ClipCreate.cs:633 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > … > ClipCreate.Create > ClipCreate.CreateFoldersRecursive |
| manage_animation.create | write_file | `AssetDatabase.CreateFolder` | Editor/Tools/Animation/ControllerCreate.cs:455 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > … > ControllerCreate.Create > ControllerCreate.CreateFoldersRecursive |
| manage_animation.create | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ClipCreate.cs:36 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > ManageAnimation.HandleClipAction > ClipCreate.Create |
| manage_animation.create | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ControllerCreate.cs:32 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > ManageAnimation.HandleControllerAction > ControllerCreate.Create |
| manage_animation.create | set_values | `.ApplyModifiedProperties` | Editor/Tools/Animation/ClipCreate.cs:66 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > ManageAnimation.HandleClipAction > ClipCreate.Create |
| manage_animation.create_blend_tree_1d | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ControllerBlendTrees.cs:56 | - | case create_blend_tree_1d > ControllerBlendTrees.CreateBlendTree1D |
| manage_animation.create_blend_tree_1d | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ControllerCreate.cs:99 | - | case create_blend_tree_1d > ControllerBlendTrees.CreateBlendTree1D > ControllerCreate.AddState |
| manage_animation.create_blend_tree_1d | write_file | `AssetDatabase.AddObjectToAsset` | Editor/Tools/Animation/ControllerBlendTrees.cs:52 | - | case create_blend_tree_1d > ControllerBlendTrees.CreateBlendTree1D |
| manage_animation.create_blend_tree_1d | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ControllerBlendTrees.cs:22 | - | case create_blend_tree_1d > ControllerBlendTrees.CreateBlendTree1D |
| manage_animation.create_blend_tree_1d | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ControllerCreate.cs:85 | clip_path, clip_path | case create_blend_tree_1d > ControllerBlendTrees.CreateBlendTree1D > ControllerCreate.AddState |
| manage_animation.create_blend_tree_1d | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ControllerCreate.cs:435 | - | case create_blend_tree_1d > … > ControllerCreate.AddState > ControllerCreate.LoadController |
| manage_animation.create_blend_tree_1d | scene_edit | `Undo.RecordObject` | Editor/Tools/Animation/ControllerBlendTrees.cs:42 | - | case create_blend_tree_1d > ControllerBlendTrees.CreateBlendTree1D |
| manage_animation.create_blend_tree_1d | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Animation/ControllerBlendTrees.cs:55 | - | case create_blend_tree_1d > ControllerBlendTrees.CreateBlendTree1D |
| manage_animation.create_blend_tree_1d | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Animation/ControllerCreate.cs:98 | - | case create_blend_tree_1d > ControllerBlendTrees.CreateBlendTree1D > ControllerCreate.AddState |
| manage_animation.create_blend_tree_2d | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ControllerBlendTrees.cs:127 | - | case create_blend_tree_2d > ControllerBlendTrees.CreateBlendTree2D |
| manage_animation.create_blend_tree_2d | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ControllerCreate.cs:99 | - | case create_blend_tree_2d > ControllerBlendTrees.CreateBlendTree2D > ControllerCreate.AddState |
| manage_animation.create_blend_tree_2d | write_file | `AssetDatabase.AddObjectToAsset` | Editor/Tools/Animation/ControllerBlendTrees.cs:123 | - | case create_blend_tree_2d > ControllerBlendTrees.CreateBlendTree2D |
| manage_animation.create_blend_tree_2d | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ControllerBlendTrees.cs:83 | - | case create_blend_tree_2d > ControllerBlendTrees.CreateBlendTree2D |
| manage_animation.create_blend_tree_2d | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ControllerCreate.cs:85 | clip_path, clip_path | case create_blend_tree_2d > ControllerBlendTrees.CreateBlendTree2D > ControllerCreate.AddState |
| manage_animation.create_blend_tree_2d | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ControllerCreate.cs:435 | - | case create_blend_tree_2d > … > ControllerCreate.AddState > ControllerCreate.LoadController |
| manage_animation.create_blend_tree_2d | scene_edit | `Undo.RecordObject` | Editor/Tools/Animation/ControllerBlendTrees.cs:112 | - | case create_blend_tree_2d > ControllerBlendTrees.CreateBlendTree2D |
| manage_animation.create_blend_tree_2d | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Animation/ControllerBlendTrees.cs:126 | - | case create_blend_tree_2d > ControllerBlendTrees.CreateBlendTree2D |
| manage_animation.create_blend_tree_2d | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Animation/ControllerCreate.cs:98 | - | case create_blend_tree_2d > ControllerBlendTrees.CreateBlendTree2D > ControllerCreate.AddState |
| manage_animation.create_preset | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ClipPresets.cs:125 | - | case create_preset > ClipPresets.CreatePreset |
| manage_animation.create_preset | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/Animation/ClipPresets.cs:124 | - | case create_preset > ClipPresets.CreatePreset |
| manage_animation.create_preset | write_file | `AssetDatabase.CreateFolder` | Editor/Tools/Animation/ClipPresets.cs:398 | - | case create_preset > ClipPresets.CreatePreset > ClipPresets.CreateFoldersRecursive |
| manage_animation.create_preset | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case create_preset > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_animation.create_preset | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ClipPresets.cs:60 | - | case create_preset > ClipPresets.CreatePreset |
| manage_animation.create_preset | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case create_preset > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.create_preset | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case create_preset > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.crossfade | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case crossfade > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_animation.crossfade | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case crossfade > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.crossfade | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case crossfade > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.crossfade | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case crossfade > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.crossfade | scene_edit | `Undo.RecordObject` | Editor/Tools/Animation/AnimatorControl.cs:51 | - | case crossfade > AnimatorControl.Crossfade |
| manage_animation.get_info | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ClipCreate.cs:97 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > ManageAnimation.HandleClipAction > ClipCreate.GetInfo |
| manage_animation.get_info | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ControllerCreate.cs:435 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > … > ControllerCreate.GetInfo > ControllerCreate.LoadController |
| manage_animation.get_info | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | ManageAnimation.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.get_parameter | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case get_parameter > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_animation.get_parameter | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case get_parameter > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.get_parameter | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case get_parameter > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.get_parameter | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case get_parameter > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.play | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case play > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_animation.play | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case play > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.play | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case play > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.play | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case play > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.play | scene_edit | `Undo.RecordObject` | Editor/Tools/Animation/AnimatorControl.cs:28 | - | case play > AnimatorControl.Play |
| manage_animation.remove_event | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ClipCreate.cs:604 | - | case remove_event > ClipCreate.RemoveEvent |
| manage_animation.remove_event | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ClipCreate.cs:568 | - | case remove_event > ClipCreate.RemoveEvent |
| manage_animation.remove_event | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Animation/ClipCreate.cs:603 | - | case remove_event > ClipCreate.RemoveEvent |
| manage_animation.remove_layer | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ControllerLayers.cs:118 | - | case remove_layer > ControllerLayers.RemoveLayer |
| manage_animation.remove_layer | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/ManageEditor.cs:383 | - | case remove_layer > ControllerLayers.RemoveLayer > ManageEditor.RemoveLayer |
| manage_animation.remove_layer | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ControllerLayers.cs:74 | - | case remove_layer > ControllerLayers.RemoveLayer |
| manage_animation.remove_layer | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Tools/ManageEditor.cs:447 | - | case remove_layer > … > ManageEditor.RemoveLayer > ManageEditor.GetTagManager |
| manage_animation.remove_layer | set_values | `.ApplyModifiedProperties` | Editor/Tools/ManageEditor.cs:381 | - | case remove_layer > ControllerLayers.RemoveLayer > ManageEditor.RemoveLayer |
| manage_animation.remove_layer | scene_edit | `Undo.RecordObject` | Editor/Tools/Animation/ControllerLayers.cs:114 | - | case remove_layer > ControllerLayers.RemoveLayer |
| manage_animation.remove_layer | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Animation/ControllerLayers.cs:117 | - | case remove_layer > ControllerLayers.RemoveLayer |
| manage_animation.remove_layer | project_settings | `tagManager` | Editor/Tools/ManageEditor.cs:344 | - | case remove_layer > ControllerLayers.RemoveLayer > ManageEditor.RemoveLayer |
| manage_animation.remove_layer | project_settings | `tagManager` | Editor/Tools/ManageEditor.cs:345 | - | case remove_layer > ControllerLayers.RemoveLayer > ManageEditor.RemoveLayer |
| manage_animation.remove_layer | project_settings | `tagManager` | Editor/Tools/ManageEditor.cs:348 | - | case remove_layer > ControllerLayers.RemoveLayer > ManageEditor.RemoveLayer |
| manage_animation.set_curve | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ClipCreate.cs:210 | - | case set_curve > ClipCreate.SetCurve > ClipCreate.SetOrAddCurve |
| manage_animation.set_curve | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case set_curve > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_animation.set_curve | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ClipCreate.cs:166 | - | case set_curve > ClipCreate.SetCurve > ClipCreate.SetOrAddCurve |
| manage_animation.set_curve | scene_edit | `Undo.RecordObject` | Editor/Tools/Animation/ClipCreate.cs:207 | - | case set_curve > ClipCreate.SetCurve > ClipCreate.SetOrAddCurve |
| manage_animation.set_curve | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Animation/ClipCreate.cs:209 | - | case set_curve > ClipCreate.SetCurve > ClipCreate.SetOrAddCurve |
| manage_animation.set_enabled | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case set_enabled > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_animation.set_enabled | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_enabled > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.set_enabled | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_enabled > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.set_enabled | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_enabled > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.set_enabled | scene_edit | `Undo.RecordObject` | Editor/Tools/Animation/AnimatorControl.cs:218 | - | case set_enabled > AnimatorControl.SetEnabled |
| manage_animation.set_layer_weight | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ControllerLayers.cs:186 | - | case set_layer_weight > ControllerLayers.SetLayerWeight |
| manage_animation.set_layer_weight | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ControllerLayers.cs:143 | - | case set_layer_weight > ControllerLayers.SetLayerWeight |
| manage_animation.set_layer_weight | scene_edit | `Undo.RecordObject` | Editor/Tools/Animation/ControllerLayers.cs:179 | - | case set_layer_weight > ControllerLayers.SetLayerWeight |
| manage_animation.set_layer_weight | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Animation/ControllerLayers.cs:185 | - | case set_layer_weight > ControllerLayers.SetLayerWeight |
| manage_animation.set_parameter | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/AnimatorControl.cs:158 | - | case set_parameter > AnimatorControl.SetParameter |
| manage_animation.set_parameter | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/AnimatorControl.cs:167 | - | case set_parameter > AnimatorControl.SetParameter |
| manage_animation.set_parameter | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/AnimatorControl.cs:176 | - | case set_parameter > AnimatorControl.SetParameter |
| manage_animation.set_parameter | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case set_parameter > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_animation.set_parameter | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_parameter > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.set_parameter | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_parameter > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.set_parameter | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_parameter > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.set_parameter | scene_edit | `Undo.RecordObject` | Editor/Tools/Animation/AnimatorControl.cs:149 | - | case set_parameter > AnimatorControl.SetParameter |
| manage_animation.set_parameter | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Animation/AnimatorControl.cs:157 | - | case set_parameter > AnimatorControl.SetParameter |
| manage_animation.set_parameter | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Animation/AnimatorControl.cs:166 | - | case set_parameter > AnimatorControl.SetParameter |
| manage_animation.set_speed | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case set_speed > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_animation.set_speed | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_speed > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.set_speed | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_speed > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.set_speed | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_speed > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_animation.set_speed | scene_edit | `Undo.RecordObject` | Editor/Tools/Animation/AnimatorControl.cs:200 | - | case set_speed > AnimatorControl.SetSpeed |
| manage_animation.set_vector_curve | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Animation/ClipCreate.cs:311 | - | case set_vector_curve > ClipCreate.SetVectorCurve |
| manage_animation.set_vector_curve | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case set_vector_curve > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_animation.set_vector_curve | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Animation/ClipCreate.cs:237 | - | case set_vector_curve > ClipCreate.SetVectorCurve |
| manage_animation.set_vector_curve | scene_edit | `Undo.RecordObject` | Editor/Tools/Animation/ClipCreate.cs:303 | - | case set_vector_curve > ClipCreate.SetVectorCurve |
| manage_animation.set_vector_curve | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Animation/ClipCreate.cs:310 | - | case set_vector_curve > ClipCreate.SetVectorCurve |
| manage_asset.import | write_file | `.EncodeToPNG` | Editor/Tools/ManageAsset.cs:1068 | generate_preview | case import > ManageAsset.ReimportAsset > ManageAsset.GetAssetData |
| manage_asset.import | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageAsset.cs:154 | - | case import > ManageAsset.ReimportAsset |
| manage_asset.import | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageAsset.cs:1041 | - | case import > ManageAsset.ReimportAsset > ManageAsset.GetAssetData |
| manage_asset.import | load_asset | `AssetPreview.GetAssetPreview` | Editor/Tools/ManageAsset.cs:1048 | generate_preview | case import > ManageAsset.ReimportAsset > ManageAsset.GetAssetData |
| manage_asset.import | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageAsset.cs:1080 | generate_preview | case import > ManageAsset.ReimportAsset > ManageAsset.GetAssetData |
| manage_asset.create | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/ManageAsset.cs:267 | - | case create > ManageAsset.CreateAsset |
| manage_asset.create | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/ManageAsset.cs:222 | - | case create > ManageAsset.CreateAsset |
| manage_asset.create | write_file | `.EncodeToPNG` | Editor/Tools/ManageAsset.cs:1068 | generate_preview | case create > ManageAsset.CreateAsset > ManageAsset.GetAssetData |
| manage_asset.create | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/ManageAsset.cs:230 | - | case create > ManageAsset.CreateAsset |
| manage_asset.create | import_compile | `AssetDatabase.Refresh` | Editor/Tools/ManageAsset.cs:184 | - | case create > ManageAsset.CreateAsset |
| manage_asset.create | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | properties | case create > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_asset.create | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageAsset.cs:1041 | - | case create > ManageAsset.CreateAsset > ManageAsset.GetAssetData |
| manage_asset.create | load_asset | `AssetPreview.GetAssetPreview` | Editor/Tools/ManageAsset.cs:1048 | generate_preview | case create > ManageAsset.CreateAsset > ManageAsset.GetAssetData |
| manage_asset.create | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/MaterialOps.cs:122 | properties | case create > ManageAsset.CreateAsset > MaterialOps.ApplyProperties |
| manage_asset.create | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/MaterialOps.cs:305 | properties, path | case create > … > MaterialOps.ApplyProperties > MaterialOps.TrySetShaderProperty |
| manage_asset.create | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/VfxGraphWrite.cs:123 | properties | case create > … > MaterialOps.TrySetShaderProperty > VfxGraphWrite.SetVector |
| manage_asset.create | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/VfxGraphWrite.cs:132 | properties | case create > … > MaterialOps.TrySetShaderProperty > VfxGraphWrite.SetVector |
| manage_asset.create | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/VfxGraphWrite.cs:202 | properties | case create > … > MaterialOps.ApplyProperties > VfxGraphWrite.SetTexture |
| manage_asset.create | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageAsset.cs:1080 | generate_preview | case create > ManageAsset.CreateAsset > ManageAsset.GetAssetData |
| manage_asset.modify | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/ManageAsset.cs:469 | - | case modify > ManageAsset.ModifyAsset |
| manage_asset.modify | write_file | `.EncodeToPNG` | Editor/Tools/ManageAsset.cs:1068 | generate_preview | case modify > ManageAsset.ModifyAsset > ManageAsset.GetAssetData |
| manage_asset.modify | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageAsset.cs:442 | - | case modify > ManageAsset.ModifyAsset |
| manage_asset.modify | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case modify > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_asset.modify | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageAsset.cs:348 | - | case modify > ManageAsset.ModifyAsset |
| manage_asset.modify | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/MaterialOps.cs:305 | path | case modify > … > MaterialOps.ApplyProperties > MaterialOps.TrySetShaderProperty |
| manage_asset.modify | load_asset | `AssetPreview.GetAssetPreview` | Editor/Tools/ManageAsset.cs:1048 | generate_preview | case modify > ManageAsset.ModifyAsset > ManageAsset.GetAssetData |
| manage_asset.modify | set_values | `propInfo.SetValue` | Editor/Tools/ManageAsset.cs:999 | - | case modify > … > ManageAsset.ApplyObjectProperties > ManageAsset.SetPropertyOrField |
| manage_asset.modify | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/ManageAsset.cs:467 | - | case modify > ManageAsset.ModifyAsset |
| manage_asset.modify | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/VfxGraphWrite.cs:123 | - | case modify > … > MaterialOps.TrySetShaderProperty > VfxGraphWrite.SetVector |
| manage_asset.modify | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/VfxGraphWrite.cs:132 | - | case modify > … > MaterialOps.TrySetShaderProperty > VfxGraphWrite.SetVector |
| manage_asset.modify | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageAsset.cs:1080 | generate_preview | case modify > ManageAsset.ModifyAsset > ManageAsset.GetAssetData |
| manage_asset.delete | delete_file | `AssetDatabase.DeleteAsset` | Editor/Tools/ManageAsset.cs:506 | - | case delete > ManageAsset.DeleteAsset |
| manage_asset.duplicate | write_file | `AssetDatabase.CopyAsset` | Editor/Tools/ManageAsset.cs:552 | - | case duplicate > ManageAsset.DuplicateAsset |
| manage_asset.duplicate | write_file | `.EncodeToPNG` | Editor/Tools/ManageAsset.cs:1068 | generate_preview | case duplicate > ManageAsset.DuplicateAsset > ManageAsset.GetAssetData |
| manage_asset.duplicate | import_compile | `AssetDatabase.Refresh` | Editor/Tools/ManageAsset.cs:873 | - | case duplicate > ManageAsset.DuplicateAsset > ManageAsset.EnsureDirectoryExists |
| manage_asset.duplicate | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageAsset.cs:1041 | - | case duplicate > ManageAsset.DuplicateAsset > ManageAsset.GetAssetData |
| manage_asset.duplicate | load_asset | `AssetPreview.GetAssetPreview` | Editor/Tools/ManageAsset.cs:1048 | generate_preview | case duplicate > ManageAsset.DuplicateAsset > ManageAsset.GetAssetData |
| manage_asset.duplicate | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageAsset.cs:1080 | generate_preview | case duplicate > ManageAsset.DuplicateAsset > ManageAsset.GetAssetData |
| manage_asset.move | write_file | `AssetDatabase.MoveAsset` | Editor/Tools/ManageAsset.cs:605 | - | case move > ManageAsset.MoveOrRenameAsset |
| manage_asset.move | write_file | `.EncodeToPNG` | Editor/Tools/ManageAsset.cs:1068 | generate_preview | case move > ManageAsset.MoveOrRenameAsset > ManageAsset.GetAssetData |
| manage_asset.move | import_compile | `AssetDatabase.Refresh` | Editor/Tools/ManageAsset.cs:873 | - | case move > ManageAsset.MoveOrRenameAsset > ManageAsset.EnsureDirectoryExists |
| manage_asset.move | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageAsset.cs:1041 | - | case move > ManageAsset.MoveOrRenameAsset > ManageAsset.GetAssetData |
| manage_asset.move | load_asset | `AssetPreview.GetAssetPreview` | Editor/Tools/ManageAsset.cs:1048 | generate_preview | case move > ManageAsset.MoveOrRenameAsset > ManageAsset.GetAssetData |
| manage_asset.move | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageAsset.cs:1080 | generate_preview | case move > ManageAsset.MoveOrRenameAsset > ManageAsset.GetAssetData |
| manage_asset.rename | write_file | `AssetDatabase.MoveAsset` | Editor/Tools/ManageAsset.cs:605 | - | case rename > ManageAsset.MoveOrRenameAsset |
| manage_asset.rename | write_file | `.EncodeToPNG` | Editor/Tools/ManageAsset.cs:1068 | generate_preview | case rename > ManageAsset.MoveOrRenameAsset > ManageAsset.GetAssetData |
| manage_asset.rename | import_compile | `AssetDatabase.Refresh` | Editor/Tools/ManageAsset.cs:873 | - | case rename > ManageAsset.MoveOrRenameAsset > ManageAsset.EnsureDirectoryExists |
| manage_asset.rename | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageAsset.cs:1041 | - | case rename > ManageAsset.MoveOrRenameAsset > ManageAsset.GetAssetData |
| manage_asset.rename | load_asset | `AssetPreview.GetAssetPreview` | Editor/Tools/ManageAsset.cs:1048 | generate_preview | case rename > ManageAsset.MoveOrRenameAsset > ManageAsset.GetAssetData |
| manage_asset.rename | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageAsset.cs:1080 | generate_preview | case rename > ManageAsset.MoveOrRenameAsset > ManageAsset.GetAssetData |
| manage_asset.search | write_file | `.EncodeToPNG` | Editor/Tools/ManageAsset.cs:1068 | generate_preview | case search > ManageAsset.SearchAssets > ManageAsset.GetAssetData |
| manage_asset.search | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageAsset.cs:1041 | - | case search > ManageAsset.SearchAssets > ManageAsset.GetAssetData |
| manage_asset.search | load_asset | `AssetPreview.GetAssetPreview` | Editor/Tools/ManageAsset.cs:1048 | generate_preview | case search > ManageAsset.SearchAssets > ManageAsset.GetAssetData |
| manage_asset.search | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageAsset.cs:1080 | generate_preview | case search > ManageAsset.SearchAssets > ManageAsset.GetAssetData |
| manage_asset.get_info | write_file | `.EncodeToPNG` | Editor/Tools/ManageAsset.cs:1068 | generate_preview | case get_info > ManageAsset.GetAssetInfo > ManageAsset.GetAssetData |
| manage_asset.get_info | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageAsset.cs:1041 | - | case get_info > ManageAsset.GetAssetInfo > ManageAsset.GetAssetData |
| manage_asset.get_info | load_asset | `AssetPreview.GetAssetPreview` | Editor/Tools/ManageAsset.cs:1048 | generate_preview | case get_info > ManageAsset.GetAssetInfo > ManageAsset.GetAssetData |
| manage_asset.get_info | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageAsset.cs:1080 | generate_preview | case get_info > ManageAsset.GetAssetInfo > ManageAsset.GetAssetData |
| manage_asset.create_folder | write_file | `AssetDatabase.CreateFolder` | Editor/Tools/ManageAsset.cs:315 | - | case create_folder > ManageAsset.CreateFolder |
| manage_asset.create_folder | write_file | `.EncodeToPNG` | Editor/Tools/ManageAsset.cs:1068 | generate_preview | case create_folder > ManageAsset.CreateFolder > ManageAsset.GetAssetData |
| manage_asset.create_folder | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageAsset.cs:1041 | - | case create_folder > ManageAsset.CreateFolder > ManageAsset.GetAssetData |
| manage_asset.create_folder | load_asset | `AssetPreview.GetAssetPreview` | Editor/Tools/ManageAsset.cs:1048 | generate_preview | case create_folder > ManageAsset.CreateFolder > ManageAsset.GetAssetData |
| manage_asset.create_folder | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageAsset.cs:1080 | generate_preview | case create_folder > ManageAsset.CreateFolder > ManageAsset.GetAssetData |
| manage_asset.get_components | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageAsset.cs:773 | - | case get_components > ManageAsset.GetComponentsFromAsset |
| manage_prefabs.create_from_gameobject | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Prefabs/ManagePrefabs.cs:280 | - | case create_from_gameobject > ManagePrefabs.CreatePrefabFromGameObject > ManagePrefabs.CreatePrefabAsset |
| manage_prefabs.create_from_gameobject | write_file | `PrefabUtility.SaveAsPrefabAssetAndConnect` | Editor/Tools/Prefabs/ManagePrefabs.cs:269 | - | case create_from_gameobject > ManagePrefabs.CreatePrefabFromGameObject > ManagePrefabs.CreatePrefabAsset |
| manage_prefabs.create_from_gameobject | import_compile | `AssetDatabase.Refresh` | Editor/Tools/Prefabs/ManagePrefabs.cs:281 | - | case create_from_gameobject > ManagePrefabs.CreatePrefabFromGameObject > ManagePrefabs.CreatePrefabAsset |
| manage_prefabs.create_from_gameobject | import_compile | `AssetDatabase.Refresh` | Editor/Tools/Prefabs/ManagePrefabs.cs:451 | - | case create_from_gameobject > ManagePrefabs.CreatePrefabFromGameObject > ManagePrefabs.EnsureAssetDirectoryExists |
| manage_prefabs.create_from_gameobject | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Prefabs/ManagePrefabs.cs:115 | - | case create_from_gameobject > ManagePrefabs.CreatePrefabFromGameObject |
| manage_prefabs.get_info | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Prefabs/ManagePrefabs.cs:515 | - | case get_info > ManagePrefabs.GetInfo |
| manage_prefabs.get_hierarchy | load_asset | `PrefabUtility.LoadPrefabContents` | Editor/Tools/Prefabs/ManagePrefabs.cs:563 | - | case get_hierarchy > ManagePrefabs.GetHierarchy |
| manage_prefabs.modify_contents | write_file | `PrefabUtility.SaveAsPrefabAsset` | Editor/Tools/Prefabs/ManagePrefabs.cs:655 | - | case modify_contents > ManagePrefabs.ModifyContents |
| manage_prefabs.modify_contents | import_compile | `AssetDatabase.Refresh` | Editor/Tools/Prefabs/ManagePrefabs.cs:662 | - | case modify_contents > ManagePrefabs.ModifyContents |
| manage_prefabs.modify_contents | load_asset | `PrefabUtility.LoadPrefabContents` | Editor/Tools/Prefabs/ManagePrefabs.cs:614 | - | case modify_contents > ManagePrefabs.ModifyContents |
| manage_prefabs.open_prefab_stage | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Prefabs/ManagePrefabs.cs:1308 | - | case open_prefab_stage > ManagePrefabs.OpenPrefabStage |
| manage_prefabs.save_prefab_stage | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Prefabs/ManagePrefabs.cs:1412 | - | case save_prefab_stage > ManagePrefabs.SavePrefabStage > ManagePrefabs.TrySavePrefabStage |
| manage_prefabs.save_prefab_stage | write_file | `PrefabUtility.SaveAsPrefabAsset` | Editor/Tools/Prefabs/ManagePrefabs.cs:1404 | - | case save_prefab_stage > ManagePrefabs.SavePrefabStage > ManagePrefabs.TrySavePrefabStage |
| manage_prefabs.save_prefab_stage | import_compile | `AssetDatabase.Refresh` | Editor/Tools/Prefabs/ManagePrefabs.cs:1413 | - | case save_prefab_stage > ManagePrefabs.SavePrefabStage > ManagePrefabs.TrySavePrefabStage |
| manage_prefabs.close_prefab_stage | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Prefabs/ManagePrefabs.cs:1412 | - | case close_prefab_stage > ManagePrefabs.ClosePrefabStage > ManagePrefabs.TrySavePrefabStage |
| manage_prefabs.close_prefab_stage | write_file | `PrefabUtility.SaveAsPrefabAsset` | Editor/Tools/Prefabs/ManagePrefabs.cs:1404 | - | case close_prefab_stage > ManagePrefabs.ClosePrefabStage > ManagePrefabs.TrySavePrefabStage |
| manage_prefabs.close_prefab_stage | import_compile | `AssetDatabase.Refresh` | Editor/Tools/Prefabs/ManagePrefabs.cs:1413 | - | case close_prefab_stage > ManagePrefabs.ClosePrefabStage > ManagePrefabs.TrySavePrefabStage |
| manage_build.batch | save_scene | `EditorSceneManager.SaveScene` | Editor/Tools/Build/BuildRunner.cs:265 | targets | case batch > … > BuildRunner.RunBuildCore > BuildRunner.SaveBeforeBuild |
| manage_build.batch | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Build/BuildRunner.cs:246 | targets | case batch > … > BuildRunner.RunBuildCore > BuildRunner.SaveBeforeBuild |
| manage_build.batch | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageBuild.cs:500 | profiles | case batch > ManageBuild.HandleBatch |
| manage_build.batch | project_settings | `EditorUserBuildSettings.SwitchActiveBuildTarget` | Editor/Tools/ManageBuild.cs:478 | targets | case batch > ManageBuild.HandleBatch |
| manage_build.batch | build_player | `BuildPipeline.BuildPlayer` | Editor/Tools/Build/BuildRunner.cs:21 | targets | case batch > ManageBuild.HandleBatch > BuildRunner.ScheduleBuild |
| manage_build.batch | build_player | `BuildPipeline.BuildPlayer` | Editor/Tools/Build/BuildRunner.cs:37 | profiles | case batch > ManageBuild.HandleBatch > BuildRunner.ScheduleProfileBuild |
| manage_build.build | save_scene | `EditorSceneManager.SaveScene` | Editor/Tools/Build/BuildRunner.cs:265 | - | case build > … > BuildRunner.RunBuildCore > BuildRunner.SaveBeforeBuild |
| manage_build.build | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Build/BuildRunner.cs:246 | - | case build > … > BuildRunner.RunBuildCore > BuildRunner.SaveBeforeBuild |
| manage_build.build | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageBuild.cs:119 | - | case build > ManageBuild.HandleBuild > ManageBuild.HandleProfileBuild |
| manage_build.build | project_settings | `PlayerSettings.SetScriptingBackend` | Editor/Tools/ManageBuild.cs:93 | scripting_backend | case build > ManageBuild.HandleBuild |
| manage_build.build | build_player | `BuildPipeline.BuildPlayer` | Editor/Tools/Build/BuildRunner.cs:21 | - | case build > ManageBuild.HandleBuild > BuildRunner.ScheduleBuild |
| manage_build.build | build_player | `BuildPipeline.BuildPlayer` | Editor/Tools/Build/BuildRunner.cs:37 | - | case build > … > ManageBuild.HandleProfileBuild > BuildRunner.ScheduleProfileBuild |
| manage_build.cancel | none found | - | - | - | MCPForUnity/Editor/Tools/ManageBuild.cs:47 |
| manage_build.platform | project_settings | `EditorUserBuildSettings.SwitchActiveBuildTarget` | Editor/Tools/ManageBuild.cs:251 | - | case platform > ManageBuild.HandlePlatform |
| manage_build.platform | project_settings | `EditorUserBuildSettings.standaloneBuildSubtarget =` | Editor/Tools/ManageBuild.cs:245 | subtarget | case platform > ManageBuild.HandlePlatform |
| manage_build.platform | project_settings | `EditorUserBuildSettings.standaloneBuildSubtarget =` | Editor/Tools/ManageBuild.cs:247 | subtarget | case platform > ManageBuild.HandlePlatform |
| manage_build.profiles | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageBuild.cs:389 | - | case profiles > ManageBuild.HandleProfiles |
| manage_build.scenes | project_settings | `EditorBuildSettings.scenes =` | Editor/Tools/ManageBuild.cs:356 | - | case scenes > ManageBuild.HandleScenes |
| manage_build.scenes | project_settings | `EditorBuildSettings.scenes =` | Editor/Tools/ManageBuild.cs:328 | - | case scenes > ManageBuild.HandleScenes |
| manage_build.settings | project_settings | `PlayerSettings.productName =` | Editor/Tools/Build/BuildSettingsHelper.cs:43 | - | case settings > ManageBuild.HandleSettings > BuildSettingsHelper.WriteProperty |
| manage_build.settings | project_settings | `PlayerSettings.companyName =` | Editor/Tools/Build/BuildSettingsHelper.cs:46 | - | case settings > ManageBuild.HandleSettings > BuildSettingsHelper.WriteProperty |
| manage_build.settings | project_settings | `PlayerSettings.bundleVersion =` | Editor/Tools/Build/BuildSettingsHelper.cs:49 | - | case settings > ManageBuild.HandleSettings > BuildSettingsHelper.WriteProperty |
| manage_build.status | none found | - | - | - | MCPForUnity/Editor/Tools/ManageBuild.cs:41 |
| manage_camera.add_extension | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case add_extension > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_camera.add_extension | reflection | `Activator.CreateInstance` | Editor/Helpers/PropertyConversion.cs:29 | - | case add_extension > … > ComponentOps.TrySetViaReflection > PropertyConversion.ConvertToType |
| manage_camera.add_extension | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Helpers/ComponentOps.cs:650 | - | case add_extension > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_camera.add_extension | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Helpers/ComponentOps.cs:676 | - | case add_extension > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_camera.add_extension | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ComponentOps.cs:700 | - | case add_extension > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_camera.add_extension | instantiate | `Undo.AddComponent` | Editor/Tools/Cameras/CameraConfigure.cs:316 | - | case add_extension > CameraConfigure.AddExtension |
| manage_camera.add_extension | set_values | `propInfo.SetValue` | Editor/Helpers/ComponentOps.cs:224 | - | case add_extension > … > ComponentOps.SetProperty > ComponentOps.TrySetViaReflection |
| manage_camera.add_extension | set_values | `.ApplyModifiedProperties` | Editor/Helpers/ComponentOps.cs:469 | - | case add_extension > … > ComponentOps.SetProperty > ComponentOps.SetViaSerializedProperty |
| manage_camera.add_extension | set_values | `.ApplyModifiedProperties` | Editor/Helpers/ComponentOps.cs:508 | - | case add_extension > … > ComponentOps.SetViaSerializedProperty > ComponentOps.SetSerializedPropertyRecursive |
| manage_camera.add_extension | scene_edit | `Undo.RecordObject` | Editor/Tools/Cameras/CameraConfigure.cs:401 | - | case add_extension > CameraConfigure.AddExtension > CameraConfigure.SetComponentProperties |
| manage_camera.add_extension | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Cameras/CameraHelpers.cs:262 | - | case add_extension > CameraConfigure.AddExtension > CameraHelpers.MarkDirty |
| manage_camera.add_extension | scene_edit | `EditorSceneManager.MarkSceneDirty` | Editor/Tools/Cameras/CameraHelpers.cs:265 | - | case add_extension > CameraConfigure.AddExtension > CameraHelpers.MarkDirty |
| manage_camera.create_camera | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case create_camera > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_camera.create_camera | instantiate | `.AddComponent` | Editor/Tools/Cameras/CameraCreate.cs:35 | - | case create_camera > CameraCreate.CreateBasicCamera |
| manage_camera.create_camera | instantiate | `.AddComponent` | Editor/Tools/Cameras/CameraCreate.cs:91 | - | case create_camera > CameraCreate.CreateCinemachineCamera |
| manage_camera.create_camera | instantiate | `.AddComponent` | Editor/Tools/Cameras/CameraCreate.cs:118 | - | case create_camera > CameraCreate.CreateCinemachineCamera |
| manage_camera.create_camera | set_values | `.ApplyModifiedProperties` | Editor/Tools/Cameras/CameraCreate.cs:103 | - | case create_camera > CameraCreate.CreateCinemachineCamera |
| manage_camera.create_camera | set_values | `prop.SetValue` | Editor/Tools/Cameras/CameraHelpers.cs:199 | - | case create_camera > CameraCreate.CreateCinemachineCamera > CameraHelpers.SetReflectionProperty |
| manage_camera.create_camera | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Cameras/CameraHelpers.cs:262 | - | case create_camera > CameraCreate.CreateCinemachineCamera > CameraHelpers.MarkDirty |
| manage_camera.create_camera | scene_edit | `.position =` | Editor/Tools/Cameras/CameraCreate.cs:46 | target | case create_camera > CameraCreate.CreateBasicCamera |
| manage_camera.create_camera | scene_edit | `EditorSceneManager.MarkSceneDirty` | Editor/Tools/Cameras/CameraHelpers.cs:265 | - | case create_camera > CameraCreate.CreateCinemachineCamera > CameraHelpers.MarkDirty |
| manage_camera.ensure_brain | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case ensure_brain > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_camera.ensure_brain | instantiate | `.AddComponent` | Editor/Tools/Cameras/CameraCreate.cs:201 | - | case ensure_brain > CameraCreate.EnsureBrain |
| manage_camera.ensure_brain | set_values | `.ApplyModifiedProperties` | Editor/Tools/Cameras/CameraCreate.cs:233 | - | case ensure_brain > CameraCreate.EnsureBrain |
| manage_camera.ensure_brain | scene_edit | `Undo.RecordObject` | Editor/Tools/Cameras/CameraCreate.cs:200 | - | case ensure_brain > CameraCreate.EnsureBrain |
| manage_camera.ensure_brain | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Cameras/CameraHelpers.cs:262 | - | case ensure_brain > CameraCreate.EnsureBrain > CameraHelpers.MarkDirty |
| manage_camera.ensure_brain | scene_edit | `EditorSceneManager.MarkSceneDirty` | Editor/Tools/Cameras/CameraHelpers.cs:265 | - | case ensure_brain > CameraCreate.EnsureBrain > CameraHelpers.MarkDirty |
| manage_camera.force_camera | reflection | `method.Invoke` | Editor/Tools/Cameras/CameraControl.cs:251 | - | case force_camera > CameraControl.ForceCamera |
| manage_camera.force_camera | set_values | `prop.SetValue` | Editor/Tools/Cameras/CameraHelpers.cs:199 | - | case force_camera > CameraControl.ForceCamera > CameraHelpers.SetReflectionProperty |
| manage_camera.get_brain_status | none found | - | - | - | MCPForUnity/Editor/Tools/Cameras/ManageCamera.cs:91 |
| manage_camera.list_cameras | reflection | `method.Invoke` | Editor/Tools/Cameras/CameraHelpers.cs:243 | - | case list_cameras > CameraControl.ListCameras > CameraHelpers.GetPipelineComponent |
| manage_camera.ping | none found | - | - | - | MCPForUnity/Editor/Tools/Cameras/ManageCamera.cs:26 |
| manage_camera.release_override | reflection | `method.Invoke` | Editor/Tools/Cameras/CameraControl.cs:300 | - | case release_override > CameraControl.ReleaseOverride |
| manage_camera.remove_extension | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case remove_extension > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_camera.remove_extension | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Cameras/CameraHelpers.cs:262 | - | case remove_extension > CameraConfigure.RemoveExtension > CameraHelpers.MarkDirty |
| manage_camera.remove_extension | scene_edit | `EditorSceneManager.MarkSceneDirty` | Editor/Tools/Cameras/CameraHelpers.cs:265 | - | case remove_extension > CameraConfigure.RemoveExtension > CameraHelpers.MarkDirty |
| manage_camera.remove_extension | scene_edit | `EditorSceneManager.MarkSceneDirty` | Editor/Tools/Cameras/CameraHelpers.cs:267 | - | case remove_extension > CameraConfigure.RemoveExtension > CameraHelpers.MarkDirty |
| manage_camera.remove_extension | destroy_object | `Undo.DestroyObjectImmediate` | Editor/Tools/Cameras/CameraConfigure.cs:348 | - | case remove_extension > CameraConfigure.RemoveExtension |
| manage_camera.screenshot | write_file | `ScreenCapture.CaptureScreenshot` | Runtime/Helpers/ScreenshotUtility.cs:82 | - | case screenshot > … > ManageScene.CaptureScreenshot > ScreenshotUtility.CaptureToProjectFolder |
| manage_camera.screenshot | write_file | `.EncodeToPNG` | Editor/Helpers/EditorWindowScreenshotUtility.cs:74 | capture_source | case screenshot > … > ManageScene.CaptureSceneViewScreenshot > EditorWindowScreenshotUtility.CaptureSceneViewViewportToProject |
| manage_camera.screenshot | write_file | `.EncodeToPNG` | Runtime/Helpers/ScreenshotUtility.cs:252 | include_image | case screenshot > … > ManageScene.CaptureScreenshot > ScreenshotUtility.CaptureComposited |
| manage_camera.screenshot | write_file | `.EncodeToPNG` | Editor/Helpers/EditorWindowScreenshotUtility.cs:87 | capture_source, include_image | case screenshot > … > ManageScene.CaptureSceneViewScreenshot > EditorWindowScreenshotUtility.CaptureSceneViewViewportToProject |
| manage_camera.screenshot | write_file | `.EncodeToPNG` | Runtime/Helpers/ScreenshotUtility.cs:261 | include_image, include_image | case screenshot > … > ManageScene.CaptureScreenshot > ScreenshotUtility.CaptureComposited |
| manage_camera.screenshot | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageScene.cs:1241 | - | case screenshot > … > ManageScene.CaptureScreenshot > ManageScene.CapturePositionedScreenshot |
| manage_camera.screenshot | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageScene.cs:622 | include_image | case screenshot > ManageScene.HandleCommand > ManageScene.CaptureScreenshot |
| manage_camera.screenshot | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageScene.cs:810 | capture_source | case screenshot > … > ManageScene.CaptureScreenshot > ManageScene.CaptureSceneViewScreenshot |
| manage_camera.screenshot | menu_item | `EditorApplication.ExecuteMenuItem` | Editor/Tools/ManageScene.cs:1506 | - | case screenshot > … > ManageScene.CaptureScreenshot > ManageScene.EnsureGameView |
| manage_camera.screenshot | menu_item | `EditorApplication.ExecuteMenuItem` | Editor/Tools/ManageScene.cs:1509 | - | case screenshot > … > ManageScene.CaptureScreenshot > ManageScene.EnsureGameView |
| manage_camera.screenshot | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case screenshot > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_camera.screenshot | reflection | `method.Invoke` | Editor/Helpers/EditorWindowScreenshotUtility.cs:289 | capture_source | case screenshot > … > EditorWindowScreenshotUtility.FocusAndRepaint > EditorWindowScreenshotUtility.InvokeMethodIfExists |
| manage_camera.screenshot | instantiate | `.AddComponent` | Editor/Tools/ManageScene.cs:1185 | - | case screenshot > … > ManageScene.CaptureScreenshot > ManageScene.CapturePositionedScreenshot |
| manage_camera.screenshot | instantiate | `.AddComponent` | Runtime/Helpers/ScreenshotUtility.cs:777 | include_image | case screenshot > … > ScreenshotUtility.CaptureCompositedAfterFrame > ScreenshotCapturer.Begin |
| manage_camera.screenshot | instantiate | `.AddComponent` | Editor/Tools/ManageScene.cs:1051 | - | case screenshot > … > ManageScene.CaptureScreenshot > ManageScene.CaptureOrbitBatch |
| manage_camera.screenshot | scene_edit | `.position =` | Editor/Tools/ManageScene.cs:1190 | - | case screenshot > … > ManageScene.CaptureScreenshot > ManageScene.CapturePositionedScreenshot |
| manage_camera.screenshot | scene_edit | `.position =` | Editor/Tools/ManageScene.cs:1081 | - | case screenshot > … > ManageScene.CaptureScreenshot > ManageScene.CaptureOrbitBatch |
| manage_camera.screenshot | scene_edit | `.rotation =` | Editor/Tools/ManageScene.cs:1195 | - | case screenshot > … > ManageScene.CaptureScreenshot > ManageScene.CapturePositionedScreenshot |
| manage_camera.screenshot | destroy_object | `Object.DestroyImmediate` | Editor/Helpers/EditorWindowScreenshotUtility.cs:424 | capture_source | case screenshot > … > EditorWindowScreenshotUtility.CaptureSceneViewViewportToProject > EditorWindowScreenshotUtility.DestroyTexture |
| manage_camera.screenshot | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageScene.cs:1263 | - | case screenshot > … > ManageScene.CaptureScreenshot > ManageScene.CapturePositionedScreenshot |
| manage_camera.screenshot | destroy_object | `Object.DestroyImmediate` | Editor/Helpers/EditorWindowScreenshotUtility.cs:234 | capture_source | case screenshot > … > EditorWindowScreenshotUtility.CaptureSceneViewViewportToProject > EditorWindowScreenshotUtility.CaptureViewRect |
| manage_camera.screenshot_multiview | none found | - | - | - | MCPForUnity/Editor/Tools/Cameras/ManageCamera.cs:64 |
| manage_camera.set_aim | reflection | `method.Invoke` | Editor/Tools/Cameras/CameraHelpers.cs:243 | - | case set_aim > CameraConfigure.SetAim > CameraHelpers.GetPipelineComponent |
| manage_camera.set_aim | reflection | `Activator.CreateInstance` | Editor/Helpers/PropertyConversion.cs:29 | - | case set_aim > … > ComponentOps.TrySetViaReflection > PropertyConversion.ConvertToType |
| manage_camera.set_aim | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case set_aim > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_camera.set_aim | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Helpers/ComponentOps.cs:650 | - | case set_aim > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_camera.set_aim | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Helpers/ComponentOps.cs:676 | - | case set_aim > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_camera.set_aim | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ComponentOps.cs:700 | - | case set_aim > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_camera.set_aim | instantiate | `Undo.AddComponent` | Editor/Tools/Cameras/CameraConfigure.cs:389 | - | case set_aim > CameraConfigure.SetAim > CameraConfigure.SwapPipelineComponent |
| manage_camera.set_aim | set_values | `propInfo.SetValue` | Editor/Helpers/ComponentOps.cs:224 | - | case set_aim > … > ComponentOps.SetProperty > ComponentOps.TrySetViaReflection |
| manage_camera.set_aim | set_values | `.ApplyModifiedProperties` | Editor/Helpers/ComponentOps.cs:469 | - | case set_aim > … > ComponentOps.SetProperty > ComponentOps.SetViaSerializedProperty |
| manage_camera.set_aim | set_values | `.ApplyModifiedProperties` | Editor/Helpers/ComponentOps.cs:508 | - | case set_aim > … > ComponentOps.SetViaSerializedProperty > ComponentOps.SetSerializedPropertyRecursive |
| manage_camera.set_aim | scene_edit | `Undo.RecordObject` | Editor/Tools/Cameras/CameraConfigure.cs:401 | - | case set_aim > CameraConfigure.SetAim > CameraConfigure.SetComponentProperties |
| manage_camera.set_aim | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Cameras/CameraHelpers.cs:262 | - | case set_aim > CameraConfigure.SetAim > CameraHelpers.MarkDirty |
| manage_camera.set_aim | scene_edit | `EditorSceneManager.MarkSceneDirty` | Editor/Tools/Cameras/CameraHelpers.cs:265 | - | case set_aim > CameraConfigure.SetAim > CameraHelpers.MarkDirty |
| manage_camera.set_aim | destroy_object | `Undo.DestroyObjectImmediate` | Editor/Tools/Cameras/CameraConfigure.cs:383 | - | case set_aim > CameraConfigure.SetAim > CameraConfigure.SwapPipelineComponent |
| manage_camera.set_blend | set_values | `.ApplyModifiedProperties` | Editor/Tools/Cameras/CameraControl.cs:206 | - | case set_blend > CameraControl.SetBlend |
| manage_camera.set_blend | scene_edit | `Undo.RecordObject` | Editor/Tools/Cameras/CameraControl.cs:175 | - | case set_blend > CameraControl.SetBlend |
| manage_camera.set_blend | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Cameras/CameraHelpers.cs:262 | - | case set_blend > CameraControl.SetBlend > CameraHelpers.MarkDirty |
| manage_camera.set_blend | scene_edit | `EditorSceneManager.MarkSceneDirty` | Editor/Tools/Cameras/CameraHelpers.cs:265 | - | case set_blend > CameraControl.SetBlend > CameraHelpers.MarkDirty |
| manage_camera.set_body | reflection | `method.Invoke` | Editor/Tools/Cameras/CameraHelpers.cs:243 | - | case set_body > CameraConfigure.SetBody > CameraHelpers.GetPipelineComponent |
| manage_camera.set_body | reflection | `Activator.CreateInstance` | Editor/Helpers/PropertyConversion.cs:29 | - | case set_body > … > ComponentOps.TrySetViaReflection > PropertyConversion.ConvertToType |
| manage_camera.set_body | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case set_body > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_camera.set_body | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Helpers/ComponentOps.cs:650 | - | case set_body > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_camera.set_body | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Helpers/ComponentOps.cs:676 | - | case set_body > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_camera.set_body | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ComponentOps.cs:700 | - | case set_body > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_camera.set_body | instantiate | `Undo.AddComponent` | Editor/Tools/Cameras/CameraConfigure.cs:389 | - | case set_body > CameraConfigure.SetBody > CameraConfigure.SwapPipelineComponent |
| manage_camera.set_body | set_values | `propInfo.SetValue` | Editor/Helpers/ComponentOps.cs:224 | - | case set_body > … > ComponentOps.SetProperty > ComponentOps.TrySetViaReflection |
| manage_camera.set_body | set_values | `.ApplyModifiedProperties` | Editor/Helpers/ComponentOps.cs:469 | - | case set_body > … > ComponentOps.SetProperty > ComponentOps.SetViaSerializedProperty |
| manage_camera.set_body | set_values | `.ApplyModifiedProperties` | Editor/Helpers/ComponentOps.cs:508 | - | case set_body > … > ComponentOps.SetViaSerializedProperty > ComponentOps.SetSerializedPropertyRecursive |
| manage_camera.set_body | scene_edit | `Undo.RecordObject` | Editor/Tools/Cameras/CameraConfigure.cs:401 | - | case set_body > CameraConfigure.SetBody > CameraConfigure.SetComponentProperties |
| manage_camera.set_body | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Cameras/CameraHelpers.cs:262 | - | case set_body > CameraConfigure.SetBody > CameraHelpers.MarkDirty |
| manage_camera.set_body | scene_edit | `EditorSceneManager.MarkSceneDirty` | Editor/Tools/Cameras/CameraHelpers.cs:265 | - | case set_body > CameraConfigure.SetBody > CameraHelpers.MarkDirty |
| manage_camera.set_body | destroy_object | `Undo.DestroyObjectImmediate` | Editor/Tools/Cameras/CameraConfigure.cs:383 | - | case set_body > CameraConfigure.SetBody > CameraConfigure.SwapPipelineComponent |
| manage_camera.set_lens | set_values | `.ApplyModifiedProperties` | Editor/Tools/Cameras/CameraConfigure.cs:144 | - | case set_lens > CameraConfigure.SetCinemachineLens |
| manage_camera.set_lens | scene_edit | `Undo.RecordObject` | Editor/Tools/Cameras/CameraConfigure.cs:130 | - | case set_lens > CameraConfigure.SetCinemachineLens |
| manage_camera.set_lens | scene_edit | `Undo.RecordObject` | Editor/Tools/Cameras/CameraConfigure.cs:53 | - | case set_lens > CameraConfigure.SetBasicCameraLens |
| manage_camera.set_lens | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Cameras/CameraHelpers.cs:262 | - | case set_lens > CameraConfigure.SetCinemachineLens > CameraHelpers.MarkDirty |
| manage_camera.set_noise | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case set_noise > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_camera.set_noise | reflection | `Activator.CreateInstance` | Editor/Helpers/PropertyConversion.cs:29 | - | case set_noise > … > ComponentOps.TrySetViaReflection > PropertyConversion.ConvertToType |
| manage_camera.set_noise | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Helpers/ComponentOps.cs:650 | - | case set_noise > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_camera.set_noise | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Helpers/ComponentOps.cs:676 | - | case set_noise > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_camera.set_noise | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ComponentOps.cs:700 | - | case set_noise > … > ComponentOps.SetSerializedPropertyRecursive > ComponentOps.SetObjectReference |
| manage_camera.set_noise | instantiate | `Undo.AddComponent` | Editor/Tools/Cameras/CameraConfigure.cs:278 | - | case set_noise > CameraConfigure.SetNoise |
| manage_camera.set_noise | set_values | `propInfo.SetValue` | Editor/Helpers/ComponentOps.cs:224 | - | case set_noise > … > ComponentOps.SetProperty > ComponentOps.TrySetViaReflection |
| manage_camera.set_noise | set_values | `.ApplyModifiedProperties` | Editor/Helpers/ComponentOps.cs:469 | - | case set_noise > … > ComponentOps.SetProperty > ComponentOps.SetViaSerializedProperty |
| manage_camera.set_noise | set_values | `.ApplyModifiedProperties` | Editor/Helpers/ComponentOps.cs:508 | - | case set_noise > … > ComponentOps.SetViaSerializedProperty > ComponentOps.SetSerializedPropertyRecursive |
| manage_camera.set_noise | scene_edit | `Undo.RecordObject` | Editor/Tools/Cameras/CameraConfigure.cs:282 | - | case set_noise > CameraConfigure.SetNoise |
| manage_camera.set_noise | scene_edit | `Undo.RecordObject` | Editor/Tools/Cameras/CameraConfigure.cs:401 | - | case set_noise > CameraConfigure.SetNoise > CameraConfigure.SetComponentProperties |
| manage_camera.set_noise | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Cameras/CameraHelpers.cs:262 | - | case set_noise > CameraConfigure.SetNoise > CameraHelpers.MarkDirty |
| manage_camera.set_priority | set_values | `.ApplyModifiedProperties` | Editor/Tools/Cameras/CameraConfigure.cs:172 | - | case set_priority > CameraConfigure.SetCinemachinePriority |
| manage_camera.set_priority | set_values | `prop.SetValue` | Editor/Tools/Cameras/CameraHelpers.cs:199 | - | case set_priority > CameraConfigure.SetCinemachinePriority > CameraHelpers.SetReflectionProperty |
| manage_camera.set_priority | scene_edit | `Undo.RecordObject` | Editor/Tools/Cameras/CameraConfigure.cs:84 | - | case set_priority > CameraConfigure.SetBasicCameraPriority |
| manage_camera.set_priority | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Cameras/CameraHelpers.cs:262 | - | case set_priority > CameraConfigure.SetCinemachinePriority > CameraHelpers.MarkDirty |
| manage_camera.set_priority | scene_edit | `Undo.RecordObject` | Editor/Tools/Cameras/CameraConfigure.cs:176 | - | case set_priority > CameraConfigure.SetCinemachinePriority |
| manage_camera.set_target | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case set_target > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_camera.set_target | set_values | `prop.SetValue` | Editor/Tools/Cameras/CameraHelpers.cs:199 | - | case set_target > … > CameraHelpers.SetTransformTarget > CameraHelpers.SetReflectionProperty |
| manage_camera.set_target | scene_edit | `Undo.RecordObject` | Editor/Tools/Cameras/CameraConfigure.cs:107 | - | case set_target > CameraConfigure.SetCinemachineTarget |
| manage_camera.set_target | scene_edit | `Undo.RecordObject` | Editor/Tools/Cameras/CameraConfigure.cs:32 | - | case set_target > CameraConfigure.SetBasicCameraTarget |
| manage_camera.set_target | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Cameras/CameraHelpers.cs:262 | - | case set_target > CameraConfigure.SetCinemachineTarget > CameraHelpers.MarkDirty |
| manage_material.ping | none found | - | - | - | MCPForUnity/Editor/Tools/ManageMaterial.cs:27 |
| manage_material.create | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/ManageMaterial.cs:705 | - | case create > ManageMaterial.CreateMaterial |
| manage_material.create | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/ManageMaterial.cs:696 | - | case create > ManageMaterial.CreateMaterial |
| manage_material.create | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | properties | case create > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_material.create | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageMaterial.cs:627 | - | case create > ManageMaterial.CreateMaterial |
| manage_material.create | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/MaterialOps.cs:122 | properties | case create > ManageMaterial.CreateMaterial > MaterialOps.ApplyProperties |
| manage_material.create | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/MaterialOps.cs:305 | properties | case create > … > MaterialOps.ApplyProperties > MaterialOps.TrySetShaderProperty |
| manage_material.create | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/ManageMaterial.cs:704 | - | case create > ManageMaterial.CreateMaterial |
| manage_material.create | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/VfxGraphWrite.cs:123 | properties | case create > … > MaterialOps.TrySetShaderProperty > VfxGraphWrite.SetVector |
| manage_material.create | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/VfxGraphWrite.cs:132 | properties | case create > … > MaterialOps.TrySetShaderProperty > VfxGraphWrite.SetVector |
| manage_material.create | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageMaterial.cs:713 | - | case create > ManageMaterial.CreateMaterial |
| manage_material.set_material_shader_property | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case set_material_shader_property > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_material.set_material_shader_property | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_material_shader_property > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_material.set_material_shader_property | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_material_shader_property > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_material.set_material_shader_property | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/MaterialOps.cs:305 | - | case set_material_shader_property > ManageMaterial.SetMaterialShaderProperty > MaterialOps.TrySetShaderProperty |
| manage_material.set_material_shader_property | scene_edit | `Undo.RecordObject` | Editor/Tools/ManageMaterial.cs:94 | - | case set_material_shader_property > ManageMaterial.SetMaterialShaderProperty |
| manage_material.set_material_shader_property | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/ManageMaterial.cs:120 | - | case set_material_shader_property > ManageMaterial.SetMaterialShaderProperty |
| manage_material.set_material_shader_property | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/ManageMaterial.cs:109 | - | case set_material_shader_property > ManageMaterial.SetMaterialShaderProperty |
| manage_material.set_material_color | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case set_material_color > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_material.set_material_color | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_material_color > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_material.set_material_color | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_material_color > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_material.set_material_color | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_material_color > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_material.set_material_color | scene_edit | `Undo.RecordObject` | Editor/Tools/ManageMaterial.cs:158 | - | case set_material_color > ManageMaterial.SetMaterialColor |
| manage_material.set_material_color | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/ManageMaterial.cs:188 | - | case set_material_color > ManageMaterial.SetMaterialColor |
| manage_material.assign_material_to_renderer | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case assign_material_to_renderer > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_material.assign_material_to_renderer | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case assign_material_to_renderer > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_material.assign_material_to_renderer | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case assign_material_to_renderer > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_material.assign_material_to_renderer | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case assign_material_to_renderer > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_material.assign_material_to_renderer | scene_edit | `Undo.RecordObject` | Editor/Tools/ManageMaterial.cs:231 | - | case assign_material_to_renderer > ManageMaterial.AssignMaterialToRenderer |
| manage_material.assign_material_to_renderer | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/ManageMaterial.cs:242 | - | case assign_material_to_renderer > ManageMaterial.AssignMaterialToRenderer |
| manage_material.set_renderer_color | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/ManageMaterial.cs:452 | mode | case set_renderer_color > ManageMaterial.SetRendererColor > ManageMaterial.CreateUniqueAndAssign |
| manage_material.set_renderer_color | write_file | `AssetDatabase.CreateFolder` | Editor/Tools/ManageMaterial.cs:382 | mode | case set_renderer_color > … > ManageMaterial.CreateUniqueAndAssign > ManageMaterial.EnsureAssetFolderExists |
| manage_material.set_renderer_color | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/ManageMaterial.cs:449 | mode | case set_renderer_color > ManageMaterial.SetRendererColor > ManageMaterial.CreateUniqueAndAssign |
| manage_material.set_renderer_color | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case set_renderer_color > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_material.set_renderer_color | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_renderer_color > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_material.set_renderer_color | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageMaterial.cs:431 | mode | case set_renderer_color > ManageMaterial.SetRendererColor > ManageMaterial.CreateUniqueAndAssign |
| manage_material.set_renderer_color | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_renderer_color > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_material.set_renderer_color | scene_edit | `Undo.RecordObject` | Editor/Helpers/RendererHelpers.cs:61 | - | case set_renderer_color > ManageMaterial.SetRendererColor > RendererHelpers.EnsureMaterial |
| manage_material.set_renderer_color | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/ManageMaterial.cs:328 | mode | case set_renderer_color > ManageMaterial.SetRendererColor |
| manage_material.set_renderer_color | scene_edit | `Undo.RecordObject` | Editor/Tools/ManageMaterial.cs:455 | mode | case set_renderer_color > ManageMaterial.SetRendererColor > ManageMaterial.CreateUniqueAndAssign |
| manage_material.set_renderer_color | scene_edit | `Undo.RecordObject` | Editor/Tools/ManageMaterial.cs:340 | mode | case set_renderer_color > ManageMaterial.SetRendererColor |
| manage_material.set_renderer_color | scene_edit | `Undo.RecordObject` | Editor/Tools/ManageMaterial.cs:357 | mode | case set_renderer_color > ManageMaterial.SetRendererColor |
| manage_material.get_material_info | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case get_material_info > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_material.get_material_info | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case get_material_info > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_material.get_material_info | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case get_material_info > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_material.get_material_info | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case get_material_info > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_shader.create | write_file | `File.WriteAllText` | Editor/Tools/ManageShader.cs:180 | - | ManageShader.HandleCommand (action not resolved: every action's effects) > ManageShader.CreateShader |
| manage_shader.create | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageShader.cs:181 | - | ManageShader.HandleCommand (action not resolved: every action's effects) > ManageShader.CreateShader |
| manage_shader.create | import_compile | `AssetDatabase.Refresh` | Editor/Tools/ManageShader.cs:182 | - | ManageShader.HandleCommand (action not resolved: every action's effects) > ManageShader.CreateShader |
| manage_shader.create | import_compile | `AssetDatabase.Refresh` | Editor/Tools/ManageShader.cs:102 | - | ManageShader.HandleCommand (action not resolved: every action's effects) |
| manage_shader.read | none found | - | - | - | MCPForUnity/Editor/Tools/ManageShader.cs:118 |
| manage_shader.update | write_file | `File.WriteAllText` | Editor/Tools/ManageShader.cs:248 | - | ManageShader.HandleCommand (action not resolved: every action's effects) > ManageShader.UpdateShader |
| manage_shader.update | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageShader.cs:249 | - | ManageShader.HandleCommand (action not resolved: every action's effects) > ManageShader.UpdateShader |
| manage_shader.update | import_compile | `AssetDatabase.Refresh` | Editor/Tools/ManageShader.cs:250 | - | ManageShader.HandleCommand (action not resolved: every action's effects) > ManageShader.UpdateShader |
| manage_shader.update | import_compile | `AssetDatabase.Refresh` | Editor/Tools/ManageShader.cs:102 | - | ManageShader.HandleCommand (action not resolved: every action's effects) |
| manage_shader.delete | delete_file | `AssetDatabase.DeleteAsset` | Editor/Tools/ManageShader.cs:272 | - | case delete > ManageShader.DeleteShader |
| manage_shader.delete | delete_file | `File.Delete` | Editor/Tools/ManageShader.cs:281 | - | case delete > ManageShader.DeleteShader |
| manage_texture.create | write_file | `.EncodeToPNG` | Editor/Helpers/TextureOps.cs:26 | - | case create > ManageTexture.CreateTexture > TextureOps.EncodeTexture |
| manage_texture.create | write_file | `.EncodeToPNG` | Editor/Helpers/TextureOps.cs:32 | - | case create > ManageTexture.CreateTexture > TextureOps.EncodeTexture |
| manage_texture.create | write_file | `File.WriteAllBytes` | Editor/Tools/ManageTexture.cs:205 | - | case create > ManageTexture.CreateTexture |
| manage_texture.create | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageTexture.cs:207 | - | case create > ManageTexture.CreateTexture |
| manage_texture.create | import_compile | `AssetDatabase.Refresh` | Editor/Tools/ManageTexture.cs:1109 | - | case create > ManageTexture.CreateTexture > ManageTexture.EnsureDirectoryExists |
| manage_texture.create | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageTexture.cs:224 | - | case create > ManageTexture.CreateTexture |
| manage_texture.create | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageTexture.cs:202 | - | case create > ManageTexture.CreateTexture |
| manage_texture.create | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageTexture.cs:151 | - | case create > ManageTexture.CreateTexture |
| manage_texture.modify | write_file | `.EncodeToPNG` | Editor/Helpers/TextureOps.cs:26 | - | case modify > ManageTexture.ModifyTexture > TextureOps.EncodeTexture |
| manage_texture.modify | write_file | `File.WriteAllBytes` | Editor/Tools/ManageTexture.cs:338 | set_pixels | case modify > ManageTexture.ModifyTexture |
| manage_texture.modify | write_file | `.EncodeToPNG` | Editor/Helpers/TextureOps.cs:32 | - | case modify > ManageTexture.ModifyTexture > TextureOps.EncodeTexture |
| manage_texture.modify | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageTexture.cs:339 | set_pixels | case modify > ManageTexture.ModifyTexture |
| manage_texture.modify | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageTexture.cs:281 | set_pixels | case modify > ManageTexture.ModifyTexture |
| manage_texture.modify | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageTexture.cs:340 | set_pixels | case modify > ManageTexture.ModifyTexture |
| manage_texture.modify | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageTexture.cs:297 | set_pixels | case modify > ManageTexture.ModifyTexture |
| manage_texture.modify | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageTexture.cs:326 | set_pixels | case modify > ManageTexture.ModifyTexture |
| manage_texture.delete | delete_file | `AssetDatabase.DeleteAsset` | Editor/Tools/ManageTexture.cs:368 | - | case delete > ManageTexture.DeleteTexture |
| manage_texture.create_sprite | write_file | `.EncodeToPNG` | Editor/Helpers/TextureOps.cs:26 | - | ManageTexture.HandleCommand (action not resolved: every action's effects) > ManageTexture.CreateTexture > TextureOps.EncodeTexture |
| manage_texture.create_sprite | write_file | `.EncodeToPNG` | Editor/Helpers/TextureOps.cs:32 | - | ManageTexture.HandleCommand (action not resolved: every action's effects) > ManageTexture.CreateTexture > TextureOps.EncodeTexture |
| manage_texture.create_sprite | write_file | `File.WriteAllBytes` | Editor/Tools/ManageTexture.cs:205 | - | ManageTexture.HandleCommand (action not resolved: every action's effects) > ManageTexture.CreateTexture |
| manage_texture.create_sprite | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageTexture.cs:207 | - | ManageTexture.HandleCommand (action not resolved: every action's effects) > ManageTexture.CreateTexture |
| manage_texture.create_sprite | import_compile | `AssetDatabase.Refresh` | Editor/Tools/ManageTexture.cs:1109 | - | ManageTexture.HandleCommand (action not resolved: every action's effects) > ManageTexture.CreateTexture > ManageTexture.EnsureDirectoryExists |
| manage_texture.create_sprite | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageTexture.cs:224 | - | ManageTexture.HandleCommand (action not resolved: every action's effects) > ManageTexture.CreateTexture |
| manage_texture.create_sprite | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageTexture.cs:202 | - | ManageTexture.HandleCommand (action not resolved: every action's effects) > ManageTexture.CreateTexture |
| manage_texture.create_sprite | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageTexture.cs:151 | - | ManageTexture.HandleCommand (action not resolved: every action's effects) > ManageTexture.CreateTexture |
| manage_texture.apply_pattern | write_file | `.EncodeToPNG` | Editor/Helpers/TextureOps.cs:26 | - | case apply_pattern > … > ManageTexture.CreateTexture > TextureOps.EncodeTexture |
| manage_texture.apply_pattern | write_file | `.EncodeToPNG` | Editor/Helpers/TextureOps.cs:32 | - | case apply_pattern > … > ManageTexture.CreateTexture > TextureOps.EncodeTexture |
| manage_texture.apply_pattern | write_file | `File.WriteAllBytes` | Editor/Tools/ManageTexture.cs:205 | - | case apply_pattern > ManageTexture.ApplyPattern > ManageTexture.CreateTexture |
| manage_texture.apply_pattern | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageTexture.cs:207 | - | case apply_pattern > ManageTexture.ApplyPattern > ManageTexture.CreateTexture |
| manage_texture.apply_pattern | import_compile | `AssetDatabase.Refresh` | Editor/Tools/ManageTexture.cs:1109 | - | case apply_pattern > … > ManageTexture.CreateTexture > ManageTexture.EnsureDirectoryExists |
| manage_texture.apply_pattern | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageTexture.cs:224 | - | case apply_pattern > ManageTexture.ApplyPattern > ManageTexture.CreateTexture |
| manage_texture.apply_pattern | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageTexture.cs:202 | - | case apply_pattern > ManageTexture.ApplyPattern > ManageTexture.CreateTexture |
| manage_texture.apply_pattern | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageTexture.cs:151 | - | case apply_pattern > ManageTexture.ApplyPattern > ManageTexture.CreateTexture |
| manage_texture.apply_gradient | write_file | `.EncodeToPNG` | Editor/Helpers/TextureOps.cs:26 | - | case apply_gradient > ManageTexture.ApplyGradient > TextureOps.EncodeTexture |
| manage_texture.apply_gradient | write_file | `.EncodeToPNG` | Editor/Helpers/TextureOps.cs:32 | - | case apply_gradient > ManageTexture.ApplyGradient > TextureOps.EncodeTexture |
| manage_texture.apply_gradient | write_file | `File.WriteAllBytes` | Editor/Tools/ManageTexture.cs:432 | - | case apply_gradient > ManageTexture.ApplyGradient |
| manage_texture.apply_gradient | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageTexture.cs:434 | - | case apply_gradient > ManageTexture.ApplyGradient |
| manage_texture.apply_gradient | import_compile | `AssetDatabase.Refresh` | Editor/Tools/ManageTexture.cs:1109 | - | case apply_gradient > ManageTexture.ApplyGradient > ManageTexture.EnsureDirectoryExists |
| manage_texture.apply_gradient | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageTexture.cs:467 | - | case apply_gradient > ManageTexture.ApplyGradient |
| manage_texture.apply_noise | write_file | `.EncodeToPNG` | Editor/Helpers/TextureOps.cs:26 | - | case apply_noise > ManageTexture.ApplyNoise > TextureOps.EncodeTexture |
| manage_texture.apply_noise | write_file | `.EncodeToPNG` | Editor/Helpers/TextureOps.cs:32 | - | case apply_noise > ManageTexture.ApplyNoise > TextureOps.EncodeTexture |
| manage_texture.apply_noise | write_file | `File.WriteAllBytes` | Editor/Tools/ManageTexture.cs:512 | - | case apply_noise > ManageTexture.ApplyNoise |
| manage_texture.apply_noise | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageTexture.cs:514 | - | case apply_noise > ManageTexture.ApplyNoise |
| manage_texture.apply_noise | import_compile | `AssetDatabase.Refresh` | Editor/Tools/ManageTexture.cs:1109 | - | case apply_noise > ManageTexture.ApplyNoise > ManageTexture.EnsureDirectoryExists |
| manage_texture.apply_noise | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageTexture.cs:548 | - | case apply_noise > ManageTexture.ApplyNoise |
| manage_texture.set_import_settings | none found | - | - | - | MCPForUnity/Editor/Tools/ManageTexture.cs:82 |
| manage_graphics.bake_cancel | none found | - | - | - | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:75 |
| manage_graphics.bake_clear | none found | - | - | - | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:79 |
| manage_graphics.bake_create_light_probe_group | instantiate | `.AddComponent` | Editor/Tools/Graphics/LightBakingOps.cs:247 | - | case bake_create_light_probe_group > LightBakingOps.CreateLightProbeGroup |
| manage_graphics.bake_create_light_probe_group | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/GraphicsHelpers.cs:257 | - | case bake_create_light_probe_group > LightBakingOps.CreateLightProbeGroup > GraphicsHelpers.MarkDirty |
| manage_graphics.bake_create_light_probe_group | scene_edit | `.position =` | Editor/Tools/Graphics/LightBakingOps.cs:244 | - | case bake_create_light_probe_group > LightBakingOps.CreateLightProbeGroup |
| manage_graphics.bake_create_light_probe_group | scene_edit | `EditorSceneManager.MarkSceneDirty` | Editor/Tools/Graphics/GraphicsHelpers.cs:262 | - | case bake_create_light_probe_group > LightBakingOps.CreateLightProbeGroup > GraphicsHelpers.MarkDirty |
| manage_graphics.bake_create_reflection_probe | instantiate | `.AddComponent` | Editor/Tools/Graphics/LightBakingOps.cs:316 | - | case bake_create_reflection_probe > LightBakingOps.CreateReflectionProbe |
| manage_graphics.bake_create_reflection_probe | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/GraphicsHelpers.cs:257 | - | case bake_create_reflection_probe > LightBakingOps.CreateReflectionProbe > GraphicsHelpers.MarkDirty |
| manage_graphics.bake_create_reflection_probe | scene_edit | `.position =` | Editor/Tools/Graphics/LightBakingOps.cs:313 | - | case bake_create_reflection_probe > LightBakingOps.CreateReflectionProbe |
| manage_graphics.bake_create_reflection_probe | scene_edit | `EditorSceneManager.MarkSceneDirty` | Editor/Tools/Graphics/GraphicsHelpers.cs:262 | - | case bake_create_reflection_probe > LightBakingOps.CreateReflectionProbe > GraphicsHelpers.MarkDirty |
| manage_graphics.bake_get_settings | none found | - | - | - | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:83 |
| manage_graphics.bake_reflection_probe | write_file | `AssetDatabase.CreateFolder` | Editor/Tools/Graphics/LightBakingOps.cs:112 | - | case bake_reflection_probe > LightBakingOps.BakeReflectionProbe |
| manage_graphics.bake_set_probe_positions | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/GraphicsHelpers.cs:257 | - | case bake_set_probe_positions > LightBakingOps.SetProbePositions > GraphicsHelpers.MarkDirty |
| manage_graphics.bake_set_probe_positions | scene_edit | `Undo.RecordObject` | Editor/Tools/Graphics/LightBakingOps.cs:363 | - | case bake_set_probe_positions > LightBakingOps.SetProbePositions |
| manage_graphics.bake_set_probe_positions | scene_edit | `EditorSceneManager.MarkSceneDirty` | Editor/Tools/Graphics/GraphicsHelpers.cs:262 | - | case bake_set_probe_positions > LightBakingOps.SetProbePositions > GraphicsHelpers.MarkDirty |
| manage_graphics.bake_set_settings | set_values | `prop.SetValue` | Editor/Tools/Graphics/LightBakingOps.cs:548 | - | case bake_set_settings > … > LightBakingOps.TrySetLightingSetting > LightBakingOps.TrySetBounceCount |
| manage_graphics.bake_set_settings | set_values | `prop.SetValue` | Editor/Tools/Graphics/LightBakingOps.cs:556 | - | case bake_set_settings > … > LightBakingOps.TrySetLightingSetting > LightBakingOps.TrySetBounceCount |
| manage_graphics.bake_set_settings | scene_edit | `Undo.RecordObject` | Editor/Tools/Graphics/LightBakingOps.cs:184 | - | case bake_set_settings > LightBakingOps.SetSettings |
| manage_graphics.bake_set_settings | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/LightBakingOps.cs:211 | - | case bake_set_settings > LightBakingOps.SetSettings |
| manage_graphics.bake_start | none found | - | - | - | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:73 |
| manage_graphics.bake_status | none found | - | - | - | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:77 |
| manage_graphics.feature_add | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/RendererFeatureOps.cs:156 | - | case feature_add > RendererFeatureOps.AddFeature |
| manage_graphics.feature_add | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/RendererFeatureOps.cs:231 | - | case feature_add > RendererFeatureOps.RemoveFeature |
| manage_graphics.feature_add | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/RendererFeatureOps.cs:273 | - | case feature_add > RendererFeatureOps.ConfigureFeature |
| manage_graphics.feature_add | write_file | `AssetDatabase.AddObjectToAsset` | Editor/Tools/Graphics/RendererFeatureOps.cs:117 | - | case feature_add > RendererFeatureOps.AddFeature |
| manage_graphics.feature_add | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/RendererFeatureOps.cs:562 | - | case feature_add > RendererFeatureOps.AddFeature > RendererFeatureOps.TrySetMaterial |
| manage_graphics.feature_add | set_values | `.ApplyModifiedProperties` | Editor/Tools/Graphics/RendererFeatureOps.cs:388 | - | case feature_add > RendererFeatureOps.ReorderFeatures |
| manage_graphics.feature_add | set_values | `.ApplyModifiedProperties` | Editor/Tools/Graphics/RendererFeatureOps.cs:128 | - | case feature_add > RendererFeatureOps.AddFeature |
| manage_graphics.feature_add | set_values | `.ApplyModifiedProperties` | Editor/Tools/Graphics/RendererFeatureOps.cs:141 | - | case feature_add > RendererFeatureOps.AddFeature |
| manage_graphics.feature_add | scene_edit | `Undo.RecordObject` | Editor/Tools/Graphics/RendererFeatureOps.cs:116 | - | case feature_add > RendererFeatureOps.AddFeature |
| manage_graphics.feature_add | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/RendererFeatureOps.cs:155 | - | case feature_add > RendererFeatureOps.AddFeature |
| manage_graphics.feature_add | scene_edit | `Undo.RecordObject` | Editor/Tools/Graphics/RendererFeatureOps.cs:198 | - | case feature_add > RendererFeatureOps.RemoveFeature |
| manage_graphics.feature_configure | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/RendererFeatureOps.cs:156 | - | case feature_configure > RendererFeatureOps.AddFeature |
| manage_graphics.feature_configure | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/RendererFeatureOps.cs:231 | - | case feature_configure > RendererFeatureOps.RemoveFeature |
| manage_graphics.feature_configure | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/RendererFeatureOps.cs:273 | - | case feature_configure > RendererFeatureOps.ConfigureFeature |
| manage_graphics.feature_configure | write_file | `AssetDatabase.AddObjectToAsset` | Editor/Tools/Graphics/RendererFeatureOps.cs:117 | - | case feature_configure > RendererFeatureOps.AddFeature |
| manage_graphics.feature_configure | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/RendererFeatureOps.cs:562 | - | case feature_configure > RendererFeatureOps.AddFeature > RendererFeatureOps.TrySetMaterial |
| manage_graphics.feature_configure | set_values | `.ApplyModifiedProperties` | Editor/Tools/Graphics/RendererFeatureOps.cs:388 | - | case feature_configure > RendererFeatureOps.ReorderFeatures |
| manage_graphics.feature_configure | set_values | `.ApplyModifiedProperties` | Editor/Tools/Graphics/RendererFeatureOps.cs:128 | - | case feature_configure > RendererFeatureOps.AddFeature |
| manage_graphics.feature_configure | set_values | `.ApplyModifiedProperties` | Editor/Tools/Graphics/RendererFeatureOps.cs:141 | - | case feature_configure > RendererFeatureOps.AddFeature |
| manage_graphics.feature_configure | scene_edit | `Undo.RecordObject` | Editor/Tools/Graphics/RendererFeatureOps.cs:116 | - | case feature_configure > RendererFeatureOps.AddFeature |
| manage_graphics.feature_configure | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/RendererFeatureOps.cs:155 | - | case feature_configure > RendererFeatureOps.AddFeature |
| manage_graphics.feature_configure | scene_edit | `Undo.RecordObject` | Editor/Tools/Graphics/RendererFeatureOps.cs:198 | - | case feature_configure > RendererFeatureOps.RemoveFeature |
| manage_graphics.feature_list | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/RendererFeatureOps.cs:156 | - | case feature_list > RendererFeatureOps.AddFeature |
| manage_graphics.feature_list | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/RendererFeatureOps.cs:231 | - | case feature_list > RendererFeatureOps.RemoveFeature |
| manage_graphics.feature_list | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/RendererFeatureOps.cs:273 | - | case feature_list > RendererFeatureOps.ConfigureFeature |
| manage_graphics.feature_list | write_file | `AssetDatabase.AddObjectToAsset` | Editor/Tools/Graphics/RendererFeatureOps.cs:117 | - | case feature_list > RendererFeatureOps.AddFeature |
| manage_graphics.feature_list | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/RendererFeatureOps.cs:562 | - | case feature_list > RendererFeatureOps.AddFeature > RendererFeatureOps.TrySetMaterial |
| manage_graphics.feature_list | set_values | `.ApplyModifiedProperties` | Editor/Tools/Graphics/RendererFeatureOps.cs:388 | - | case feature_list > RendererFeatureOps.ReorderFeatures |
| manage_graphics.feature_list | set_values | `.ApplyModifiedProperties` | Editor/Tools/Graphics/RendererFeatureOps.cs:128 | - | case feature_list > RendererFeatureOps.AddFeature |
| manage_graphics.feature_list | set_values | `.ApplyModifiedProperties` | Editor/Tools/Graphics/RendererFeatureOps.cs:141 | - | case feature_list > RendererFeatureOps.AddFeature |
| manage_graphics.feature_list | scene_edit | `Undo.RecordObject` | Editor/Tools/Graphics/RendererFeatureOps.cs:116 | - | case feature_list > RendererFeatureOps.AddFeature |
| manage_graphics.feature_list | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/RendererFeatureOps.cs:155 | - | case feature_list > RendererFeatureOps.AddFeature |
| manage_graphics.feature_list | scene_edit | `Undo.RecordObject` | Editor/Tools/Graphics/RendererFeatureOps.cs:198 | - | case feature_list > RendererFeatureOps.RemoveFeature |
| manage_graphics.feature_remove | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/RendererFeatureOps.cs:156 | - | case feature_remove > RendererFeatureOps.AddFeature |
| manage_graphics.feature_remove | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/RendererFeatureOps.cs:231 | - | case feature_remove > RendererFeatureOps.RemoveFeature |
| manage_graphics.feature_remove | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/RendererFeatureOps.cs:273 | - | case feature_remove > RendererFeatureOps.ConfigureFeature |
| manage_graphics.feature_remove | write_file | `AssetDatabase.AddObjectToAsset` | Editor/Tools/Graphics/RendererFeatureOps.cs:117 | - | case feature_remove > RendererFeatureOps.AddFeature |
| manage_graphics.feature_remove | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/RendererFeatureOps.cs:562 | - | case feature_remove > RendererFeatureOps.AddFeature > RendererFeatureOps.TrySetMaterial |
| manage_graphics.feature_remove | set_values | `.ApplyModifiedProperties` | Editor/Tools/Graphics/RendererFeatureOps.cs:388 | - | case feature_remove > RendererFeatureOps.ReorderFeatures |
| manage_graphics.feature_remove | set_values | `.ApplyModifiedProperties` | Editor/Tools/Graphics/RendererFeatureOps.cs:128 | - | case feature_remove > RendererFeatureOps.AddFeature |
| manage_graphics.feature_remove | set_values | `.ApplyModifiedProperties` | Editor/Tools/Graphics/RendererFeatureOps.cs:141 | - | case feature_remove > RendererFeatureOps.AddFeature |
| manage_graphics.feature_remove | scene_edit | `Undo.RecordObject` | Editor/Tools/Graphics/RendererFeatureOps.cs:116 | - | case feature_remove > RendererFeatureOps.AddFeature |
| manage_graphics.feature_remove | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/RendererFeatureOps.cs:155 | - | case feature_remove > RendererFeatureOps.AddFeature |
| manage_graphics.feature_remove | scene_edit | `Undo.RecordObject` | Editor/Tools/Graphics/RendererFeatureOps.cs:198 | - | case feature_remove > RendererFeatureOps.RemoveFeature |
| manage_graphics.feature_reorder | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/RendererFeatureOps.cs:156 | - | case feature_reorder > RendererFeatureOps.AddFeature |
| manage_graphics.feature_reorder | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/RendererFeatureOps.cs:231 | - | case feature_reorder > RendererFeatureOps.RemoveFeature |
| manage_graphics.feature_reorder | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/RendererFeatureOps.cs:273 | - | case feature_reorder > RendererFeatureOps.ConfigureFeature |
| manage_graphics.feature_reorder | write_file | `AssetDatabase.AddObjectToAsset` | Editor/Tools/Graphics/RendererFeatureOps.cs:117 | - | case feature_reorder > RendererFeatureOps.AddFeature |
| manage_graphics.feature_reorder | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/RendererFeatureOps.cs:562 | - | case feature_reorder > RendererFeatureOps.AddFeature > RendererFeatureOps.TrySetMaterial |
| manage_graphics.feature_reorder | set_values | `.ApplyModifiedProperties` | Editor/Tools/Graphics/RendererFeatureOps.cs:388 | - | case feature_reorder > RendererFeatureOps.ReorderFeatures |
| manage_graphics.feature_reorder | set_values | `.ApplyModifiedProperties` | Editor/Tools/Graphics/RendererFeatureOps.cs:128 | - | case feature_reorder > RendererFeatureOps.AddFeature |
| manage_graphics.feature_reorder | set_values | `.ApplyModifiedProperties` | Editor/Tools/Graphics/RendererFeatureOps.cs:141 | - | case feature_reorder > RendererFeatureOps.AddFeature |
| manage_graphics.feature_reorder | scene_edit | `Undo.RecordObject` | Editor/Tools/Graphics/RendererFeatureOps.cs:116 | - | case feature_reorder > RendererFeatureOps.AddFeature |
| manage_graphics.feature_reorder | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/RendererFeatureOps.cs:155 | - | case feature_reorder > RendererFeatureOps.AddFeature |
| manage_graphics.feature_reorder | scene_edit | `Undo.RecordObject` | Editor/Tools/Graphics/RendererFeatureOps.cs:198 | - | case feature_reorder > RendererFeatureOps.RemoveFeature |
| manage_graphics.feature_toggle | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/RendererFeatureOps.cs:156 | - | case feature_toggle > RendererFeatureOps.AddFeature |
| manage_graphics.feature_toggle | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/RendererFeatureOps.cs:231 | - | case feature_toggle > RendererFeatureOps.RemoveFeature |
| manage_graphics.feature_toggle | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/RendererFeatureOps.cs:273 | - | case feature_toggle > RendererFeatureOps.ConfigureFeature |
| manage_graphics.feature_toggle | write_file | `AssetDatabase.AddObjectToAsset` | Editor/Tools/Graphics/RendererFeatureOps.cs:117 | - | case feature_toggle > RendererFeatureOps.AddFeature |
| manage_graphics.feature_toggle | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/RendererFeatureOps.cs:562 | - | case feature_toggle > RendererFeatureOps.AddFeature > RendererFeatureOps.TrySetMaterial |
| manage_graphics.feature_toggle | set_values | `.ApplyModifiedProperties` | Editor/Tools/Graphics/RendererFeatureOps.cs:388 | - | case feature_toggle > RendererFeatureOps.ReorderFeatures |
| manage_graphics.feature_toggle | set_values | `.ApplyModifiedProperties` | Editor/Tools/Graphics/RendererFeatureOps.cs:128 | - | case feature_toggle > RendererFeatureOps.AddFeature |
| manage_graphics.feature_toggle | set_values | `.ApplyModifiedProperties` | Editor/Tools/Graphics/RendererFeatureOps.cs:141 | - | case feature_toggle > RendererFeatureOps.AddFeature |
| manage_graphics.feature_toggle | scene_edit | `Undo.RecordObject` | Editor/Tools/Graphics/RendererFeatureOps.cs:116 | - | case feature_toggle > RendererFeatureOps.AddFeature |
| manage_graphics.feature_toggle | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/RendererFeatureOps.cs:155 | - | case feature_toggle > RendererFeatureOps.AddFeature |
| manage_graphics.feature_toggle | scene_edit | `Undo.RecordObject` | Editor/Tools/Graphics/RendererFeatureOps.cs:198 | - | case feature_toggle > RendererFeatureOps.RemoveFeature |
| manage_graphics.ping | none found | - | - | - | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:26 |
| manage_graphics.pipeline_get_info | none found | - | - | - | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:105 |
| manage_graphics.pipeline_get_settings | none found | - | - | - | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:109 |
| manage_graphics.pipeline_set_quality | project_settings | `QualitySettings.SetQualityLevel` | Editor/Tools/Graphics/RenderPipelineOps.cs:105 | - | case pipeline_set_quality > RenderPipelineOps.SetQuality |
| manage_graphics.pipeline_set_settings | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/RenderPipelineOps.cs:237 | - | case pipeline_set_settings > RenderPipelineOps.SetSettings |
| manage_graphics.pipeline_set_settings | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/GraphicsHelpers.cs:203 | - | case pipeline_set_settings > RenderPipelineOps.SetSettings > GraphicsHelpers.SetSerializedValue |
| manage_graphics.pipeline_set_settings | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/GraphicsHelpers.cs:211 | path | case pipeline_set_settings > RenderPipelineOps.SetSettings > GraphicsHelpers.SetSerializedValue |
| manage_graphics.pipeline_set_settings | set_values | `.ApplyModifiedProperties` | Editor/Tools/Graphics/RenderPipelineOps.cs:233 | - | case pipeline_set_settings > RenderPipelineOps.SetSettings |
| manage_graphics.pipeline_set_settings | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/RenderPipelineOps.cs:236 | - | case pipeline_set_settings > RenderPipelineOps.SetSettings |
| manage_graphics.skybox_get | none found | - | - | - | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:138 |
| manage_graphics.skybox_set_ambient | scene_edit | `EditorSceneManager.MarkSceneDirty` | Editor/Tools/Graphics/SkyboxOps.cs:493 | - | case skybox_set_ambient > SkyboxOps.SetAmbient > SkyboxOps.MarkSceneDirty |
| manage_graphics.skybox_set_fog | scene_edit | `EditorSceneManager.MarkSceneDirty` | Editor/Tools/Graphics/SkyboxOps.cs:493 | - | case skybox_set_fog > SkyboxOps.SetFog > SkyboxOps.MarkSceneDirty |
| manage_graphics.skybox_set_material | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/SkyboxOps.cs:112 | - | case skybox_set_material > SkyboxOps.SetMaterial |
| manage_graphics.skybox_set_material | scene_edit | `EditorSceneManager.MarkSceneDirty` | Editor/Tools/Graphics/SkyboxOps.cs:493 | - | case skybox_set_material > SkyboxOps.SetMaterial > SkyboxOps.MarkSceneDirty |
| manage_graphics.skybox_set_properties | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/SkyboxOps.cs:171 | - | case skybox_set_properties > SkyboxOps.SetMaterialProperties |
| manage_graphics.skybox_set_properties | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case skybox_set_properties > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_graphics.skybox_set_properties | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/SkyboxOps.cs:472 | - | case skybox_set_properties > SkyboxOps.SetMaterialProperties > SkyboxOps.SetMaterialProperty |
| manage_graphics.skybox_set_properties | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case skybox_set_properties > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_graphics.skybox_set_properties | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case skybox_set_properties > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_graphics.skybox_set_properties | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/SkyboxOps.cs:170 | - | case skybox_set_properties > SkyboxOps.SetMaterialProperties |
| manage_graphics.skybox_set_properties | scene_edit | `EditorSceneManager.MarkSceneDirty` | Editor/Tools/Graphics/SkyboxOps.cs:493 | - | case skybox_set_properties > SkyboxOps.SetMaterialProperties > SkyboxOps.MarkSceneDirty |
| manage_graphics.skybox_set_properties | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/VfxGraphWrite.cs:123 | - | case skybox_set_properties > … > SkyboxOps.SetMaterialProperty > VfxGraphWrite.SetVector |
| manage_graphics.skybox_set_reflection | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/SkyboxOps.cs:319 | path | case skybox_set_reflection > SkyboxOps.SetReflection |
| manage_graphics.skybox_set_reflection | scene_edit | `EditorSceneManager.MarkSceneDirty` | Editor/Tools/Graphics/SkyboxOps.cs:493 | - | case skybox_set_reflection > SkyboxOps.SetReflection > SkyboxOps.MarkSceneDirty |
| manage_graphics.skybox_set_sun | scene_edit | `EditorSceneManager.MarkSceneDirty` | Editor/Tools/Graphics/SkyboxOps.cs:493 | - | case skybox_set_sun > SkyboxOps.SetSun > SkyboxOps.MarkSceneDirty |
| manage_graphics.stats_get | none found | - | - | - | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:95 |
| manage_graphics.stats_get_memory | none found | - | - | - | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:101 |
| manage_graphics.stats_list_counters | none found | - | - | - | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:97 |
| manage_graphics.stats_set_scene_debug | none found | - | - | - | MCPForUnity/Editor/Tools/Graphics/ManageGraphics.cs:99 |
| manage_graphics.volume_add_effect | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/VolumeOps.cs:442 | - | case volume_add_effect > VolumeOps.CreateProfile |
| manage_graphics.volume_add_effect | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/Graphics/VolumeOps.cs:441 | - | case volume_add_effect > VolumeOps.CreateProfile |
| manage_graphics.volume_add_effect | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/Graphics/VolumeOps.cs:60 | profile_path | case volume_add_effect > VolumeOps.CreateVolume |
| manage_graphics.volume_add_effect | write_file | `AssetDatabase.CreateFolder` | Editor/Tools/Graphics/VolumeOps.cs:435 | - | case volume_add_effect > VolumeOps.CreateProfile |
| manage_graphics.volume_add_effect | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/VolumeOps.cs:655 | - | case volume_add_effect > … > VolumeOps.SetVolumeParameter > VolumeOps.ConvertToParameterType |
| manage_graphics.volume_add_effect | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/VolumeOps.cs:52 | profile_path | case volume_add_effect > VolumeOps.CreateVolume |
| manage_graphics.volume_add_effect | instantiate | `.AddComponent` | Editor/Tools/Graphics/VolumeOps.cs:40 | - | case volume_add_effect > VolumeOps.CreateVolume |
| manage_graphics.volume_add_effect | set_values | `prop.SetValue` | Editor/Tools/Graphics/VolumeOps.cs:696 | - | case volume_add_effect > VolumeOps.CreateVolume > VolumeOps.SetProperty |
| manage_graphics.volume_add_effect | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/GraphicsHelpers.cs:257 | - | case volume_add_effect > VolumeOps.CreateVolume > GraphicsHelpers.MarkDirty |
| manage_graphics.volume_add_effect | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/VolumeOps.cs:116 | effects | case volume_add_effect > VolumeOps.CreateVolume |
| manage_graphics.volume_add_effect | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/VolumeOps.cs:186 | - | case volume_add_effect > VolumeOps.AddEffect |
| manage_graphics.volume_create | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/VolumeOps.cs:442 | - | case volume_create > VolumeOps.CreateProfile |
| manage_graphics.volume_create | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/Graphics/VolumeOps.cs:441 | - | case volume_create > VolumeOps.CreateProfile |
| manage_graphics.volume_create | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/Graphics/VolumeOps.cs:60 | profile_path | case volume_create > VolumeOps.CreateVolume |
| manage_graphics.volume_create | write_file | `AssetDatabase.CreateFolder` | Editor/Tools/Graphics/VolumeOps.cs:435 | - | case volume_create > VolumeOps.CreateProfile |
| manage_graphics.volume_create | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/VolumeOps.cs:655 | - | case volume_create > … > VolumeOps.SetVolumeParameter > VolumeOps.ConvertToParameterType |
| manage_graphics.volume_create | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/VolumeOps.cs:52 | profile_path | case volume_create > VolumeOps.CreateVolume |
| manage_graphics.volume_create | instantiate | `.AddComponent` | Editor/Tools/Graphics/VolumeOps.cs:40 | - | case volume_create > VolumeOps.CreateVolume |
| manage_graphics.volume_create | set_values | `prop.SetValue` | Editor/Tools/Graphics/VolumeOps.cs:696 | - | case volume_create > VolumeOps.CreateVolume > VolumeOps.SetProperty |
| manage_graphics.volume_create | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/GraphicsHelpers.cs:257 | - | case volume_create > VolumeOps.CreateVolume > GraphicsHelpers.MarkDirty |
| manage_graphics.volume_create | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/VolumeOps.cs:116 | effects | case volume_create > VolumeOps.CreateVolume |
| manage_graphics.volume_create | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/VolumeOps.cs:186 | - | case volume_create > VolumeOps.AddEffect |
| manage_graphics.volume_create_profile | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/VolumeOps.cs:442 | - | case volume_create_profile > VolumeOps.CreateProfile |
| manage_graphics.volume_create_profile | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/Graphics/VolumeOps.cs:441 | - | case volume_create_profile > VolumeOps.CreateProfile |
| manage_graphics.volume_create_profile | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/Graphics/VolumeOps.cs:60 | profile_path | case volume_create_profile > VolumeOps.CreateVolume |
| manage_graphics.volume_create_profile | write_file | `AssetDatabase.CreateFolder` | Editor/Tools/Graphics/VolumeOps.cs:435 | - | case volume_create_profile > VolumeOps.CreateProfile |
| manage_graphics.volume_create_profile | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/VolumeOps.cs:655 | - | case volume_create_profile > … > VolumeOps.SetVolumeParameter > VolumeOps.ConvertToParameterType |
| manage_graphics.volume_create_profile | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/VolumeOps.cs:52 | profile_path | case volume_create_profile > VolumeOps.CreateVolume |
| manage_graphics.volume_create_profile | instantiate | `.AddComponent` | Editor/Tools/Graphics/VolumeOps.cs:40 | - | case volume_create_profile > VolumeOps.CreateVolume |
| manage_graphics.volume_create_profile | set_values | `prop.SetValue` | Editor/Tools/Graphics/VolumeOps.cs:696 | - | case volume_create_profile > VolumeOps.CreateVolume > VolumeOps.SetProperty |
| manage_graphics.volume_create_profile | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/GraphicsHelpers.cs:257 | - | case volume_create_profile > VolumeOps.CreateVolume > GraphicsHelpers.MarkDirty |
| manage_graphics.volume_create_profile | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/VolumeOps.cs:116 | effects | case volume_create_profile > VolumeOps.CreateVolume |
| manage_graphics.volume_create_profile | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/VolumeOps.cs:186 | - | case volume_create_profile > VolumeOps.AddEffect |
| manage_graphics.volume_get_info | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/VolumeOps.cs:442 | - | case volume_get_info > VolumeOps.CreateProfile |
| manage_graphics.volume_get_info | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/Graphics/VolumeOps.cs:441 | - | case volume_get_info > VolumeOps.CreateProfile |
| manage_graphics.volume_get_info | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/Graphics/VolumeOps.cs:60 | profile_path | case volume_get_info > VolumeOps.CreateVolume |
| manage_graphics.volume_get_info | write_file | `AssetDatabase.CreateFolder` | Editor/Tools/Graphics/VolumeOps.cs:435 | - | case volume_get_info > VolumeOps.CreateProfile |
| manage_graphics.volume_get_info | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/VolumeOps.cs:655 | - | case volume_get_info > … > VolumeOps.SetVolumeParameter > VolumeOps.ConvertToParameterType |
| manage_graphics.volume_get_info | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/VolumeOps.cs:52 | profile_path | case volume_get_info > VolumeOps.CreateVolume |
| manage_graphics.volume_get_info | instantiate | `.AddComponent` | Editor/Tools/Graphics/VolumeOps.cs:40 | - | case volume_get_info > VolumeOps.CreateVolume |
| manage_graphics.volume_get_info | set_values | `prop.SetValue` | Editor/Tools/Graphics/VolumeOps.cs:696 | - | case volume_get_info > VolumeOps.CreateVolume > VolumeOps.SetProperty |
| manage_graphics.volume_get_info | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/GraphicsHelpers.cs:257 | - | case volume_get_info > VolumeOps.CreateVolume > GraphicsHelpers.MarkDirty |
| manage_graphics.volume_get_info | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/VolumeOps.cs:116 | effects | case volume_get_info > VolumeOps.CreateVolume |
| manage_graphics.volume_get_info | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/VolumeOps.cs:186 | - | case volume_get_info > VolumeOps.AddEffect |
| manage_graphics.volume_list_effects | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/VolumeOps.cs:442 | - | case volume_list_effects > VolumeOps.CreateProfile |
| manage_graphics.volume_list_effects | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/Graphics/VolumeOps.cs:441 | - | case volume_list_effects > VolumeOps.CreateProfile |
| manage_graphics.volume_list_effects | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/Graphics/VolumeOps.cs:60 | profile_path | case volume_list_effects > VolumeOps.CreateVolume |
| manage_graphics.volume_list_effects | write_file | `AssetDatabase.CreateFolder` | Editor/Tools/Graphics/VolumeOps.cs:435 | - | case volume_list_effects > VolumeOps.CreateProfile |
| manage_graphics.volume_list_effects | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/VolumeOps.cs:655 | - | case volume_list_effects > … > VolumeOps.SetVolumeParameter > VolumeOps.ConvertToParameterType |
| manage_graphics.volume_list_effects | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/VolumeOps.cs:52 | profile_path | case volume_list_effects > VolumeOps.CreateVolume |
| manage_graphics.volume_list_effects | instantiate | `.AddComponent` | Editor/Tools/Graphics/VolumeOps.cs:40 | - | case volume_list_effects > VolumeOps.CreateVolume |
| manage_graphics.volume_list_effects | set_values | `prop.SetValue` | Editor/Tools/Graphics/VolumeOps.cs:696 | - | case volume_list_effects > VolumeOps.CreateVolume > VolumeOps.SetProperty |
| manage_graphics.volume_list_effects | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/GraphicsHelpers.cs:257 | - | case volume_list_effects > VolumeOps.CreateVolume > GraphicsHelpers.MarkDirty |
| manage_graphics.volume_list_effects | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/VolumeOps.cs:116 | effects | case volume_list_effects > VolumeOps.CreateVolume |
| manage_graphics.volume_list_effects | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/VolumeOps.cs:186 | - | case volume_list_effects > VolumeOps.AddEffect |
| manage_graphics.volume_remove_effect | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/VolumeOps.cs:442 | - | case volume_remove_effect > VolumeOps.CreateProfile |
| manage_graphics.volume_remove_effect | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/Graphics/VolumeOps.cs:441 | - | case volume_remove_effect > VolumeOps.CreateProfile |
| manage_graphics.volume_remove_effect | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/Graphics/VolumeOps.cs:60 | profile_path | case volume_remove_effect > VolumeOps.CreateVolume |
| manage_graphics.volume_remove_effect | write_file | `AssetDatabase.CreateFolder` | Editor/Tools/Graphics/VolumeOps.cs:435 | - | case volume_remove_effect > VolumeOps.CreateProfile |
| manage_graphics.volume_remove_effect | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/VolumeOps.cs:655 | - | case volume_remove_effect > … > VolumeOps.SetVolumeParameter > VolumeOps.ConvertToParameterType |
| manage_graphics.volume_remove_effect | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/VolumeOps.cs:52 | profile_path | case volume_remove_effect > VolumeOps.CreateVolume |
| manage_graphics.volume_remove_effect | instantiate | `.AddComponent` | Editor/Tools/Graphics/VolumeOps.cs:40 | - | case volume_remove_effect > VolumeOps.CreateVolume |
| manage_graphics.volume_remove_effect | set_values | `prop.SetValue` | Editor/Tools/Graphics/VolumeOps.cs:696 | - | case volume_remove_effect > VolumeOps.CreateVolume > VolumeOps.SetProperty |
| manage_graphics.volume_remove_effect | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/GraphicsHelpers.cs:257 | - | case volume_remove_effect > VolumeOps.CreateVolume > GraphicsHelpers.MarkDirty |
| manage_graphics.volume_remove_effect | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/VolumeOps.cs:116 | effects | case volume_remove_effect > VolumeOps.CreateVolume |
| manage_graphics.volume_remove_effect | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/VolumeOps.cs:186 | - | case volume_remove_effect > VolumeOps.AddEffect |
| manage_graphics.volume_set_effect | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/VolumeOps.cs:442 | - | case volume_set_effect > VolumeOps.CreateProfile |
| manage_graphics.volume_set_effect | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/Graphics/VolumeOps.cs:441 | - | case volume_set_effect > VolumeOps.CreateProfile |
| manage_graphics.volume_set_effect | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/Graphics/VolumeOps.cs:60 | profile_path | case volume_set_effect > VolumeOps.CreateVolume |
| manage_graphics.volume_set_effect | write_file | `AssetDatabase.CreateFolder` | Editor/Tools/Graphics/VolumeOps.cs:435 | - | case volume_set_effect > VolumeOps.CreateProfile |
| manage_graphics.volume_set_effect | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/VolumeOps.cs:655 | - | case volume_set_effect > … > VolumeOps.SetVolumeParameter > VolumeOps.ConvertToParameterType |
| manage_graphics.volume_set_effect | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/VolumeOps.cs:52 | profile_path | case volume_set_effect > VolumeOps.CreateVolume |
| manage_graphics.volume_set_effect | instantiate | `.AddComponent` | Editor/Tools/Graphics/VolumeOps.cs:40 | - | case volume_set_effect > VolumeOps.CreateVolume |
| manage_graphics.volume_set_effect | set_values | `prop.SetValue` | Editor/Tools/Graphics/VolumeOps.cs:696 | - | case volume_set_effect > VolumeOps.CreateVolume > VolumeOps.SetProperty |
| manage_graphics.volume_set_effect | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/GraphicsHelpers.cs:257 | - | case volume_set_effect > VolumeOps.CreateVolume > GraphicsHelpers.MarkDirty |
| manage_graphics.volume_set_effect | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/VolumeOps.cs:116 | effects | case volume_set_effect > VolumeOps.CreateVolume |
| manage_graphics.volume_set_effect | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/VolumeOps.cs:186 | - | case volume_set_effect > VolumeOps.AddEffect |
| manage_graphics.volume_set_properties | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Graphics/VolumeOps.cs:442 | - | case volume_set_properties > VolumeOps.CreateProfile |
| manage_graphics.volume_set_properties | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/Graphics/VolumeOps.cs:441 | - | case volume_set_properties > VolumeOps.CreateProfile |
| manage_graphics.volume_set_properties | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/Graphics/VolumeOps.cs:60 | profile_path | case volume_set_properties > VolumeOps.CreateVolume |
| manage_graphics.volume_set_properties | write_file | `AssetDatabase.CreateFolder` | Editor/Tools/Graphics/VolumeOps.cs:435 | - | case volume_set_properties > VolumeOps.CreateProfile |
| manage_graphics.volume_set_properties | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/VolumeOps.cs:655 | - | case volume_set_properties > … > VolumeOps.SetVolumeParameter > VolumeOps.ConvertToParameterType |
| manage_graphics.volume_set_properties | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Graphics/VolumeOps.cs:52 | profile_path | case volume_set_properties > VolumeOps.CreateVolume |
| manage_graphics.volume_set_properties | instantiate | `.AddComponent` | Editor/Tools/Graphics/VolumeOps.cs:40 | - | case volume_set_properties > VolumeOps.CreateVolume |
| manage_graphics.volume_set_properties | set_values | `prop.SetValue` | Editor/Tools/Graphics/VolumeOps.cs:696 | - | case volume_set_properties > VolumeOps.CreateVolume > VolumeOps.SetProperty |
| manage_graphics.volume_set_properties | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/GraphicsHelpers.cs:257 | - | case volume_set_properties > VolumeOps.CreateVolume > GraphicsHelpers.MarkDirty |
| manage_graphics.volume_set_properties | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/VolumeOps.cs:116 | effects | case volume_set_properties > VolumeOps.CreateVolume |
| manage_graphics.volume_set_properties | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Graphics/VolumeOps.cs:186 | - | case volume_set_properties > VolumeOps.AddEffect |
| manage_packages.add_package | send | `Client.Add` | Editor/Tools/ManagePackages.cs:93 | - | case add_package > ManagePackages.AddPackage |
| manage_packages.add_registry | write_file | `File.WriteAllText` | Editor/Tools/ManagePackages.cs:473 | - | case add_registry > ManagePackages.AddRegistry |
| manage_packages.add_registry | send | `Client.Resolve` | Editor/Tools/ManagePackages.cs:474 | - | case add_registry > ManagePackages.AddRegistry |
| manage_packages.embed_package | send | `Client.Embed` | Editor/Tools/ManagePackages.cs:559 | - | case embed_package > ManagePackages.EmbedPackage |
| manage_packages.get_package_info | none found | - | - | - | MCPForUnity/Editor/Tools/ManagePackages.cs:55 |
| manage_packages.list_packages | none found | - | - | - | MCPForUnity/Editor/Tools/ManagePackages.cs:51 |
| manage_packages.list_registries | none found | - | - | - | MCPForUnity/Editor/Tools/ManagePackages.cs:57 |
| manage_packages.ping | none found | - | - | - | MCPForUnity/Editor/Tools/ManagePackages.cs:67 |
| manage_packages.remove_package | send | `Client.Remove` | Editor/Tools/ManagePackages.cs:146 | - | case remove_package > ManagePackages.RemovePackage |
| manage_packages.remove_registry | write_file | `File.WriteAllText` | Editor/Tools/ManagePackages.cs:539 | - | case remove_registry > ManagePackages.RemoveRegistry |
| manage_packages.remove_registry | send | `Client.Resolve` | Editor/Tools/ManagePackages.cs:540 | - | case remove_registry > ManagePackages.RemoveRegistry |
| manage_packages.resolve_packages | send | `Client.Resolve` | Editor/Tools/ManagePackages.cs:582 | - | case resolve_packages > ManagePackages.ResolvePackages |
| manage_packages.search_packages | send | `Client.Search` | Editor/Tools/ManagePackages.cs:301 | - | case search_packages > ManagePackages.SearchPackages |
| manage_packages.status | none found | - | - | - | MCPForUnity/Editor/Tools/ManagePackages.cs:49 |
| manage_physics.add_joint | instantiate | `Undo.AddComponent` | Editor/Tools/Physics/JointOps.cs:115 | - | case add_joint > JointOps.AddJoint |
| manage_physics.add_joint | set_values | `propInfo.SetValue` | Editor/Tools/Physics/JointOps.cs:476 | properties | case add_joint > JointOps.AddJoint > JointOps.SetPropertiesViaReflection |
| manage_physics.add_joint | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Physics/JointOps.cs:135 | - | case add_joint > JointOps.AddJoint |
| manage_physics.apply_force | none found | - | - | - | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:70 |
| manage_physics.assign_physics_material | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | component_index | case assign_physics_material > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_physics.assign_physics_material | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Physics/PhysicsMaterialOps.cs:90 | - | case assign_physics_material > PhysicsMaterialOps.Assign |
| manage_physics.assign_physics_material | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Physics/PhysicsMaterialOps.cs:92 | - | case assign_physics_material > PhysicsMaterialOps.Assign |
| manage_physics.assign_physics_material | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Physics/PhysicsMaterialOps.cs:94 | - | case assign_physics_material > PhysicsMaterialOps.Assign |
| manage_physics.assign_physics_material | scene_edit | `Undo.RecordObject` | Editor/Tools/Physics/PhysicsMaterialOps.cs:105 | - | case assign_physics_material > PhysicsMaterialOps.Assign |
| manage_physics.assign_physics_material | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Physics/PhysicsMaterialOps.cs:107 | - | case assign_physics_material > PhysicsMaterialOps.Assign |
| manage_physics.assign_physics_material | scene_edit | `Undo.RecordObject` | Editor/Tools/Physics/PhysicsMaterialOps.cs:141 | - | case assign_physics_material > PhysicsMaterialOps.Assign |
| manage_physics.configure_joint | set_values | `propInfo.SetValue` | Editor/Tools/Physics/JointOps.cs:476 | properties | case configure_joint > JointOps.ConfigureJoint > JointOps.SetPropertiesViaReflection |
| manage_physics.configure_joint | scene_edit | `Undo.RecordObject` | Editor/Tools/Physics/JointOps.cs:189 | - | case configure_joint > JointOps.ConfigureJoint |
| manage_physics.configure_joint | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Physics/JointOps.cs:306 | - | case configure_joint > JointOps.ConfigureJoint |
| manage_physics.configure_physics_material | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Physics/PhysicsMaterialOps.cs:361 | - | case configure_physics_material > PhysicsMaterialOps.Configure > PhysicsMaterialOps.Configure3D |
| manage_physics.configure_physics_material | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Physics/PhysicsMaterialOps.cs:414 | dimension | case configure_physics_material > PhysicsMaterialOps.Configure > PhysicsMaterialOps.Configure2D |
| manage_physics.configure_physics_material | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Physics/PhysicsMaterialOps.cs:300 | - | case configure_physics_material > PhysicsMaterialOps.Configure > PhysicsMaterialOps.Configure3D |
| manage_physics.configure_physics_material | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Physics/PhysicsMaterialOps.cs:390 | dimension | case configure_physics_material > PhysicsMaterialOps.Configure > PhysicsMaterialOps.Configure2D |
| manage_physics.configure_physics_material | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Physics/PhysicsMaterialOps.cs:302 | - | case configure_physics_material > PhysicsMaterialOps.Configure > PhysicsMaterialOps.Configure3D |
| manage_physics.configure_physics_material | scene_edit | `Undo.RecordObject` | Editor/Tools/Physics/PhysicsMaterialOps.cs:307 | - | case configure_physics_material > PhysicsMaterialOps.Configure > PhysicsMaterialOps.Configure3D |
| manage_physics.configure_physics_material | scene_edit | `Undo.RecordObject` | Editor/Tools/Physics/PhysicsMaterialOps.cs:394 | dimension | case configure_physics_material > PhysicsMaterialOps.Configure > PhysicsMaterialOps.Configure2D |
| manage_physics.configure_physics_material | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Physics/PhysicsMaterialOps.cs:360 | - | case configure_physics_material > PhysicsMaterialOps.Configure > PhysicsMaterialOps.Configure3D |
| manage_physics.configure_rigidbody | scene_edit | `Undo.RecordObject` | Editor/Tools/Physics/PhysicsRigidbodyOps.cs:207 | - | case configure_rigidbody > PhysicsRigidbodyOps.ConfigureRigidbody > PhysicsRigidbodyOps.ConfigureRigidbody3D |
| manage_physics.configure_rigidbody | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Physics/PhysicsRigidbodyOps.cs:303 | - | case configure_rigidbody > PhysicsRigidbodyOps.ConfigureRigidbody > PhysicsRigidbodyOps.ConfigureRigidbody3D |
| manage_physics.configure_rigidbody | scene_edit | `Undo.RecordObject` | Editor/Tools/Physics/PhysicsRigidbodyOps.cs:331 | - | case configure_rigidbody > PhysicsRigidbodyOps.ConfigureRigidbody > PhysicsRigidbodyOps.ConfigureRigidbody2D |
| manage_physics.create_physics_material | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Physics/PhysicsMaterialOps.cs:224 | - | case create_physics_material > PhysicsMaterialOps.Create > PhysicsMaterialOps.Create3D |
| manage_physics.create_physics_material | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/Physics/PhysicsMaterialOps.cs:260 | dimension | case create_physics_material > PhysicsMaterialOps.Create > PhysicsMaterialOps.Create2D |
| manage_physics.create_physics_material | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/Physics/PhysicsMaterialOps.cs:223 | - | case create_physics_material > PhysicsMaterialOps.Create > PhysicsMaterialOps.Create3D |
| manage_physics.create_physics_material | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/Physics/PhysicsMaterialOps.cs:259 | dimension | case create_physics_material > PhysicsMaterialOps.Create > PhysicsMaterialOps.Create2D |
| manage_physics.create_physics_material | write_file | `AssetDatabase.CreateFolder` | Editor/Tools/Physics/PhysicsMaterialOps.cs:520 | - | case create_physics_material > PhysicsMaterialOps.Create > PhysicsMaterialOps.EnsureFolderExists |
| manage_physics.create_physics_material | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Physics/PhysicsMaterialOps.cs:188 | - | case create_physics_material > PhysicsMaterialOps.Create > PhysicsMaterialOps.Create3D |
| manage_physics.create_physics_material | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Physics/PhysicsMaterialOps.cs:250 | dimension | case create_physics_material > PhysicsMaterialOps.Create > PhysicsMaterialOps.Create2D |
| manage_physics.get_collision_matrix | none found | - | - | - | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:36 |
| manage_physics.get_rigidbody | none found | - | - | - | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:74 |
| manage_physics.get_settings | none found | - | - | - | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:30 |
| manage_physics.linecast | none found | - | - | - | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:62 |
| manage_physics.overlap | none found | - | - | - | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:66 |
| manage_physics.ping | none found | - | - | - | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:26 |
| manage_physics.raycast | none found | - | - | - | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:58 |
| manage_physics.raycast_all | none found | - | - | - | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:60 |
| manage_physics.remove_joint | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Physics/JointOps.cs:392 | - | case remove_joint > JointOps.RemoveJoint |
| manage_physics.remove_joint | destroy_object | `Undo.DestroyObjectImmediate` | Editor/Tools/Physics/JointOps.cs:388 | - | case remove_joint > JointOps.RemoveJoint |
| manage_physics.set_collision_matrix | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Tools/Physics/CollisionMatrixOps.cs:110 | dimension | case set_collision_matrix > CollisionMatrixOps.SetCollisionMatrix > CollisionMatrixOps.MarkSettingsDirty |
| manage_physics.set_collision_matrix | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Physics/CollisionMatrixOps.cs:112 | dimension | case set_collision_matrix > CollisionMatrixOps.SetCollisionMatrix > CollisionMatrixOps.MarkSettingsDirty |
| manage_physics.set_settings | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Tools/Physics/PhysicsSettingsOps.cs:294 | - | case set_settings > … > PhysicsSettingsOps.SetSettings3D > PhysicsSettingsOps.MarkDynamicsManagerDirty |
| manage_physics.set_settings | load_asset | `AssetDatabase.LoadAllAssetsAtPath` | Editor/Tools/Physics/PhysicsSettingsOps.cs:301 | dimension | case set_settings > … > PhysicsSettingsOps.SetSettings2D > PhysicsSettingsOps.MarkPhysics2DSettingsDirty |
| manage_physics.set_settings | set_values | `prop.SetValue` | Runtime/Helpers/UnityPhysicsCompat.cs:132 | - | case set_settings > … > PhysicsSettingsOps.SetSettings3D > UnityPhysicsCompat.TrySetPhysicsAutoSyncTransforms |
| manage_physics.set_settings | set_values | `prop.SetValue` | Runtime/Helpers/UnityPhysicsCompat.cs:80 | dimension | case set_settings > … > PhysicsSettingsOps.SetSettings2D > UnityPhysicsCompat.TrySetPhysics2DAutoSyncTransforms |
| manage_physics.set_settings | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Physics/PhysicsSettingsOps.cs:296 | - | case set_settings > … > PhysicsSettingsOps.SetSettings3D > PhysicsSettingsOps.MarkDynamicsManagerDirty |
| manage_physics.set_settings | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Physics/PhysicsSettingsOps.cs:303 | dimension | case set_settings > … > PhysicsSettingsOps.SetSettings2D > PhysicsSettingsOps.MarkPhysics2DSettingsDirty |
| manage_physics.shapecast | none found | - | - | - | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:64 |
| manage_physics.simulate_step | simulate | `Physics2D.Simulate` | Editor/Tools/Physics/PhysicsSimulationOps.cs:27 | dimension | case simulate_step > PhysicsSimulationOps.SimulateStep |
| manage_physics.simulate_step | simulate | `Physics.Simulate` | Editor/Tools/Physics/PhysicsSimulationOps.cs:38 | not dimension | case simulate_step > PhysicsSimulationOps.SimulateStep |
| manage_physics.validate | none found | - | - | - | MCPForUnity/Editor/Tools/Physics/ManagePhysics.cs:80 |
| manage_probuilder.append_vertices_to_edge | reflection | `Activator.CreateInstance` | Editor/Tools/ProBuilder/ManageProBuilder.cs:540 | - | case append_vertices_to_edge > ManageProBuilder.AppendVerticesToEdge > ManageProBuilder.ToTypedEdgeList |
| manage_probuilder.append_vertices_to_edge | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.append_vertices_to_edge | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case append_vertices_to_edge > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.append_vertices_to_edge | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case append_vertices_to_edge > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.append_vertices_to_edge | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:1884 | - | case append_vertices_to_edge > ManageProBuilder.AppendVerticesToEdge |
| manage_probuilder.auto_smooth | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.auto_smooth | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case auto_smooth > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.auto_smooth | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case auto_smooth > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.auto_smooth | scene_edit | `Undo.RecordObject` | Editor/Tools/ProBuilder/ProBuilderSmoothing.cs:72 | - | case auto_smooth > ProBuilderSmoothing.AutoSmooth |
| manage_probuilder.bevel_edges | reflection | `Activator.CreateInstance` | Editor/Tools/ProBuilder/ManageProBuilder.cs:540 | - | case bevel_edges > ManageProBuilder.BevelEdges > ManageProBuilder.ToTypedEdgeList |
| manage_probuilder.bevel_edges | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.bevel_edges | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case bevel_edges > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.bevel_edges | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case bevel_edges > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.bevel_edges | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:1018 | - | case bevel_edges > ManageProBuilder.BevelEdges |
| manage_probuilder.bridge_edges | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.bridge_edges | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case bridge_edges > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.bridge_edges | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case bridge_edges > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.bridge_edges | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:1166 | - | case bridge_edges > ManageProBuilder.BridgeEdges |
| manage_probuilder.center_pivot | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.center_pivot | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case center_pivot > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.center_pivot | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case center_pivot > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.center_pivot | scene_edit | `Undo.RecordObject` | Editor/Tools/ProBuilder/ProBuilderMeshUtils.cs:35 | - | case center_pivot > ProBuilderMeshUtils.CenterPivot |
| manage_probuilder.center_pivot | scene_edit | `Undo.RecordObject` | Editor/Tools/ProBuilder/ProBuilderMeshUtils.cs:36 | - | case center_pivot > ProBuilderMeshUtils.CenterPivot |
| manage_probuilder.combine_meshes | reflection | `Activator.CreateInstance` | Editor/Tools/ProBuilder/ManageProBuilder.cs:1406 | - | case combine_meshes > ManageProBuilder.CombineMeshes |
| manage_probuilder.combine_meshes | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case combine_meshes > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_probuilder.combine_meshes | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.combine_meshes | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case combine_meshes > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.combine_meshes | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case combine_meshes > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.combine_meshes | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:1403 | - | case combine_meshes > ManageProBuilder.CombineMeshes |
| manage_probuilder.connect_elements | reflection | `Activator.CreateInstance` | Editor/Tools/ProBuilder/ManageProBuilder.cs:428 | - | case connect_elements > ManageProBuilder.ConnectElements > ManageProBuilder.ToTypedFaceList |
| manage_probuilder.connect_elements | reflection | `Activator.CreateInstance` | Editor/Tools/ProBuilder/ManageProBuilder.cs:540 | - | case connect_elements > ManageProBuilder.ConnectElements > ManageProBuilder.ToTypedEdgeList |
| manage_probuilder.connect_elements | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.connect_elements | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case connect_elements > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.connect_elements | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case connect_elements > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.connect_elements | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:1212 | - | case connect_elements > ManageProBuilder.ConnectElements |
| manage_probuilder.convert_to_probuilder | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case convert_to_probuilder > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_probuilder.convert_to_probuilder | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.convert_to_probuilder | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case convert_to_probuilder > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.convert_to_probuilder | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case convert_to_probuilder > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.convert_to_probuilder | instantiate | `.AddComponent` | Editor/Tools/ProBuilder/ManageProBuilder.cs:2475 | - | case convert_to_probuilder > ManageProBuilder.ConvertToProBuilder |
| manage_probuilder.convert_to_probuilder | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:2473 | - | case convert_to_probuilder > ManageProBuilder.ConvertToProBuilder |
| manage_probuilder.create_poly_shape | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.create_poly_shape | instantiate | `.AddComponent` | Editor/Tools/ProBuilder/ManageProBuilder.cs:872 | - | case create_poly_shape > ManageProBuilder.CreatePolyShape |
| manage_probuilder.create_poly_shape | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ProBuilder/ManageProBuilder.cs:876 | - | case create_poly_shape > ManageProBuilder.CreatePolyShape |
| manage_probuilder.create_poly_shape | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ProBuilder/ManageProBuilder.cs:888 | - | case create_poly_shape > ManageProBuilder.CreatePolyShape |
| manage_probuilder.create_polygon | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.create_polygon | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case create_polygon > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.create_polygon | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case create_polygon > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.create_polygon | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:1581 | - | case create_polygon > ManageProBuilder.CreatePolygon |
| manage_probuilder.create_shape | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.create_shape | scene_edit | `.position =` | Editor/Tools/ProBuilder/ManageProBuilder.cs:587 | - | case create_shape > ManageProBuilder.CreateShape |
| manage_probuilder.create_shape | scene_edit | `.eulerAngles =` | Editor/Tools/ProBuilder/ManageProBuilder.cs:592 | - | case create_shape > ManageProBuilder.CreateShape |
| manage_probuilder.delete_faces | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.delete_faces | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case delete_faces > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.delete_faces | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case delete_faces > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.delete_faces | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:1087 | - | case delete_faces > ManageProBuilder.DeleteFaces |
| manage_probuilder.detach_faces | reflection | `Activator.CreateInstance` | Editor/Tools/ProBuilder/ManageProBuilder.cs:428 | - | case detach_faces > ManageProBuilder.DetachFaces > ManageProBuilder.ToTypedFaceList |
| manage_probuilder.detach_faces | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.detach_faces | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case detach_faces > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.detach_faces | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case detach_faces > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.detach_faces | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:1286 | - | case detach_faces > ManageProBuilder.DetachFaces |
| manage_probuilder.duplicate_and_flip | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.duplicate_and_flip | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case duplicate_and_flip > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.duplicate_and_flip | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case duplicate_and_flip > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.duplicate_and_flip | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:1543 | - | case duplicate_and_flip > ManageProBuilder.DuplicateAndFlip |
| manage_probuilder.extrude_edges | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.extrude_edges | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case extrude_edges > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.extrude_edges | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case extrude_edges > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.extrude_edges | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:975 | - | case extrude_edges > ManageProBuilder.ExtrudeEdges |
| manage_probuilder.extrude_faces | reflection | `MethodInfo.Invoke` | Editor/Tools/ProBuilder/ManageProBuilder.cs:944 | - | case extrude_faces > ManageProBuilder.ExtrudeFaces |
| manage_probuilder.extrude_faces | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.extrude_faces | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case extrude_faces > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.extrude_faces | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case extrude_faces > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.extrude_faces | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:933 | - | case extrude_faces > ManageProBuilder.ExtrudeFaces |
| manage_probuilder.flip_normals | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.flip_normals | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case flip_normals > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.flip_normals | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case flip_normals > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.flip_normals | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:1329 | - | case flip_normals > ManageProBuilder.FlipNormals |
| manage_probuilder.freeze_transform | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.freeze_transform | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case freeze_transform > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.freeze_transform | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case freeze_transform > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.freeze_transform | scene_edit | `Undo.RecordObject` | Editor/Tools/ProBuilder/ProBuilderMeshUtils.cs:74 | - | case freeze_transform > ProBuilderMeshUtils.FreezeTransform |
| manage_probuilder.freeze_transform | scene_edit | `Undo.RecordObject` | Editor/Tools/ProBuilder/ProBuilderMeshUtils.cs:75 | - | case freeze_transform > ProBuilderMeshUtils.FreezeTransform |
| manage_probuilder.freeze_transform | scene_edit | `.position =` | Editor/Tools/ProBuilder/ProBuilderMeshUtils.cs:83 | - | case freeze_transform > ProBuilderMeshUtils.FreezeTransform |
| manage_probuilder.get_mesh_info | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.get_mesh_info | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case get_mesh_info > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.get_mesh_info | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case get_mesh_info > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.insert_vertex | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.insert_vertex | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case insert_vertex > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.insert_vertex | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case insert_vertex > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.insert_vertex | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:1817 | - | case insert_vertex > ManageProBuilder.InsertVertex |
| manage_probuilder.merge_faces | reflection | `Activator.CreateInstance` | Editor/Tools/ProBuilder/ManageProBuilder.cs:428 | - | case merge_faces > ManageProBuilder.MergeFaces > ManageProBuilder.ToTypedFaceList |
| manage_probuilder.merge_faces | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.merge_faces | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case merge_faces > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.merge_faces | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case merge_faces > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.merge_faces | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:1355 | - | case merge_faces > ManageProBuilder.MergeFaces |
| manage_probuilder.merge_objects | reflection | `Activator.CreateInstance` | Editor/Tools/ProBuilder/ManageProBuilder.cs:1507 | - | case merge_objects > ManageProBuilder.MergeObjects |
| manage_probuilder.merge_objects | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case merge_objects > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_probuilder.merge_objects | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.merge_objects | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case merge_objects > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.merge_objects | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case merge_objects > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.merge_objects | instantiate | `.AddComponent` | Editor/Tools/ProBuilder/ManageProBuilder.cs:1440 | - | case merge_objects > ManageProBuilder.MergeObjects > ManageProBuilder.ConvertToProBuilderInternal |
| manage_probuilder.merge_objects | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:1504 | - | case merge_objects > ManageProBuilder.MergeObjects |
| manage_probuilder.merge_vertices | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.merge_vertices | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case merge_vertices > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.merge_vertices | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case merge_vertices > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.merge_vertices | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:1625 | - | case merge_vertices > ManageProBuilder.MergeVertices |
| manage_probuilder.move_vertices | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.move_vertices | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case move_vertices > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.move_vertices | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case move_vertices > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.move_vertices | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:1744 | - | case move_vertices > ManageProBuilder.MoveVertices |
| manage_probuilder.ping | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.repair_mesh | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.repair_mesh | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case repair_mesh > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.repair_mesh | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case repair_mesh > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.repair_mesh | scene_edit | `Undo.RecordObject` | Editor/Tools/ProBuilder/ProBuilderMeshUtils.cs:220 | - | case repair_mesh > ProBuilderMeshUtils.RepairMesh |
| manage_probuilder.select_faces | reflection | `Activator.CreateInstance` | Editor/Tools/ProBuilder/ManageProBuilder.cs:428 | - | case select_faces > ManageProBuilder.SelectFaces > ManageProBuilder.ToTypedFaceList |
| manage_probuilder.select_faces | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.select_faces | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case select_faces > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.select_faces | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case select_faces > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.set_face_color | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.set_face_color | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_face_color > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.set_face_color | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_face_color > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.set_face_color | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:2162 | - | case set_face_color > ManageProBuilder.SetFaceColor |
| manage_probuilder.set_face_material | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.set_face_material | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:2090 | - | case set_face_material > ManageProBuilder.SetFaceMaterial |
| manage_probuilder.set_face_material | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_face_material > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.set_face_material | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:2094 | - | case set_face_material > ManageProBuilder.SetFaceMaterial |
| manage_probuilder.set_face_uvs | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.set_face_uvs | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_face_uvs > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.set_face_uvs | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_face_uvs > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.set_face_uvs | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:2207 | - | case set_face_uvs > ManageProBuilder.SetFaceUVs |
| manage_probuilder.set_pivot | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.set_pivot | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_pivot > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.set_pivot | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_pivot > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.set_pivot | scene_edit | `Undo.RecordObject` | Editor/Tools/ProBuilder/ProBuilderMeshUtils.cs:177 | - | case set_pivot > ProBuilderMeshUtils.SetPivot |
| manage_probuilder.set_pivot | scene_edit | `Undo.RecordObject` | Editor/Tools/ProBuilder/ProBuilderMeshUtils.cs:178 | - | case set_pivot > ProBuilderMeshUtils.SetPivot |
| manage_probuilder.set_pivot | scene_edit | `.position =` | Editor/Tools/ProBuilder/ProBuilderMeshUtils.cs:199 | - | case set_pivot > ProBuilderMeshUtils.SetPivot |
| manage_probuilder.set_smoothing | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.set_smoothing | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_smoothing > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.set_smoothing | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_smoothing > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.set_smoothing | scene_edit | `Undo.RecordObject` | Editor/Tools/ProBuilder/ProBuilderSmoothing.cs:31 | - | case set_smoothing > ProBuilderSmoothing.SetSmoothing |
| manage_probuilder.split_vertices | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.split_vertices | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case split_vertices > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.split_vertices | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case split_vertices > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.split_vertices | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:1699 | - | case split_vertices > ManageProBuilder.SplitVertices |
| manage_probuilder.subdivide | reflection | `Activator.CreateInstance` | Editor/Tools/ProBuilder/ManageProBuilder.cs:428 | - | case subdivide > ManageProBuilder.Subdivide > ManageProBuilder.ToTypedFaceList |
| manage_probuilder.subdivide | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.subdivide | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case subdivide > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.subdivide | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case subdivide > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.subdivide | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:1047 | - | case subdivide > ManageProBuilder.Subdivide |
| manage_probuilder.validate_mesh | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.validate_mesh | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case validate_mesh > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.validate_mesh | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case validate_mesh > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.weld_vertices | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ProBuilder/ManageProBuilder.cs:157 | - | ManageProBuilder.HandleCommand > ManageProBuilder.EnsureProBuilder > ManageProBuilder.PatchProBuilderDefaultMaterial |
| manage_probuilder.weld_vertices | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case weld_vertices > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.weld_vertices | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case weld_vertices > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_probuilder.weld_vertices | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ProBuilder/ManageProBuilder.cs:1663 | - | case weld_vertices > ManageProBuilder.WeldVertices |
| manage_profiler.frame_debugger_disable | none found | - | - | - | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:55 |
| manage_profiler.frame_debugger_enable | menu_item | `EditorApplication.ExecuteMenuItem` | Editor/Tools/Profiler/Operations/FrameDebuggerOps.cs:68 | - | case frame_debugger_enable > FrameDebuggerOps.Enable |
| manage_profiler.frame_debugger_get_events | reflection | `Activator.CreateInstance` | Editor/Tools/Profiler/Operations/FrameDebuggerOps.cs:181 | - | case frame_debugger_get_events > FrameDebuggerOps.GetEvents |
| manage_profiler.get_counters | none found | - | - | - | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:39 |
| manage_profiler.get_frame_timing | none found | - | - | - | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:37 |
| manage_profiler.get_object_memory | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Profiler/Operations/ObjectMemoryOps.cs:38 | - | case get_object_memory > ObjectMemoryOps.GetObjectMemory |
| manage_profiler.memory_compare_snapshots | none found | - | - | - | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:49 |
| manage_profiler.memory_list_snapshots | none found | - | - | - | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:47 |
| manage_profiler.memory_take_snapshot | none found | - | - | - | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:45 |
| manage_profiler.ping | none found | - | - | - | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:61 |
| manage_profiler.profiler_set_areas | none found | - | - | - | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:33 |
| manage_profiler.profiler_start | none found | - | - | - | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:27 |
| manage_profiler.profiler_status | none found | - | - | - | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:31 |
| manage_profiler.profiler_stop | none found | - | - | - | MCPForUnity/Editor/Tools/Profiler/ManageProfiler.cs:29 |
| manage_scene.create | save_scene | `EditorSceneManager.SaveScene` | Editor/Tools/ManageScene.cs:361 | - | case create > ManageScene.CreateScene |
| manage_scene.create | save_scene | `EditorSceneManager.SaveScene` | Editor/Tools/ManageScene.cs:1791 | - | case create > ManageScene.CreateSceneFromTemplate |
| manage_scene.create | scene_switch | `EditorSceneManager.NewScene` | Editor/Tools/ManageScene.cs:356 | - | case create > ManageScene.CreateScene |
| manage_scene.create | scene_switch | `EditorSceneManager.NewScene` | Editor/Tools/ManageScene.cs:1771 | - | case create > ManageScene.CreateSceneFromTemplate |
| manage_scene.create | import_compile | `AssetDatabase.Refresh` | Editor/Tools/ManageScene.cs:365 | - | case create > ManageScene.CreateScene |
| manage_scene.create | instantiate | `GameObject.CreatePrimitive` | Editor/Tools/ManageScene.cs:1775 | template | case create > ManageScene.CreateSceneFromTemplate |
| manage_scene.create | scene_edit | `.position =` | Editor/Tools/ManageScene.cs:1777 | template | case create > ManageScene.CreateSceneFromTemplate |
| manage_scene.load | scene_switch | `EditorSceneManager.OpenScene` | Editor/Tools/ManageScene.cs:404 | - | case load > ManageScene.LoadScene |
| manage_scene.load | scene_switch | `EditorSceneManager.OpenScene` | Editor/Tools/ManageScene.cs:440 | - | case load > ManageScene.LoadScene |
| manage_scene.load | scene_switch | `EditorSceneManager.OpenScene` | Editor/Tools/ManageScene.cs:1654 | - | case load > ManageScene.LoadSceneAdditive |
| manage_scene.load | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageScene.cs:1630 | - | case load > ManageScene.LoadSceneAdditive > ManageScene.SceneAssetExists |
| manage_scene.save | save_scene | `EditorSceneManager.SaveScene` | Editor/Tools/ManageScene.cs:480 | - | case save > ManageScene.SaveScene |
| manage_scene.save | save_scene | `EditorSceneManager.SaveScene` | Editor/Tools/ManageScene.cs:493 | - | case save > ManageScene.SaveScene |
| manage_scene.save | import_compile | `AssetDatabase.Refresh` | Editor/Tools/ManageScene.cs:498 | - | case save > ManageScene.SaveScene |
| manage_scene.get_hierarchy | none found | - | - | - | MCPForUnity/Editor/Tools/ManageScene.cs:273 |
| manage_scene.get_active | none found | - | - | - | MCPForUnity/Editor/Tools/ManageScene.cs:278 |
| manage_scene.get_build_settings | none found | - | - | - | MCPForUnity/Editor/Tools/ManageScene.cs:283 |
| manage_scene.scene_view_frame | none found | - | - | - | MCPForUnity/Editor/Tools/ManageScene.cs:287 |
| manage_scene.close_scene | scene_switch | `EditorSceneManager.CloseScene` | Editor/Tools/ManageScene.cs:1677 | - | case close_scene > ManageScene.CloseScene |
| manage_scene.set_active_scene | none found | - | - | - | MCPForUnity/Editor/Tools/ManageScene.cs:293 |
| manage_scene.get_loaded_scenes | none found | - | - | - | MCPForUnity/Editor/Tools/ManageScene.cs:295 |
| manage_scene.move_to_scene | none found | - | - | - | MCPForUnity/Editor/Tools/ManageScene.cs:297 |
| manage_scene.validate | scene_edit | `EditorSceneManager.MarkSceneDirty` | Editor/Tools/ManageScene.cs:1865 | - | case validate > ManageScene.ValidateScene |
| manage_scene.validate | scene_edit | `Undo.RegisterCompleteObjectUndo` | Editor/Tools/ManageScene.cs:1841 | auto_repair | case validate > ManageScene.ValidateScene |
| manage_ui.ping | none found | - | - | - | MCPForUnity/Editor/Tools/ManageUI.cs:60 |
| manage_ui.create | write_file | `File.WriteAllText` | Editor/Tools/ManageUI.cs:187 | - | case create > ManageUI.CreateFile |
| manage_ui.create | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageUI.cs:188 | - | case create > ManageUI.CreateFile |
| manage_ui.create | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageUI.cs:1903 | - | case create > ManageUI.CreateFile > ManageUI.ValidateUxmlPostImport |
| manage_ui.read | none found | - | - | - | MCPForUnity/Editor/Tools/ManageUI.cs:66 |
| manage_ui.update | write_file | `File.WriteAllText` | Editor/Tools/ManageUI.cs:279 | - | case update > ManageUI.UpdateFile |
| manage_ui.update | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageUI.cs:280 | - | case update > ManageUI.UpdateFile |
| manage_ui.update | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageUI.cs:1903 | - | case update > ManageUI.UpdateFile > ManageUI.ValidateUxmlPostImport |
| manage_ui.delete | delete_file | `AssetDatabase.DeleteAsset` | Editor/Tools/ManageUI.cs:1265 | - | case delete > ManageUI.DeleteFile |
| manage_ui.delete | delete_file | `File.Delete` | Editor/Tools/ManageUI.cs:1274 | - | case delete > ManageUI.DeleteFile |
| manage_ui.attach_ui_document | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/ManageUI.cs:508 | not panel_settings | case attach_ui_document > ManageUI.AttachUIDocument > ManageUI.CreateDefaultPanelSettings |
| manage_ui.attach_ui_document | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/ManageUI.cs:507 | not panel_settings | case attach_ui_document > ManageUI.AttachUIDocument > ManageUI.CreateDefaultPanelSettings |
| manage_ui.attach_ui_document | write_file | `AssetDatabase.CreateFolder` | Editor/Tools/ManageUI.cs:701 | not panel_settings | case attach_ui_document > … > ManageUI.CreateDefaultPanelSettings > ManageUI.EnsureFolderExists |
| manage_ui.attach_ui_document | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case attach_ui_document > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_ui.attach_ui_document | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageUI.cs:326 | - | case attach_ui_document > ManageUI.AttachUIDocument |
| manage_ui.attach_ui_document | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageUI.cs:355 | not panel_settings | case attach_ui_document > ManageUI.AttachUIDocument |
| manage_ui.attach_ui_document | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageUI.cs:341 | panel_settings, panel_settings | case attach_ui_document > ManageUI.AttachUIDocument |
| manage_ui.attach_ui_document | instantiate | `Undo.AddComponent` | Editor/Tools/ManageUI.cs:374 | - | case attach_ui_document > ManageUI.AttachUIDocument |
| manage_ui.attach_ui_document | scene_edit | `Undo.RecordObject` | Editor/Tools/ManageUI.cs:368 | - | case attach_ui_document > ManageUI.AttachUIDocument |
| manage_ui.attach_ui_document | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/ManageUI.cs:383 | - | case attach_ui_document > ManageUI.AttachUIDocument |
| manage_ui.detach_ui_document | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case detach_ui_document > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_ui.detach_ui_document | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case detach_ui_document > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_ui.detach_ui_document | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case detach_ui_document > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_ui.detach_ui_document | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case detach_ui_document > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_ui.detach_ui_document | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/ManageUI.cs:1415 | - | case detach_ui_document > ManageUI.DetachUIDocument |
| manage_ui.detach_ui_document | destroy_object | `Undo.DestroyObjectImmediate` | Editor/Tools/ManageUI.cs:1414 | - | case detach_ui_document > ManageUI.DetachUIDocument |
| manage_ui.create_panel_settings | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/ManageUI.cs:456 | - | case create_panel_settings > ManageUI.CreatePanelSettings |
| manage_ui.create_panel_settings | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/ManageUI.cs:508 | - | case create_panel_settings > ManageUI.CreatePanelSettings > ManageUI.CreateDefaultPanelSettings |
| manage_ui.create_panel_settings | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/ManageUI.cs:507 | - | case create_panel_settings > ManageUI.CreatePanelSettings > ManageUI.CreateDefaultPanelSettings |
| manage_ui.create_panel_settings | write_file | `AssetDatabase.CreateFolder` | Editor/Tools/ManageUI.cs:701 | - | case create_panel_settings > … > ManageUI.CreateDefaultPanelSettings > ManageUI.EnsureFolderExists |
| manage_ui.create_panel_settings | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageUI.cs:414 | - | case create_panel_settings > ManageUI.CreatePanelSettings |
| manage_ui.create_panel_settings | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageUI.cs:596 | - | case create_panel_settings > ManageUI.CreatePanelSettings > ManageUI.ApplyPanelSettingsProperties |
| manage_ui.create_panel_settings | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/ManageUI.cs:455 | - | case create_panel_settings > ManageUI.CreatePanelSettings |
| manage_ui.update_panel_settings | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/ManageUI.cs:492 | - | case update_panel_settings > ManageUI.UpdatePanelSettings |
| manage_ui.update_panel_settings | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageUI.cs:477 | - | case update_panel_settings > ManageUI.UpdatePanelSettings |
| manage_ui.update_panel_settings | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageUI.cs:596 | - | case update_panel_settings > ManageUI.UpdatePanelSettings > ManageUI.ApplyPanelSettingsProperties |
| manage_ui.update_panel_settings | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/ManageUI.cs:491 | - | case update_panel_settings > ManageUI.UpdatePanelSettings |
| manage_ui.get_visual_tree | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case get_visual_tree > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_ui.get_visual_tree | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case get_visual_tree > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_ui.get_visual_tree | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case get_visual_tree > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_ui.get_visual_tree | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case get_visual_tree > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_ui.render_ui | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/ManageUI.cs:1064 | - | case render_ui > ManageUI.RenderUI |
| manage_ui.render_ui | save_assets | `AssetDatabase.SaveAssets` | Editor/Tools/ManageUI.cs:508 | not target | case render_ui > ManageUI.RenderUI > ManageUI.CreateDefaultPanelSettings |
| manage_ui.render_ui | delete_file | `AssetDatabase.DeleteAsset` | Editor/Tools/ManageUI.cs:1045 | - | case render_ui > ManageUI.RenderUI |
| manage_ui.render_ui | delete_file | `AssetDatabase.DeleteAsset` | Editor/Tools/ManageUI.cs:1182 | - | case render_ui > ManageUI.RenderUI |
| manage_ui.render_ui | write_file | `.EncodeToPNG` | Editor/Tools/ManageUI.cs:1115 | - | case render_ui > ManageUI.RenderUI |
| manage_ui.render_ui | write_file | `.EncodeToPNG` | Editor/Tools/ManageUI.cs:1148 | include_image | case render_ui > ManageUI.RenderUI |
| manage_ui.render_ui | write_file | `AssetDatabase.CreateAsset` | Editor/Tools/ManageUI.cs:507 | not target | case render_ui > ManageUI.RenderUI > ManageUI.CreateDefaultPanelSettings |
| manage_ui.render_ui | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageUI.cs:1120 | - | case render_ui > ManageUI.RenderUI |
| manage_ui.render_ui | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageUI.cs:883 | - | case render_ui > ManageUI.RenderUI |
| manage_ui.render_ui | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | target | case render_ui > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_ui.render_ui | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/ManageUI.cs:984 | not target | case render_ui > ManageUI.RenderUI |
| manage_ui.render_ui | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | target | case render_ui > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_ui.render_ui | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | target | case render_ui > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_ui.render_ui | instantiate | `.AddComponent` | Runtime/Helpers/ScreenshotUtility.cs:777 | - | case render_ui > ManageUI.RenderUI > ScreenshotCapturer.Begin |
| manage_ui.render_ui | instantiate | `.AddComponent` | Editor/Tools/ManageUI.cs:990 | not target | case render_ui > ManageUI.RenderUI |
| manage_ui.render_ui | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/ManageUI.cs:1072 | - | case render_ui > ManageUI.RenderUI |
| manage_ui.render_ui | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/ManageUI.cs:1093 | - | case render_ui > ManageUI.RenderUI |
| manage_ui.render_ui | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/ManageUI.cs:1033 | - | case render_ui > ManageUI.RenderUI |
| manage_ui.render_ui | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageUI.cs:1047 | - | case render_ui > ManageUI.RenderUI |
| manage_ui.render_ui | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageUI.cs:918 | include_image | case render_ui > ManageUI.RenderUI |
| manage_ui.render_ui | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageUI.cs:1165 | - | case render_ui > ManageUI.RenderUI |
| manage_ui.render_ui | destroy_object | `Object.DestroyImmediate` | Editor/Tools/ManageUI.cs:1161 | include_image | case render_ui > ManageUI.RenderUI |
| manage_ui.link_stylesheet | write_file | `File.WriteAllText` | Editor/Tools/ManageUI.cs:1239 | - | case link_stylesheet > ManageUI.LinkStylesheet |
| manage_ui.link_stylesheet | import_compile | `AssetDatabase.ImportAsset` | Editor/Tools/ManageUI.cs:1240 | - | case link_stylesheet > ManageUI.LinkStylesheet |
| manage_ui.list | none found | - | - | - | MCPForUnity/Editor/Tools/ManageUI.cs:93 |
| manage_ui.modify_visual_element | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case modify_visual_element > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_ui.modify_visual_element | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case modify_visual_element > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_ui.modify_visual_element | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case modify_visual_element > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_ui.modify_visual_element | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case modify_visual_element > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_ui.modify_visual_element | scene_edit | `Undo.RecordObject` | Editor/Tools/Animation/AnimatorControl.cs:218 | enabled | case modify_visual_element > ManageUI.ModifyVisualElement > AnimatorControl.SetEnabled |
| manage_vfx.add_burst | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case add_burst > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.add_burst | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case add_burst > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.add_burst | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case add_burst > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.add_burst | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/ParticleControl.cs:186 | - | case add_burst > ParticleControl.AddBurst |
| manage_vfx.add_burst | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/ParticleControl.cs:206 | - | case add_burst > ParticleControl.AddBurst |
| manage_vfx.add_burst | scene_edit | `Undo.RecordObject` | Editor/Helpers/RendererHelpers.cs:61 | - | case add_burst > ParticleControl.AddBurst > RendererHelpers.EnsureMaterial |
| manage_vfx.add_position | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case add_position > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.add_position | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case add_position > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.add_position | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case add_position > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.add_position | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/LineWrite.cs:44 | - | case add_position > LineWrite.AddPosition |
| manage_vfx.add_position | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/LineWrite.cs:48 | - | case add_position > LineWrite.AddPosition |
| manage_vfx.add_position | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/LineWrite.cs:65 | - | case add_position > LineWrite.AddPosition > LineWrite.SetPosition |
| manage_vfx.assign_asset | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Vfx/VfxGraphAssets.cs:270 | - | case assign_asset > VfxGraphAssets.AssignAsset |
| manage_vfx.assign_asset | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case assign_asset > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.assign_asset | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case assign_asset > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.assign_asset | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/VfxGraphAssets.cs:288 | - | case assign_asset > VfxGraphAssets.AssignAsset |
| manage_vfx.assign_asset | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/VfxGraphAssets.cs:290 | - | case assign_asset > VfxGraphAssets.AssignAsset |
| manage_vfx.clear | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.clear | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.clear | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.clear | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/LineWrite.cs:182 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > ManageVFX.HandleLineRendererAction > LineWrite.Clear |
| manage_vfx.clear | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/LineWrite.cs:184 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > ManageVFX.HandleLineRendererAction > LineWrite.Clear |
| manage_vfx.clear | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/TrailControl.cs:15 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > ManageVFX.HandleTrailRendererAction > TrailControl.Clear |
| manage_vfx.clear_bursts | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case clear_bursts > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.clear_bursts | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case clear_bursts > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.clear_bursts | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case clear_bursts > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.clear_bursts | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/ParticleControl.cs:222 | - | case clear_bursts > ParticleControl.ClearBursts |
| manage_vfx.clear_bursts | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/ParticleControl.cs:227 | - | case clear_bursts > ParticleControl.ClearBursts |
| manage_vfx.create | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case create > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_vfx.create | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case create > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.create | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case create > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.create | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case create > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.create | instantiate | `.AddComponent` | Editor/Tools/Vfx/ParticleControl.cs:58 | - | case create > ParticleControl.Create |
| manage_vfx.create | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/ParticleControl.cs:82 | - | case create > ParticleControl.Create |
| manage_vfx.create | scene_edit | `.position =` | Editor/Tools/Vfx/ParticleControl.cs:44 | - | case create > ParticleControl.Create |
| manage_vfx.create | scene_edit | `.eulerAngles =` | Editor/Tools/Vfx/ParticleControl.cs:48 | - | case create > ParticleControl.Create |
| manage_vfx.create_arc | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case create_arc > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.create_arc | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case create_arc > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.create_arc | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case create_arc > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.create_arc | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/LineCreate.cs:119 | - | case create_arc > LineCreate.CreateArc |
| manage_vfx.create_arc | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/LineCreate.cs:153 | - | case create_arc > LineCreate.CreateArc |
| manage_vfx.create_arc | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/LineWrite.cs:65 | - | case create_arc > LineCreate.CreateArc > LineWrite.SetPosition |
| manage_vfx.create_asset | delete_file | `AssetDatabase.DeleteAsset` | Editor/Tools/Vfx/VfxGraphAssets.cs:88 | - | case create_asset > VfxGraphAssets.CreateAsset |
| manage_vfx.create_asset | write_file | `AssetDatabase.CopyAsset` | Editor/Tools/Vfx/VfxGraphAssets.cs:99 | - | case create_asset > VfxGraphAssets.CreateAsset |
| manage_vfx.create_asset | write_file | `AssetDatabase.CreateFolder` | Editor/Tools/Vfx/VfxGraphAssets.cs:72 | - | case create_asset > VfxGraphAssets.CreateAsset |
| manage_vfx.create_asset | import_compile | `AssetDatabase.Refresh` | Editor/Tools/Vfx/VfxGraphAssets.cs:103 | - | case create_asset > VfxGraphAssets.CreateAsset |
| manage_vfx.create_asset | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Vfx/VfxGraphAssets.cs:81 | - | case create_asset > VfxGraphAssets.CreateAsset |
| manage_vfx.create_asset | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Vfx/VfxGraphAssets.cs:104 | - | case create_asset > VfxGraphAssets.CreateAsset |
| manage_vfx.create_bezier | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case create_bezier > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.create_bezier | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case create_bezier > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.create_bezier | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case create_bezier > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.create_bezier | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/LineCreate.cs:171 | - | case create_bezier > LineCreate.CreateBezier |
| manage_vfx.create_bezier | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/LineCreate.cs:216 | - | case create_bezier > LineCreate.CreateBezier |
| manage_vfx.create_bezier | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/LineWrite.cs:65 | - | case create_bezier > LineCreate.CreateBezier > LineWrite.SetPosition |
| manage_vfx.create_circle | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case create_circle > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.create_circle | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case create_circle > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.create_circle | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case create_circle > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.create_circle | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/LineCreate.cs:65 | - | case create_circle > LineCreate.CreateCircle |
| manage_vfx.create_circle | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/LineCreate.cs:98 | - | case create_circle > LineCreate.CreateCircle |
| manage_vfx.create_circle | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/LineWrite.cs:65 | - | case create_circle > LineCreate.CreateCircle > LineWrite.SetPosition |
| manage_vfx.create_line | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case create_line > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.create_line | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case create_line > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.create_line | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case create_line > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.create_line | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/LineCreate.cs:18 | - | case create_line > LineCreate.CreateLine |
| manage_vfx.create_line | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/LineCreate.cs:45 | - | case create_line > LineCreate.CreateLine |
| manage_vfx.create_line | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/LineWrite.cs:65 | - | case create_line > LineCreate.CreateLine > LineWrite.SetPosition |
| manage_vfx.emit | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case emit > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.emit | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case emit > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.emit | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case emit > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.emit | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/LineWrite.cs:44 | - | case emit > TrailControl.Emit > LineWrite.AddPosition |
| manage_vfx.emit | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/LineWrite.cs:48 | - | case emit > TrailControl.Emit > LineWrite.AddPosition |
| manage_vfx.emit | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/LineWrite.cs:65 | - | case emit > … > LineWrite.AddPosition > LineWrite.SetPosition |
| manage_vfx.enable_module | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case enable_module > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.enable_module | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case enable_module > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.enable_module | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case enable_module > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.enable_module | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/ParticleControl.cs:111 | - | case enable_module > ParticleControl.EnableModule |
| manage_vfx.enable_module | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/ParticleControl.cs:127 | - | case enable_module > ParticleControl.EnableModule |
| manage_vfx.get_info | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.get_info | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.get_info | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.list_assets | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Tools/Vfx/VfxGraphAssets.cs:462 | - | case list_assets > VfxGraphAssets.ListAssets |
| manage_vfx.list_templates | none found | - | - | - | MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:343 |
| manage_vfx.pause | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.pause | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.pause | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.pause | scene_edit | `Undo.RecordObject` | Editor/Helpers/RendererHelpers.cs:61 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ParticleControl.Control > RendererHelpers.EnsureMaterial |
| manage_vfx.pause | scene_edit | `EditorUtility.SetDirty` | Editor/Helpers/RendererHelpers.cs:63 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ParticleControl.Control > RendererHelpers.EnsureMaterial |
| manage_vfx.play | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.play | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.play | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.play | scene_edit | `Undo.RecordObject` | Editor/Helpers/RendererHelpers.cs:61 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ParticleControl.Control > RendererHelpers.EnsureMaterial |
| manage_vfx.play | scene_edit | `EditorUtility.SetDirty` | Editor/Helpers/RendererHelpers.cs:63 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ParticleControl.Control > RendererHelpers.EnsureMaterial |
| manage_vfx.reinit | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case reinit > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.reinit | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case reinit > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.reinit | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case reinit > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.restart | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case restart > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.restart | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case restart > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.restart | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case restart > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.restart | scene_edit | `Undo.RecordObject` | Editor/Helpers/RendererHelpers.cs:61 | - | case restart > ParticleControl.Control > RendererHelpers.EnsureMaterial |
| manage_vfx.restart | scene_edit | `EditorUtility.SetDirty` | Editor/Helpers/RendererHelpers.cs:63 | - | case restart > ParticleControl.Control > RendererHelpers.EnsureMaterial |
| manage_vfx.send_event | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case send_event > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.send_event | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case send_event > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.send_event | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case send_event > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_bool | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_bool > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_bool | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_bool > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_bool | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_bool > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_bool | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/VfxGraphWrite.cs:96 | - | case set_bool > VfxGraphWrite.SetParameter |
| manage_vfx.set_bool | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/VfxGraphWrite.cs:98 | - | case set_bool > VfxGraphWrite.SetParameter |
| manage_vfx.set_color | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_color | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_color | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_color | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/LineWrite.cs:106 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > ManageVFX.HandleLineRendererAction > LineWrite.SetColor |
| manage_vfx.set_color | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/LineWrite.cs:98 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > ManageVFX.HandleLineRendererAction > LineWrite.SetColor |
| manage_vfx.set_color | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/TrailWrite.cs:54 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > ManageVFX.HandleTrailRendererAction > TrailWrite.SetColor |
| manage_vfx.set_color_over_lifetime | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_color_over_lifetime > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_color_over_lifetime | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_color_over_lifetime > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_color_over_lifetime | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_color_over_lifetime > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_color_over_lifetime | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/ParticleWrite.cs:119 | - | case set_color_over_lifetime > ParticleWrite.SetColorOverLifetime |
| manage_vfx.set_color_over_lifetime | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/ParticleWrite.cs:126 | - | case set_color_over_lifetime > ParticleWrite.SetColorOverLifetime |
| manage_vfx.set_color_over_lifetime | scene_edit | `Undo.RecordObject` | Editor/Helpers/RendererHelpers.cs:61 | - | case set_color_over_lifetime > … > ParticleWrite.EnsureParticleRendererMaterial > RendererHelpers.EnsureMaterial |
| manage_vfx.set_curve | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_curve > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_curve | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_curve > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_curve | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_curve > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_curve | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/VfxGraphWrite.cs:253 | - | case set_curve > VfxGraphWrite.SetCurve |
| manage_vfx.set_curve | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/VfxGraphWrite.cs:255 | - | case set_curve > VfxGraphWrite.SetCurve |
| manage_vfx.set_emission | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_emission > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_emission | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_emission > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_emission | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_emission > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_emission | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/ParticleWrite.cs:73 | - | case set_emission > ParticleWrite.SetEmission |
| manage_vfx.set_emission | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/ParticleWrite.cs:81 | - | case set_emission > ParticleWrite.SetEmission |
| manage_vfx.set_emission | scene_edit | `Undo.RecordObject` | Editor/Helpers/RendererHelpers.cs:61 | - | case set_emission > … > ParticleWrite.EnsureParticleRendererMaterial > RendererHelpers.EnsureMaterial |
| manage_vfx.set_float | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_float > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_float | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_float > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_float | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_float > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_float | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/VfxGraphWrite.cs:96 | - | case set_float > VfxGraphWrite.SetParameter |
| manage_vfx.set_float | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/VfxGraphWrite.cs:98 | - | case set_float > VfxGraphWrite.SetParameter |
| manage_vfx.set_gradient | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_gradient > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_gradient | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_gradient > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_gradient | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_gradient > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_gradient | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/VfxGraphWrite.cs:173 | - | case set_gradient > VfxGraphWrite.SetGradient |
| manage_vfx.set_gradient | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/VfxGraphWrite.cs:175 | - | case set_gradient > VfxGraphWrite.SetGradient |
| manage_vfx.set_int | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_int > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_int | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_int > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_int | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_int > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_int | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/VfxGraphWrite.cs:96 | - | case set_int > VfxGraphWrite.SetParameter |
| manage_vfx.set_int | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/VfxGraphWrite.cs:98 | - | case set_int > VfxGraphWrite.SetParameter |
| manage_vfx.set_main | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_main > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_main | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_main > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_main | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_main > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_main | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/ParticleWrite.cs:34 | - | case set_main > ParticleWrite.SetMain |
| manage_vfx.set_main | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/ParticleWrite.cs:53 | - | case set_main > ParticleWrite.SetMain |
| manage_vfx.set_main | scene_edit | `Undo.RecordObject` | Editor/Helpers/RendererHelpers.cs:61 | - | case set_main > … > ParticleWrite.EnsureParticleRendererMaterial > RendererHelpers.EnsureMaterial |
| manage_vfx.set_material | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_material | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_material | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_material | scene_edit | `Undo.RecordObject` | Editor/Helpers/RendererHelpers.cs:269 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > LineWrite.SetMaterial > RendererHelpers.SetRendererMaterial |
| manage_vfx.set_material | scene_edit | `EditorUtility.SetDirty` | Editor/Helpers/RendererHelpers.cs:271 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > LineWrite.SetMaterial > RendererHelpers.SetRendererMaterial |
| manage_vfx.set_material | scene_edit | `Undo.RecordObject` | Editor/Helpers/RendererHelpers.cs:256 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > LineWrite.SetMaterial > RendererHelpers.SetRendererMaterial |
| manage_vfx.set_mesh | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case set_mesh > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_vfx.set_mesh | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_mesh > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_mesh | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_mesh > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_mesh | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_mesh > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_mesh | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/VfxGraphWrite.cs:231 | - | case set_mesh > VfxGraphWrite.SetMesh |
| manage_vfx.set_mesh | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/VfxGraphWrite.cs:233 | - | case set_mesh > VfxGraphWrite.SetMesh |
| manage_vfx.set_noise | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_noise > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_noise | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_noise > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_noise | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_noise > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_noise | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/ParticleWrite.cs:196 | - | case set_noise > ParticleWrite.SetNoise |
| manage_vfx.set_noise | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/ParticleWrite.cs:208 | - | case set_noise > ParticleWrite.SetNoise |
| manage_vfx.set_noise | scene_edit | `Undo.RecordObject` | Editor/Helpers/RendererHelpers.cs:61 | - | case set_noise > … > ParticleWrite.EnsureParticleRendererMaterial > RendererHelpers.EnsureMaterial |
| manage_vfx.set_playback_speed | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_playback_speed > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_playback_speed | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_playback_speed > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_playback_speed | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_playback_speed > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_playback_speed | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/VfxGraphControl.cs:62 | - | case set_playback_speed > VfxGraphControl.SetPlaybackSpeed |
| manage_vfx.set_playback_speed | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/VfxGraphControl.cs:64 | - | case set_playback_speed > VfxGraphControl.SetPlaybackSpeed |
| manage_vfx.set_position | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_position > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_position | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_position > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_position | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_position > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_position | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/LineWrite.cs:65 | - | case set_position > LineWrite.SetPosition |
| manage_vfx.set_position | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/LineWrite.cs:67 | - | case set_position > LineWrite.SetPosition |
| manage_vfx.set_position | scene_edit | `Undo.RecordObject` | Editor/Helpers/RendererHelpers.cs:61 | - | case set_position > LineWrite.SetPosition > RendererHelpers.EnsureMaterial |
| manage_vfx.set_positions | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_positions > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_positions | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_positions > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_positions | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_positions > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_positions | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/LineWrite.cs:27 | - | case set_positions > LineWrite.SetPositions |
| manage_vfx.set_positions | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/LineWrite.cs:30 | - | case set_positions > LineWrite.SetPositions |
| manage_vfx.set_positions | scene_edit | `Undo.RecordObject` | Editor/Helpers/RendererHelpers.cs:61 | - | case set_positions > LineWrite.SetPositions > RendererHelpers.EnsureMaterial |
| manage_vfx.set_properties | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_vfx.set_properties | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_properties | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_properties | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_properties | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/LineWrite.cs:123 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > ManageVFX.HandleLineRendererAction > LineWrite.SetProperties |
| manage_vfx.set_properties | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/LineWrite.cs:172 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > ManageVFX.HandleLineRendererAction > LineWrite.SetProperties |
| manage_vfx.set_properties | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/TrailWrite.cs:126 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > ManageVFX.HandleTrailRendererAction > TrailWrite.SetProperties |
| manage_vfx.set_renderer | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case set_renderer > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_vfx.set_renderer | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_renderer > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_renderer | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_renderer > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_renderer | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_renderer > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_renderer | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/ParticleWrite.cs:223 | - | case set_renderer > ParticleWrite.SetRenderer |
| manage_vfx.set_renderer | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/ParticleWrite.cs:272 | - | case set_renderer > ParticleWrite.SetRenderer |
| manage_vfx.set_renderer | scene_edit | `Undo.RecordObject` | Editor/Helpers/RendererHelpers.cs:61 | - | case set_renderer > ParticleWrite.SetRenderer > RendererHelpers.EnsureMaterial |
| manage_vfx.set_seed | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_seed > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_seed | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_seed > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_seed | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_seed > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_seed | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/VfxGraphControl.cs:80 | - | case set_seed > VfxGraphControl.SetSeed |
| manage_vfx.set_seed | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/VfxGraphControl.cs:83 | - | case set_seed > VfxGraphControl.SetSeed |
| manage_vfx.set_shape | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_shape > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_shape | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_shape > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_shape | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_shape > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_shape | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/ParticleWrite.cs:107 | - | case set_shape > ParticleWrite.SetShape |
| manage_vfx.set_shape | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/ParticleWrite.cs:93 | - | case set_shape > ParticleWrite.SetShape |
| manage_vfx.set_shape | scene_edit | `.position =` | Editor/Tools/Vfx/ParticleWrite.cs:103 | - | case set_shape > ParticleWrite.SetShape |
| manage_vfx.set_size_over_lifetime | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_size_over_lifetime > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_size_over_lifetime | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_size_over_lifetime > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_size_over_lifetime | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_size_over_lifetime > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_size_over_lifetime | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/ParticleWrite.cs:138 | - | case set_size_over_lifetime > ParticleWrite.SetSizeOverLifetime |
| manage_vfx.set_size_over_lifetime | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/ParticleWrite.cs:161 | - | case set_size_over_lifetime > ParticleWrite.SetSizeOverLifetime |
| manage_vfx.set_size_over_lifetime | scene_edit | `Undo.RecordObject` | Editor/Helpers/RendererHelpers.cs:61 | - | case set_size_over_lifetime > … > ParticleWrite.EnsureParticleRendererMaterial > RendererHelpers.EnsureMaterial |
| manage_vfx.set_texture | reflection | `method.Invoke` | Runtime/Helpers/UnityAssembliesCompat.cs:117 | - | case set_texture > … > UnityAssembliesCompat.ResolveCurrentAssembliesDelegate > UnityAssembliesCompat.TryBindGetLoadedAssemblies |
| manage_vfx.set_texture | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_texture > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_texture | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_texture > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_texture | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_texture > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_texture | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/VfxGraphWrite.cs:202 | - | case set_texture > VfxGraphWrite.SetTexture |
| manage_vfx.set_texture | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/VfxGraphWrite.cs:204 | - | case set_texture > VfxGraphWrite.SetTexture |
| manage_vfx.set_time | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_time > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_time | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_time > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_time | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_time > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_time | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/TrailWrite.cs:21 | - | case set_time > TrailWrite.SetTime |
| manage_vfx.set_time | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/TrailWrite.cs:23 | - | case set_time > TrailWrite.SetTime |
| manage_vfx.set_time | scene_edit | `Undo.RecordObject` | Editor/Helpers/RendererHelpers.cs:61 | - | case set_time > TrailWrite.SetTime > RendererHelpers.EnsureMaterial |
| manage_vfx.set_vector2 | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_vector2 > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_vector2 | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_vector2 > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_vector2 | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_vector2 > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_vector2 | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/VfxGraphWrite.cs:123 | - | case set_vector2 > VfxGraphWrite.SetVector |
| manage_vfx.set_vector2 | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/VfxGraphWrite.cs:132 | - | case set_vector2 > VfxGraphWrite.SetVector |
| manage_vfx.set_vector3 | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_vector3 > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_vector3 | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_vector3 > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_vector3 | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_vector3 > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_vector3 | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/VfxGraphWrite.cs:123 | - | case set_vector3 > VfxGraphWrite.SetVector |
| manage_vfx.set_vector3 | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/VfxGraphWrite.cs:132 | - | case set_vector3 > VfxGraphWrite.SetVector |
| manage_vfx.set_vector4 | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_vector4 > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_vector4 | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_vector4 > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_vector4 | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_vector4 > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_vector4 | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/VfxGraphWrite.cs:123 | - | case set_vector4 > VfxGraphWrite.SetVector |
| manage_vfx.set_vector4 | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/VfxGraphWrite.cs:132 | - | case set_vector4 > VfxGraphWrite.SetVector |
| manage_vfx.set_velocity_over_lifetime | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | case set_velocity_over_lifetime > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_velocity_over_lifetime | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | case set_velocity_over_lifetime > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_velocity_over_lifetime | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | case set_velocity_over_lifetime > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_velocity_over_lifetime | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/ParticleWrite.cs:173 | - | case set_velocity_over_lifetime > ParticleWrite.SetVelocityOverLifetime |
| manage_vfx.set_velocity_over_lifetime | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/ParticleWrite.cs:184 | - | case set_velocity_over_lifetime > ParticleWrite.SetVelocityOverLifetime |
| manage_vfx.set_velocity_over_lifetime | scene_edit | `Undo.RecordObject` | Editor/Helpers/RendererHelpers.cs:61 | - | case set_velocity_over_lifetime > … > ParticleWrite.EnsureParticleRendererMaterial > RendererHelpers.EnsureMaterial |
| manage_vfx.set_width | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_width | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_width | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.set_width | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/LineWrite.cs:79 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > ManageVFX.HandleLineRendererAction > LineWrite.SetWidth |
| manage_vfx.set_width | scene_edit | `EditorUtility.SetDirty` | Editor/Tools/Vfx/LineWrite.cs:87 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > ManageVFX.HandleLineRendererAction > LineWrite.SetWidth |
| manage_vfx.set_width | scene_edit | `Undo.RecordObject` | Editor/Tools/Vfx/TrailWrite.cs:35 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > ManageVFX.HandleTrailRendererAction > TrailWrite.SetWidth |
| manage_vfx.stop | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:173 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.stop | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:178 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.stop | load_asset | `AssetDatabase.LoadAssetAtPath` | Editor/Helpers/ObjectResolver.cs:188 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ObjectResolver.Resolve > ObjectResolver.TryLoadAsset |
| manage_vfx.stop | scene_edit | `Undo.RecordObject` | Editor/Helpers/RendererHelpers.cs:61 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ParticleControl.Control > RendererHelpers.EnsureMaterial |
| manage_vfx.stop | scene_edit | `EditorUtility.SetDirty` | Editor/Helpers/RendererHelpers.cs:63 | - | ManageVFX.HandleCommand (action not resolved: every action's effects) > … > ParticleControl.Control > RendererHelpers.EnsureMaterial |
| run_tests | save_scene | `EditorSceneManager.SaveScene` | Editor/Services/TestRunnerService.cs:569 | - | RunTests.HandleCommand > … > TestRunnerService.RunTestsAsync > TestRunnerService.SaveDirtyScenesIfNeeded |
| run_tests | delete_file | `File.Delete` | Editor/Services/TestRunnerService.cs:91 | - | RunTests.HandleCommand > … > TestRunnerService.RestoreEnterPlayModeOptions > PlayModeOptionsGuard.Clear |
| run_tests | write_file | `File.WriteAllText` | Editor/Services/TestRunnerService.cs:63 | mode | RunTests.HandleCommand > … > TestRunnerService.EnsurePlayModeRunsWithoutDomainReload > PlayModeOptionsGuard.Save |
| run_tests | run_tests | `new ExecutionSettings` | Editor/Services/TestRunnerService.cs:267 | - | RunTests.HandleCommand > TestJobManager.StartJob > TestRunnerService.RunTestsAsync |
| run_tests | editor_prefs | `EditorPrefs.SetInt` | Editor/Services/TestRunnerNoThrottle.cs:97 | mode | RunTests.HandleCommand > … > TestRunnerNoThrottle.ApplyNoThrottlingPreemptive > TestRunnerNoThrottle.ApplyNoThrottling |
| run_tests | editor_prefs | `EditorPrefs.SetInt` | Editor/Services/TestRunnerNoThrottle.cs:98 | mode | RunTests.HandleCommand > … > TestRunnerNoThrottle.ApplyNoThrottlingPreemptive > TestRunnerNoThrottle.ApplyNoThrottling |
| get_test_job | none found | - | - | - | HandleCommand |
| unity_docs.get_doc | send | `urllib.request` | Server/src/services/tools/unity_docs.py | - | unity_docs |
| unity_docs.get_manual | send | `urllib.request` | Server/src/services/tools/unity_docs.py | - | unity_docs |
| unity_docs.get_package_doc | send | `urllib.request` | Server/src/services/tools/unity_docs.py | - | unity_docs |
| unity_docs.lookup | send | `urllib.request` | Server/src/services/tools/unity_docs.py | - | unity_docs |
