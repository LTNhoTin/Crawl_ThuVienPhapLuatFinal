from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import os
import re
import time
import requests
from pathlib import Path

class ThuVienPhapLuatCrawler:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.options)
        self.data_dir = Path("/Data")
        self.data_dir.mkdir(exist_ok=True)

    def login(self):
        try:
            username_field = self.driver.find_element(By.CSS_SELECTOR, "#usernameTextBox")
            password_field = self.driver.find_element(By.CSS_SELECTOR, "#passwordTextBox")
            login_button = self.driver.find_element(By.CSS_SELECTOR, "input#loginButton")

            username_field.clear()
            username_field.send_keys("CrawLaw")

            password_field.clear()
            password_field.send_keys("123456")

            login_button.click()
            print("Login attempt completed.")
            return True
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def try_download_pdf(self, file_name):
        try:
            download_div = self.driver.find_elements(By.CSS_SELECTOR, "#divContentDoc > div.content1 > div > div.TaiVanBan")
            
            if download_div:
                pdf_link = self.driver.find_elements(By.CSS_SELECTOR, "#divContentDoc > div.content1 > div > div.TaiVanBan > a:nth-child(1)")
                
                if pdf_link:
                    pdf_url = pdf_link[0].get_attribute("href")
                    
                    if pdf_url:
                        safe_file_name = f"{file_name}.pdf"
                        file_path = self.data_dir / safe_file_name
                        
                        print(f"Downloading PDF from {pdf_url} to {file_path}")
                        
                        # Get cookies from Selenium session
                        cookies = self.driver.get_cookies()
                        cookie_string = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
                        
                        # Download using requests
                        headers = {"Cookie": cookie_string}
                        response = requests.get(pdf_url, headers=headers)
                        
                        if response.status_code == 200:
                            with open(file_path, "wb") as f:
                                f.write(response.content)
                            return True
        except Exception as e:
            print(f"Error downloading PDF: {str(e)}")
        return False

    def crawl(self):
        self.driver.get("https://thuvienphapluat.vn/page/tim-van-ban.aspx?keyword=&type=3&match=True&area=0")
        time.sleep(0.1)

        count = int(self.driver.find_element(By.ID, "lbTotal").text)
        count_txt = len(list(self.data_dir.glob("*.txt")))
        count_current = count - count_txt
        page_current = (count_current + 19) // 20  # Equivalent to Math.Ceiling

        self.driver.get(f"https://thuvienphapluat.vn/page/tim-van-ban.aspx?keyword=&area=0&match=True&type=3&status=0&signer=0&sort=1&lan=1&scan=0&org=0&fields=&page={page_current}")
        time.sleep(0.1)

        if not self.login():
            return

        time.sleep(3)

        unique_hrefs = set()

        while count_current > 0:
            content_divs = self.driver.find_elements(By.CSS_SELECTOR, "div[class^='content-']")
            content_divs = [div for div in content_divs 
                          if div.find_elements(By.CSS_SELECTOR, "div.number") 
                          and div.find_element(By.CSS_SELECTOR, "div.number").text.strip() == str(count_current)]

            for div in content_divs:
                try:
                    link_element = div.find_element(By.CSS_SELECTOR, "a[onclick='Doc_CT(MemberGA)']")
                    href = link_element.get_attribute("href")
                    file_name = re.sub(r'[\\/:*?"<>|]', '_', link_element.text.strip().replace("–", "-"))
                    file_name = file_name[:150] if len(file_name) > 150 else file_name

                    if href and href not in unique_hrefs:
                        unique_hrefs.add(href)
                        self.driver.execute_script("window.open(arguments[0]);", href)
                        time.sleep(0.1)

                        tabs = self.driver.window_handles
                        self.driver.switch_to.window(tabs[-1])
                        pdf_downloaded = self.try_download_pdf(file_name)

                        if not pdf_downloaded:
                            try:
                                content_div = self.driver.find_element(By.CSS_SELECTOR, ".content1")
                                content_texts = [f"Href: {href}"]
                                elements = content_div.find_elements(By.XPATH, ".//*")
                                paragraphs_in_tables = set()

                                # First pass: collect paragraphs in tables
                                for element in elements:
                                    if element.tag_name == "table":
                                        table_paragraphs = element.find_elements(By.XPATH, ".//p")
                                        for p in table_paragraphs:
                                            paragraphs_in_tables.add(p.text.strip())

                                # Second pass: process content
                                for element in elements:
                                    if element.tag_name == "table":
                                        width = element.get_attribute("width")
                                        table_texts = []
                                        rows = element.find_elements(By.TAG_NAME, "tr")
                                        should_skip_table = False
                                        tds_to_remove = set()

                                        for row in rows:
                                            cells = row.find_elements(By.TAG_NAME, "td")
                                            for cell in cells:
                                                cell_text = cell.text.strip().lower()
                                                if "kính gửi" in cell_text:
                                                    should_skip_table = True
                                                    break
                                                if "nơi nhận" in cell_text:
                                                    tds_to_remove.add(cell)
                                            if should_skip_table:
                                                break

                                        if not should_skip_table:
                                            for row in rows:
                                                cells = row.find_elements(By.TAG_NAME, "td")
                                                row_texts = []

                                                for cell in cells:
                                                    if cell not in tds_to_remove:
                                                        row_texts.append(cell.text.strip())

                                                if width == "100%" and len(rows) > 1:
                                                    table_texts.append(" || ".join(row_texts))
                                                else:
                                                    table_texts.extend(row_texts)

                                            content_texts.extend(table_texts)
                                    elif element.tag_name == "p" and element.text.strip() not in paragraphs_in_tables:
                                        content_texts.append(element.text.strip())

                                file_path = self.data_dir / f"{file_name}.txt"
                                with open(file_path, "w", encoding="utf-8") as f:
                                    f.write("\n".join(content_texts))

                            except Exception as e:
                                print(f"Error processing content: {str(e)}")

                        self.driver.close()
                        self.driver.switch_to.window(tabs[0])
                        count_current -= 1

                except NoSuchElementException:
                    print("Không tìm thấy liên kết phù hợp trong phần tử này.")
                except Exception as e:
                    print(f"Unexpected error: {str(e)}")

            if count_current > 0 and count_current % 20 == 0:
                try:
                    prev_page_buttons = self.driver.find_elements(By.CSS_SELECTOR, "a[rel='nofollow']")
                    prev_page_button = next((btn for btn in prev_page_buttons if btn.text.strip() == "Trang trước"), None)
                    if prev_page_button:
                        prev_page_button.click()
                        time.sleep(0.1)
                except NoSuchElementException:
                    print("Không tìm thấy nút chuyển trang.")
                    break

        self.driver.quit()

if __name__ == "__main__":
    crawler = ThuVienPhapLuatCrawler()
    crawler.crawl() 