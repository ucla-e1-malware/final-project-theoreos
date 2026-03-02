from ..commands import Command
# import the Python standard library modules for sending email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Phish(Command):
    """
    Send a phishing email to a specific address.
    Usage: phish <EMAIL_ADDRESS>
    Example: phish test@example.com
    """

    def do_command(self, lines: str, *args):
        recipient = lines.strip()

        if not recipient:
            print("Error: No email address provided.")
            print("Usage: phish <EMAIL_ADDRESS>")
            return
            
        # Set variables for credentials to our email server
        #
        # Gmail is a bit annoying to set up for sending email with Python,
        # so instead we'll be using a server set up just for this class :D
        smtp_server, port = ("e1-mail.acmcyber.com", 32525)
        # Our email server is set up to allow any username/password combo
        # Note that you should never include passwords in your source code in a real app!
        username, password = ("expert-hacker", "hunter2")

        # Start building a a new "multipart" MIME file
        # (MIME, or "Multipurpose Internet Mail Extensions", is the format that modern email uses)
        message = MIMEMultipart("alternative")
        message["From"] = "oreos@e1-mail.acmcyber.com" # put your team name here! (make sure that it's a valid email though)
        message["To"] = "e1-instructors@e1-mail.acmcyber.com" 
        message["Subject"] = "CS 32 Project 1 Score" # add a subject line here!

        # add your email HTML here!
        html = """\
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
        <head>
            <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Invitation from Paul Eggert</title>
            <style>
                @media (max-width: 512px) { .mercado-container { width: 100% !important; } }
                @media (max-width: 480px) { .inline-button, .inline-button table { display: none !important; } .full-width-button, .full-width-button table { display: table !important; } }
                body { font-family: -apple-system, system-ui, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', 'Fira Sans', Ubuntu, Oxygen, 'Oxygen Sans', Cantarell, 'Droid Sans', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Lucida Grande', Helvetica, Arial, sans-serif; }
            </style>
        </head>
        <body dir="ltr" class="font-sans bg-color-background-canvas w-full m-0 p-0 pt-1" style="-webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; margin: 0px; width: 100%; background-color: #f3f2f0; padding: 0px; padding-top: 8px; font-family: -apple-system, system-ui, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Helvetica, Arial, sans-serif;">
            
            <!-- Preheader -->
            <div style="display: none; max-height: 0px; overflow: hidden;">
                Paul Eggert wants to connect with you. "I noticed your use of tabs instead of spaces..."
            </div>

            <!-- Main Table -->
            <table role="presentation" valign="top" border="0" cellspacing="0" cellpadding="0" width="512" align="center" class="mercado-container" style="margin: 0 auto; width: 512px; max-width: 512px;">
                <tbody>
                    <tr>
                        <td>
                            <table role="presentation" valign="top" border="0" cellspacing="0" cellpadding="0" width="100%" style="background-color: #ffffff;">
                                <tbody>
                                    <!-- LinkedIn Header -->
                                    <tr>
                                        <td class="text-center p-3" style="padding: 24px; text-align: center;">
                                            <img alt="LinkedIn" src="https://static.licdn.com/aero-v1/sc/h/2fp5x7ci191mxbdy1eynscn59" style="height: 37px; width: 101px;">
                                        </td>
                                    </tr>

                                    <!-- Content -->
                                    <tr>
                                        <td style="padding: 0 24px 24px 24px;">
                                            <table role="presentation" border="0" cellspacing="0" cellpadding="0" width="100%">
                                                <tbody>
                                                    <!-- Title -->
                                                    <tr>
                                                        <td style="text-align: center; font-size: 24px; color: #282828; padding-bottom: 24px;">
                                                            You have an invitation from <strong>Paul Eggert</strong>
                                                        </td>
                                                    </tr>

                                                    <!-- Profile Card -->
                                                    <tr>
                                                        <td align="center">
                                                            <!-- Profile Pic -->
                                                            <img src="https://samueli.ucla.edu/wp-content/uploads/samueli/Paul_Eggert.jpg" alt="Paul Eggert" style="display: block; height: 120px; width: 120px; border-radius: 50%; border: 4px solid #ffffff; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-bottom: 16px; object-fit: cover;">
                                                            
                                                            <!-- Name & Headline -->
                                                            <h3 style="margin: 0; font-size: 20px; color: #282828; font-weight: 600;">Paul Eggert</h3>
                                                            <p style="margin: 4px 0 16px 0; font-size: 16px; color: #666666; line-height: 1.5;">
                                                                Senior Lecturer at UCLA Computer Science<br>
                                                                Maintainer of the Time Zone Database | GNU Coreutils
                                                            </p>

                                                            <!-- Connection Message (The "Eggert" touch) -->
                                                            <div style="background-color: #f3f2f0; padding: 16px; border-radius: 8px; text-align: left; margin-bottom: 24px;">
                                                                <p style="margin: 0; font-size: 14px; color: #444; font-style: italic;">
                                                                    "I reviewed your Project 3 submission on GitHub. Your handling of POSIX signals is race-prone and your indentation style violates GNU standards. Accept this connection so I can send you the correct documentation."
                                                                </p>
                                                            </div>
                                                        </td>
                                                    </tr>

                                                    <!-- Buttons -->
                                                    <tr>
                                                        <td align="center">
                                                            <table role="presentation" border="0" cellspacing="0" cellpadding="0">
                                                                <tr>
                                                                    <!-- Accept Button -->
                                                                    <td style="padding-right: 12px;">
                                                                        <a href="www.linkedin.com/in/trevortankengkit" style="background-color: #0a66c2; color: #ffffff; display: inline-block; padding: 12px 24px; border-radius: 24px; text-decoration: none; font-weight: 600; font-size: 16px; border: 1px solid #0a66c2;">
                                                                            Accept
                                                                        </a>
                                                                    </td>
                                                                    <!-- Ignore Button -->
                                                                    <td>
                                                                        <a href="#" style="background-color: transparent; color: #666666; display: inline-block; padding: 12px 24px; border-radius: 24px; text-decoration: none; font-weight: 600; font-size: 16px; border: 1px solid #666666;">
                                                                            Ignore
                                                                        </a>
                                                                    </td>
                                                                </tr>
                                                            </table>
                                                        </td>
                                                    </tr>

                                                </tbody>
                                            </table>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f3f2f0; padding: 24px; text-align: center;">
                            <p style="margin: 0 0 10px 0; font-size: 12px; color: #666666;">
                                This email was intended for Trevor Tan (UCLA Computer Science 2025).
                            </p>
                            <p style="margin: 0; font-size: 12px; color: #666666;">
                                &copy; 2026 LinkedIn Corporation, Sunnyvale, CA.
                            </p>
                        </td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """

        # Make an HTML email attachment from that string, and attach it to our message
        message.attach(MIMEText(html, "html"))
        try:
            # Open up an SMTP (Simple Mail Transfer Protocol) to our server, and send your email!
            with smtplib.SMTP(smtp_server, port) as server:
                server.login(username, password)
                server.sendmail(message["From"], message["To"], message.as_string())
            print("Email sent")
        except Exception as e:
            print(f"Failed to send email: {e}")

command = Phish