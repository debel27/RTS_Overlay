# AoE4 game overlay
import os

from PyQt5.QtWidgets import QComboBox, QApplication
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QSize

from common.build_order_tools import get_total_on_resource
from common.useful_tools import widget_x_end, widget_y_end
from common.rts_overlay import RTSGameOverlay, scale_list_int, PanelID
from common.build_order_window import BuildOrderWindow

from aoe4.aoe4_settings import AoE4OverlaySettings
from aoe4.aoe4_build_order import check_valid_aoe4_build_order
from aoe4.aoe4_build_order import get_aoe4_build_order_step, get_aoe4_build_order_template
from aoe4.aoe4_civ_icon import aoe4_civilization_icon, get_aoe4_faction_selection


class AoE4GameOverlay(RTSGameOverlay):
    """Game overlay application for AoE4"""

    def __init__(self, app: QApplication, directory_main: str):
        """Constructor

        Parameters
        ----------
        app               main application instance
        directory_main    directory where the main file is located
        """
        super().__init__(app=app, directory_main=directory_main, name_game='aoe4', settings_name='aoe4_settings.json',
                         settings_class=AoE4OverlaySettings, check_valid_build_order=check_valid_aoe4_build_order,
                         get_build_order_step=get_aoe4_build_order_step,
                         get_build_order_template=get_aoe4_build_order_template,
                         get_faction_selection=get_aoe4_faction_selection,
                         build_order_category_name='civilization')

        # build order instructions
        self.build_order_instructions = \
            'Replace this text by any build order in correct JSON format, ' \
            'then click on \'Add build order\'.' \
            '\n\nYou can get many build orders with the requested format from aoe4guides.com ' \
            'or age4builder.com (use the corresponding buttons below).' \
            '\nOn aoe4guides.com, click on the 3 dots (upper right corner, after selecting a build order), then on ' \
            'the \'Overlay Tool\' copy button, and paste the content here.' \
            '\nOn age4builder.com, click on the salamander icon (after selecting a build order), ' \
            'then paste the content here.' \
            '\n\nYou can also manually write your build order as JSON format, using the following buttons:' \
            '\n    * \'Reset build order\' : Reset the build order to a minimal template (adapt the initial fields).' \
            '\n    * \'Add step\' : Add a step (i.e. a new page) to the build order.' \
            '\n    * \'Format\' : Format the build order to a proper JSON indentation.' \
            '\n\nIn the \'Image selection\' section, you can obtain images by selecting a category and clicking ' \
            'on the requested image. You can then paste it anywhere in this panel.' \
            '\nThe \'select faction\' category provides all the available civilization names ' \
            'for the \'civilization\' field.' \
            '\n\nThe build order validity is constantly checked. If it is not valid, a message appears below ' \
            'to explain what is the issue.' \
            '\nFor more details, check the Readme.md and the existing samples.' \
            '\n\nYou can find all your saved build orders as JSON files by clicking on \'Open build orders folder\'.' \
            '\nTo remove any build order, just delete the corresponding file and use \'reload settings\' ' \
            '(or relaunch the overlay).'

        self.bo_tooltip_available = True  # activate tooltip feature in build order

        # civilization selection
        layout = self.settings.layout
        color_default = layout.color_default
        style_description = f'color: rgb({color_default[0]}, {color_default[1]}, {color_default[2]})'
        flag_select_size = layout.configuration.flag_select_size

        self.civilization_select = QComboBox(self)
        self.civilization_select.activated.connect(self.update_build_order_display)
        self.civilization_combo_ids = []  # corresponding IDs
        for civ_name, letters_icon in aoe4_civilization_icon.items():
            assert len(letters_icon) == 2
            self.civilization_select.addItem(
                QIcon(os.path.join(self.directory_game_pictures, 'civilization_flag', letters_icon[1])),
                letters_icon[0])
            self.civilization_combo_ids.append(civ_name)
        self.civilization_select.setIconSize(QSize(flag_select_size[0], flag_select_size[1]))
        self.civilization_select.setStyleSheet(f'QWidget{{ {style_description} }};')
        self.civilization_select.setToolTip('select civilization')
        self.civilization_select.setFont(QFont(layout.font_police, layout.font_size))
        self.civilization_select.adjustSize()

        # create build orders folder
        os.makedirs(self.directory_build_orders, exist_ok=True)

        self.update_panel_elements()  # update the current panel elements

    def reload(self, update_settings):
        """Reload the application settings, build orders...

        Parameters
        ----------
        update_settings   True to update (reload) the settings, False to keep the current ones
        """
        super().reload(update_settings=update_settings)

        # civilization selection
        layout = self.settings.layout
        color_default = layout.color_default
        style_description = f'color: rgb({color_default[0]}, {color_default[1]}, {color_default[2]})'
        flag_select_size = layout.configuration.flag_select_size

        self.civilization_select.setIconSize(QSize(flag_select_size[0], flag_select_size[1]))
        self.civilization_select.setStyleSheet(f'QWidget{{ {style_description} }};')
        self.civilization_select.setFont(QFont(layout.font_police, layout.font_size))
        self.civilization_select.adjustSize()

        self.update_panel_elements()  # update the current panel elements

    def settings_scaling(self):
        """Apply the scaling on the settings"""
        super().settings_scaling()
        assert 0 <= self.scaling_input_selected_id < len(self.scaling_input_combo_ids)
        layout = self.settings.layout
        unscaled_layout = self.unscaled_settings.layout
        scaling = self.scaling_input_combo_ids[self.scaling_input_selected_id] / 100.0

        layout.configuration.flag_select_size = scale_list_int(
            scaling, unscaled_layout.configuration.flag_select_size)

    def hide_elements(self):
        """Hide elements"""
        super().hide_elements()

        self.civilization_select.hide()

    def get_age_image(self, age_id: int) -> str:
        """Get the image for a requested age

        Parameters
        ----------
        age_id    ID of the age

        Returns
        -------
        age image with path
        """
        if age_id == 1:
            return self.settings.images.age_1
        elif age_id == 2:
            return self.settings.images.age_2
        elif age_id == 3:
            return self.settings.images.age_3
        elif age_id == 4:
            return self.settings.images.age_4
        else:
            return self.settings.images.age_unknown

    def update_build_order_display(self):
        """Update the build order search matching display"""
        civilization_id = self.civilization_select.currentIndex()
        assert 0 <= civilization_id < len(self.civilization_combo_ids)
        self.obtain_build_order_search(key_condition={'civilization': self.civilization_combo_ids[civilization_id]})
        self.config_panel_layout()

    def config_panel_layout(self):
        """Layout of the configuration panel"""
        super().config_panel_layout()

        # show elements
        self.civilization_select.show()

        layout = self.settings.layout
        border_size = layout.border_size
        horizontal_spacing = layout.horizontal_spacing
        vertical_spacing = layout.vertical_spacing
        action_button_size = layout.action_button_size

        # next Y position
        next_y = border_size + max(action_button_size, self.font_size_input.height(),
                                   self.scaling_input.height()) + vertical_spacing

        # build order selection
        self.build_order_title.move(border_size, next_y)
        next_x = border_size + self.build_order_title.width() + horizontal_spacing

        # civilization selection
        self.civilization_select.move(next_x, next_y)

        if self.civilization_select.height() > self.build_order_title.height():
            self.build_order_title.move(self.build_order_title.x(),
                                        widget_y_end(self.civilization_select) - self.build_order_title.height())
        next_y += max(self.build_order_title.height(), self.civilization_select.height()) + vertical_spacing

        # build order search
        self.build_order_search.move(border_size, next_y)
        next_y += self.build_order_search.height() + vertical_spacing

        if widget_x_end(self.build_order_search) > widget_x_end(self.civilization_select):
            self.civilization_select.move(
                widget_x_end(self.build_order_search) - self.civilization_select.width(), self.civilization_select.y())
        elif widget_x_end(self.build_order_search) < widget_x_end(self.civilization_select):
            self.build_order_search.resize(
                widget_x_end(self.civilization_select) - self.build_order_search.x(), self.build_order_search.height())

        self.build_order_selection.update_size_position(init_y=next_y)

        max_x = max(widget_x_end(self.next_panel_button), widget_x_end(self.build_order_search),
                    self.build_order_selection.x() + self.build_order_selection.row_max_width)

        max_y = max(widget_y_end(self.build_order_search),
                    self.build_order_selection.y() + self.build_order_selection.row_total_height)

        # resize main window
        self.resize(max_x + border_size, max_y + border_size)

        # next panel on top right corner
        self.next_panel_button.move(self.width() - border_size - self.next_panel_button.width(), border_size)

        # update position (in case the size changed)
        self.update_position()

    def select_build_order_id(self, build_order_id: int = -1) -> bool:
        """Select build order ID

        Parameters
        ----------
        build_order_id    ID of the build order, negative to select next build order

        Returns
        -------
        True if valid build order selection
        """
        if self.selected_panel == PanelID.CONFIG:
            if super().select_build_order_id(build_order_id):
                civilization_id = self.civilization_select.currentIndex()
                assert 0 <= civilization_id < len(self.civilization_combo_ids)
                self.obtain_build_order_search(
                    key_condition={'civilization': self.civilization_combo_ids[civilization_id]})
                if build_order_id >= 0:  # directly select in case of clicking
                    self.select_build_order(key_condition={
                        'civilization': self.civilization_combo_ids[self.civilization_select.currentIndex()]})
                self.config_panel_layout()
                return True
        return False

    def update_build_order(self):
        """Update the build order panel"""

        # clear the elements (also hide them)
        self.build_order_resources.clear()
        self.build_order_notes.clear()

        if self.selected_build_order is None:  # no build order selected
            self.build_order_notes.add_row_from_picture_line(parent=self, line='No build order selected.')

        else:  # valid build order selected
            selected_build_order_content = self.selected_build_order['build_order']

            # select current step
            assert 0 <= self.selected_build_order_step_id < self.selected_build_order_step_count
            selected_step = selected_build_order_content[self.selected_build_order_step_id]
            assert selected_step is not None

            # target resources
            target_resources = selected_step['resources']
            target_food = get_total_on_resource(target_resources['food'])
            target_wood = get_total_on_resource(target_resources['wood'])
            target_gold = get_total_on_resource(target_resources['gold'])
            target_stone = get_total_on_resource(target_resources['stone'])
            target_builder = get_total_on_resource(target_resources['builder']) if (
                    'builder' in target_resources) else -1
            target_villager = selected_step['villager_count']
            target_population = selected_step['population_count']

            # space between the resources
            spacing = ''
            layout = self.settings.layout
            for i in range(layout.build_order.resource_spacing):
                spacing += ' '

            # display selected step
            self.update_build_order_step_label()

            images = self.settings.images

            # line to display the target resources
            resources_line = images.food + '@ ' + (str(target_food) if (target_food >= 0) else ' ')
            resources_line += spacing + '@' + images.wood + '@ ' + (str(target_wood) if (target_wood >= 0) else ' ')
            resources_line += spacing + '@' + images.gold + '@ ' + (str(target_gold) if (target_gold >= 0) else ' ')
            resources_line += spacing + '@' + images.stone + '@ ' + (
                str(target_stone) if (target_stone >= 0) else ' ')
            if target_builder > 0:  # add builders count if indicated
                resources_line += spacing + '@' + images.builder + '@ ' + str(target_builder)
            if target_villager >= 0:
                resources_line += spacing + '@' + images.villager + '@ ' + str(target_villager)
            if target_population >= 0:
                resources_line += spacing + '@' + images.population + '@ ' + str(target_population)
            if 1 <= selected_step['age'] <= 4:
                resources_line += spacing + '@' + self.get_age_image(selected_step['age'])
            if ('time' in selected_step) and (selected_step['time'] != ''):  # add time if indicated
                resources_line += '@' + spacing + '@' + self.settings.images.time + '@' + selected_step['time']

            # for dict type target_resources, create a tooltip to associate with the resource icon
            mapping = {'wood': images.wood, 'food': images.food, 'gold': images.gold, 'stone': images.stone}
            tooltip = dict(
                (mapping[key], value) for (key, value) in target_resources.items() if type(value) is dict)
            self.build_order_resources.add_row_from_picture_line(
                parent=self, line=str(resources_line), tooltips=tooltip)

            # line before notes
            self.build_order_notes.add_row_color(
                parent=self, height=layout.build_order.height_line_notes, color=layout.build_order.color_line_notes)

            # notes of the current step
            notes = selected_step['notes']
            for note in notes:
                self.build_order_notes.add_row_from_picture_line(parent=self, line=note)

        self.build_order_panel_layout()  # update layout

    def build_order_panel_layout(self):
        """Layout of the Build order panel"""
        super().build_order_panel_layout()

        # show elements
        self.build_order_resources.show()

        # size and position
        layout = self.settings.layout
        border_size = layout.border_size
        vertical_spacing = layout.vertical_spacing
        horizontal_spacing = layout.horizontal_spacing
        action_button_size = layout.action_button_size
        action_button_spacing = layout.action_button_spacing
        bo_next_tab_spacing = layout.build_order.bo_next_tab_spacing

        # action buttons
        next_y = border_size + action_button_size + vertical_spacing

        if self.selected_build_order is not None:
            self.build_order_step_time.adjustSize()
            next_y = max(next_y, border_size + self.build_order_step_time.height() + vertical_spacing)

        # build order resources
        self.build_order_resources.update_size_position(init_y=next_y)
        next_y += self.build_order_resources.row_total_height + vertical_spacing

        # maximum width
        max_x = max(
            (self.build_order_step_time.width() + 3 * action_button_size +
             horizontal_spacing + action_button_spacing + bo_next_tab_spacing),
            self.build_order_resources.row_max_width)

        # build order notes
        self.build_order_notes.update_size_position(init_y=next_y, panel_init_width=max_x + 2 * border_size)

        # resize of the full window
        max_x = max(max_x, self.build_order_notes.row_max_width)
        self.resize(max_x + 2 * border_size, next_y + self.build_order_notes.row_total_height + border_size)

        # adapt buttons positions after window resize
        self.build_order_panel_layout_action_buttons()

        # position update to stay with the same upper right corner position
        self.update_position()

    def enter_key_actions(self):
        """Actions performed when pressing the Enter key"""
        if self.selected_panel == PanelID.CONFIG:
            if self.build_order_search.hasFocus():
                self.select_build_order(key_condition={
                    'civilization': self.civilization_combo_ids[self.civilization_select.currentIndex()]})

            self.config_panel_layout()  # update layout

    def open_panel_add_build_order(self):
        """Open/close the panel to add a build order"""
        if (self.panel_add_build_order is not None) and self.panel_add_build_order.isVisible():  # close panel
            self.panel_add_build_order.close()
            self.panel_add_build_order = None
        else:  # open new panel
            config = self.settings.panel_build_order
            self.panel_add_build_order = BuildOrderWindow(
                app=self.app, parent=self, game_icon=self.game_icon, build_order_folder=self.directory_build_orders,
                panel_settings=self.settings.panel_build_order, edit_init_text=self.build_order_instructions,
                build_order_websites=[['aoe4guides.com', 'https://aoe4guides.com'],
                                      ['age4builder.com', 'https://age4builder.com']],
                directory_game_pictures=self.directory_game_pictures,
                directory_common_pictures=self.directory_common_pictures)
