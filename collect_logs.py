import os
import re 
from datetime import date, timedelta
import datetime
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

def click_function(element_xpath):
    driver.find_element(
        by = By.XPATH,
        value = element_xpath
    ).click()

def fill_out_form(element_xpath, text_to_send):

    if text_to_send == "enter":
        form_element = driver.find_element(
        by = By.XPATH,
        value = element_xpath
        )
        form_element.send_keys(Keys.ENTER)

    else:
        form_element = driver.find_element(
            by = By.XPATH,
            value = element_xpath
        )

        form_element.clear()
        form_element.send_keys(text_to_send)

def flow_function(start_date, end_date, machine_code):

    start_date = f"{start_date[6:8]}/{start_date[4:6]}/{start_date[:4]}"
    end_date = f"{end_date[6:8]}/{end_date[4:6]}/{end_date[:4]}"

    store_code = machine_code[:4]

    flow = {
        "iris_button" : r'//*[@id="main"]/div[2]/form/div[2]/div/div[1]/div[2]/select/option[4]',
        "login_button" : r'//*[@id="main"]/div[2]/form/div[2]/div/div[3]/a[1]',
        "transaction_history_button" : r'/html/body/div/div/div[2]/ng-view/div/div[13]/div[2]',
        "transaction_expand_button" : r'//*[@id="selected-network"]/div[1]',
        "aps_machines_button" : r'//*[@id="ui-select-choices-row-4-0"]',
        
        "start_date_form" : r'//*[@id="dateFrom"]',
        "end_date_form" : r'//*[@id="dateTo"]',
        "store_code_button" : r'//*[@id="selected-spot"]',
        "store_code_form" : r'//*[@id="selected-spot"]/input[1]',
        "machine_code_widget_button" : r'//*[@id="selected-device"]/div[1]/span',
        "machine_code_button" : r'//*[@id="ui-select-choices-row-8-0"]/span',
        "machine_code_button2" : r'//*[@id="ui-select-choices-row-8-1"]/span',
        "search_button" : r'//*[@id="stats-actions"]/div[2]/div/i[5]',
        "download_excel_button" : r'//*[@id="stats-actions"]/div[2]/div/i[2]', 
    }
    
    for flow_element in flow:
        if "button" in flow_element:
            if machine_code[-1] == '2' and flow_element == 'machine_code_button':
                continue
            elif machine_code[-1] != '2' and flow_element == 'machine_code_button2':
                continue
            else:
                click_function(flow[flow_element])
        elif "form" in flow_element:
            if "start_date" in flow_element:
                fill_out_form(flow[flow_element], start_date)
            if "end_date" in flow_element:
                click_function(flow[flow_element])
                fill_out_form(flow[flow_element], end_date)
            if "store_code" in flow_element:
                fill_out_form(flow[flow_element], store_code)
                time.sleep(2)
                fill_out_form(flow[flow_element], "enter")
        
        time.sleep(2)

def sign_out():
    driver.find_element(
        by = By.XPATH,
        value = r'/html/body/div[1]/div/div[1]/div[2]/span[2]/i[1]'
    ).click()

def date_sanity_check(which_date):
    while True:
        try:
            date_input = int(input("Please enter the " + which_date + " date (YYYYMMDD): "))
            if len(str(date_input)) != 8:
                print("The date format does not match the requirements!")
                continue
            else:
                return str(date_input)
                break
        except ValueError:
            print("Please input only numbers!")


def machine_code_sanity_check():
    while True:
        try:
            machine_code = input("Please enter the machine code you like to find (with a 0 in front): ")
            machine_code_digit = int(machine_code)
            if len(machine_code) != 6:
                print("The machine code LENGTH does not match the requirements!")
                continue
            if str(machine_code)[0] != "0":
                print("The machine code must start with a 0!")
                continue
            else:
                return str(machine_code)
                break
        except ValueError:
            print("Please input only numbers!")


def user_sanity_check():

    f = open('vid.txt')

    lines = f.readlines()

    for line in lines:
        if 'Alex' in line:
            alex_code = re.findall("W\d\d\d\d\d\d\d\d\d", line)
        if 'George' in line:
            george_code = re.findall("V\d\d\d\d\d\d\d\d\d", line)

    while True:
        user = input("Please enter the user (Alex/George): ")
        if user == 'Alex':
            print("You picked: Alex")                
            return alex_code
            break
        if user == 'George':
            print("You picked: George")                
            return george_code
            break
        else:
            print("Please enter a valid user")
            continue

def daterange(start_date, end_date):
    #Here we add one more day because otherwise the very final day of the range is not returned
    for n in range(int(((end_date+timedelta(days=1)) - start_date).days)):
        yield start_date + timedelta(n)

def create_dates_list(start_date, end_date):
    dates_list = []
    start = datetime.datetime.strptime(start_date,"%Y%m%d")
    end = datetime.datetime.strptime(end_date,"%Y%m%d")
    for single_date in daterange(start,end):
        dates_list.append(single_date.strftime("%Y%m%d"))
    return dates_list

def create_peripherals_directory(parent_folder, new_folder, start_date, end_date):
    # Sample created file: Logs_XXXXXX_from_DD_MM_to_DD_MM_YYYY where XXXXXX is the machine code
    from_to = "_from_" + start_date[6:8] + "_" + start_date[4:6] + "_to_" + end_date[6:8] + "_" + end_date[4:6] + "_" + end_date[0:4]
    # Sample command: cmd /c mkdir "PARENTFOLDER\Logs_XXXXXX_from_DD_MM_to_DD_MM_YYYY\peripherals"
    os.system("cmd /c mkdir " + '"' + parent_folder + "\\Logs_" +str(new_folder) + from_to + "\\" + 'Peripherals"')
    print("Created peripherals directory!")

