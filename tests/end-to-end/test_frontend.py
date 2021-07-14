import datetime
import logging
import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from smartsexplore.database import get_session
from smartsexplore.database.models import SMARTS, DirectedEdge, Molecule, Match

PORT = 7353
HOST = 'localhost'
APP_URL = f'http://{HOST}:{PORT}'


@pytest.fixture
def full_running_server(full_app, caplog):
    def run():
        return full_app.run(host=HOST, port=PORT)

    caplog.set_level(logging.INFO)
    import multiprocessing
    proc = multiprocessing.Process(target=run)
    proc.start()
    logging.info("Server subprocess started")

    yield

    logging.info("Terminating server subprocess...")
    proc.terminate()
    proc.join(3)
    proc.kill()
    assert proc.exitcode is not None, "Couldn't get server process to terminate within 3 seconds!"
    logging.info(f"Server subprocess exited with code {proc.exitcode}")


# Many thanks to https://github.com/alex028502/istanbulseleniumexample/blob/master/test.py
@pytest.fixture
def driver(full_running_server):
    _driver = webdriver.Chrome()
    _driver.get(APP_URL)
    _driver.implicitly_wait(1)
    yield _driver
    coverage_info = _driver.execute_script('return JSON.stringify(window.__coverage__);')
    assert coverage_info is not None,\
        "Coverage from the frontend is missing! Did you run `npm run testprep`?"

    if os.environ.get('GENERATE_E2E_COVERAGE', False):
        timestamp = datetime.datetime.timestamp(datetime.datetime.now())
        outfile = f"coverage/frontend/coverage-e2e-{timestamp}.json"
        logging.info(f"Writing E2E coverage JSON to {outfile}.")
        file = open(outfile, 'w')
        file.write(coverage_info)
        file.close()
    else:
        logging.info(
            "Not writing E2E coverage because GENERATE_E2E_COVERAGE env var is not truthy.")

    _driver.close()
    _driver.quit()
    logging.info("Quit Webdriver.")
    time.sleep(1)


def test_smarts_objects_are_rendered_and_colored(driver, full_session):
    assert driver.find_element_by_css_selector('svg') is not None

    nodes = driver.find_elements_by_tag_name('circle')
    assert len(nodes) == full_session.query(SMARTS).count()

    edges = driver.find_elements_by_css_selector('line.real')
    # exact expectations are difficult, because the client compounds forward and backwards edges
    # to one 'equal' edge. Let's just expect that there are edges rendered...
    assert len(edges) > 0

    get_node_fills = """
    return arguments[0].map(function(node) { return node.getAttribute('fill'); });
    """
    node_fills = driver.execute_script(get_node_fills, nodes)
    get_edge_strokes = """
        return arguments[0].map(function(edge) { return edge.getAttribute('stroke'); });
        """
    edge_strokes = driver.execute_script(get_edge_strokes, edges)
    node_colors = set(node_fills)
    edge_colors = set(edge_strokes)

    nof_libraries = full_session.query(SMARTS)\
        .distinct(SMARTS.library).group_by(SMARTS.library).count()
    assert len(node_colors) == nof_libraries
    assert len(edge_colors) > 3  # similar issues as above apply again


def test_node_dragging(driver):
    time.sleep(10)  # wait for simulation to relax
    node = driver.find_element_by_css_selector('circle[data-id="447"]')
    node2 = driver.find_element_by_css_selector('circle[data-id="578"]')
    cx, cy = node.get_attribute('cx'), node.get_attribute('cy')
    cx2, cy2 = node2.get_attribute('cx'), node2.get_attribute('cy')

    # Simulate a dragging action (in x)
    action = ActionChains(driver)
    action.click_and_hold(node).move_by_offset(10, 0).release().perform()
    time.sleep(1)  # let simulation relax
    cx_new, cy_new = node.get_attribute('cx'), node.get_attribute('cy')
    cx2_new, cy2_new = node2.get_attribute('cx'), node2.get_attribute('cy')
    assert cx_new != cx
    assert abs(float(cy_new) - float(cy)) < 1
    # This should also have moved the neighboring node
    assert cx2_new != cx2
    assert cy2_new != cy2

    # Simulate another dragging action (in y)
    action = ActionChains(driver)
    action.click_and_hold(node).move_by_offset(0, 10).release().perform()
    time.sleep(5)  # let simulation relax
    cx_new2, cy_new2 = node.get_attribute('cx'), node.get_attribute('cy')
    cx2_new2, cy2_new2 = node2.get_attribute('cx'), node2.get_attribute('cy')
    assert abs(float(cx_new2) - float(cx_new)) < 1
    assert cy_new2 != cy_new
    assert cx_new2 != cx
    assert cy_new2 != cy
    # This should also have moved the neighboring node
    assert cx2_new2 != cx2_new
    assert cy2_new2 != cy2_new


