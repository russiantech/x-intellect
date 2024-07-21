from flask import render_template

import mailtrap as mt

def s_m():

    # create mail object
    mail = mt.MailFromTemplate(
        sender=mt.Address(email="jameschristo962@gmail.com", name="Mailtrap Test"),
        to=[mt.Address(email="jameschristo962@gmail.com")],
        template_uuid = render_template('email/verify.html', user='chris', token='some-random-token'),
        template_variables={"username": "Chris James . Russian Technologies"},
    )
    # create client and send
    client = mt.MailtrapClient(token="your-api-key")
    client.send(mail)
s_m()