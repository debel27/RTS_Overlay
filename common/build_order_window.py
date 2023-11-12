import os
import webbrowser
import subprocess
from functools import partial

from PySide6.QtWidgets import QMainWindow, QPushButton, QLineEdit
from PySide6.QtWidgets import QTextEdit, QLabel, QComboBox
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt, QSize

from common.useful_tools import set_background_opacity, widget_x_end, widget_y_end, list_directory_files


def open_website(website_link):
    """Open the build order website

    Parameters
    ----------
    website_link    link to the website to open
    """
    if website_link is not None:
        webbrowser.open(website_link)


class BuildOrderWindow(QMainWindow):
    """Window to add a new build order"""

    def __init__(self, parent, game_icon: str, build_order_folder: str, font_police: str, font_size: int,
                 color_font: list, color_background: list, opacity: float, border_size: int,
                 edit_width: int, edit_height: int, edit_init_text: str, button_margin: int,
                 vertical_spacing: int, horizontal_spacing: int, build_order_websites: list,
                 directory_game_pictures: str, directory_common_pictures: str, icon_bo_write_size: list):
        """Constructor

        Parameters
        ----------
        parent                       parent window
        game_icon                    icon of the game
        build_order_folder           folder where the build orders are saved
        font_police                  font police type
        font_size                    font size
        color_font                   color of the font
        color_background             color of the background
        opacity                      opacity of the window
        border_size                  size of the borders
        edit_width                   width for the build order text input
        edit_height                  height for the build order text input
        edit_init_text               initial text for the build order text input
        button_margin                margin from text to button border
        vertical_spacing             vertical spacing between the elements
        horizontal_spacing           horizontal spacing between the elements
        build_order_websites         list of website elements as [[button name 0, website link 0], [...]],
                                     (each item contains these 2 elements)
        directory_game_pictures      directory where the game pictures are located
        directory_common_pictures    directory where the common pictures are located
        icon_bo_write_size           size of the BO writing helper icons
        """
        super().__init__()

        self.border_size = border_size
        self.vertical_spacing = vertical_spacing
        self.directory_game_pictures = directory_game_pictures
        self.directory_common_pictures = directory_common_pictures

        # style to apply on the different parts
        self.style_description = f'color: rgb({color_font[0]}, {color_font[1]}, {color_font[2]})'
        self.style_text_edit = 'QWidget{' + self.style_description + '; border: 1px solid white}'
        self.style_button = 'QWidget{' + self.style_description + '; border: 1px solid white; padding: ' + str(
            button_margin) + 'px}'

        # text input for the build order
        self.text_input = QTextEdit(self)
        self.text_input.setPlainText(edit_init_text)
        self.text_input.setFont(QFont(font_police, font_size))
        self.text_input.setStyleSheet(self.style_text_edit)
        self.text_input.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.text_input.resize(edit_width, edit_height)
        self.text_input.move(border_size, border_size)
        self.text_input.show()
        self.max_width = border_size + self.text_input.width()

        # button to add build order
        self.update_button = QPushButton('Add build order', self)
        self.update_button.setFont(QFont(font_police, font_size))
        self.update_button.setStyleSheet(self.style_button)
        self.update_button.adjustSize()
        self.update_button.move(border_size, border_size + self.text_input.height() + vertical_spacing)
        self.update_button.clicked.connect(parent.add_build_order)
        self.update_button.show()

        # button to open build order folder
        self.folder_button = QPushButton('Open build orders folder', self)
        self.folder_button.setFont(QFont(font_police, font_size))
        self.folder_button.setStyleSheet(self.style_button)
        self.folder_button.adjustSize()
        self.folder_button.move(
            widget_x_end(self.update_button) + horizontal_spacing, self.update_button.y())
        self.folder_button.clicked.connect(lambda: subprocess.run(['explorer', build_order_folder]))
        self.folder_button.show()
        self.max_width = max(self.max_width, widget_x_end(self.folder_button))

        # open build order website(s)
        website_button_x = widget_x_end(self.folder_button) + horizontal_spacing
        for build_order_website in build_order_websites:
            if len(build_order_website) == 2:
                assert isinstance(build_order_website[0], str) and isinstance(build_order_website[1], str)
                website_link = build_order_website[1]
                website_button = QPushButton(build_order_website[0], self)
                website_button.setFont(QFont(font_police, font_size))
                website_button.setStyleSheet(self.style_button)
                website_button.adjustSize()
                website_button.move(website_button_x, self.folder_button.y())
                website_button.clicked.connect(partial(open_website, website_link))
                website_button.show()
                website_button_x += website_button.width() + horizontal_spacing
                self.max_width = max(self.max_width, widget_x_end(website_button))

        # BO writer helper: get list of icons
        raw_icons_list = dict()  # raw list of pictures
        raw_icons_list['game'] = list_directory_files(directory=directory_game_pictures,
                                                      extension=['.png', '.jpg'], recursive=True)
        raw_icons_list['common'] = list_directory_files(directory=directory_common_pictures,
                                                        extension=['.png', '.jpg'], recursive=True)

        self.icons_list = dict()  # divide in sub-classes
        for key, sub_raw_icons_list in raw_icons_list.items():
            directory_pictures = directory_game_pictures if (key == 'game') else directory_common_pictures

            self.icons_list[key] = dict()
            sub_icons_list = self.icons_list[key]

            for raw_icon in sub_raw_icons_list:  # loop on the icons
                file_name = os.path.relpath(raw_icon, directory_pictures)
                dir_name = os.path.relpath(os.path.dirname(raw_icon), directory_pictures)
                if dir_name in sub_icons_list:
                    sub_icons_list[dir_name].append(file_name)
                else:
                    sub_icons_list[dir_name] = [file_name]

        self.max_y = widget_y_end(self.update_button)
        self.combobox = QComboBox(self)
        self.combobox_dict = dict()
        self.combobox.addItem('-- Select category --')
        self.combobox_dict[self.combobox.count() - 1] = None

        for section_1, values in self.icons_list.items():

            label_section_1 = QLabel(section_1.replace('_', ' ').capitalize(), self)
            label_section_1.setFont(QFont(font_police, font_size))
            label_section_1.setStyleSheet(self.style_description)
            label_section_1.adjustSize()
            label_section_1.move(border_size, self.max_y + vertical_spacing)
            self.max_y = widget_y_end(label_section_1)
            label_section_1.show()

            for section_2, images in values.items():
                self.combobox.addItem(section_2.replace('_', ' '))
                self.combobox_dict[self.combobox.count() - 1] = {
                    'section_1': section_1,
                    'section_2': section_2,
                    'images': images
                }

        self.combobox.setFont(QFont(font_police, font_size))
        self.combobox.setStyleSheet('QWidget{' + self.style_description + '; border: 1px solid white}')
        self.combobox.adjustSize()
        self.combobox.resize(self.combobox.width() + 10, self.combobox.height())
        self.combobox.move(border_size, self.max_y + vertical_spacing)
        # self.combobox.currentIndexChanged.connect(lambda: self.update_icons('Nico'))
        self.combobox.currentIndexChanged.connect(self.update_icons)
        self.max_y = widget_y_end(self.combobox)
        self.combobox.show()

        # game_picture = self.icons_list['game']['unique_unit'][0]
        # image_path = os.path.join(directory_game_pictures, game_picture)
        # image_icon = QPushButton(self)
        # image_icon.setIcon(QIcon(image_path))
        # image_icon.setIconSize(QSize(40, 40))
        # image_icon.resize(QSize(40, 40))
        # image_icon.clicked.connect(partial(self.print_icon_path, game_picture))
        # image_icon.move(border_size, self.max_y + vertical_spacing)
        # self.max_y = widget_y_end(image_icon)
        # image_icon.show()

        self.copy_line = QLineEdit(self)
        self.copy_line.setText('')
        self.copy_line.setFont(QFont(font_police, font_size))
        self.copy_line.setStyleSheet(self.style_description)
        self.copy_line.setReadOnly(True)
        self.copy_line.resize(600, 30)
        self.copy_line.move(border_size, self.max_y + vertical_spacing)
        self.max_y = widget_y_end(self.copy_line)

        # window properties and show
        self.setWindowTitle('New build order')
        self.setWindowIcon(QIcon(game_icon))
        self.resize(self.max_width + self.border_size, self.max_y + self.border_size)
        set_background_opacity(self, color_background, opacity)
        self.show()

    def closeEvent(self, _):
        """Called when clicking on the cross icon (closing window icon)"""
        super().close()

    def update_icons(self):
        combobox_id = self.combobox.currentIndex()
        assert 0 <= combobox_id < len(self.combobox_dict)
        data = self.combobox_dict[combobox_id]
        for game_picture in data['images']:
            root_folder = self.directory_game_pictures if data[
                                                              'section_1'] == 'game' else self.directory_common_pictures
            image_path = os.path.join(root_folder, game_picture)
            image_icon = QPushButton(self)
            image_icon.setIcon(QIcon(image_path))
            image_icon.setIconSize(QSize(40, 40))
            image_icon.resize(QSize(40, 40))
            image_icon.clicked.connect(partial(self.print_icon_path, game_picture))
            image_icon.move(self.border_size, self.max_y + self.vertical_spacing)
            self.max_y = widget_y_end(image_icon)
            image_icon.show()
        self.resize(self.max_width + self.border_size, self.max_y + self.border_size)

    def print_icon_path(self, test):
        name = '@' + test.replace('\\', '/') + '@'
        self.copy_line.setText(name)
