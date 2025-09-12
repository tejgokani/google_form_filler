from flask import Flask, request, jsonify
from flask_cors import CORS
from faker import Faker
from playwright.sync_api import sync_playwright
import time
import random

app = Flask(__name__)
CORS(app)
fake = Faker()

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    form_url = data.get('formUrl')
    num_responses = int(data.get('numResponses', 1))
    if not form_url or num_responses < 1 or num_responses > 50:
        return jsonify({"message": "Invalid input."}), 400

    try:
        with sync_playwright() as p:
            for i in range(num_responses):
                # Add random delay between 30 and 45 seconds before each response
                delay = random.randint(30, 45)
                print(f"Waiting {delay} seconds before response {i+1}")
                time.sleep(delay)

                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(form_url)

                # Fill text fields
                text_inputs = page.query_selector_all('input[type="text"]')
                for input in text_inputs:
                    input.fill(fake.name())

                # Fill email fields
                email_inputs = page.query_selector_all('input[type="email"]')
                for input in email_inputs:
                    input.fill(fake.email())

                # Click random radio buttons
                radio_groups = page.query_selector_all('div[role="radiogroup"]')
                for group in radio_groups:
                    radios = group.query_selector_all('div[role="radio"]')
                    if radios:
                        fake_radio = fake.random_int(min=0, max=len(radios)-1)
                        radios[fake_radio].click()

                # Click random checkboxes
                checkbox_groups = page.query_selector_all('div[role="list"]')
                for group in checkbox_groups:
                    checkboxes = group.query_selector_all('div[role="checkbox"]')
                    for checkbox in checkboxes:
                        if fake.boolean(chance_of_getting_true=30):
                            checkbox.click()

                # Submit the form
                submit_btn = page.query_selector('span:text("Submit")')
                if submit_btn:
                    submit_btn.click()
                else:
                    submit_btn = page.query_selector('span:text("Send")')
                    if submit_btn:
                        submit_btn.click()
                    else:
                        browser.close()
                        return jsonify({"message": "Submit button not found."}), 500

                page.wait_for_timeout(2000)  # Wait for 2 seconds
                browser.close()
        return jsonify({"message": f"Generated {num_responses} fake responses!"}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Error generating responses.", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)