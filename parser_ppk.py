from selenium import webdriver
import time
from bs4 import BeautifulSoup
import re
import pandas as pd
def collect_kadastr_numbers(text_for_search, file_name):
	driver = webdriver.Chrome()	#Открытие браузера
	driver.implicitly_wait(10)	#Заданное время в секундах, в течении которого будет опрашиваться DOM
	link = "https://pkk.rosreestr.ru/#/search/65.64951699999888,122.73014399999792/4/@5w3tqxnc7"
	numbers_list = []
	try:
		driver.get(link)	#Переход по заданной ссылке
		driver.find_element_by_css_selector(".tutorial-button-outline").click()  # Закрытие окна с предложением об обучении
		driver.find_element_by_css_selector(".type-ahead-select").clear()  # Очищаем поле ввода
		driver.find_element_by_css_selector(".type-ahead-select").send_keys(text_for_search)	#Передача параметров в поисковую строку
		driver.find_element_by_css_selector(".type-ahead-select").send_keys("\n")
		while True:
			all_numbers = driver.find_elements_by_css_selector('.info-item-container .title')	#Поиск элемента страницы
			for number in all_numbers:	#Сбор кадастровых намеров на конкретной странице
				numbers_list.append(number.get_attribute("innerHTML"))
			try:
				driver.find_element_by_css_selector('.next.pgn').click()	#Переключение страниц
			except Exception:
				break
	finally:
		driver.quit()	#Закрытие окна браузера
		file = open(f'{file_name}.txt', 'w')
		for number in numbers_list:	#Запись кадастровых номеров в текстовый файл
			file.write(number + '\n')
		file.close()


def collect_data(file_name):
	data_dict = {}	#Создание словаря
	with open(f'{file_name}.txt', 'r') as file:	#Окртыие текстового документа с кадастровыми номерами
		lines = [line.strip() for line in file]
	number_list = []	#Создание списка
	for number in lines:	#Запись в список кадастровых номеров
		number_list.append(number)
	driver = webdriver.Chrome()	#Открытие браузера
	driver.implicitly_wait(10) #Ожидание 10 секунд
	link = "https://pkk.rosreestr.ru/#/search/65.64951699999888,122.73014399999792/4/@5w3tqxnc7"
	try:
		driver.get(link)
		driver.find_element_by_css_selector(".tutorial-button-outline").click()  # Закрытие окна с предложением об обучении
		for number in number_list:
			driver.find_element_by_css_selector(".type-ahead-select").clear()  # Очищаем поле ввода
			driver.find_element_by_css_selector(".type-ahead-select").send_keys(number)
			driver.find_element_by_css_selector(".type-ahead-select").send_keys("\n")
			time.sleep(5)  # Ждём пока загрузится контент
			page_source = driver.page_source	#З агружаем код страницы
			soup = BeautifulSoup(page_source, 'html.parser')  # Передали ее в Soup
			all_row = soup.find_all('div', class_=re.compile(r"detail-info item\b.*"))  # Собираем все строки
			if not all_row:
				driver.delete_all_cookies()
				driver.get(link)
				print(f"Невозможно предоставить информацию по запросу - {number}!") # Выводим ошибку, в случае если в кадастровом номере содержится ошибка
			else:
				for row in all_row:	# Собираем строки с данными, из каждой строки получаем имя и значение
					name = row.find('div', class_='field-name').text.strip().capitalize().replace(':', '')
					value = row.find('div', class_='expanding-box').text.strip()
					if name not in data_dict:	# Проверка наличия имени в словаре
						data_dict[name] = [value]	# Добавление в словарь, в случае отсутствия
						if len(data_dict[name]) < len(data_dict['Тип']):
							data_dict[name] = ['-'] * (len(data_dict['Тип']) - len(data_dict[name])) + [value]
					else:
						data_dict[name].append(value)	# Иначе добавляем значение
				for key in data_dict:	# Проверка длины словаря
					if len(data_dict[key]) < len(data_dict['Тип']):
						data_dict[key].append('-')
	finally:
		df = pd.DataFrame(data_dict)	# Экспорт в Dataframe
		pd.set_option("max_colwidth", 40)
		df.to_excel(f'./{file_name}.xlsx', sheet_name="Info", index=False)	# Экспорт в Excel
		driver.quit()	# Закрытие браузера
		
collect_kadastr_numbers('Амурская область, Благовещенск', 'kadastr')
collect_data('kadastr')