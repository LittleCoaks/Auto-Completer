import time
from enum import Enum
import concurrent.futures

# selenium
from selenium import webdriver
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.common.by import By

# prompt
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

sep = "\n-----------------------------\n"

# user configs
# manually type this info here if you don't want to have to do it yourself upon running the program
preferred_browser = ""
username = ""
password = ""
show_time = None
watch_videos = None

class slideType(Enum):
    unknown = 0
    standard = 1
    question = 2
    question_osha = 3

def main():
    global preferred_browser
    global username
    global password
    global show_time
    global watch_videos

    introMessage()

    while preferred_browser == "":
        browser_list = ["Chrome", "Edge", "Firefox", "Safari", "Internet Explorer"]
        browser_completer = WordCompleter(browser_list, ignore_case=True)
        preferred_browser = prompt(f"Enter your preferred browser {browser_list}: ", completer=browser_completer).lower()
        if preferred_browser not in (browser.lower() for browser in browser_list):
            print("\nERROR:\tplease re-enter your choice.")
            preferred_browser = ""

    print()

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
        elif show_time_str == "no" or show_time_str == "no":
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
    
    preferred_driver = getPreferredDriver(preferred_browser)

    print("Runtime information:")
    starting_time = time.perf_counter()
    print(f"{'- Start time:' : <25}{time.ctime() : <25}")
    print(sep)

    if not login(preferred_driver):
        return
    runAutoCompleter(preferred_driver)

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



def getPreferredDriver(preferred_browser: str):
    preferred_driver = ChromiumDriver
    
    if preferred_browser == "chrome":
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        preferred_driver = webdriver.Chrome(options=chrome_options)

    elif preferred_browser == "edge":
        edge_options = webdriver.EdgeOptions()
        edge_options.add_argument("--log-level=3")
        edge_options.add_argument('--ignore-certificate-errors')
        edge_options.add_argument('--ignore-ssl-errors')
        edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        preferred_driver = webdriver.Edge(options=edge_options)

    elif preferred_browser == "firefox":
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument("--log-level=3")
        firefox_options.add_argument('--ignore-certificate-errors')
        firefox_options.add_argument('--ignore-ssl-errors')
        preferred_driver = webdriver.Firefox(options=firefox_options)

    elif preferred_browser == "safari":
        safari_options = webdriver.SafariOptions()
        safari_options.add_argument("--log-level=3")
        safari_options.add_argument('--ignore-certificate-errors')
        safari_options.add_argument('--ignore-ssl-errors')
        preferred_driver = webdriver.Edge(options=edge_options)

    elif preferred_browser == "internet explorer":
        ie_options = webdriver.IeOptions()
        ie_options.add_argument("--log-level=3")
        ie_options.add_argument('--ignore-certificate-errors')
        ie_options.add_argument('--ignore-ssl-errors')
        preferred_driver = webdriver.Ie(options=ie_options)

    return preferred_driver



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
        driver.find_element(By.XPATH, '//*[@id="navLeft"]/ul/li[2]/a/span').click()
        return True
    except:
        print("Login attempt failed. Please restart the program and ensure username/password is entered correctly.")
        driver.close()
        return False



def runAutoCompleter(driver: ChromiumDriver) -> int:
    # Find Next Assignment
    assignments = driver.find_element(By.XPATH, '//*[@id="content"]/table').find_elements(By.TAG_NAME, "tr")

    print("Assignment Info:")
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for x in range(1, len(assignments)):
            executor.submit(completeAssignment, x)
    
    driver.close()


# opens a new window
def completeAssignment(new_assignment_number: int):
    global show_time
    global watch_videos

    this_driver = getPreferredDriver(preferred_browser)
    login(this_driver)

    try:
        assignments = this_driver.find_element(By.XPATH, '//*[@id="content"]/table').find_elements(By.TAG_NAME, "tr")
        this_assignment = assignments[new_assignment_number].find_element(By.XPATH, ".//a")
        assignment_name = this_assignment.text
        is_osha = assignment_name.lower().startswith("new york osha")
        
        this_assignment.click() # open next assignment

        print(f"-\tStarted: -- {assignment_name}")
        
        completion_percent = findCompletionPercent(this_driver)
        remaining_percent = 100-completion_percent
        
        course_in_progress = True
        while course_in_progress:
            time_per_slide = 1
            if show_time and not is_osha:
                time_per_slide = 30 # seconds

            if is_osha:
                completion_percent = findCompletionPercent(this_driver)
                remaining_percent = 100-completion_percent
                if completion_percent != 100:
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
            try:
                this_driver.find_elements(By.CLASS_NAME, "tf_course1")
            except:
                slide_type = slideType.unknown
            slide_name = this_driver.find_elements(By.CLASS_NAME, "tf_course1")
            if len(slide_name) > 0:
                if slide_name[0].text.lower().startswith("study exercise"):
                    if is_osha:
                        slide_type = slideType.question_osha
                    else:
                        slide_type = slideType.question
            
            match slide_type:
                case slideType.standard:
                    this_driver.find_element(By.ID, "nextA").click()
                case slideType.question:
                    correct_modal_info = determineCorrectModal(this_driver)
                    next_slide_command = correct_modal_info[0].find_element(By.CLASS_NAME, correct_modal_info[1]).get_attribute("onclick")
                    this_driver.execute_script(next_slide_command)
                case slideType.question_osha:
                    this_driver.execute_script("document.myform.submit()")
                case slideType.unknown:
                    course_in_progress = False

        this_driver.close()
        print(f"-\t***Completed: -- {assignment_name}***")

    except:
        print(f"-\t!!!Some error occured: -- {assignment_name}!!!")
        this_driver.close()



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
