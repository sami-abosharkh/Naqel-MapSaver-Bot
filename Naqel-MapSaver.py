import sys
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder, interaction
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os

os.system('cls' if os.name == 'nt' else 'clear')

capabilities = dict(
    platformName='Android',
    automationName='uiautomator2',
    deviceName='CNT6R16B14000922',
    appPackage='com.naqelexpress.naqelpointer',
    appActivity='com.naqelexpress.naqelpointer.Activity.Login.SplashScreenActivity',
    autoGrantPermissions=True,
    noReset=True,
    language='en',
    locale='US'
)

#Global Variables
appium_server_url = 'http://localhost:4723'
driver = webdriver.Remote(appium_server_url, options=UiAutomator2Options().load_capabilities(capabilities))
wait = WebDriverWait(driver, 10)
totalShipments  = 51
lastShipment    = 36
scrollIndex     = 4

noLocation  = 0
outsideZone = 0

print("||||||||||||||||||||||||||||||||||||||||||||||||||")

def ConditionSetup():
    
    if driver.current_activity != ".Activity.MainPage.MainPageActivity":
        print("Condition not met. Exiting.\n", driver.current_activity)
        driver.quit()  # Exit the program
        sys.exit()
    else:
        global totalShipments
        totalShipments = int(float(driver.find_element(by=AppiumBy.ID, value="com.naqelexpress.naqelpointer:id/ofd").text))
        driver.find_element(by=AppiumBy.XPATH, value="(//android.widget.ImageView[@resource-id=\"com.naqelexpress.naqelpointer:id/icons\"])[2]").click()

def process():

    if totalShipments == 0:
        print("There is no Shipments Amount. Exiting.")
        driver.quit()  # Exit the program
        sys.exit()
    
    while lastShipment <= totalShipments:
        CheckList()
    print("_________________________")
    print("No Location: ", noLocation)
    print("Outsize Zone: ", outsideZone)

def CheckList():
    
    global lastShipment
    global noLocation
    global scrollIndex

    shipmentNum = len(driver.find_elements(by=AppiumBy.XPATH, value="//*[@resource-id=\"com.naqelexpress.naqelpointer:id/lbSerial\" and contains(@text, '"+str(lastShipment)+"')]"))
    
    if shipmentNum > 0:
        rowParent = driver.find_elements(by=AppiumBy.XPATH, value="//*[@resource-id=\"com.naqelexpress.naqelpointer:id/lbSerial\" and contains(@text, '"+str(lastShipment)+"')]/parent::*")
        
        for e in rowParent:
            HasLocation = len(e.find_elements(by=AppiumBy.ID, value="com.naqelexpress.naqelpointer:id/imgHasLocation"))
            HasMultiOrders = len(e.find_elements(by=AppiumBy.ID, value="com.naqelexpress.naqelpointer:id/txtExpectedTime"))
            
        if HasLocation > 0:
            
            if HasMultiOrders > 0:
                multiShipments = e.find_element(by=AppiumBy.ID, value="com.naqelexpress.naqelpointer:id/txtExpectedTime").text
               
                if multiShipments != '':
                    list = multiShipments.split(",")
                    
                    for n in list:
                        if int(n) < lastShipment:
                            print(str(lastShipment) + " is Added with " + multiShipments)
                            lastShipment+=1
                            return
                    e.click()
                    ShipmentsDetails(multiShipments)
                else:
                    e.click()
                    ShipmentsDetails(str(lastShipment))
            else:
                e.click()
                ShipmentsDetails(str(lastShipment))
        else:
            print(lastShipment, "(No Location)")
            lastShipment+=1
            noLocation+=1
    
    # Scrolling Down
    if lastShipment == scrollIndex + 1:
        for a in range(4):
            ScrollDown()
            scrollIndex+=1

def ShipmentsDetails(aNum):

    global outsideZone

    #Shipments Details
    shipmentNum     = wait.until(EC.visibility_of_element_located((By.ID, 'com.naqelexpress.naqelpointer:id/txtWaybilll'))).text
    shipperName     = wait.until(EC.visibility_of_element_located((By.ID, 'com.naqelexpress.naqelpointer:id/txtShipperName'))).text
    shipmentCOD     = wait.until(EC.visibility_of_element_located((By.ID, 'com.naqelexpress.naqelpointer:id/tv_total_amount_body'))).text
    shipmentWeight  = wait.until(EC.visibility_of_element_located((By.ID, 'com.naqelexpress.naqelpointer:id/txtweight'))).text
    # phoneNum        = wait.until(EC.visibility_of_element_located((By.ID, 'com.naqelexpress.naqelpointer:id/txtPhoneNo'))).text
    # mobileNum       = wait.until(EC.visibility_of_element_located((By.ID, 'com.naqelexpress.naqelpointer:id/txtMobileNo'))).text
    shipmentAddress = wait.until(EC.visibility_of_element_located((By.ID, 'com.naqelexpress.naqelpointer:id/txtaddress'))).text

    # if (phoneNum == mobileNum): customerNumber = phoneNum
    # else: customerNumber = phoneNum + "-" + mobileNum

    details = aNum + " - " + shipperName + " [W:" + shipmentWeight + " COD:" + shipmentCOD + "]\n-> " + shipmentAddress

    shipmentPin = len(driver.find_elements(by=AppiumBy.XPATH, value="(//android.view.View[@content-desc='" + shipmentNum + ". '])"))
        
    # if shipmentPin == 0:
    #     driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value="Zoom out").click()

    if shipmentPin == 0:
        print(lastShipment, "(Outside Zone)")
        ExitDetailsPage()
        outsideZone+=1
        return
    else:
        driver.find_element(by=AppiumBy.XPATH, value="(//android.view.View[@content-desc='" + shipmentNum + ". '])").click()
    
    wait.until(EC.visibility_of_element_located((By.XPATH, "//android.widget.ImageView[@content-desc=\"Open in Google Maps\"]"))).click()
    MapSave(details, float(shipmentCOD))

def MapSave(aDetails, aCOD):

    wait.until(EC.visibility_of_element_located((By.XPATH, "//android.view.View[@text=\"Save\"]"))).click()

    if (aCOD > 0.0):
        wait.until(EC.visibility_of_element_located((By.XPATH, "//android.widget.TextView[@text=\"Want to go\"]"))).click()
    else:
        wait.until(EC.visibility_of_element_located((By.XPATH, "//android.widget.TextView[@text=\"Favorites\"]"))).click()
    
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "android.widget.EditText"))).click()
    wait.until(EC.visibility_of_element_located((By.ID, "com.google.android.apps.maps:id/multiline_text_property_editor_text_field"))).send_keys(aDetails)
    wait.until(EC.visibility_of_element_located((By.XPATH, "//android.widget.Button[@text=\"Done\"]"))).click()

    while (driver.current_activity != ".Activity.Waybill.WaybillPlanActivity"):
        driver.back()
    
    ExitDetailsPage()

def ExitDetailsPage():
    
    global lastShipment

    while True:
        if len(driver.find_elements(by=AppiumBy.ID, value="android:id/parentPanel")) > 0:
            driver.find_element(by=AppiumBy.ID, value="android:id/button1").click()
            break
        else:
            driver.back()
    
    lastShipment+=1

def ScrollDown(): 
    actions = ActionChains(driver)
    actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
    actions.w3c_actions.pointer_action.move_to_location(500, 1550)
    actions.w3c_actions.pointer_action.pointer_down()
    actions.w3c_actions.pointer_action.move_to_location(500, 1000)
    actions.perform()

##################################################################################
# ConditionSetup() #Get number of shipments
process()