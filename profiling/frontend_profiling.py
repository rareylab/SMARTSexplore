"""
Profiles the frontend by performing various typical user actions, timing them,
and writing the results to named .csv files.

Requires Selenium (as a Python package), Chrome, and a Selenium Chrome Driver to
be installed. Currently only works in Google Chrome: The geckodriver (Firefox)
Selenium backend errors on global await (see tc39 GitHub) even though the Firefox
version implements it. Other browsers untested; global await is required.

:Authors:
    Simon Welker
"""
from io import StringIO
import sys

import time
from collections import defaultdict
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


# https://stackoverflow.com/a/16571630/3090225
class CaptureToList(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout


class Timer:
    def __init__(self, name):
        self.start = None
        self.end = None
        self.name = name

    def __enter__(self):
        self.start = time.perf_counter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.perf_counter()
        self.elapsed_ms = (self.end - self.start) * 1000
        print(f'{self.name},{self.elapsed_ms:.2f}')


def perf(*actions):
    action_lines = ";\n".join(actions)
    return f'''
    const start = performance.now();
    {action_lines};
    const end = performance.now();
    return end - start;
    '''


def await_event(element, event_name, element_is_css=True):
    if element_is_css:
        element = f"document.querySelector('{element}')"
    return f"await {element}.dispatchEvent(new Event('{event_name}'));"


def profile_search(driver):
    # Locate search input field
    search_field = driver.find_element_by_id("searchbar")
    search_field.clear()

    for search_string in ["(qu|ch)inone", "a", "XYZASD"]:
        search_field.send_keys(search_string)
        timing = driver.execute_script(perf(await_event('#searchbar', 'change')))
        time.sleep(.3)
        print(f'search_{search_string},{timing}')
        # .clear() might trigger 'change' on its own... so send backspaces instead
        search_field.send_keys(Keys.BACKSPACE * len(search_string))
        timing = driver.execute_script(perf(await_event('#searchbar', 'change')))
        time.sleep(.3)
        print(f'reset_search_{search_string},{timing}')


def profile_info_hover(driver):
    circles = driver.find_elements_by_css_selector('.node')
    lines = driver.find_elements_by_css_selector('.composite-line')

    for j, circle in enumerate(random.sample(circles, 10)):
        timing = driver.execute_script(
            perf(await_event('arguments[0]', 'mouseover', element_is_css=False)),
            circle)
        time.sleep(.3)
        print(f'circle_hover_{j},{timing}')

    for j, line in enumerate(random.sample(lines, 10)):
        timing = driver.execute_script(
            perf(await_event('arguments[0]', 'mouseover', element_is_css=False)),
            line)
        time.sleep(.3)
        print(f'line_hover_{j},{timing}')


def profile_library_selection(driver):
    # --- Deselection and reselection of all libraries at once

    selection_container = driver.find_element_by_css_selector('.library-select')
    all_link = selection_container.find_element_by_link_text('All')
    none_link = selection_container.find_element_by_link_text('None')

    timing = driver.execute_script(
        perf(
            await_event('arguments[0]', 'click', element_is_css=False)
        ),
        none_link
    )
    print(f'deselect_all_libraries,{timing}')
    time.sleep(.5)

    timing = driver.execute_script(
        perf(
            await_event('arguments[0]', 'click', element_is_css=False)
        ),
        all_link
    )
    print(f'reselect_all_libraries,{timing}')
    time.sleep(.5)

    # --- Randomized deselection and reselection of single libraries

    labels = driver.find_elements_by_css_selector('.library-selector label')
    random.shuffle(labels)

    for j, label in enumerate(labels):
        cb = label.find_element_by_css_selector('input[type=checkbox]')
        library_name = cb.get_attribute('id')[len('__library-checkbox-'):]

        timing = driver.execute_script(
            perf(
                "arguments[0].checked = false;",
                await_event('arguments[0]', 'change', element_is_css=False)
            ),
            cb
        )
        print(f'library_deselect_{library_name},{timing}')
        time.sleep(.5)

    random.shuffle(labels)

    for j, label in enumerate(labels):
        cb = label.find_element_by_css_selector('input[type=checkbox]')
        library_name = cb.get_attribute('id')[len('__library-checkbox-'):]

        timing = driver.execute_script(
            perf(
                "arguments[0].checked = true;",
                await_event('arguments[0]', 'change', element_is_css=False)
            ),
            cb
        )
        print(f'library_reselect_{library_name},{timing}')
        time.sleep(.5)


profilers = [
    (profile_search, 'search.csv'),
    (profile_info_hover, 'info_hover.csv'),
    (profile_library_selection, 'library_selection.csv')
]


if __name__ == '__main__':
    repeats = 5

    drivers = [
        # firefox is not available for this: top-level await (tc39) fails with SyntaxError in
        # Selenium geckodriver (but works in the opened browser???)
        #('firefox', webdriver.Firefox()),
        ('chrome', webdriver.Chrome())
    ]
    for driver_name, driver in drivers:
        driver.implicitly_wait(3)
        driver.get("http://localhost:5000")
        driver.maximize_window()
        input()

        for (fn, outfile) in profilers:
            outfile_prefixed = f'{driver_name}.{outfile}'
            with open(outfile_prefixed, 'w') as f:
                with CaptureToList() as output_lines:
                    for i in range(repeats):
                        fn(driver)
                f.write("\n".join(output_lines) + "\n")


# Browserfenster schließen
#driver.quit()
