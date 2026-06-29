import bpy
import math
from bpy_extras.io_utils import ExportHelper

# ブレンダーに登録するアドオン情報
bl_info = {
    "name": "レベルエディタ",
    "author": "Gento Yoshino",
    "version": (1, 0),
    "blender": (4, 4, 0),
    "location": "Top Bar > MyMenu / Object Properties > FileName",
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
# オペレータクラス：file_name カスタムプロパティ追加
# ==========================================
class MYADDON_OT_add_filename(bpy.types.Operator):
    bl_idname = "myaddon.add_filename"
    bl_label = "FileName 追加"
    bl_description = "選択中のオブジェクトに file_name カスタムプロパティを追加します"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object

        if obj is None:
            self.report({'WARNING'}, "オブジェクトが選択されていません。")
            return {'CANCELLED'}

        obj["file_name"] = ""

        self.report({'INFO'}, "file_name を追加しました。")
        return {'FINISHED'}


# ==========================================
# オペレータクラス：シーン出力
# ==========================================
class MYADDON_OT_export_scene(bpy.types.Operator, ExportHelper):
    bl_idname = "myaddon.export_scene"
    bl_label = "シーン出力"
    bl_description = "現在のシーン内のオブジェクト情報をファイルに出力します"
    bl_options = {'REGISTER'}

    # 出力ファイルの拡張子
    filename_ext = ".scene"

    def write_and_print(self, file, text):
        """
        コンソール表示とファイル出力を同時に行う関数
        """
        print(text)
        file.write(text)
        file.write("\n")

    def parse_scene_recursive(self, file, obj, level):
        """
        オブジェクトを1つ出力し、その子オブジェクトも再帰的に出力する関数
        """

        # 深さに応じてインデントを作る
        indent = ""
        for _ in range(level):
            indent += "\t"

        # オブジェクト種別を出力
        self.write_and_print(file, indent + obj.type)

        # ローカルトランスフォームを取得
        trans, rot, scale = obj.matrix_local.decompose()
        rot = rot.to_euler()

        # 回転をラジアンから度数に変換
        rot_x = math.degrees(rot.x)
        rot_y = math.degrees(rot.y)
        rot_z = math.degrees(rot.z)

        # トランスフォーム情報を出力
        self.write_and_print(
            file,
            indent + "T %.6f %.6f %.6f" % (
                trans.x,
                trans.y,
                trans.z
            )
        )

        self.write_and_print(
            file,
            indent + "R %.6f %.6f %.6f" % (
                rot_x,
                rot_y,
                rot_z
            )
        )

        self.write_and_print(
            file,
            indent + "S %.6f %.6f %.6f" % (
                scale.x,
                scale.y,
                scale.z
            )
        )

        # デバッグ用にオブジェクト名を出力
        self.write_and_print(
            file,
            indent + "Name %s" % obj.name
        )

        # file_name カスタムプロパティがあれば出力
        if "file_name" in obj:
            self.write_and_print(
                file,
                indent + "N %s" % obj["file_name"]
            )

        self.write_and_print(file, indent + "END")
        self.write_and_print(file, "")

        # 子オブジェクトを再帰的に出力
        for child in obj.children:
            self.parse_scene_recursive(file, child, level + 1)

    def execute(self, context):
        scene = context.scene

        if scene is None:
            self.report({'ERROR'}, "有効なシーンがありません。")
            return {'CANCELLED'}

        if self.filepath == "":
            self.report({'ERROR'}, "出力先ファイルパスが空です。")
            return {'CANCELLED'}

        print("シーン情報をExportします")
        print("シーン情報出力開始... %r" % self.filepath)

        try:
            with open(self.filepath, "w", encoding="utf-8") as file:
                self.write_and_print(file, "SCENE")

                # シーン直下のオブジェクトだけを起点にする
                for obj in scene.objects:
                    if obj.parent is not None:
                        continue

                    self.parse_scene_recursive(file, obj, 0)

        except OSError as error:
            self.report({'ERROR'}, "ファイル出力に失敗しました: " + str(error))
            return {'CANCELLED'}

        print("シーン情報をExportしました")
        self.report({'INFO'}, "シーン情報をExportしました")

        return {'FINISHED'}


# ==========================================
# パネルクラス：file_name 表示・編集
# ==========================================
class OBJECT_PT_file_name(bpy.types.Panel):
    bl_idname = "OBJECT_PT_file_name"
    bl_label = "FileName"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        if obj is None:
            layout.label(text="オブジェクトが選択されていません。")
            return

        # file_name がある場合は編集欄を表示
        if "file_name" in obj:
            layout.prop(obj, '["file_name"]', text="FileName")
        else:
            # file_name がない場合は追加ボタンを表示
            layout.operator(MYADDON_OT_add_filename.bl_idname)


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
    MYADDON_OT_add_filename,
    MYADDON_OT_export_scene,
    OBJECT_PT_file_name,
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