from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep
import os
import random
import json


class Autolike_vk:

    def __init__(self):

        self.profile_path = os.path.abspath("Profile")
        self._check_and_create_profile()

        self.browser_options = webdriver.ChromeOptions()
        self.browser_options.add_argument('--allow-profiles-outside-user-dir')
        self.browser_options.add_argument('--enable-profile-shortcut-manager')
        self.browser_options.add_argument(f'user-data-dir={self.profile_path}')
        self.browser_options.add_argument('--profile-directory=Default')

        self.browser_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.browser_options.add_argument('--log-level=3')

        # Запуск в фоновом режиме (без отображения браузера) #FOR TEST
        # self.browser_options.add_argument("--headless") 
        # self.browser_options.add_argument("--disable-gpu")
        # self.browser_options.add_argument("--no-sandbox")

        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=self.browser_options)
 
        # Счетчики статистики
        # self.total_counter = 0
        # self.like_counter = 0
        # self.dislike_counter = 0

        self.JSON_FILE = 'stats.json'
        self.SHOW_CURRENT_STATISTIC = True

        # self.stats = {
        #     "total_profile": 0,
        #     "total_like": 0,
        #     "total_dislike": 0,
        #     "session_profile": 0,
        #     "session_like": 0,
        #     "session_dislike": 0
        # }

        # Проверка наличия файла JSON и его чтение
        if os.path.exists(self.JSON_FILE):
            with open(self.JSON_FILE, 'r') as file:
                self.stats = json.load(file)

        self.stats["session_profile"] = 0
        self.stats["session_like"] = 0 
        self.stats["session_dislike"] = 0
        


        self.driver.get("https://vk.com/dating")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        sleep(3)
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        self.driver.switch_to.frame(iframes[1])
        sleep(3)

    def _check_and_create_profile(self):
        if not os.path.exists(self.profile_path):
            print("Папка Profile не найдена. Создаем новый профиль...")
            os.makedirs(self.profile_path)
            temp_driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
            temp_driver.get("chrome://settings/")
            sleep(3)
            temp_driver.quit()
            print("Профиль Chrome создан и сохранен в папке Profile.")

    def _check_like_disslike_button(self):
        try:
            self.like_button = self.driver.find_element(By.CSS_SELECTOR, 'div[data-testid="like"]')
            self.dislike_button = self.driver.find_element(By.CSS_SELECTOR, 'div[data-testid="dislike"]')
            return True
        except Exception as e:
            return False
        
    def _check_quote(self, code):
        # Ковычки присутствуют когда есть описания, поэтому проверяем наличие описания по ним
        try:
            for div_element in code:
                div_html = (str(div_element.get_attribute("outerHTML")) + "\n")
                if 'quote' in div_html:
                    return True
            return False
        except:
            return False
        
    def _is_verified(self):
        try:
            if self.driver.find_element(By.CSS_SELECTOR, 'svg[data-testid="verification-icon"]'):
                return True
            return False
        except:
           return False

    def _is_decription(self):
        try:
            description_temp = self.driver.find_element(
                    By.CSS_SELECTOR, 'div[aria-labelledby="/"]'
                ).find_elements(
                    By.CSS_SELECTOR, '.vkuiCustomScrollView'
                )[1].find_elements(
                    By.TAG_NAME, 'section'
                )[0].find_elements(
                     By.TAG_NAME, 'div'
                )
            
            if self._check_quote(description_temp) == True:
                return True
            return False
        
        except Exception as e:
            print(f"Ошибка описания: \n{e}")
            self._open_website()
            
    def _get_photo_count(self):

        self.photo_list = self.driver.find_element(
            By.CSS_SELECTOR, 'div[data-testid="current-card"]'
        ).find_elements(
            By.TAG_NAME, "div"
        )[0].find_elements(
            By.TAG_NAME, "div"
        )[0].find_elements(
             By.TAG_NAME, "div"
        )[1]

       # Находим элемент с определенным стилем translate3d(100%, 0px, 0px)
        target_element = self.photo_list.find_element(By.XPATH, "//div[@style='transform: translate3d(100%, 0px, 0px);']")

        # Получаем родительский элемент, который содержит все три div
        parent_element = target_element.find_element(By.XPATH, "./ancestor::div[1]")

        # Найдём весь блок, содержащий нужные элементы
        desired_block = parent_element.find_element(By.XPATH, "./parent::div/parent::div")

        # f = open('test.html', 'w')
        # f.write(desired_block.get_attribute('outerHTML'))
        # f.close()
        # exit()
        # ).find_elements(
        #     By.TAG_NAME, 'div'
        # )[0][0][1][2][0][0][0]
        # print(self.photo_list)
            


    def _use_like_ruleset(self):
        if self._is_verified() == True or self._is_decription() == True:
            self.like_button.click()
            self._update_stats("like")
        else:
            self.dislike_button.click()
            self._update_stats("dislike")


    def _update_stats(self, action, json_file=None):

        if json_file is None:
            json_file = self.JSON_FILE
            
        # Обновление общего и сессионного количества профилей
        self.stats["total_profile"] += 1
        self.stats["session_profile"] += 1

        # Обновление статистики в зависимости от действия
        if action == "like":
            self.stats["total_like"] += 1
            self.stats["session_like"] += 1
        elif action == "dislike":
            self.stats["total_dislike"] += 1
            self.stats["session_dislike"] += 1

        # Сохранение обновленной статистики в JSON
        with open(json_file, 'w') as file:
            json.dump(self.stats, file, indent=4)

        if self.SHOW_CURRENT_STATISTIC == True:
            print(f'Action: {action}\n'
                  f'All: {self.stats["session_profile"]}\n'
                  f'Like: {self.stats["session_like"]}\n'
                  f'Dislike {self.stats["session_dislike"]}\n')


    def _reboot_website(self):
        self.driver.get("https://vk.com/dating")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )

        sleep(3)
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        self.driver.switch_to.frame(iframes[1])
        sleep(3)
    

    def _bot(self):
        while True:
            try:
                if self._check_like_disslike_button() == False:
                    print("Ошибка нахождения кнопок like disslike ")
                    self._reboot_website()

                # self._get_photo_count() #TEST FUNCTION

                self._use_like_ruleset()
                sleep(random.randint(3, 15))


            except Exception as e:
                sleep(5)
                print(f"Ошибка: {e}")
                self._reboot_website()

def main():
    Autolike_vk()._bot()

if __name__ == "__main__":
    main()

#Добавить функцию создания профиля (Проверяем, если профиля нет)