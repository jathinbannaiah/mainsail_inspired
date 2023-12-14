import flet
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
	FilledButton
)


class CalculatorApp(UserControl):
	def build(self):
		self.reset()
		self.result = Text(value="0", color=colors.WHITE, size=22)

		# application's root control (i.e. "view") containing all other controls
		return Container(
			width=325,
			height = 500,
			bgcolor=colors.BLUE_900,
			border_radius=border_radius.all(15),
			padding=20,
			content=Column(
				controls=[
					Row(
						controls=[
							ElevatedButton(
								text="AC",
								bgcolor=colors.YELLOW_400,
								color=colors.BLACK,
								on_click=self.on_button_clicked,
								data="AC",
							),
							ElevatedButton(
								text="+/-",
								bgcolor=colors.YELLOW_400,
								color=colors.BLACK,
								on_click=self.on_button_clicked,
								data="+/-",
							),
							ElevatedButton(
								text="%",
								bgcolor=colors.GREEN_900,
								color=colors.WHITE,
								on_click=self.on_button_clicked,
								data="%",
							),
							ElevatedButton(
								text="/",
								bgcolor=colors.GREEN_900,
								color=colors.WHITE,
								on_click=self.on_button_clicked,
								data="/",
							),
						],
					),
					Row(
						controls=[
							FilledButton(
								text="7",
								on_click=self.on_button_clicked,
								data="7",
							),
							FilledButton(
								text="8",
								on_click=self.on_button_clicked,
								data="8",
							),
							FilledButton(
								text="9",
								on_click=self.on_button_clicked,
								data="9",
							),
							ElevatedButton(
								text="*",
								bgcolor=colors.GREEN_900,
								color=colors.WHITE,
								on_click=self.on_button_clicked,
								data="*",
							),
						]
					),
					Row(
						controls=[
							FilledButton(
								text="4",
								on_click=self.on_button_clicked,
								data="4",
							),
							FilledButton(
								text="5",
								on_click=self.on_button_clicked,
								data="5",
							),
							FilledButton(
								text="6",
								on_click=self.on_button_clicked,
								data="6",
							),
							ElevatedButton(
								text="-",
								bgcolor=colors.GREEN_900,
								color=colors.WHITE,
								on_click=self.on_button_clicked,
								data="-",
							),
						]
					),
					Row(
						controls=[
							FilledButton(
								text="1",
								on_click=self.on_button_clicked,
								data="1",
							),
							FilledButton(
								text="2",
								on_click=self.on_button_clicked,
								data="2",
							),
							FilledButton(
								text="3",
								on_click=self.on_button_clicked,
								data="3",
							),
							ElevatedButton(
								text="+",
								on_click=self.on_button_clicked,
								bgcolor=colors.GREEN_900,
								color=colors.WHITE,
								data="+",
							),
						]
					),
					Row(
						controls=[
							FilledButton(
								text="0",
								on_click=self.on_button_clicked,
								data="0",
							),
							FilledButton(
								text="00",
								on_click=self.on_button_clicked,
								data="00",
							),
							ElevatedButton(
								text=".",
								bgcolor=colors.AMBER_600,
								color=colors.WHITE,
								on_click=self.on_button_clicked,
								data=".",
							),
							ElevatedButton(
								text="=",
								bgcolor=colors.ORANGE,
								color=colors.WHITE,
								on_click=self.on_button_clicked,
								data="=",
							),
						]
					),
				],
			),
		)

	def on_button_clicked(self, e):
		data = e.control.data
		if self.result.value == "Error" or data == "AC":
			self.result.value = "0"
			self.reset()

		elif data in ("1", "2", "3", "4", "5", "6", "7", "8",
					"9", "0", ".", "00"):
			if self.result.value == "0" or self.new_operand == True:
				self.result.value = data
				self.new_operand = False
			else:
				self.result.value = self.result.value + data

		elif data in ("+", "-", "*", "/"):
			self.result.value = self.calculate_value(
				self.operand1, float(self.result.value), self.operator
			)
			self.operator = data
			if self.result.value == "Error":
				self.operand1 = "0"
			else:
				self.operand1 = float(self.result.value)
			self.new_operand = True

		elif data in ("="):
			self.result.value = self.calculate_value(
				self.operand1, float(self.result.value), self.operator
			)
			self.reset()

		elif data in ("%"):
			self.result.value = float(self.result.value) / 100
			self.reset()

		elif data in ("+/-"):
			if float(self.result.value) > 0:
				self.result.value = "-" + str(self.result.value)

			elif float(self.result.value) < 0:
				self.result.value = str(
					self.format_number(abs(float(self.result.value)))
				)

		self.update()

	def format_number(self, num):
		if num % 1 == 0:
			return int(num)
		else:
			return num

	def calculate_value(self, operand1, operand2, operator):

		if operator == "+":
			return self.format_number(operand1 + operand2)

		elif operator == "-":
			return self.format_number(operand1 - operand2)

		elif operator == "*":
			return self.format_number(operand1 * operand2)

		elif operator == "/":
			if operand2 == 0:
				return "Error"
			else:
				return self.format_number(operand1 / operand2)

	def reset(self):
		self.operator = "+"
		self.operand1 = 0
		self.new_operand = True


def myCal(page: flet.Page):
	page.title = "Basic Calculator using Flet"

	page.window_height = 375
	page.window_width = 350

	calculator = CalculatorApp()

	page.update()

	# adding application's root control to the page
	page.add(calculator)


flet.app(target=myCal)
