import os
import re
import pandas as pd
from datetime import date, timedelta
import datetime
from tkinter import filedialog


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

def get_ncr_files(source, destination, i):
    # print(f"{source}\\NcrFileSink.txt")
    # print(f' cmd /c copy "{source}\\NcrFileSink.txt" "{destination}\\NcrFileSink{i}.txt" ')
    os.system(f' cmd /c mkdir "{destination}" ')
    os.system(f' cmd /c copy "{source}\\NcrFileSink.txt" "{destination}\\NcrFileSink{i}.txt" ')

###############################################################################################################

print("Please select destination folder")
target = filedialog.askdirectory().replace("/","\\")

# May need to add sanity checks in the future
investigation_name = input("Please enter the name of the investigation: ")

final_target = f"{target}\\NcrInvestigation_{investigation_name}"

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

device_sources = [
r'\\v00001a184.central.nbg.gr\PrintecLogs\DeviceService',
r'\\v00001b184.central.nbg.gr\PrintecLogs\DeviceService',
r'\\v00001c184.central.nbg.gr\PrintecLogs\DeviceService'
]

start_date = date_sanity_check("Starting")
end_date = date_sanity_check("Ending")

dates_list = create_dates_list(start_date, end_date)

for i, source_path in enumerate(device_sources):
    get_ncr_files(source_path, final_target, i)

for i in range(len(dates_list)):
    final_ncr = open(f"{final_target}\\Ncr{dates_list[i]}.csv", "w")
    final_ncr.write("(ST);code;aps_code;date;time;error_code;error_message;;")
    final_ncr.write("\n")

    for file in os.listdir(final_target):
        
        file_path = os.path.join(final_target, file)

        if "NcrFile" in file:
            ncr_file = open(file_path, "r")

            for line in ncr_file.readlines():
                date_regex = "\d\d\d\d\d\d\d\d"
                regex_result = re.findall(date_regex, line)
                if dates_list[i] in regex_result:
                    # print("Found 2023 line")
                    line = line.replace("<fs>", ";")
                    line = line.replace("<lf>", ";")
                    line = line.replace(";;", ";")
                    # line = line.replace(",,,", ",")
                    final_ncr.write(line)


    final_ncr.close()

    df = pd.read_csv(f"{final_target}\\Ncr{dates_list[i]}.csv", sep=';')
    final_df = df.sort_values(["time"], axis=0, ascending=False)

    final_df.to_excel(f"{final_target}\\NcrFinal{dates_list[i]}.xlsx", index=False)

