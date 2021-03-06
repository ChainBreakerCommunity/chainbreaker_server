"""
Welcome to ChainBreaker Community Template.
"""
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
                                width: 600px;
                              "></span>
                                            <p style="
                                color: #fff;
                                font-size: 15px;
                                line-height: 24px;
                                margin: 0;
                              ">            
                                                <span style = "color: #fff;">
                                                    <strong>{name}</strong>, we want to welcome you to the Chainbreaker
                                                    Community.
                                                    We are team of academics, data scientists and human trafficking experts
                                                    focused
                                                    on collecting data from several online sexual services to combat human
                                                    trafficking.
                                                </span>
                                                <br><br>
                                                <u style = "color: #fff;">Here are your API credentials:</u>
                                                <br><br>
                                                <span style = "color: #fff;">Email:</span> <strong style="color:#47b2e4;">{email}</strong>
                                                <br>
                                                Password: <strong>{password}</strong>
                                                <br><br>
                                                <span style = "color: #fff">
                                                We highly recommend you to change your password as soon as possible. To make
                                                this, and
                                                to learn more about how you can access our data, press the next button:
                                                </span>
                                            </p>
                                            <a href="{link}" style="
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


"""
ChainBreaker Community Password Recovery.
"""
def recover(name, email, token, link):

    name = name
    email = email
    token = token
    link = link

    html = """<!DOCTYPE html>
        <html lang="es">

        <head>
            <meta content="text/html; charset=utf-8" http-equiv="Content-Type" />
            <title>Chainbreaker | Password recovery</title>
            <meta name="description" content="Reset Password Email." />
        </head>

        <body marginheight="0" topmargin="0" marginwidth="0" style="margin: 0px; background-color: #37517e; color: #fff;"
            leftmargin="0">

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
                                                    ChainBreaker Password Recovery
                                                </h1>
                                                <span style="
                                    display: inline-block;
                                    vertical-align: middle;
                                    margin: 29px 0 26px;
                                    border-bottom: 1px solid #cecece;
                                    width: 600px;
                                "></span>
                                                <p style="
                                    color: #fff;
                                    font-size: 15px;
                                    line-height: 24px;
                                    margin: 0;
                                ">            
                                                    <span style = "color: #fff;">
                                                        Hi <strong>{name}</strong>! 
                                                        Someone recently requested a password change for your ChainBreaker account registered with <strong>{email}.</strong>
                                                        If this was you, you just need to copy the following token:
                                                    </span>
                                                    <br><br>
                                                    <span style = "color: #fff;">Token:</span> <strong style="color:#47b2e4;">{token}</strong>
                                                    <br><br>
                                                    <span style = "color: #fff">
                                                    and follow the tutorial you will find by here:
                                                    </span>
                                                </p>
                                                <a href="{link}" style="
                                    background: #47b2e4;
                                    text-decoration: none !important;
                                    font-weight: 500;
                                    margin-top: 20px;
                                    color: #fff;
                                    text-transform: uppercase;
                                    font-size: 14px;
                                    padding: 10px 24px;
                                    display: inline-block;
                                    text-align: center;
                                    border-radius: 50px;
                                ">Change Password</a>
                                                <p style = "color: #fff;
                                                font-size: 15px;
                                                line-height: 24px;
                                                margin-top: 25px;">
                                                    <span style = "color: #fff;">
                                                        If you dont' want to change your password or didn't request this, just ignore and delete this message.
                                                        
                                                    </span>
                                                    <br><br>
                                                    <span style = "color: #fff;">
                                                        Happy coding!
                                                    </span>
                                                </p>
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
    
    return html