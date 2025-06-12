import os
import time
from enum import Enum
import concurrent.futures
import warnings
warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    module=r"trio\._core\._multierror"
)

# selenium
from selenium import webdriver
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from selenium.common.exceptions import WebDriverException

# prompt
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

# chatgpt
import openai
from bs4 import BeautifulSoup


sep = "\n-----------------------------\n"

# user configs
# manually type this info here if you don't want to have to do it yourself upon running the program
username = ""
password = ""
show_time = None
watch_videos = None
openai_api_key = ""

class slideType(Enum):
    unknown = 0
    standard = 1
    question = 2
    question_osha = 3
    user_agreement = 4
    exam = 5
    warning = 6

def main():
    global username
    global password
    global show_time
    global watch_videos

    introMessage()

    if username == "":
        username = prompt(f"Enter your username/email: ")
    if password == "":
        password = prompt(f"Enter your password (case-sensitive): ")

    print()

    while show_time == None:
        print("Would you like to show completion time?")
        print("-\tYes: the program will wait 30 seconds per slide so you'll have time completed for the assignment")
        print("-\tNo: the program will skip slides in 1 second. Note: this can result in 0 minute completion times.")
        show_time_msg = "Enter Yes/No: "
        show_time_completer = WordCompleter(["Yes", "No"], ignore_case=True)
        show_time_str = prompt(show_time_msg, completer=show_time_completer).lower()
        if show_time_str == "yes" or show_time_str == "y":
            show_time = True
        elif show_time_str == "no" or show_time_str == "n":
            show_time = False
        else:
            show_time = None
            print("\nERROR:\tplease re-enter your choice.")

    print()
    
    while watch_videos == None:
        print("Would you like to watch video slides?")
        print("-\tYes: the program will wait until a video finishes before going to the next slide.")
        print("-\tNo: the program will skip the video in 1 second. Note: this can result in 0 minute completion times.")
        watch_videos_msg = "Enter Yes/No: "
        watch_videos_completer = WordCompleter(["Yes", "No"], ignore_case=True)
        watch_videos_str = prompt(watch_videos_msg, completer=watch_videos_completer).lower()
        if watch_videos_str == "yes" or watch_videos_str == "y":
            watch_videos = True
        elif watch_videos_str == "no" or watch_videos_str == "n":
            watch_videos = False
        else:
            watch_videos = None
            print("\nERROR:\tplease re-enter your choice.")
    
    print(sep)
    print("The program will now begin. Please do not close this window or any browser window.")
    print(sep)

    driver = getDriver()

    print("Runtime information:")
    starting_time = time.perf_counter()
    print(f"{'- Start time:' : <25}{time.ctime() : <25}")
    print(sep)

    if not login(driver):
        return
    runAutoCompleter(driver)

    print(sep)
    ending_time = time.perf_counter()
    print(f"{'- End time:' : <25}{time.ctime() : <25}")
    total_time = int(ending_time - starting_time)
    hours = total_time // 3600
    minutes = (total_time - (hours*3600)) // 60
    seconds = (total_time - (hours*3600)) - (minutes*60)
    formatted_runtime = f"{hours} Hours {minutes} Minutes & {seconds} Seconds"
    print(f"{'- Total runtime:' : <25}{formatted_runtime : <25}")
    print(sep)

    print("All assigmnet(s) are now complete! Please make sure to complete the final exams at the end :)")
    input("Press \"Enter\" to close this window: ")



def getDriver():
    # only supporting Chrome from now on, the other ones are too annoying plus no one's using anything else
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option("detach", True)
    
    chrome_install = ChromeDriverManager().install()
    folder = os.path.dirname(chrome_install)
    chromedriver_path = os.path.join(folder, "chromedriver.exe")
    service = Service(chromedriver_path)

    return webdriver.Chrome(service=service, options=options)



def expand_shadow_element(driver, element):
    return driver.execute_script('return arguments[0].shadowRoot', element)

