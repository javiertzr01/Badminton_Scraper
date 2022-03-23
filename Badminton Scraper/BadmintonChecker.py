import requests
import re
from bs4 import BeautifulSoup
import datetime
import time

def get_html(url):
    response = requests.get(url)
    if not response.ok:
        print(f"Code: {response.status_code}, url: {url}")
    return response.text

def get_available_dates(html):
    global next_day
    timeslots = []
    all_courts = []
    all_court_status_list = []
    all_timeslots_status = []
    soup = BeautifulSoup(html,'lxml', multi_valued_attributes=None)
    time_slots = soup.find('div', class_ = "timeslotsContainer")
    check_date_available = soup.find('span', id = "content_0_lblError")
    try:
        if (check_date_available.get_text() != ""):
            next_day = False
        final_time_slots = time_slots.find_all(attrs={"class" : "slots"})
        for time in final_time_slots:
            time = str(time)
            timeslots_1 = time.split('<div class="slots">')
            timeslots_2 = timeslots_1[1]
            timeslots_3 = timeslots_2.split('</div>')
            timeslots.append(timeslots_3[0])
    except:
        print("website down")
        next_day = False
    
    #print(timeslots)
    
    column = soup.find_all('div', class_ = "facilitiesType")
    for court in column:
        #Getting the number of courts
        court_span = court.find_all(re.compile('span'))
        court_number_id = court_span[0]
        court_number_id = str(court_number_id.get('id'))
        court_number = court_number_id[-1]
        all_courts.append(court_number)
        
        #Getting the status of courts
        court_status = court_span[1:]
        court_status_list = []
        for i in court_status:
            court_availability = i.get('class')
            court_status_list.append(court_availability)
        all_court_status_list.append(court_status_list)
    
    #Associating all the timeslots into their respective availabilities
    for y in all_court_status_list:
        timeslot_availability_dict = {}
        for z in range(len(timeslots)):
            timeslot_availability_dict[timeslots[z]] = y[z]
        all_timeslots_status.append(timeslot_availability_dict)
    
    #Filtering
    for a in range(len(all_timeslots_status)):
        for time in all_timeslots_status[a]:
            if all_timeslots_status[a][time] != 'slots booked' and all_timeslots_status[a][time] != "slots notAvailable":
                print(time, a+1)
                pass
            else:
                pass

def getdate(number_of_days_forward):
    if number_of_days_forward == 0:
        date_unformatted = datetime.date.today()
    else:
        date_unformatted = datetime.date.today() + datetime.timedelta(days=number_of_days_forward)
    date_unformatted_str = str(date_unformatted)
    year = str(date_unformatted_str[0:4])
    month = str(date_unformatted_str[5:7])
    day = str(date_unformatted_str[8:10])
    date = day + "-" + month + "-" + year
    return date, date_unformatted

def main(location):
    global next_day
    global check_weekend
    number_of_days_forward = 0
    while next_day == True:
        date = getdate(number_of_days_forward)
        if check_weekend == True:
            if date[1].strftime("%A") == "Saturday" or date[1].strftime("%A") == "Sunday":
                print(date[0])
                url = "https://www.onepa.gov.sg/facilities/" + location + "?date=" + date[0]
                request = get_html(url)
                time.sleep(2)
                get_available_dates(request)
                number_of_days_forward += 1
            else:
                number_of_days_forward += 1
        else:
            print(date[0])
            url = "https://www.onepa.gov.sg/facilities/" + location + "?date=" + date[0]
            request = get_html(url)
            time.sleep(2)
            get_available_dates(request)
            number_of_days_forward += 1


if __name__ == "__main__":
    Location_Code = {
        "Braddell Heights CC" : "4190CCMCPA-BM",
        "Hougang CC" : "4670CCMCPA-BM",
        "Our Tampines Hub" : "2400IPOGPA-BM",
        "Punggol 21 CC": "4040CCMCPA-BM",
        "Tampines Changkat CC" : "4390CCMCPA-BM",
        "Tampines North CC" : "5250CCMCPA-BM",
        "Tampines West CC" : "5630CCMCPA-BM",
        "Teck Ghee CC" : "5690CCMCPA-BM"
    }
    for location in Location_Code:
        print(location)
    start_from = input("Please type from which CC you want to start searching? (Top to bottom, space-sensitive): ")
    check_weekend = input("Do you want weekends only? [Y/N]: ")
    while check_weekend != True and check_weekend != False:
        if check_weekend.casefold() == "y":
            check_weekend = True
        elif check_weekend.casefold() == "n":
            check_weekend = False
        else:
            check_weekend = input("Please input y or n only: ")
    start = False
    for x in Location_Code:
        if start == False:
            if start_from.casefold() == x.casefold():
                print(x)
                next_day = True
                main(Location_Code[x])
                start = True
        else:
            print(x)
            next_day = True
            main(Location_Code[x])
