import bpy
import math

# ブレンダーに登録するアドオン情報
bl_info = {
    "name": "レベルエディタ",
    "author": "Gento Yoshino",
    "version": (1, 0),
    "blender": (4, 4, 0),
    "location": "Top Bar > MyMenu",
    "description": "レベルエディタ",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}


# ==========================================
# オペレータクラス：頂点を伸ばす
# ==========================================
class MYADDON_OT_stretch_vertex(bpy.types.Operator):
    bl_idname = "myaddon.stretch_vertex"
    bl_label = "頂点を伸ばす"
    bl_description = "頂点座標を引っ張って伸ばします"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = bpy.data.objects.get("Cube")

        if obj is None:
            self.report({'WARNING'}, "Cubeが見つかりません。")
            return {'CANCELLED'}

        if obj.type != 'MESH':
            self.report({'WARNING'}, "Cubeはメッシュオブジェクトではありません。")
            return {'CANCELLED'}

        if obj.data is None or len(obj.data.vertices) == 0:
            self.report({'WARNING'}, "Cubeに頂点がありません。")
            return {'CANCELLED'}

        obj.data.vertices[0].co.x += 1.0
        obj.data.update()

        print("頂点を伸ばしました。")
        self.report({'INFO'}, "頂点を伸ばしました。")

        return {'FINISHED'}


# ==========================================
# オペレータクラス：ICO球生成
# ==========================================
class MYADDON_OT_create_ico_sphere(bpy.types.Operator):
    bl_idname = "myaddon.create_ico_sphere"
    bl_label = "ICO球生成"
    bl_description = "ICO球を生成します"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.mesh.primitive_ico_sphere_add()

        print("ICO球を生成しました。")
        self.report({'INFO'}, "ICO球を生成しました。")

        return {'FINISHED'}


# ==========================================
# オペレータクラス：シーン出力
# ==========================================
class MYADDON_OT_export_scene(bpy.types.Operator):
    bl_idname = "myaddon.export_scene"
    bl_label = "シーン出力"
    bl_description = "現在のシーン内のオブジェクト情報をコンソールに出力します"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene

        if scene is None:
            self.report({'ERROR'}, "有効なシーンがありません。")
            return {'CANCELLED'}

        print("シーン情報をExportします")

        for obj in scene.objects:
            print(f"{obj.type} - {obj.name}")

            trans, rot, scale = obj.matrix_local.decompose()
            rot = rot.to_euler()

            print("Trans({:.6f},{:.6f},{:.6f})".format(
                trans.x,
                trans.y,
                trans.z
            ))

            print("Rot({:.6f},{:.6f},{:.6f})".format(
                math.degrees(rot.x),
                math.degrees(rot.y),
                math.degrees(rot.z)
            ))

            print("Scale({:.6f},{:.6f},{:.6f})".format(
                scale.x,
                scale.y,
                scale.z
            ))

            if obj.parent is not None:
                print(f"Parent:{obj.parent.name}")

            print()

        print("シーン情報をExportしました")
        self.report({'INFO'}, "シーン情報をExportしました")

        return {'FINISHED'}


# ==========================================
# メニュークラス
# ==========================================
class TOPBAR_MT_my_menu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_my_menu"
    bl_label = "MyMenu"
    bl_description = "拡張メニュー by " + bl_info["author"]

    def draw(self, context):
        layout = self.layout

        layout.operator(
            MYADDON_OT_stretch_vertex.bl_idname,
            text=MYADDON_OT_stretch_vertex.bl_label
        )

        layout.separator()

        layout.operator(
            MYADDON_OT_create_ico_sphere.bl_idname,
            text=MYADDON_OT_create_ico_sphere.bl_label
        )

        layout.separator()

        layout.operator(
            MYADDON_OT_export_scene.bl_idname,
            text=MYADDON_OT_export_scene.bl_label
        )


# ==========================================
# トップバーにメニューを表示するための関数
# ==========================================
def menu_func(self, context):
    self.layout.menu(TOPBAR_MT_my_menu.bl_idname)


# ==========================================
# 登録するクラスのリスト
# ==========================================
classes = (
    MYADDON_OT_stretch_vertex,
    MYADDON_OT_create_ico_sphere,
    MYADDON_OT_export_scene,
    TOPBAR_MT_my_menu,
)


# ==========================================
# 有効化時の処理
# ==========================================
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_editor_menus.append(menu_func)

    print("レベルエディタが有効化されました。")


# ==========================================
# 無効化時の処理
# ==========================================
def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(menu_func)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    print("レベルエディタが無効化されました。")


if __name__ == "__main__":
    register()