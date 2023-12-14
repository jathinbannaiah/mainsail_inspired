import flet as flt
from flet import (
    Column,
    Container,
    ElevatedButton,
    Page,
    Row,
    Text,
    UserControl,
    border_radius,
    colors,
    FilledButton,
    alignment,
)

class Flutter_UI(UserControl):                                    #Passes the control to the class

    def build(self):
        title = Text(value="Reocater System", color=colors.WHITE, size=22)
        C1 = Container(
            content =Row(
            controls = [Container(
            content = Column(
                controls = [

                    Container(
                    width = 180,
                    height = 980,
                    bgcolor = colors.BLUE_900,
                    border_radius = border_radius.all(15),
                    padding = 20
                    )
                ]
            )
        ),
        Container(
            content = Column(
                controls = [
                    Row(controls = [title]),
                    Container(
                    width = 550,
                    height = 250,
                    bgcolor = colors.GREY_900,
                    border_radius = border_radius.all(15),
                    padding = 20,
                    content = Column(
                        controls = [
                            Row(
                                controls = [
                                    Container(
                                        width = 150,
                                        height = 40,
                                        bgcolor = colors.GREEN_900,
                                        border_radius = border_radius.all(15),
                                        padding = 20,
                                        alignment=alignment.top_left,
                                    ),
                                    Container(
                                        width = 150,
                                        height = 40,
                                        bgcolor = colors.GREEN_900,
                                        border_radius = border_radius.all(15),
                                        padding = 20,
                                        alignment=alignment.top_right,
                                        ),
                                ]
                            ),
                            Row(
                                controls = [
                                    ElevatedButton(
                                        text = "Move Left",
                                        bgcolor = colors.GREY_700,
                                        color = colors.BLACK,
                                        on_click = self.on_button_clicked,
                                        data="move left",
                                        width = 150,
                                        height = 40,
                                    ),

                                    ElevatedButton(
                                        text = "Clockwise",
                                        bgcolor = colors.GREY_700,
                                        color = colors.BLACK,
                                        on_click = self.on_button_clicked,
                                        data="clockwise",
                                        width = 150,
                                        height = 40,
                                    )

                                ]
                            ),
                            Row(
                                controls = [
                                    ElevatedButton(
                                        text = "Brake",
                                        bgcolor = colors.GREY_700,
                                        color = colors.BLACK,
                                        on_click = self.on_button_clicked,
                                        data="Recoater Brake",
                                    ),
                                    ElevatedButton(
                                        text = "Stop",
                                        bgcolor = colors.GREY_700,
                                        color = colors.BLACK,
                                        on_click = self.on_button_clicked,
                                        data="Recoater Stop",
                                    ),
                                    ElevatedButton(
                                        text = "Brake",
                                        bgcolor = colors.GREY_700,
                                        color = colors.BLACK,
                                        on_click = self.on_button_clicked,
                                        data="Roller Brake",
                                    ),
                                    ElevatedButton(
                                        text = "Stop",
                                        bgcolor = colors.GREY_700,
                                        color = colors.BLACK,
                                        on_click = self.on_button_clicked,
                                        data="Roller Stop",
                            )
                        ]
                    )

                ]
            )

        ),
                    Container(
                    width = 550,
                    height = 30,
                    bgcolor = colors.BLUE_900,
                    border_radius = border_radius.all(15),
                    padding = 20,
                    ),

                    Row(controls = [Text(value="Hopper System", color=colors.WHITE, size=22)]),
                    Container(
                    width = 550,
                    height = 250,
                    bgcolor = colors.GREY_900,
                    border_radius = border_radius.all(15),
                    padding = 20,
                    content = Column(
                        controls = [
                            Row(
                                controls = [
                                    ElevatedButton(
                                        text = "Move Left",
                                        bgcolor = colors.GREY_700,
                                        color = colors.BLACK,
                                        on_click = self.on_button_clicked,
                                        data="move left",
                                    ),

                                    ElevatedButton(
                                        text = "Clockwise",
                                        bgcolor = colors.GREY_700,
                                        color = colors.BLACK,
                                        on_click = self.on_button_clicked,
                                        data="clockwise",
                                    )

                                ]
                            ),
                            Row(
                                controls = [
                                    ElevatedButton(
                                        text = "Brake",
                                        bgcolor = colors.GREY_700,
                                        color = colors.BLACK,
                                        on_click = self.on_button_clicked,
                                        data="Recoater Brake",
                                    ),
                                    ElevatedButton(
                                        text = "Stop",
                                        bgcolor = colors.GREY_700,
                                        color = colors.BLACK,
                                        on_click = self.on_button_clicked,
                                        data="Recoater Stop",
                                    ),
                                    ElevatedButton(
                                        text = "Brake",
                                        bgcolor = colors.GREY_700,
                                        color = colors.BLACK,
                                        on_click = self.on_button_clicked,
                                        data="Roller Brake",
                                    ),
                                    ElevatedButton(
                                        text = "Stop",
                                        bgcolor = colors.GREY_700,
                                        color = colors.BLACK,
                                        on_click = self.on_button_clicked,
                                        data="Roller Stop",
                            )
                        ]
                    )

                ]
            )

        ),
                    Container(
                    width = 550,
                    height = 30,
                    bgcolor = colors.BLUE_900,
                    border_radius = border_radius.all(15),
                    padding = 20,
                    ),
                    Row(controls = [Text(value="Z axis System", color=colors.WHITE, size=22)]),
                    Container(
                    width = 550,
                    height = 250,
                    bgcolor = colors.GREY_900,
                    border_radius = border_radius.all(15),
                    padding = 20,
                    content = Column(
                        controls = [
                            Row(
                                controls = [
                                    ElevatedButton(
                                        text = "Move Left",
                                        bgcolor = colors.GREY_700,
                                        color = colors.BLACK,
                                        on_click = self.on_button_clicked,
                                        data="move left",
                                    ),

                                    ElevatedButton(
                                        text = "Clockwise",
                                        bgcolor = colors.GREY_700,
                                        color = colors.BLACK,
                                        on_click = self.on_button_clicked,
                                        data="clockwise",
                                    )

                                ]
                            ),
                            Row(
                                controls = [
                                    ElevatedButton(
                                        text = "Brake",
                                        bgcolor = colors.GREY_700,
                                        color = colors.BLACK,
                                        on_click = self.on_button_clicked,
                                        data="Recoater Brake",
                                    ),
                                    ElevatedButton(
                                        text = "Stop",
                                        bgcolor = colors.GREY_700,
                                        color = colors.BLACK,
                                        on_click = self.on_button_clicked,
                                        data="Recoater Stop",
                                    ),
                                    ElevatedButton(
                                        text = "Brake",
                                        bgcolor = colors.GREY_700,
                                        color = colors.BLACK,
                                        on_click = self.on_button_clicked,
                                        data="Roller Brake",
                                    ),
                                    ElevatedButton(
                                        text = "Stop",
                                        bgcolor = colors.GREY_700,
                                        color = colors.BLACK,
                                        on_click = self.on_button_clicked,
                                        data="Roller Stop",
                            )
                        ]
                    )

                ]
            )

        )

        ]
        )
        )
        ]
        )
        )

        return C1

    def on_button_clicked(self, button):
        pass





def myapp(page: flt.Page):
        page.theme_mode = flt.ThemeMode.DARK  #Theme of the page
        page.window_height = 1000
        page.window_width = 1890

        ui = Flutter_UI()

        page.update()
        page.add(ui)




flt.app(target = myapp)

