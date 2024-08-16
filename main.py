from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import random

# Путь к вашему профилю Firefox (Чтобы не вводить логпас каждый раз)
profile_path = "/path/to/your/firefox/profile"

# Настройка опций браузера
browser_options = webdriver.ChromeOptions()
browser_options.add_experimental_option('excludeSwitches', ['enable-logging'])
browser_options.add_argument('--allow-profiles-outside-user-dir')
browser_options.add_argument('--enable-profile-shortcut-manager')
browser_options.add_argument(r'user-data-dir=Profile')
browser_options.add_argument('--profile-directory=MyProfile')
driver = webdriver.Chrome(service=webdriver.ChromeService(ChromeDriverManager().install()), options=browser_options)
# timeout = WebDriverWait(driver, timeout_sec)



def write_html(driver):
    file = open('vk.html', 'w')
    file.write(driver.page_source)
    file.close()
    print("Данные обновлены - VK.html")




total_counter = 0
like_counter = 0
dislike_counter = 0


def OPTIMIZIROVAT():
    driver.get("https://vk.com/dating")
            
    # Ждем, пока страница загрузится и iframe станет доступным
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
    )

    # Переключаемся на iframe на странице (Выяснил, что это 2й)
    driver.switch_to.frame(1)
    # write_html(driver) # JUST FOR TEST
    time.sleep(3)

OPTIMIZIROVAT()


# Открытие сайта
while True:
    try:
        
        
        



        # Ищем кнопку 'like' и 'dislike'
        try:
            like_button = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="like"]')
            dislike_button = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="dislike"]')
        except Exception as e:
            print(f"Не удалось найти кнопки 'like', 'dislike': \n{e}")

        try:
            if driver.find_element(By.CSS_SELECTOR, 'svg[data-testid="verification-icon"]'):
                Profile_verified = True
        except:
            Profile_verified = False


        # Ищем описание
        try:
            description_temp = driver.find_element(
                    By.CSS_SELECTOR, 'div[aria-labelledby="/"]'
                ).find_elements(
                    By.CSS_SELECTOR, '.vkuiCustomScrollView'
                )[1].find_elements(
                    By.TAG_NAME, 'section'
                )[0].find_elements(
                     By.TAG_NAME, 'div'
                )
            
            # Проверяем на ковыяки (символ, когда есть описание)
            try:
                Profile_have_description = False
                for div_element in description_temp:
                    div_html = (str(div_element.get_attribute("outerHTML")) + "\n")
                    if 'quote' in div_html:
                        Profile_have_description = True
            except:
                Profile_have_description = False
        
        except Exception as e:
            print(f"Ошибка описания: \n{e}")
            OPTIMIZIROVAT()




        #Лайкаем только верефицированных или с описанием
        if Profile_verified == True or Profile_have_description == True:
            like_button.click()
            like_counter += 1
            print("Like")
        else:
            dislike_button.click()
            dislike_counter += 1
            print("Dislike")
        total_counter += 1
        print(f"A | L | D\n{total_counter} | {like_counter} | {dislike_counter}\n")
        fstat = open('statistic.txt', 'w')
        fstat.write(f"A | L | D\n{total_counter} | {like_counter} | {dislike_counter}\n")
        fstat.close()

        time.sleep(random.randint(3, 15))
        
    except Exception as e:
        print(f"Ошибка: {e}")
    # finally:
    #     print("Exit")
    #     driver.quit()




'''
    data-testid="verification-icon" - Если страница подтверждена
'''
