def welcome(name, email, password, link):

    name = name
    email = email
    password = password
    link = link
    
    html = """
    <!DOCTYPE html>
    <html lang="es">

    <head>
        <meta content="text/html; charset=utf-8" http-equiv="Content-Type" />
        <title>Chainbreaker | Welcome</title>
        <meta name="description" content="Reset Password Email." />
    </head>

    <body marginheight="0" topmargin="0" marginwidth="0" style="margin: 0px; background-color: #37517e; color: #fff;"
        leftmargin="0">
        <!--100% body table-->
        <table cellspacing="0" border="0" cellpadding="0" width="100%" bgcolor="#37517e" style="
              font-family: 'Open Sans', sans-serif;
            ">
            <tr>
                <td>
                    <table style="background-color: #37517e; max-width: 670px; margin: 0 auto" width="100%" border="0"
                        align="center" cellpadding="0" cellspacing="0">
                        <tr>
                            <td style="height: 80px">&nbsp;</td>
                        </tr>
                        <tr>
                            <td style="text-align: center">
                                <img width="350px" src="cid:communitylogo" title="logo" alt="logo" />
                            </td>
                        </tr>

                        <tr>
                            <td style="height: 20px">&nbsp;</td>
                        </tr>
                        <tr>
                            <td>
                                <table width="95%" border="0" align="center" cellpadding="0" cellspacing="0" style="
                          max-width: 750px;
                          border-radius: 3px;
                          
                        ">
                                    <tr>
                                        <td style="height: 0px">&nbsp;</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 0 0">
                                            <h1 style="
                                color: white;
                                font-weight: 500;
                                margin: 0;
                                font-size: 32px;
                                font-family: 'Rubik', sans-serif;
                                text-align: center;
                              ">
                                                <img src="cid:chainlogo" width="30px" height="30px" \>
                                                Welcome to the ChainBreaker Community!
                                            </h1>
                                            <span style="
                                display: inline-block;
                                vertical-align: middle;
                                margin: 29px 0 26px;
                                border-bottom: 1px solid #cecece;
                                width: 300px;
                              "></span>
                                            <p style="
                                color: #fff;
                                font-size: 15px;
                                line-height: 24px;
                                margin: 0;
                              ">
                                                <strong>{name}</strong>, we want to welcome you to the Chainbreaker
                                                Community.
                                                We are team of academics, data scientists and human trafficking experts
                                                focused
                                                on collecting data from several online sexual services to combat human
                                                trafficking.

                                                <br><br>
                                                <u>Here are your API credentials:</u>
                                                <br><br>
                                                Email: <strong style="color:#47b2e4;">{email}</strong>
                                                <br>
                                                Password: <strong>{password}</strong>
                                                <br><br>
                                                We highly recommend you to change your password as soon as possible. To make
                                                this, and
                                                to learn more about how you can access our data, press the next button.
                                            </p>
                                            <a href="juanchobanano.com" style="
                                background: #47b2e4;
                                text-decoration: none !important;
                                font-weight: 500;
                                margin-top: 35px;
                                color: #fff;
                                text-transform: uppercase;
                                font-size: 14px;
                                padding: 10px 24px;
                                display: inline-block;
                                text-align: center;
                                border-radius: 50px;
                              ">Learn More</a>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="height: 40px">&nbsp;</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <tr>
                            <td style="height: 20px">&nbsp;</td>
                        </tr>
                        <tr></tr>
                        <tr>
                            <td style="height: 80px">&nbsp;</td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>

    </body>

    </html>
    """.format(**locals())
    #html.format(name = name)
    #html.format(email = email)
    #html.format(password = password)
    #html.format(link = link)

    return html