def test_upload_molecule_file(driver: webdriver.Chrome):
    test_file = os.path.join(os.path.dirname(__file__), 'ten_molecules.smi')
    some_node = driver.find_element_by_css_selector(f'circle[data-id="392"]')
    some_node_fill = some_node.get_attribute('fill')

    with open(test_file, 'r') as file:
        # Get the file contents from the test SMILES file, 'ten_molecules.smi'.
        file_contents = file.read()
        # JavaScript code to simulate uploading the test file.
        js_code = """
        // this code is designed like so for test debugging purposes -- if it fails, add a sleep
        // instruction somewhere in the Python code, then you can manually call these functions
        // in the running test browser.
        window.fileInput = arguments[0];
        window.runTestFn = function() {
            const file = new File(["%s"], "ten_molecules.smi", {type: 'chemical/x-daylight-smiles'});
            const container = new DataTransfer();
            container.items.add(file);
            fileInput.files = container.files;
            fileInput.dispatchEvent(new Event('change'));
        };
        window.runTestFn();
        """ % (repr(file_contents)[1:-1])  # [1:-1] cuts out the enclosing '' of the repr return val
        # we used repr in the line above to ensure linebreaks are inserted as quoted into the JS

        file_input = driver.find_element_by_css_selector('.upload-box input[type="file"]')
        driver.execute_script(js_code, file_input)
        time.sleep(5)  # wait for code execution

        # Expect that the fill of the node changed :)
        some_node_fill_new = some_node.get_attribute('fill')
        assert some_node_fill != some_node_fill_new

        # Now expect to find the toggle for showing molecule matches (or not)
        toggle = driver.find_element_by_xpath("//*[text()='Show molecule matches']")
        toggle.click()
        time.sleep(1)
        # and then expect that to have changed the fill back
        some_node_fill_new2 = some_node.get_attribute('fill')
        assert some_node_fill_new2 != some_node_fill_new
        assert some_node_fill_new2 == some_node_fill

        # Now let's hover a node which we know should match
        matching_node = driver.find_element_by_css_selector('circle[data-id="447"]')
        driver.execute_script("arguments[0].scrollIntoView()", matching_node)
        ActionChains(driver).move_to_element(matching_node).perform()
        molecule_el = driver.find_element_by_css_selector('.molecule')
        # Expect that the name matches the one we know it should have
        molecule_name = molecule_el.find_element_by_tag_name('label').get_attribute('innerHTML')
        assert molecule_name == 'NCGC00188429-03'
        # Expect the corresponding image to exist and have been successfully loaded
        molecule_img = molecule_el.find_element_by_tag_name('img')
        img_valid = driver.execute_script(
            'return arguments[0].complete && arguments[0].naturalHeight', molecule_img)
        assert img_valid, "Molecule image should have rendered but seems to be missing!"

        # Now let's hover an edge between nodes which we know should match
        matching_edge = driver.find_element_by_css_selector('line.real[data-id="1315"]')
        driver.execute_script("arguments[0].scrollIntoView()", matching_node)
        ActionChains(driver).move_to_element(matching_edge).perform()
        matches_el = driver.find_element_by_css_selector('.molecule-matches')
        # expect there to be a 'common match' molecule
        molecule_el = matches_el.find_element_by_css_selector('.molecule.common-match')
        # Expect that the name matches the one we know it should have
        molecule_name = molecule_el.find_element_by_tag_name('label').get_attribute('innerHTML')
        assert molecule_name == 'NCGC00188429-03'
        # Expect the corresponding image to exist and have been successfully loaded
        molecule_img = molecule_el.find_element_by_tag_name('img')
        img_valid = driver.execute_script(
            'return arguments[0].complete && arguments[0].naturalHeight', molecule_img)
        assert img_valid, "Molecule image should have rendered but seems to be missing!"


def test_hovering_graph_objects_updates_infobox(driver, full_session):
    info_container = driver.find_element_by_css_selector('.info-container')
    image_container = info_container.find_element_by_tag_name('image')
    title_div = info_container.find_element_by_css_selector('.title')
    title_text = title_div.get_attribute('innerHTML')
    assert 'hover over' in title_text.lower()

    # For a random SMARTS
    smarts = full_session.query(SMARTS).get(392)
    node = driver.find_element_by_css_selector(f'circle[data-id="392"]')
    driver.execute_script("arguments[0].scrollIntoView()", node)
    ActionChains(driver).move_to_element(node).perform()

    title_text = title_div.get_attribute('innerHTML')
    assert 'hover over' not in title_text.lower()
    assert smarts.name in title_text
    assert str(smarts.id) in image_container.get_attribute('href')

    # For a random edge
    edge = full_session.query(DirectedEdge).get(897)
    line = driver.find_element_by_css_selector(f'line.real[data-id="897"]')
    driver.execute_script("arguments[0].scrollIntoView()", line)
    ActionChains(driver).move_to_element(line).perform()

    title_text = title_div.get_attribute('innerHTML')
    assert 'hover over' not in title_text.lower()
    assert smarts.name not in title_text
    assert edge.from_smarts.name in title_text
    assert edge.to_smarts.name in title_text
    assert str(edge.id) in image_container.get_attribute('href')
