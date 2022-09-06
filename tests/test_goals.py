import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import datetime
import time
from .utils import *
from .test_user import get_user, add_new_user, delete_user


def get_goal(id):
    goals = [{
        "user": 1,
        "name": "Kids education",
        "start_dt": datetime.date(day=10, month=12, year=2021),
        "time_period": 144,
        "current_val": 25000,
        "inflation": 4
    },
    {
        "user": 1,
        "name": "Home downpayment",
        "start_dt": datetime.date(day=13, month=1, year=2021),
        "time_period": 60,
        "current_val": 250000,
        "inflation": 5
    }]
    return goals[id]

def add_new_goal(driver, goal):
    time.sleep(3)
    driver.find_element(By.XPATH, "//a[@href='create']").click()

    time.sleep(3)
    driver.find_element(By.ID, "name").click()
    driver.find_element(By.ID, "name").send_keys(goal["name"])
    driver.find_element(By.ID, "startdate").send_keys(goal["start_dt"].strftime('%m/%d/%Y'))
    
    driver.find_element(By.ID, "curr_val").send_keys(goal["current_val"])
    driver.find_element(By.ID, "inflation").send_keys(goal["inflation"])
    driver.find_element(By.ID, "time_period").send_keys(goal["time_period"])
    time.sleep(3)
    select = Select(driver.find_element(By.ID, 'user'))
    # select by visible text
    #select.select_by_visible_text('Banana')

    # select by value 
    select.select_by_value(str(goal["user"]))
    driver.find_element(By.NAME, "calculate").click()
    time.sleep(5)
    driver.find_element(By.NAME, "submit").click()
    time.sleep(5)
    driver.find_element(By.LINK_TEXT, "Cancel").click()
    time.sleep(5)

def delete_goal_with_row_id(driver, id):
    count, rows = get_rows_of_table(driver, 'goal-table')
    for row in rows:
        th = row.find_element(By.TAG_NAME, 'th')
        print(f'text is {th.text}')
        if th.text == str(id):
            driver.maximize_window()
            cols = row.find_elements(By.TAG_NAME, 'td')
            cols[len(cols)-1].find_element(By.CSS_SELECTOR, "a[href*='delete']").click()
            time.sleep(2)
            obj = driver.switch_to.alert
            #Retrieve the message on the Alert window
            msg=obj.text
            print ("Alert shows following message: "+ msg )

            time.sleep(2)

            #use the accept() method to accept the alert
            obj.accept()

def set_prerequisites(driver):
    driver.find_element(By.XPATH, "//a[@href='/user']").click()
    i = 0
    while True:
        try:
            u = get_user(i)
            if not u:
                break
            add_new_user(driver, u)
            i += 1
        except IndexError:
            break
    driver.find_element(By.XPATH, "//a[@href='/goal']").click()
    time.sleep(3)
    print(f'current url is {driver.current_url}')


@pytest.mark.usefixtures("driver_init")
@pytest.mark.django_db
class Test_Goal:
    def test_flow(self, live_server):
        self.driver.get(("%s%s" % (live_server.url, "/user/")))
        self.open_url()
        self.add_new_goal()
        self.add_another_goal()
        self.delete_goals()

    def open_url(self):
        set_prerequisites(self.driver)
        time.sleep(5)
        count, _ = get_rows_of_table(self.driver, 'goal-table')
        assert count == 0
    
    def add_new_goal(self):
        u = get_goal(0)
        add_new_goal(self.driver,  u)
        count, _ = get_rows_of_table(self.driver, 'goal-table')
        assert count == 1
    
    def add_another_goal(self):
        u = get_goal(1)
        add_new_goal(self.driver,  u)
        count, _ = get_rows_of_table(self.driver, 'goal-table')
        assert count == 2
    
    def delete_goals(self):
        expected_count = 2
        count, rows = get_rows_of_table(self.driver, 'goal-table')
        assert count == expected_count
        delete_goal_with_row_id(self.driver, 1)
        count, rows = get_rows_of_table(self.driver, 'goal-table')
        assert count == expected_count-1
        # instead of deleting the remaining goal, delete its user and make sure that the goal is gone
        # when user is deleted
        remaining_goal = get_goal(1)
        self.driver.find_element(By.XPATH, "//a[@href='/user']").click()
        time.sleep(3)
        delete_user(self.driver, remaining_goal['user'])
        time.sleep(3)
        self.driver.find_element(By.XPATH, "//a[@href='/goal']").click()
        time.sleep(3)
        count, rows = get_rows_of_table(self.driver, 'goal-table')
        assert count == 0
 