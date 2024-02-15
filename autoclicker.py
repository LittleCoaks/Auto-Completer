import sys
import platform
import mouse
import time
import winsound


def dl_progress(count, block_size, total_size):
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write("\r...%d%%" % percent)
    sys.stdout.flush()

print("Welcome to the Platform Assignment auto-clicker!")
print("This auto-clicker will automatically click through the assignment slides for you. Very nice!\n")

print("Please take note of the following:")
print("1.\tTo complete an assignment, you must view the material for a minimum of 2 hours in total.")
print("2.\tYou will still need to answer the questions yourself as they come up.")
print("3.\tYou will likely finish the slides before the program finished running. Simply close this window to exit at any time.")

input("\nLet's begin the program! Press \"Enter\" to continue: ")
slides = int(input("1.\tEnter the number of slides in the assignment: "))
print("2.\tEnsure that your browser window is opened to the assignment and is visible on the screen.")
print("\tNOTE: don't move, scroll, or minimize the webpage, otherwise the clicker won't click the button.")
input("\tPress \"Enter\" to continue: ")
print("3.\tHover your mouse exactly over the \"next slide\" button without clicking it. This is where the program will click for you.")
input("\tOnce the mouse is positioned, press \"Enter\" to begin: ")

next_slide_position = mouse.get_position()

minutes = 130
seconds = minutes*60
completed_loops = 0
time_per_slide = int(seconds//(slides-(slides*.1)) + 1)

print("\nBeginning program...\n")

print("Runtime information:")
current_time = int(time.time())
print(f"\t{'- Start time:' : <35}{time.ctime() : <35}")
complete_time = current_time + 7200
print(f"\t{'- Earliest completion time:' : <35}{time.ctime(complete_time) : <35}")
print(f"\t{'- Number of slides to complete:' : <35}{slides : <35}")
print(f"\t{'- Time to be spent per slide:' : <35}{str(round(time_per_slide/60, 2)) + ' minutes' : <35}")

print("\nRunning autoclicker...")

while completed_loops <= slides:
    time_spent = round((int(time.time()) - current_time)/60, 2)
    sys.stdout.write("\rTime Spent: %s minutes" % str(time_spent))
    sys.stdout.flush()
    mouse.move(750, 500, True, 1)
    time.sleep(time_per_slide)
    mouse.move(next_slide_position[0], next_slide_position[1], True, 1)
    mouse.click(button = 'left')
    if platform.system() == "Windows":
        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
    completed_loops += 1

mouse.move(750, 500, True, 2)
print("\nComplete :)")
input("Click this line and press \"Enter\" to exit the program: ")
sys.exit()