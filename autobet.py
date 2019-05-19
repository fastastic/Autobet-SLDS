#!/usr/bin/python3
import urllib, mechanize, time, datetime, yaml, requests, csv
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from pyvirtualdisplay import Display
from pyfiglet import Figlet


'''
Autobet.py

'''


def splashart():
	ascii_banner = Figlet(font='larry3d')
	print(ascii_banner.renderText("Autobet"))


def login(driver, conf):
	print('Login in...')
	try:
		email = driver.find_element_by_id("user_login")
		password = driver.find_element_by_id("user_password")
		email.send_keys(conf['user']['email'])
		password.send_keys(conf['user']['password'])
		password.send_keys(Keys.ENTER)
		time.sleep(3)

	except Exception as e:
		print("Error login, skipping...")

	try:
		print("Trying to get daily coins...")
		driver.find_element_by_class_name("btn.btn--succes.btn--huge.gtm-event-submit") .click()
		time.sleep(5)
	except Exception as e:
		print("There isn't any daily reward yet, skipping...")



def get_coins(driver):
	try:
		profile_parsed = BeautifulSoup(driver.page_source, "html.parser")
		coins = profile_parsed.findAll("b", {"class": "active-coins"})[0].string
		return coins.replace(".", "")
	except Exception as e:
		print("Error getting coins, skipping..")
		exit

def get_total_coins(driver):
	try:
		profile_parsed = BeautifulSoup(driver.page_source, "html.parser")
		coins = profile_parsed.findAll("b", {"class": "active-coins"})[0].string
		coins = coins.replace(".", "")
		coins_played = profile_parsed.findAll("b", {"class": "played"})[0].string
		coins_played = coins_played.replace(".", "")
		return int(coins) + int(coins_played)
	except Exception as e:
		print("Error getting total coins, skipping...")
	

def post(text):
	print("Making post request")
	try:
		r = requests.post("http://192.168.1.50:1880/message", data={'message': text})
	except ValueError:
		print("Error post")


def get_links(driver):
	print("Getting links")
	links = []
	try:
		driver.get('https://playfulbet.com/deportes/baloncesto')
		time.sleep(3)
		elements = driver.find_elements_by_class_name('right.hide-for-small.link-outline')
		for element in elements:
			if element.get_attribute('text') == "Juega\xa0\xa0":
				links.append(element.get_attribute('href'))
		return links
	except Exception as e:
		print("Error getting links, skipping...")




def autobet(driver, links):
	# Obtenemos las coins iniciales
	coins = get_coins(driver)
	print("Initial coins: " + coins)

	# Iteramos sobre cada link
	for link in links:
		driver.get(link)
		time.sleep(5)

		# Intentamos cerrar los popups que puedan salir
		try:
			close = driver.find_element_by_class_name("fa.fa-times-circle.fa-2x.wrapper--title")
			close.click()
			close2 = driver.find_element_by_class_name('link-outline')
			close2.click()
		except NoSuchElementException:
			print("There's no element to click (first try)")
		try:
			close2 = driver.find_element_by_class_name('link-outline')
			close2.click()
		except NoSuchElementException:
			print("There's no element to click (second try)")

		print("Link: " + link)
		
		# Buscamos y seleccionamos la apuesta con la cuota mas baja
		try:
			ul_tag = driver.find_element_by_class_name("no-bullet.bet-options.row")
			li_tags = ul_tag.find_elements_by_tag_name("li")
			best_num = 100.00
			best_li = ""
			for li in li_tags:
				li_aux = str(li.text)
				num = float(li_aux.replace("\n", " ").split()[0])
				if num < best_num:
					best_li = li
					best_num = num
			
			best_li.click()

			# Esperamos a que aparezca el popup
			time.sleep(5)
			
			# Introducimos el valor que queramos
			input_bet = driver.find_element_by_class_name("js-bet-input")
			for i in range(1,4):
				input_bet.send_keys(Keys.BACKSPACE)
			input_bet.send_keys("200")
			time.sleep(2)

			# Apostamos y si alcanzamos el límite cortamos el bucle 
			if int(coins) > 300:
				driver.find_element_by_class_name("btn.btn--succes.btn--big.btn--full.gtm-event-submit") .click()
			
			else:
				break

			# Obtemos las coins restantes
			coins = get_coins(driver)
			print("Remaining coins: " + coins)

		except Exception as e:
			print("Error betting, skipping...")


'''
Si son las 00:00h guarda en un fichero de texto los coins actuales
y genera el gráfico hasta ese dío
'''
def plot(driver):
	print("Hour ? 11: " + time.strftime("%H"))
	if str(time.strftime("%H")) == "11":
		print("Generating plot...")
		x = []
		y = []

		# Añadimos el nuevo punto
		with open('/home/raul/Autobet/points.csv', 'a') as writecsv:
			writecsv.write(str(datetime.datetime.today().strftime('%d/%m/%Y')) + "," + str(get_total_coins(driver)))
			writecsv.write("\n")
		
		with open('/home/raul/Autobet/points.csv', "r") as readcsv:
			points = csv.reader(readcsv, delimiter=',')
			for row in points:
				x.append(str(row[0]))
				y.append(int(row[1]))

		writecsv.close()
		readcsv.close()
		
		print(x, y)
		plt.plot(x, y, color='blue')
		plt.xlabel('Day')
		plt.ylabel('Coins')
		plt.title('Progress in Playfulbet')
		plt.savefig('/home/raul/Autobet/lineplot.png')



def main():
	# Preparamos el display
	display = Display(visible=0, size=(1920,1080))
	display.start()
	
	# Splashart
	splashart()

	# Preparamos el navegador de Mechanize para hacer el login y obtener los links
	caps = DesiredCapabilities().FIREFOX
	caps["marionette"] = True
	driver = webdriver.Firefox(capabilities=caps)
	try:
		driver.get('https://playfulbet.com/users/sign_in?locale=es/')
	except Exception as e:
		print(e)
		driver.quit()
		display.stop()

	# Obtenemos el fichero yaml
	conf = yaml.load(open('/home/raul/Autobet/application.yml'), Loader=yaml.FullLoader)

	# Hacemos login con la instancia de Selenium y las credenciales
	login(driver, conf)

	# Obtenemos los links de los eventos
	links = get_links(driver)

	# Ejecutamos autobet
	autobet(driver, links)

	# Realización del gráfico
	plot(driver)

	# Notificamos a Google Home
	total_coins =  str(get_total_coins(driver))
	print("Total coins: " + total_coins)
	#post("Ha finalizado la ejecución de Autobet. Coins totales: " + total_coins)

	# Eliminamos las instancias creadas de Selenium y de PyVirtualDisplay
	driver.quit()
	display.stop()


if __name__ == '__main__':
	main()
