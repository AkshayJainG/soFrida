from gpapi.googleplay import GooglePlayAPI, RequestError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import sys, os, time
import traceback
import argparse
import subprocess
import platform

class Downloader:
    def __init__ (self):
        self.gid = ""
        self.gwd = ""
        self.authSubToken = ""
        self.options = Options()
        self.options.headless = False
        self.chrome_driver = "./chromedriver"
        if platform.system() == "Windows":
            self.chrome_driver = "./chromedriver.exe"
        self.request_url = "https://accounts.google.com/b/0/DisplayUnlockCaptcha"

        self.apkfile_path = os.path.join("./tmp/")
        if os.path.exists(self.apkfile_path) == False:
            os.mkdir(self.apkfile_path)
        self.server = GooglePlayAPI('ko_KR', 'Asia/Seoul')
        self.devices_codenames = GooglePlayAPI.getDevicesCodenames()
        self.devices_codenames.reverse()

    # LOGIN
    def firstlogin(self, gid, gpw):
        self.gid = gid
        self.gpw = gpw
        #print(self.gid+" "+self.gpw)
        try:
            print('\nLogging in with email and password\n')
            self.server.login(self.gid, self.gpw, None, None)
            self.gsfId = self.server.gsfId
            self.authSubToken = self.server.authSubToken
            return self.secondlogin()
        except:
            traceback.print_exc()
            return False
            #print ("Need to unlock account")
            #self.browser = webdriver.Chrome(self.chrome_driver, chrome_options=self.options)
            #self.browser.get(self.request_url)
            ##self.browser.find_element_by_css_selector("#submitChallenge").click()
            #val = input("Recall firstlogin")
            #self.browser.close()
            #self.firstlogin(gid, gpw)
            #self.UnlockCaptcha()

    def secondlogin(self):
        print('\nNow trying secondary login with ac2dm token and gsfId saved\n')
        self.server = GooglePlayAPI('ko_KR', 'Asia/Seoul')
        self.server.login(None, None, self.gsfId, self.authSubToken)

        # call DOWNLOAD
        self.startdownload()
        return True

    def download_packages(self, package_list):
        for package in package_list:
            self.startdownload(package)

    def startdownload(self, pkgid=""):
        self.pkgid = pkgid
        if self.pkgid == "":
            return 
        print('\nAttempting to download %s\n' % self.pkgid)
        try:
            fl = ""
            for codename in self.devices_codenames:
                print("try "+codename)
                self.server = GooglePlayAPI('ko_KR', 'Asia/Seoul', device_codename=codename)
                self.server.login(None, None, self.gsfId, self.authSubToken)
                try:
                    fl = self.server.download(self.pkgid)
                    break
                except Exception as e:
                    print(e)
                    continue
            if fl == "":
                raise Exception("No Device")
            with open(self.apkfile_path + self.pkgid + '.apk', 'wb') as apk_file:
                for chunk in fl.get('file').get('data'):
                    apk_file.write(chunk)
                print('\n[+] Download successful\n')
        except :
            print("Unexpected error:", sys.exc_info()[0])
            traceback.print_exc()
            #time.sleep(3)
            pass

        # time.sleep(1)

    def check_aws_sdk(self, pkgid):
        print('[+] Checking AWS_SDK')
        apkfinal_path = apkfile_path + pkgid + '.apk'
        s = os.popen('/usr/bin/grep -i "aws-android-sdk" {0}'.format(apkfinal_path)).read()
        if 'matches' in s:
            print ("[!] This Application use AWS_SDK")
            pass
        else:
            print ("[!] NO AWS_SDK FOUND")
            os.remove(apkfinal_path)

