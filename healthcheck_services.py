import os
import datetime

# connect to services
transaction_sources = [
    r'\\v00001a184.central.nbg.gr\PrintecLogs\TransactionService',
    r'\\v00001b184.central.nbg.gr\PrintecLogs\TransactionService',
    r'\\v00001c184.central.nbg.gr\PrintecLogs\TransactionService'
]

# key-words to search for
key_words = [
    "NbgTokenAcquirer - Get token failed!",
    "BadRequest",
    "Post to NBG API failed",
    "TransactionPaymentHelper - Payment responded",
    "Api-Proxy-Error"
]

# scan through all files
todays_date = datetime.date.today().strftime("%Y%m%d")

print(f"Today's date: {todays_date}")
print(f"---------------------------")

hit_count = 0

for service in transaction_sources:

    files = os.listdir(service)

    for log_file in files:
        # print(log_file)
        if todays_date in log_file and ".log" in log_file:
            service_file = open(os.path.join(service, log_file), "r", encoding="utf-8")

            print(f"Currently checking {os.path.join(service, log_file)}")

            file_lines = service_file.read().splitlines()

            # Reseting the hit count for each file!
            hit_count = 0

            for line in file_lines:
                for key_word in key_words:
                    if key_word in line:
                        if hit_count < 10:
                            print(f"Found an {key_word} error!")
                        else:
                            continue
                        hit_count += 1

            print(f"---------------------------")

            if hit_count == 0:
                print(f"No hits! | {service}")
            else:
                print(f"Had a hit, a total of {hit_count} times | {service}")