def get_nested_shadow_element(driver, selectors):
    """
    selectors: list of (By, value) tuples, each pointing to the next shadow root element
    """
    parent = driver
    for by, selector in selectors:
        # wait for the element inside shadow dom or document
        WebDriverWait(driver, 10).until(lambda d: parent.find_element(by, selector))
        parent = parent.find_element(by, selector)
        parent = expand_shadow_element(driver, parent)
    return parent



def login(driver: ChromiumDriver):
    global username
    global password

    url = "https://app.targetsolutions.com/"
    driver.get(url)
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.CLASS_NAME, "btn-1").click()

    # open My Assignments
    try:
        sidenav = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "vwc-sidenav#sidenav"))
        )
        sidenav_shadow = expand_shadow_element(driver, sidenav)
        assignment_item = sidenav_shadow.find_element(By.CSS_SELECTOR, "vwc-item#vwc-sidenav-item-19_1_6")
        item_shadow = expand_shadow_element(driver, assignment_item)
        link = item_shadow.find_element(By.CSS_SELECTOR, "a#item")
        driver.execute_script("arguments[0].click();", link)
        return True
    except:
        print("Login attempt failed. Please restart the program and ensure username/password is entered correctly.")
        driver.close()
        return False



def runAutoCompleter(driver: ChromiumDriver) -> int:
    # Find Next Assignment
    table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="banner-content-section"]/table'))
    )
    assignments = table.find_elements(By.TAG_NAME, "tr")

    print("Assignment Info:")
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for x in range(1, len(assignments)):
            executor.submit(completeAssignment, x)
    
    driver.close()


# opens a new window
def completeAssignment(new_assignment_number: int):
    global show_time
    global watch_videos

    this_driver = getDriver()
    login(this_driver)

    try:
        table = WebDriverWait(this_driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="banner-content-section"]/table'))
        )
        assignments = table.find_elements(By.TAG_NAME, "tr")
        this_assignment = assignments[new_assignment_number].find_element(By.XPATH, ".//a")
        assignment_name = this_assignment.text
        is_osha = assignment_name.lower().startswith("new york osha")
        answers = ""
        
        this_assignment.click() # open next assignment

        print(f"-\tStarted: -- {assignment_name}")
        
        course_in_progress = True
        while course_in_progress:
            completion_percent = findCompletionPercent(this_driver)
            remaining_percent = 100-completion_percent
            time_per_slide = 1
            
            if completion_percent == -1:
                if show_time:
                    time_per_slide = 30 # seconds
            
            elif completion_percent != 100:
                if remaining_percent > 10:
                    time_per_slide = 600 # 10 minutes
                else:
                    time_per_slide = remaining_percent * 60
            
            # check if this is a video slide
            if watch_videos:
                video_element = this_driver.find_elements(By.ID, "mediaspace")
                if len(video_element) > 0:
                    video_length_txt = this_driver.find_element(By.XPATH, '//*[@id="mediaspaceVideo"]/div[4]/div[4]/span[2]').get_attribute("innerHTML")
                    video_length = video_length_txt.split(":")
                    time_per_slide = int(video_length[0])*60 + int(video_length[1])

            remaining_time_slide = time_per_slide
            while remaining_time_slide > 0:
                remaining_time_slide -= 1
                time.sleep(1)
            
            slide_type = slideType.standard
            slide_name = this_driver.find_elements(By.CLASS_NAME, "tf_course1")
            if this_driver.find_elements(By.XPATH, '//h1[text()="User Agreement"]'):
                slide_type = slideType.user_agreement
            elif this_driver.find_elements(By.XPATH, '//*[@id="body"]/div/div[1]/div/div[1][text()="Warning"]'):
                slide_type = slideType.warning
            elif len(slide_name) > 0:
                if slide_name[0].text.lower().startswith("study exercise"):
                    if is_osha:
                        slide_type = slideType.question_osha
                    else:
                        slide_type = slideType.question
            else:
                if this_driver.find_elements(By.XPATH, '//div[@class="header" and normalize-space(text())="Exam Agreement"]'):
                    slide_type = slideType.exam
                else:
                    slide_type = slideType.unknown
            
            match slide_type:
                case slideType.standard:
                    this_driver.find_element(By.ID, "nextA").click()
                case slideType.question:
                    correct_modal_info = determineCorrectModal(this_driver)
                    if correct_modal_info[0]:
                        next_slide_command = correct_modal_info[0].find_element(By.CLASS_NAME, correct_modal_info[1]).get_attribute("onclick")
                        this_driver.execute_script(next_slide_command)
                    else:
                        answer = slide_name[0].find_element(By.CSS_SELECTOR, '[href]:not([href="#"])')
                        answer.click()
                        alert = this_driver.switch_to.alert
                        alert.accept()
                case slideType.question_osha:
                    this_driver.execute_script("document.myform.submit()")
                case slideType.exam:
                    if openai_api_key != "":
                        this_driver.find_element(By.ID, "iAgree").click()
                        this_driver .find_element(By.ID, "saveBtn").click()
                        exam_html = this_driver.find_element(By.CLASS_NAME, "examList").get_attribute('innerHTML')
                        answers = answerExam(exam_html)
                    course_in_progress = False
                case slideType.user_agreement:
                    this_driver.find_element(By.ID, "agree").click()
                case slideType.warning:
                    this_driver.find_element(By.ID, "backBtn").click()
                case slideType.unknown:
                    course_in_progress = False

        print(f"-\t***Completed: -- {assignment_name}***")
        if answers != "":
            print(f"-\tExam Answers:\t{answers}")
        else:
            this_driver.close() # don't close page if there's an exam. each new time opening the exam changes the quesitons
    except:
        print(f"-\t!!!Some error occured: -- {assignment_name}!!!")
        this_driver.close()



