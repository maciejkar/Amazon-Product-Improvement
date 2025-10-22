import logging
import random
import re
import time
from typing import Optional, Tuple
import undetected_chromedriver as uc  # type: ignore
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from src.config import settings

LOGGER = logging.getLogger("fetcher")


class ScrapingError(Exception):
    pass


class AmazonScraper:
    def __init__(self, email: str, password: str) -> None:
        self.email: str = email
        self.password: str = password

        self.chrome_options = Options()
        self._config_chrome()

        self.driver: WebDriver

    def _config_chrome(self) -> None:
        if not settings.HEADFUL_BROWSER:
            self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument(
            "--disable-blink-features=AutomationControlled"
        )
        self.chrome_options.add_argument("--incognito")
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--remote-debugging-port=9222")
        self.chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        )

    def _random_wait(
        self, min_time: float = 0.5, max_time: float = 2, explicit: bool = False
    ) -> None:
        wait_time: float = random.uniform(min_time, max_time)
        if explicit:
            time.sleep(wait_time)
        else:
            self.driver.implicitly_wait(wait_time)

    def open_connection(self) -> None:
        self.close_connection()
        try:
            self._open_connection()
        except WebDriverException as e:
            LOGGER.error(f"Error during login: {e}")
            self.close_connection()
            raise ScrapingError()

    def _open_connection(self) -> None:
        self.driver = uc.Chrome(
            service=Service(settings.CHROME_DRIVER_PATH), options=self.chrome_options
        )
        self.driver.maximize_window()
        self.driver.get("https://www.amazon.com")
        self._random_wait()
        self._random_wait(min_time=2, max_time=4, explicit=True)

        navigated = False
        times = 0
        while not navigated and times < 3:
            try:
                self._navigate_sign_in()
            except NoSuchElementException:

                LOGGER.warning("Sign-in navigation failed, retrying via direct URL.")
                try:
                    self.driver.get("https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0")
                except WebDriverException:
                    times += 1
                    LOGGER.error("Direct navigation to sign-in page failed.")
                # self.driver.get("https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0")
                self._random_wait()
                self._random_wait(min_time=2, max_time=4, explicit=True)
            try:
                email_element = self.driver.find_element(By.ID, "ap_email")
            except NoSuchElementException:
                continue
            email_element.clear()
            email_element.send_keys(self.email)
            continue_button = self.driver.find_element(By.ID, "continue")
            continue_button.click()
            navigated = True
            self._random_wait(explicit=True)

        
        password_element = self.driver.find_element(By.ID, "ap_password")
        password_element.clear()
        password_element.send_keys(self.password)
        sign_in_button = self.driver.find_element(By.ID, "signInSubmit")
        sign_in_button.click()
        self._random_wait(explicit=True)

        try:
            self.driver.find_element(By.ID, "nav-link-accountList-nav-line-1")
            LOGGER.info("Logged in successfully!")
        except NoSuchElementException:
            raise Exception("Login failed. Could not find logged-in element.")

    def _navigate_sign_in(self) -> None:
        try:
            self.driver.find_element(
                By.CSS_SELECTOR, 'a[data-nav-role="signin"]'
            ).click()
        except NoSuchElementException:
            self.driver.find_element(
                By.ID, "nav-flyout-ya-signin"
            ).click()
        self._random_wait(explicit=True)

    def close_connection(self) -> None:
        if driver := getattr(self, "driver", None):
            driver.quit()

    def fetch_product_data(
        self, product_url: str, max_review_pages: int
    ) -> dict[str, str | float | list[str]]:
        product_url, _ = self._cleanse_url(product_url)
        if not product_url:
            raise ScrapingError("Invalid URL")
        details = self.fetch_product_details(product_url)
        comments = self.fetch_product_comments(product_url, max_review_pages)
        return {
            "product": details.get("product", ""),
            "price": details.get("price", ""),
            "category": details.get("category", ""),
            "rating": details.get("rating", -1.0),
            "url": product_url,
            "comments": comments,
        }

    @staticmethod
    def _cleanse_url(url: str) -> Tuple[str, Optional[str]]:
        match = re.search(r"/dp/([A-Z0-9]{10})", url)
        if match:
            product_id = match.group(1)
            return f"https://www.amazon.pl/dp/{product_id}", product_id
        else:
            return "Invalid URL format", None

    def fetch_product_details(self, product_url: str) -> dict[str, str | float]:
        if not self.driver:
            raise ScrapingError("Connection not opened. Call open_connection() first.")
        details: dict[str, str | float] = {}
        try:
            self.driver.get(product_url)
            self._random_wait()
            product_el = self.driver.find_element(
                By.XPATH, "//span[@id='productTitle']"
            )
            details["product"] = product_el.text.strip()
            price_el = self.driver.find_element(
                By.XPATH, "//div[@id='corePrice_feature_div']"
            )
            details["price"] = price_el.text.strip().replace("\n", ".")
            LOGGER.info("-" + price_el.text.strip() + "-")
            category_el = self.driver.find_element(
                By.XPATH, "//div[@id='wayfinding-breadcrumbs_feature_div']//li[1]"
            )
            details["category"] = category_el.text.strip()
            rating_el = self.driver.find_element(
                By.XPATH,
                "//div[@id='averageCustomerReviews_feature_div']"
                "//span[contains(@class, 'a-size-base') and contains(@class, 'a-color-base')]",
            )
            details["rating"] = float(rating_el.text.strip().replace(",", "."))
        except NoSuchElementException as e:
            LOGGER.error(f"Error fetching details: {e}")
        return details

    def fetch_product_comments(self, product_url: str, max_pages: int) -> list[str]:
        if not self.driver:
            raise ScrapingError("Connection not opened. Call open_connection() first.")
        try:
            _, product_id = self._cleanse_url(product_url)
            self.driver.get(f"https://www.amazon.pl/product-reviews/{product_id}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews")
            self._random_wait()
            # self._navigate_to_reviews()
            
            page_ix = 1
            comments: list[str] = []
            has_next = True
            while has_next and page_ix <= max_pages:
                page_comments = self._extract_single_page_reviews()
                comments.extend(page_comments)
                LOGGER.info(
                    f"{len(page_comments)} comments fetched from page {page_ix}."
                )
                has_next = self._change_review_page()
                page_ix += 1
            LOGGER.info("No more pages of reviews.")
            return comments
        except NoSuchElementException as e:
            LOGGER.error(f"Error fetching comments: {e}")
            return []

    def _navigate_to_reviews(self) -> None:
        try:
            reviews_tab = self.driver.find_element(
                By.XPATH, "//a[contains(text(), 'See more reviews')]"
            )
            reviews_tab.click()
            self._random_wait()
        except NoSuchElementException:
            LOGGER.warning("Reviews tab not found, staying on the current page.")
            
        LOGGER.debug(f"Navigated to reviews page. {self.driver.current_url}")

    def _extract_single_page_reviews(self) -> list[str]:
        self._random_wait(explicit=True)
        comment_elements = self.driver.find_elements(
            By.XPATH, "//span[contains(@class, 'review-text')]"
        )
        return [comm_el.text.strip() for comm_el in comment_elements]

    def _change_review_page(self) -> bool:
        self._random_wait(explicit=True)
        try:
            next_button = self.driver.find_element(
                By.XPATH, "//ul[@class='a-pagination']//li[@class='a-last']/a"
            )
            self._random_wait(explicit=True)
            next_button.click()
        except NoSuchElementException:
            return False
        return True

    def __del__(self) -> None:
        self.close_connection()