def create_client_directory(parent_folder, new_folder, start_date, end_date):
    # Sample created file: Logs_XXXXXX_from_DD_MM_to_DD_MM_YYYY where XXXXXX is the machine code
    from_to = "_from_" + start_date[6:8] + "_" + start_date[4:6] + "_to_" + end_date[6:8] + "_" + end_date[4:6] + "_" + end_date[0:4]
    # Sample command: cmd /c mkdir "PARENTFOLDER\Logs_XXXXXX_from_DD_MM_to_DD_MM_YYYY\peripherals"
    os.system("cmd /c mkdir " + '"' + parent_folder + "\\Logs_" +str(new_folder) + from_to + "\\" + 'Client"')
    print("Created client directory!")

def create_ej_directory(parent_folder, new_folder, start_date, end_date):
    # Sample created file: Logs_XXXXXX_from_DD_MM_to_DD_MM_YYYY where XXXXXX is the machine code
    from_to = "_from_" + start_date[6:8] + "_" + start_date[4:6] + "_to_" + end_date[6:8] + "_" + end_date[4:6] + "_" + end_date[0:4]
    # Sample command: cmd /c mkdir "PARENTFOLDER\Logs_XXXXXX_from_DD_MM_to_DD_MM_YYYY\peripherals"
    os.system("cmd /c mkdir " + '"' + parent_folder + "\\Logs_" +str(new_folder) + from_to + "\\" + 'EJ"')
    print("Created EJ directory!")

def create_litedb_directory(parent_folder, new_folder, start_date, end_date):
    # Sample created file: Logs_XXXXXX_from_DD_MM_to_DD_MM_YYYY where XXXXXX is the machine code
    from_to = "_from_" + start_date[6:8] + "_" + start_date[4:6] + "_to_" + end_date[6:8] + "_" + end_date[4:6] + "_" + end_date[0:4]
    # Sample command: cmd /c mkdir "PARENTFOLDER\Logs_XXXXXX_from_DD_MM_to_DD_MM_YYYY\peripherals"
    os.system("cmd /c mkdir " + '"' + parent_folder + "\\Logs_" +str(new_folder) + from_to + "\\" + 'LiteDB"')
    print("Created LiteDB directory!")

def retrieve_ip(machine_code):
    df = pd.read_csv("assets/aps_ip.csv")
    info = df[df['Νεα ταυτότητα'] == f"NBP{machine_code[1:]}"]
    print(info)
    print("\n")
    print(f"Username: apsuser[machine code] e.g. apsuser034001")
    print(f"Password: ete[machine code] e.g. ete034001")

#################################################################################################################################

transaction_sources = [
r'\\v00001a184.central.nbg.gr\PrintecLogs\TransactionService',
r'\\v00001b184.central.nbg.gr\PrintecLogs\TransactionService',
r'\\v00001c184.central.nbg.gr\PrintecLogs\TransactionService'
]

print("Hi there!")

how_many_services_prompt = input("Would you like to pull the transaction services too (y/n)? ")
if how_many_services_prompt == "y":
    services = [transaction_sources]

#Server name dictionary
server_names = {
    "0" : "A",
    "1" : "B",
    "2" : "C"
}

#Service dictionary
services_names = {
    "0" : "Client",
    "1" : "Transactions"
}

#Dialog box to select storing location
target = filedialog.askdirectory().replace("/","\\")

# 2) Identify the machine code that needs investigation
machine_code_interested_in = machine_code_sanity_check()

# 3) Copy the logs for the dates of interest and paste them in a local folder
start_date = date_sanity_check("STARTING")
end_date = date_sanity_check("ENDING")

#Currently the system is heavily dependent on the structure of the services list
service_counter = 0

create_peripherals_directory(
    parent_folder = target, 
    new_folder = machine_code_interested_in,  
    start_date = start_date, 
    end_date = end_date)

create_client_directory(
    parent_folder = target, 
    new_folder = machine_code_interested_in,  
    start_date = start_date, 
    end_date = end_date)

create_ej_directory(
    parent_folder = target, 
    new_folder = machine_code_interested_in,  
    start_date = start_date, 
    end_date = end_date)

create_litedb_directory(
    parent_folder = target, 
    new_folder = machine_code_interested_in,  
    start_date = start_date, 
    end_date = end_date)

print('Find the credentials and IP below!')
print("\n")

retrieve_ip(machine_code_interested_in)

promt_flag = True
while promt_flag:
    counterfeit_promt = input("Would you like to retrieve the Excel file (y/n)? ")
    if counterfeit_promt == 'y':
        print("Collecting excel!")

        vdi_code = user_sanity_check()

        print(vdi_code)

        #Could turn this into its own function
        driver_flag=True
        while driver_flag:
            print("Please select the chromedriver path: ")
            time.sleep(1)
            driver_path = filedialog.askopenfilename().replace("/","\\")

            if "chromedriver.exe" not in driver_path:
                print("Please select the chromedriver path: ")
                time.sleep(1.5)
                driver_path = filedialog.askopenfilename().replace("/","\\")

            else:
                print("Thanks!")
                driver_flag=False
            
            time.sleep(1)


        driver = webdriver.Chrome(executable_path=driver_path)
        driver.get(
                f"https://intranetsts.nbg.gr/Online/Index/tppadminportal?workstationname={vdi_code[0]}")

        flow_function(start_date, end_date, machine_code_interested_in)
        # Wait for download to finish
        time.sleep(5)

        sign_out()

        time.sleep(2)

        promt_flag = False
   
    elif counterfeit_promt == 'n':
        promt_flag = False 
    else:
        promt_flag = True

print("Bye!")

time.sleep(2)