def answerExam(exam_html):
    soup = BeautifulSoup(exam_html, 'html.parser')
    output = []
    questions = soup.find_all('li', class_='examQuestion')
    options = soup.find_all('li', class_='examOptions')
    for i in range(len(questions)):
        question_text = questions[i].get_text(strip=True)
        output.append(question_text)
        answers = options[i].find_all('li')
        for j, ans in enumerate(answers):
            answer_text = ans.get_text(strip=True)
            output.append(f"    {chr(65 + j)}. {answer_text}")
    exam_string = '\n'.join(output)

    client = openai.OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You will receive an exam. Correctly answer the questions and respond only with a comma-seperated list of the answers by letter in the order of the questions."},
            {"role": "user", "content": exam_string}
        ]
    )
    return response.choices[0].message.content



def determineCorrectModal(driver: ChromiumDriver):
    correct_modal = ""
    button_name = ""
    try:
        correct_modal = driver.find_element(By.ID, "correctModal")
        button_name = "btn"
    except:
        pass
    try:
        correct_modal = driver.find_element(By.ID, "correctMSModal")
        button_name = "btn"
    except:
        pass
    try:
        correct_modal = driver.find_element(By.ID, "correctAnswer")
        button_name = "continueBtn"
    except:
        pass

    return [correct_modal, button_name]


def introMessage():
    print(sep)
    print("Welcome to the Target Solutions assignment auto-completer!")
    print("This program will automatically complete the training assignments for you. Nice!\n")
    print("Please take note of the following:")
    print("1.\tThe program will complete all of the slides automatically, including question slides.")
    print("2.\tThe program will NOT complete the final exam at the end. You must do that yourself.")
    print("3.\tA lot of browser windows will appear on your computer screen. Do **NOT** close any of them.")
    print("4.\tEnsure your computer does **NOT** sleep or turn off during runtime, as this will end the program.")
    print("5.\tAllow the program to run until the windows automatically close and a completion message appears.")
    input("\nPress \"Enter\" to continue: ")
    print(sep)



def findCompletionPercent(driver: ChromiumDriver):
    try:
        driver.find_element(By.XPATH, '//*[@id="courseProgress-item"]/div/div/div/span')
    except:
        return -1
    bar = driver.find_element(By.XPATH, '//*[@id="courseProgress-item"]/div/div/div/span')
    text = bar.get_attribute("innerHTML")
    percent = int(text.split("%")[0])
    return percent


if __name__ == "__main__":
    main()
