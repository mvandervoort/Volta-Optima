import os
import logging
import resend
import datetime


class EmailService:
    @staticmethod
    def send_email(to_email: str, subject: str, content: str) -> bool:
        api_key = os.getenv("RESEND_API_KEY")
        if not api_key:
            logging.warning(
                f"RESEND_API_KEY not set. Simulating email send to {to_email}: {subject}"
            )
            return True
        try:
            resend.api_key = api_key
            params = {
                "from": "Energie Insight <info@energie-insight.nl>",
                "to": [to_email],
                "subject": subject,
                "html": content,
            }
            resend.Emails.send(params)
            logging.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logging.exception(f"Failed to send email to {to_email}: {e}")
            return False

    @staticmethod
    def send_results_email(to_email: str, subject: str, data: dict) -> bool:
        """
        Sends a rich HTML email with results dashboard.
        data dict should contain:
        - title: str
        - main_metric_label: str
        - main_metric_value: str
        - main_metric_sub: str
        - stats: list[dict] -> [{"label": "x", "value": "y"}] (should be even number ideally 4)
        - details: list[tuple] -> [("Label", "Value")]
        """
        api_key = os.getenv("RESEND_API_KEY")
        if not api_key:
            logging.warning(
                f"RESEND_API_KEY not set. Simulating rich email send to {to_email}: {subject}"
            )
            return True
        stats_html = ""
        stats = data.get("stats", [])
        for i in range(0, len(stats), 2):
            row_stats = stats[i : i + 2]
            stats_html += "<tr>"
            for stat in row_stats:
                stats_html += f"""\n                <td width="50%" style="padding: 8px;">\n                    <div style="background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #e5e7eb; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">\n                        <div style="color: #6b7280; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">{stat["label"]}</div>\n                        <div style="color: #111827; font-size: 18px; font-weight: 700;">{stat["value"]}</div>\n                    </div>\n                </td>\n                """
            if len(row_stats) == 1:
                stats_html += '<td width="50%" style="padding: 8px;"></td>'
            stats_html += "</tr>"
        details_html = ""
        for label, value in data.get("details", []):
            details_html += f'\n            <tr>\n                <td style="padding: 12px 8px; border-bottom: 1px solid #f3f4f6; color: #4b5563;">{label}</td>\n                <td style="padding: 12px 8px; border-bottom: 1px solid #f3f4f6; color: #111827; font-weight: 600; text-align: right;">{value}</td>\n            </tr>\n            '
        current_year = datetime.datetime.now().year
        html_content = f"""\n        <!DOCTYPE html>\n        <html>\n        <head>\n            <meta charset="utf-8">\n            <meta name="viewport" content="width=device-width, initial-scale=1.0">\n        </head>\n        <body style="margin: 0; padding: 0; background-color: #ffffff; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">\n            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">\n                <!-- Header -->\n                <div style="padding: 30px 20px 20px 20px; text-align: center; border-bottom: 1px solid #f0f0f0;">\n                    <div style="display: inline-flex; align-items: center; justify-content: center;">\n                        <img src="https://energie-insight.nl/full_trimmed_transparent_customcolor.png" alt="Energie Insight Logo" style="height: 40px; width: auto; margin-right: 12px;" />\n                        <span style="color: #059669; font-size: 24px; font-weight: 800; letter-spacing: -0.5px;">Energie Insight</span>\n                    </div>\n                    <div style="color: #6b7280; font-size: 14px; margin-top: 5px;">Energy Transition Advisory Platform</div>\n                </div>\n\n                <!-- Main Content -->\n                <div style="padding: 30px 20px;">\n                    <h1 style="color: #1f2937; margin: 0 0 25px 0; font-size: 22px; text-align: center;">{data.get("title", "Your Results")}</h1>\n                    \n                    <!-- Visual Dashboard -->\n                    <div style="background-color: #f9fafb; padding: 20px; border-radius: 16px; border: 1px solid #f3f4f6; margin-bottom: 30px;">\n                        \n                        <!-- Main Metric Card -->\n                        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 12px; padding: 30px 20px; text-align: center; color: white; margin-bottom: 20px; box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.2);">\n                            <div style="font-size: 13px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9; margin-bottom: 8px;">{data.get("main_metric_label", "")}</div>\n                            <div style="font-size: 42px; font-weight: 800; line-height: 1; margin-bottom: 8px; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">{data.get("main_metric_value", "")}</div>\n                            <div style="font-size: 14px; opacity: 0.9; font-weight: 500;">{data.get("main_metric_sub", "")}</div>\n                        </div>\n\n                        <!-- Secondary Stats Grid -->\n                        <table width="100%" cellpadding="0" cellspacing="0" border="0">\n                            {stats_html}\n                        </table>\n                    </div>\n\n                    <!-- Detailed Breakdown -->\n                    <div style="margin-bottom: 30px;">\n                        <h3 style="color: #111827; font-size: 16px; border-bottom: 2px solid #059669; padding-bottom: 10px; display: inline-block; margin-top: 0;">Detailed Breakdown</h3>\n                        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top: 10px;">\n                            {details_html}\n                        </table>\n                    </div>\n\n                    <!-- Call to Action -->\n                    <div style="text-align: center; margin-top: 40px; padding: 20px; background-color: #ecfdf5; border-radius: 8px;">\n                        <p style="color: #065f46; font-size: 14px; margin: 0 0 10px 0;">Need more detailed advice?</p>\n                        <a href="https://energie-insight.nl/contact-about" style="display: inline-block; background-color: #059669; color: white; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: 600; font-size: 14px;">Contact Our Experts</a>\n                    </div>\n                </div>\n\n                <!-- Footer -->\n                <div style="text-align: center; color: #9ca3af; font-size: 12px; padding: 30px 20px; background-color: #f9fafb; border-top: 1px solid #f3f4f6;">\n                    <p style="margin: 0 0 10px 0;">Generated on {datetime.date.today().strftime("%B %d, %Y")}</p>\n                    <p style="margin: 0;">&copy; {current_year} Energie Insight. All rights reserved.</p>\n                </div>\n            </div>\n        </body>\n        </html>\n        """
        try:
            resend.api_key = api_key
            params = {
                "from": "Energie Insight <info@energie-insight.nl>",
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            }
            resend.Emails.send(params)
            logging.info(f"Rich email sent successfully to {to_email}")
            return True
        except Exception as e:
            logging.exception(f"Failed to send rich email to {to_email}: {e}")
            return False

    @staticmethod
    def send_feedback_email(
        to_email: str,
        feedback_type: str,
        description: str,
        screenshot_base64: str,
        page_url: str,
        user_email: str,
    ) -> bool:
        api_key = os.getenv("RESEND_API_KEY")
        if not api_key:
            logging.warning(
                f"RESEND_API_KEY not set. Simulating feedback email from {user_email}"
            )
            return True
        type_colors = {
            "Bug Report": "#ef4444",
            "Suggestion": "#10b981",
            "Question": "#3b82f6",
            "Other": "#6b7280",
        }
        badge_color = type_colors.get(feedback_type, "#10b981")
        attachments = []
        screenshot_html = ""
        if screenshot_base64 and "," in screenshot_base64:
            try:
                content_type_part, base64_data = screenshot_base64.split(",", 1)
                content_type = content_type_part.split(":", 1)[1].split(";", 1)[0]
                attachments.append(
                    {
                        "content": base64_data,
                        "filename": "screenshot.jpg",
                        "content_type": content_type,
                        "content_id": "feedback_screenshot",
                    }
                )
                screenshot_html = f'\n                <div style="margin-top: 30px; border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden;">\n                    <div style="background: #f9fafb; padding: 10px 15px; border-bottom: 1px solid #e5e7eb; font-size: 12px; color: #6b7280; font-weight: 600;">SCREENSHOT BIJGEVOEGD</div>\n                    <div style="padding: 10px; background: white;">\n                        <img src="cid:feedback_screenshot" style="width: 100%; max-width: 100%; height: auto; display: block; border-radius: 4px;" />\n                    </div>\n                </div>\n                '
            except Exception as e:
                logging.exception(f"Error processing screenshot for email: {e}")
                screenshot_html = "<p style='color: #ef4444; font-size: 12px;'>Fout bij verwerken van screenshot bijlage.</p>"
        html_content = f"""\n        <!DOCTYPE html>\n        <html>\n        <body style="font-family: sans-serif; line-height: 1.6; color: #374151; padding: 20px;">\n            <div style="max-width: 600px; margin: 0 auto;">\n                <div style="border-bottom: 2px solid #f3f4f6; padding-bottom: 20px; margin-bottom: 25px;">\n                    <h2 style="color: #111827; margin: 0 0 10px 0;">Nieuwe Website Feedback</h2>\n                    <span style="background-color: {badge_color}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; text-transform: uppercase;">{feedback_type}</span>\n                </div>\n                \n                <div style="background: #f9fafb; padding: 20px; border-radius: 12px; border: 1px solid #f3f4f6;">\n                    <p style="margin-top: 0;"><strong>Beschrijving:</strong></p>\n                    <div style="white-space: pre-wrap; font-size: 15px;">{description}</div>\n                </div>\n\n                <table style="width: 100%; margin-top: 25px; border-collapse: collapse; font-size: 14px;">\n                    <tr>\n                        <td style="padding: 8px 0; color: #6b7280; width: 120px;">Pagina:</td>\n                        <td style="padding: 8px 0; font-weight: 600;">{page_url}</td>\n                    </tr>\n                    <tr>\n                        <td style="padding: 8px 0; color: #6b7280;">Gebruiker:</td>\n                        <td style="padding: 8px 0; font-weight: 600;">{user_email}</td>\n                    </tr>\n                    <tr>\n                        <td style="padding: 8px 0; color: #6b7280;">Datum:</td>\n                        <td style="padding: 8px 0; font-weight: 600;">{datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}</td>\n                    </tr>\n                </table>\n\n                {screenshot_html}\n\n                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #f3f4f6; text-align: center; color: #9ca3af; font-size: 12px;">\n                    Verzonden door Energie Insight Feedback Widget\n                </div>\n            </div>\n        </body>\n        </html>\n        """
        try:
            resend.api_key = api_key
            params = {
                "from": "EI Feedback <info@energie-insight.nl>",
                "to": [to_email],
                "subject": f"[{feedback_type}] Website Feedback - {page_url}",
                "html": html_content,
            }
            if attachments:
                params["attachments"] = attachments
            resend.Emails.send(params)
            return True
        except Exception as e:
            logging.exception(f"Failed to send feedback email: {e}")
            return False