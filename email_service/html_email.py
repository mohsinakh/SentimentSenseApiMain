REGISTER_HTML_BODY = """
<html>
    <head>
        <style>
            /* Global Styles */
            body {{
                font-family: 'Arial', sans-serif;
                background-color: #f4f7fc;
                margin: 0;
                padding: 0;
                color: #333;
            }}
            .container {{
                width: 100%;
                max-width: 600px;
                margin: 0 auto;
                padding: 30px;
                background-color: #fff;
                border-radius: 8px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            }}
            h1 {{
                color: #4CAF50;
                font-size: 36px;
                text-align: center;
                margin-top: 0;
            }}
            h2 {{
                color: #4CAF50;
                font-size: 24px;
                text-align: center;
            }}
            p {{
                font-size: 16px;
                line-height: 1.6;
                color: #555;
                text-align: center;
            }}
            
            footer {{
                text-align: center;
                font-size: 12px;
                color: #888;
                margin-top: 30px;
            }}
            .footer-text {{
                color: #777;
                font-size: 13px;
                margin-top: 15px;
            }}
            .footer-link {{
                color: #f5a623;
                text-decoration: none;
            }}
            .header-logo {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .header-logo img {{
                max-width: 150px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-logo">
                <img src="https://i.imgur.com/kSZUI1a.png" alt="Sentiment Sense Logo">
            </div>
            <h1>Welcome to Sentiment Sense, {username}!</h1>
            <h2>We're thrilled to have you with us!</h2>
            <p>Your account has been successfully registered. We are excited to support you in your journey toward understanding sentiments better.</p>
            <p>If you need any assistance, don't hesitate to reach out to our support team. We're here to help at sensesentiment@gmail.com</p>
            <footer>
                <p class="footer-text">Best regards,</p>
                <p class="footer-text"><strong>Sentiment Sense Team</strong></p>
            </footer>
        </div>
    </body>
</html>
"""




LOGIN_HTML_BODY = """
<html>
    <head>
        <style>
            /* Global Styles */
            body {{
                font-family: 'Arial', sans-serif;
                background-color: #f4f7fc;
                margin: 0;
                padding: 0;
                color: #333;
            }}
            .container {{
                width: 100%;
                max-width: 600px;
                margin: 0 auto;
                padding: 30px;
                background-color: #fff;
                border-radius: 8px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            }}
            h1 {{
                color: #4CAF50;
                font-size: 36px;
                text-align: center;
                margin-top: 0;
            }}
            h2 {{
                color: #4CAF50;
                font-size: 24px;
                text-align: center;
            }}
            p {{
                font-size: 16px;
                line-height: 1.6;
                color: #555;
                text-align: center;
            }}
           
            footer {{
                text-align: center;
                font-size: 12px;
                color: #888;
                margin-top: 30px;
            }}
            .footer-text {{
                color: #777;
                font-size: 13px;
                margin-top: 15px;
            }}
            .footer-link {{
                color: #f5a623;
                text-decoration: none;
            }}
            .header-logo {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .header-logo img {{
                max-width: 150px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-logo">
                <img src="https://i.imgur.com/kSZUI1a.png" alt="Sentiment Sense Logo">
            </div>
            <h1>Welcome Back to Sentiment Sense, {username}!</h1>
            <h2>We’re happy to see you again!</h2>
            <p>If you need any assistance, don’t hesitate to reach out to our support team at sensesentiment@gmail.com.</p>
            <footer>
                <p class="footer-text">Best regards,</p>
                <p class="footer-text"><strong>Sentiment Sense Team</strong></p>
            </footer>
        </div>
    </body>
</html>
"""
