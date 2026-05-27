import bpy

# ブレンダーに登録するアドオン情報
bl_info = {
    "name": "レベルエディタ",
    "author": "Taro Kamata",
    "version": (1, 0),
    "blender": (4, 4, 0),
    "location": "",
    "description": "レベルエディタ",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}

# ==========================================
# サブメニュークラス
# ==========================================
class TOPBAR_MT_my_menu(bpy.types.Menu):
    # Blenderがクラスを識別するための固有の文字列
    bl_idname = "TOPBAR_MT_my_menu"
    # メニューのラベルとして表示される文字列
    bl_label = "MyMenu"
    # 著者表示用の文字列
    bl_description = "拡張メニュー by " +  bl_info["author"]
    
    # サブメニューの描画
    def draw(self, context):
        # トップバーの「エディターメニュー」に項目(オペレーター)を追加
        self.layout.operator("wm.url_open_preset", text="Manual", icon='HELP')
        
    # 既存のメニューにサブメニューを追加
    def submenu(self, context):
        # ID指定でサブメニューを追加
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)


# ==========================================
# 登録するクラスのリスト
# ==========================================
classes = (
    TOPBAR_MT_my_menu,
)

# ==========================================
# サブメニュークラス
# ==========================================
class TOPBAR_MT_my_menu(bpy.types.Menu):
    # Blenderがクラスを識別するための固有の文字列
    bl_idname = "TOPBAR_MT_my_menu"
    # メニューのラベルとして表示される文字列
    bl_label = "MyMenu"
    # 著者表示用の文字列
    bl_description = "拡張メニュー by " +  bl_info["author"]
    
    # サブメニューの描画
    def draw(self, context):
        self.layout.operator("wm.url_open_preset", text="Manual", icon='HELP')
        self.layout.operator("wm.url_open_preset", text="Manual", icon='HELP')
        
        # 区切り線
        self.layout.separator()
        
        self.layout.operator("wm.url_open_preset", text="Manual", icon='HELP')
        
        # 区切り線
        self.layout.separator()
        
        self.layout.operator("wm.url_open_preset", text="Manual", icon='HELP')
        
    # 既存のメニューにサブメニューを追加
    def submenu(self, context):
        # ID指定でサブメニューを追加
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)


# ==========================================
# 有効化時の処理
# ==========================================
def register():
    # Blenderにクラスを登録
    for cls in classes:
        bpy.utils.register_class(cls)

    # メニューに項目を追加（TOPBAR_MT_my_menu.submenu を指定）
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_my_menu.submenu)
    print("レベルエディタが有効化されました。")


# ==========================================
# 無効化時の処理
# ==========================================
def unregister():
    # メニューから項目を削除
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_my_menu.submenu)

    # クラスの登録解除
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    print("レベルエディタが無効化されました。")
    
    
if __name__ == "__main__":
    register()