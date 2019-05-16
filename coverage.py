import unittest
from selenium import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.chrome.options import Options
import os
class PythonOrgSearch(unittest.TestCase):
    def setUp(self, src_path=""):
        myProxy = "localhost:3128"
        proxy = Proxy({
            'proxyType': ProxyType.MANUAL,
            'httpProxy': myProxy,
            'ftpProxy': myProxy,
            'sslProxy': myProxy,
            'noProxy': ''  # set this value as desired
        })
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--proxy-server=%s' % myProxy)
        self.driver = webdriver.Chrome(executable_path="./chromedriver", chrome_options=chrome_options)
        cmd = "java -jar ./JSCover-2.0.6/target/dist/JSCover.jar -ws --no-branch --document-root={} --report-dir=target --no-instrument=test --no-instrument=js/lib".format(src_path)
        os.system(cmd)
    def test_search_in_python_org(self):
        driver = self.driver
        driver.get("http://localhost-proxy:8080/index.html")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "radio1")))
        driver.find_element_by_id('radio1').click()
        driver.execute_script("jscoverage_report('python');");
    def tearDown(self):
        self.driver.close()
if __name__ == '__main__':
    unittest.main()
