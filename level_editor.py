import bpy
import math
import copy
import gpu
import gpu_extras.batch
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

        indent = ""
        for _ in range(level):
            indent += "\t"

        self.write_and_print(file, indent + obj.type)

        trans, rot, scale = obj.matrix_local.decompose()
        rot = rot.to_euler()

        rot_x = math.degrees(rot.x)
        rot_y = math.degrees(rot.y)
        rot_z = math.degrees(rot.z)

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

        self.write_and_print(
            file,
            indent + "Name %s" % obj.name
        )

        if "file_name" in obj:
            self.write_and_print(
                file,
                indent + "N %s" % obj["file_name"]
            )

        self.write_and_print(file, indent + "END")
        self.write_and_print(file, "")

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

        if "file_name" in obj:
            layout.prop(obj, '["file_name"]', text="FileName")
        else:
            layout.operator(MYADDON_OT_add_filename.bl_idname)


# ==========================================
# コライダー描画クラス
# ==========================================
class DrawCollider:
    """
    3Dビュー上に、各オブジェクトの周りのBoxを描画するクラス
    """

    handle = None

    @staticmethod
    def draw_collider():
        context = bpy.context
        scene = context.scene

        if scene is None:
            return

        # 頂点データ
        vertices = {"pos": []}

        # インデックスデータ
        indices = []

        # 立方体の8頂点分のオフセット
        offsets = [
            [-0.5, -0.5, -0.5],
            [+0.5, -0.5, -0.5],
            [-0.5, +0.5, -0.5],
            [+0.5, +0.5, -0.5],
            [-0.5, -0.5, +0.5],
            [+0.5, -0.5, +0.5],
            [-0.5, +0.5, +0.5],
            [+0.5, +0.5, +0.5],
        ]

        # 今回は一律サイズのBox
        size = [2.0, 2.0, 2.0]

        # シーン内の全オブジェクトを走査
        for obj in scene.objects:
            start = len(vertices["pos"])

            # Boxの8頂点を追加
            for offset in offsets:
                pos = copy.copy(obj.location)

                pos.x += offset[0] * size[0]
                pos.y += offset[1] * size[1]
                pos.z += offset[2] * size[2]

                vertices["pos"].append(pos)

            # 前面の4辺
            indices.append([start + 0, start + 1])
            indices.append([start + 2, start + 3])
            indices.append([start + 0, start + 2])
            indices.append([start + 1, start + 3])

            # 奥面の4辺
            indices.append([start + 4, start + 5])
            indices.append([start + 6, start + 7])
            indices.append([start + 4, start + 6])
            indices.append([start + 5, start + 7])

            # 前面と奥面をつなぐ4辺
            indices.append([start + 0, start + 4])
            indices.append([start + 1, start + 5])
            indices.append([start + 2, start + 6])
            indices.append([start + 3, start + 7])

        if len(vertices["pos"]) == 0 or len(indices) == 0:
            return

        # 単色描画用シェーダー
        shader = gpu.shader.from_builtin("UNIFORM_COLOR")

        # 線描画用バッチを作成
        batch = gpu_extras.batch.batch_for_shader(
            shader,
            "LINES",
            vertices,
            indices=indices
        )

        # 水色
        color = [0.5, 1.0, 1.0, 1.0]

        shader.bind()
        shader.uniform_float("color", color)

        # 描画
        batch.draw(shader)


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

    # 3Dビューにコライダー描画関数を登録
    if DrawCollider.handle is None:
        DrawCollider.handle = bpy.types.SpaceView3D.draw_handler_add(
            DrawCollider.draw_collider,
            (),
            "WINDOW",
            "POST_VIEW"
        )

    print("レベルエディタが有効化されました。")


# ==========================================
# 無効化時の処理
# ==========================================
def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(menu_func)

    # 3Dビューのコライダー描画関数を解除
    if DrawCollider.handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(
            DrawCollider.handle,
            "WINDOW"
        )
        DrawCollider.handle = None

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    print("レベルエディタが無効化されました。")


if __name__ == "__main__":
    register()