import wx
import cv2
import numpy as np
import matplotlib.pyplot as plt
import mplcursors
import argparse

class MyPanel(wx.Panel):
    def __init__(self, parent, image_file_path):
        super().__init__(parent)

        self.image_ctrl = wx.StaticBitmap(self)
        self.image = None
        self.image_path = image_file_path

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.image_ctrl, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_SIZE, self.on_resize)
        if image_file_path != "":
            self.load_image(image_file_path)

    def load_image(self, path):
        image = wx.Image(path, wx.BITMAP_TYPE_ANY)
        self.image = image.ConvertToBitmap()
        self.image_ctrl.SetBitmap(self.image)
        self.resize_image()
        self.image_path = path  # 画像のパスを記録

    def resize_image(self):
        if self.image:
            size = self.image.GetSize()
            client_size = self.GetClientSize()
            ratio_x = client_size.width / size.width
            ratio_y = client_size.height / size.height
            min_ratio = min(ratio_x, ratio_y)
            new_width = int(size.width * min_ratio)
            new_height = int(size.height * min_ratio)
            new_image = self.image.ConvertToImage().Rescale(new_width, new_height, wx.IMAGE_QUALITY_HIGH)
            self.image_ctrl.SetBitmap(wx.Bitmap(new_image))

    def on_browse(self, event):
        with wx.FileDialog(self, 'Select Image File', 
                           wildcard='Image files (*.png;*.bmp;*.tiff;*.jpg)|*.png;*.bmp;*.tiff;*.jpg', 
                           style=wx.FD_OPEN) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.load_image(dialog.GetPath())

    def on_resize(self, event):
        self.resize_image()
        event.Skip()

    def plot_profile(self, event):
        if self.image_path is None:
            wx.MessageBox("Please open an image first.", "Error", wx.OK | wx.ICON_ERROR)
            return

        image = cv2.imread(self.image_path)
        if image is None:
            wx.MessageBox(f"{self.image_path} not found", "Error", wx.OK | wx.ICON_ERROR)
            return

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, _ = image.shape

        x_positions = np.arange(width)

        red_channel_means = np.mean(image[:, :, 0], axis=0)
        green_channel_means = np.mean(image[:, :, 1], axis=0)
        blue_channel_means = np.mean(image[:, :, 2], axis=0)

        fig, ax = plt.subplots(figsize=(10, 5))

        ax.plot(x_positions, red_channel_means, label='Red Channel', color='red')
        ax.plot(x_positions, green_channel_means, label='Green Channel', color='green')
        ax.plot(x_positions, blue_channel_means, label='Blue Channel', color='blue')

        ax.set_xlabel('Horizontal Position')
        ax.set_ylabel('Mean Value')
        ax.set_title(self.image_path)
        ax.legend()

        mplcursors.cursor(hover=True)

        plt.tight_layout()
        plt.legend()
        plt.show()

class MyFrame(wx.Frame):
    def __init__(self, image_file_path):
        super().__init__(None, id=-1, title='MyImgViewer - My Image Viewer')
        self.panel = MyPanel(self, image_file_path)
        self.create_menu()

        self.Show()

    def create_menu(self):
        menu_bar = wx.MenuBar()

        file_menu = wx.Menu()
        open_menu_item = file_menu.Append(wx.ID_OPEN, "Open...", "Open an image file")
        exit_menu_item = file_menu.Append(wx.ID_EXIT, "Quit", "Exit the application")
        menu_bar.Append(file_menu, "File")

        # Imageメニューを作成し、Plot Profile項目を追加
        image_menu = wx.Menu()
        plot_menu_item = image_menu.Append(wx.ID_ANY, "Plot Profile", "Plot profile of the image")
        menu_bar.Append(image_menu, "Image")

        self.Bind(wx.EVT_MENU, self.panel.on_browse, open_menu_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_menu_item)
        self.Bind(wx.EVT_MENU, self.panel.plot_profile, plot_menu_item)

        self.SetMenuBar(menu_bar)

    def on_exit(self, event):
        self.Close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='画像ファイルviewer')

    # image_file位置引数にデフォルト値Noneを設定
    parser.add_argument('image_file', default="", nargs='?', help='表示する画像ファイル')

    args = parser.parse_args()
    image_file_path = args.image_file

    app = wx.App()
    frame = MyFrame(image_file_path)
    app.MainLoop()
