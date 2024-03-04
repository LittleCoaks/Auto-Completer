import time

# selenium
from selenium import webdriver
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.common.by import By

# prompt
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

sep = "\n-----------------------------\n"

def main():
    introMessage()

    browser_list = ["Chrome", "Edge", "Firefox", "Safari", "Internet Explorer", "Exit"]
    browser_completer = WordCompleter(browser_list, ignore_case=True)
    preferred_browser = prompt(f"Enter your preferred browser {browser_list}: ", completer=browser_completer).lower()

    print(sep)
    print("Steps:")
    print("1.\tLog into your account")
    print("2.\tNavigate to the training session page")
    print(sep)

    url = "https://app.targetsolutions.com/"
    driver = ChromiumDriver
    if preferred_browser == "chrome":
        driver = webdriver.Chrome()
    elif preferred_browser == "edge":
        driver = webdriver.Edge()
    elif preferred_browser == "firefox":
        driver = webdriver.Firefox()
    elif preferred_browser == "safari":
        driver = webdriver.Safari()
    elif preferred_browser == "internet explorer":
        driver = webdriver.Ie()
    else:
        return
    
    driver.get(url)
    print(sep)

    run = True
    while run:
        decision = prompt("Open the training session, then press \"Enter\" to run the script. Type \"Exit\" to end: ", completer=WordCompleter(["Exit"], ignore_case=True)).lower()
        if decision == "exit":
            run = False
        if run:
            runAutoCompleter(driver)

def runAutoCompleter(driver: ChromiumDriver):
    # only support OSHA for now
    # the other trainings have different quiz questions to workout
    print(sep)
    print("Runtime information:")
    current_time = int(time.time())
    print(f"\t{'- Start time:' : <35}{time.ctime() : <35}")
    completion_percent = findCompletionPercent(driver)
    if completion_percent == -1:
        errorMsg()
        return
    remaining_percent = 100-completion_percent
    complete_time = (remaining_percent * 60) + current_time
    print(f"\t{'- Estimated completion time:' : <35}{time.ctime(complete_time) : <35}")
    
    course_in_progress = True
    while course_in_progress:
        try:
            driver.find_element(By.CLASS_NAME, "course-title").text.lower()
        except:
            errorMsg()
            course_in_progress = False  
            return
        page_title = driver.find_element(By.CLASS_NAME, "course-title").text.lower()
        if not page_title.startswith("new york osha/pesh annual refresher"):
            errorMsg()   
            course_in_progress = False  
            return
        
        time_per_slide = 2 # seconds
        completion_percent = findCompletionPercent(driver)
        remaining_percent = 100-completion_percent
        if completion_percent != 100:
            if remaining_percent > 10:
                time_per_slide = 600 # 10 minutes
            else:
                time_per_slide = remaining_percent * 60
        
        remaining_time_slide = time_per_slide
        while remaining_time_slide > 0:
            print(f"\rTime until next slide: {remaining_time_slide} seconds", end="")
            remaining_time_slide -= 1
            time.sleep(1)

        question_slide = False
        driver
        slide_type = driver.find_element(By.CLASS_NAME, "tf_course1").text.lower()

        if slide_type.startswith("study exercise"):
            question_slide = True
        
        if question_slide:
            driver.execute_script("document.myform.submit()")
        else:
            driver.find_element(By.ID, "nextA").click()

    return

def introMessage():
    print(sep)
    print("Welcome to the Platform Assignment auto-completer!")
    print("This auto-clicker will automatically complete the OSHA training assignments for you. Very nice!\n")
    print("Please take note of the following:")
    print("-\tThe program will complete all of the slides automatically, including question slides.")
    print("-\tThe program will NOT complete the final exam at the end. You must do that yourself.")
    print("-\tThe current version only works with the 4 OSHA training modules, and no other training assignments.")
    print(sep)
    return

def errorMsg():
    print("\nThis does not appear to be the OSHA course. This program currently only works with OSHA training.")   
    return

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
