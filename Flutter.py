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

class Flutter_GUI():
    def __init__(self):
        self.dashboard_paine = Container(
            alignment=alignment.top_left,
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
        )
        self.recoater_paine = Container(
                    width = 550,
                    height = 300,
                    bgcolor = colors.GREY_900,
                    border_radius = border_radius.all(15),
                    padding = 20,
                    alignment=alignment.top_right,
                    content = Column(
                        controls = [
                            Row(
                                controls = [
                                    Container(
                                        width = 150,
                                        height = 40,
                                        bgcolor = colors.GREEN_900,
                                        border_radius = border_radius.all(15),
                                        padding = 0,
                                        alignment=alignment.Alignment(-0.3,-0.4),
                                    ),
                                    Container(
                                        width = 200,
                                        height = 80,
                                        padding = 30,
                                        content = Column(
                                            controls = [
                                                ElevatedButton(
                                                text = "Limit switch",
                                                bgcolor = colors.GREY_700,
                                                color = colors.BLACK,
                                                on_click = self.on_button_clicked,
                                                data="move left",
                                                width = 150,
                                                height = 40,
                                                ),

                                                ElevatedButton(
                                                    text = "direction",
                                                    bgcolor = colors.GREY_700,
                                                    color = colors.BLACK,
                                                    on_click = self.on_button_clicked,
                                                    data="clockwise",
                                                    width = 150,
                                                    height = 40,
                                                )
                                            ]
                                        )
                                    ),
                                    Container(
                                        width = 150,
                                        height = 40,
                                        bgcolor = colors.GREEN_900,
                                        border_radius = border_radius.all(15),
                                        padding = 10,
                                        alignment=alignment.Alignment(0.3,0.4),
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
                                        width = 170,
                                        height = 40,
                                    ),
                                    Container(                                  # Don't put equal to, it caused an error
                                        width = 160,
                                        height = 50,
                                            ),

                                    ElevatedButton(
                                        text = "Clockwise",
                                        bgcolor = colors.GREY_700,
                                        color = colors.BLACK,
                                        on_click = self.on_button_clicked,
                                        data="clockwise",
                                        width = 170,
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
                                     Container(                                  # Don't put equal to, it caused an error
                                        width = 150,
                                        height = 50,
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

        self.hopper_paine = Container(
                    width = 550,
                    height = 300,
                    bgcolor = colors.GREY_900,
                    border_radius = border_radius.all(15),
                    padding = 20,
                    alignment=alignment.top_right,
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
                                        alignment=alignment.Alignment(-0.3,-0.4),
                                    ),
                                    Container(
                                        width = 200,
                                        height = 80,
                                        padding = 30,
                                        content = Column(
                                            controls = [
                                                ElevatedButton(
                                                text = "Limit switch",
                                                bgcolor = colors.GREY_700,
                                                color = colors.BLACK,
                                                on_click = self.on_button_clicked,
                                                data="move left",
                                                width = 150,
                                                height = 40,
                                                ),

                                                ElevatedButton(
                                                    text = "direction",
                                                    bgcolor = colors.GREY_700,
                                                    color = colors.BLACK,
                                                    on_click = self.on_button_clicked,
                                                    data="clockwise",
                                                    width = 150,
                                                    height = 40,
                                                )
                                            ]
                                        )
                                    ),
                                    Container(
                                        width = 150,
                                        height = 40,
                                        bgcolor = colors.GREEN_900,
                                        border_radius = border_radius.all(15),
                                        padding = 10,
                                        alignment=alignment.Alignment(0.3,0.4),
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
                                        width = 170,
                                        height = 40,
                                    ),
                                     Container(                                  # Don't put equal to, it caused an error
                                        width = 160,
                                        height = 50,
                                            ),

                                    ElevatedButton(
                                        text = "Clockwise",
                                        bgcolor = colors.GREY_700,
                                        color = colors.BLACK,
                                        on_click = self.on_button_clicked,
                                        data="clockwise",
                                        width = 170,
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
                                     Container(                                  # Don't put equal to, it caused an error
                                        width = 150,
                                        height = 50,
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

        self.Z_paine = Container(
                    width = 550,
                    height = 300,
                    bgcolor = colors.GREY_900,
                    border_radius = border_radius.all(15),
                    padding = 20,
                    alignment=alignment.top_right,
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
                                        alignment=alignment.Alignment(-0.3,-0.4),
                                    ),
                                    Container(
                                        width = 200,
                                        height = 80,
                                        padding = 30,
                                        content = Column(
                                            controls = [
                                                ElevatedButton(
                                                text = "Limit switch",
                                                bgcolor = colors.GREY_700,
                                                color = colors.BLACK,
                                                on_click = self.on_button_clicked,
                                                data="move left",
                                                width = 150,
                                                height = 40,
                                                ),

                                                ElevatedButton(
                                                    text = "direction",
                                                    bgcolor = colors.GREY_700,
                                                    color = colors.BLACK,
                                                    on_click = self.on_button_clicked,
                                                    data="clockwise",
                                                    width = 150,
                                                    height = 40,
                                                )
                                            ]
                                        )
                                    ),
                                    Container(
                                        width = 150,
                                        height = 40,
                                        bgcolor = colors.GREEN_900,
                                        border_radius = border_radius.all(15),
                                        padding = 10,
                                        alignment=alignment.Alignment(0.3,0.4),
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
                                        width = 170,
                                        height = 40,
                                    ),
                                     Container(                                  # Don't put equal to, it caused an error
                                        width = 160,
                                        height = 50,
                                            ),

                                    ElevatedButton(
                                        text = "Clockwise",
                                        bgcolor = colors.GREY_700,
                                        color = colors.BLACK,
                                        on_click = self.on_button_clicked,
                                        data="clockwise",
                                        width = 170,
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
                                     Container(                                  # Don't put equal to, it caused an error
                                        width = 150,
                                        height = 50,
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
        flt.app(target = self.build)
    def build(self, page):
        page.theme_mode = flt.ThemeMode.DARK  #Theme of the page
        page.window_height = 1000
        page.window_width = 1890
        column_container = Container(
            content=Column(
                controls=[self.recoater_paine, self.hopper_paine, self.Z_paine]
            )
        )
        row_container = Container(
            content=Row(
                controls=[self.dashboard_paine, column_container]
            )
        )
        page.add(row_container)
        page.update()

    def on_button_clicked(self):
        pass



def main():
    gui = Flutter_GUI()


if __name__ == "__main__":
    main()
