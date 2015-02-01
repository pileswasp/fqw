<?php	
	function output_recipient_options()
	{
		global $recipients;
		foreach($recipients as $name => $email)
		{
			if ($id++ == 0)
			{
				echo '<option value="'.$name.'" selected="selected">'.$name.'</option>';
			}
			else
			{
				echo '<option value="'.$name.'">'.$name.'</option>';
			}		
		}
	}
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Friends of Queen's Wood :: Welcome!</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
<meta name="keywords" content="Queen's Wood, Highgate Wood, Haringey, London, capital
 ring"/>
<meta name="keywords" content="woods, woodland,
 trees, open spaces, parks, conservation"/>
<meta name="keywords" content="Hornbeam, Hawfinch" />
<link rel="stylesheet" type="text/css" href="/styles/main.css"/>
</head>
<body> 
<div id="page"> 
    <div id="masthead"></div> 
    <div id="content"> 
        <div id="navigation"> 
            <div class="section" id="toc" > 
                <div class="header"> 
                    <h1>Contents</h1> 
                </div> 
                <ul> 
                    <li><a href="/">Welcome ...</a></li> 
                    <li><a href="/events/">Coming events</a></li> 
		    <li><a href="/woodchat/">Woodchat</a></li>
                    <li><a href="/aims/">Future aims</a></li> 
                    <li><a href="/history/">History of Queen's Wood</a></li> 
                    <li><a href="/flora_and_fauna/">Flora and fauna</a></li>
		    <li><a href="/coppicing/">Coppicing in the wood</a></li>
                    <li><a href="/garden/">Organic garden &amp; café</a></li> 
                    <li><a href="/photos/">Photo gallery</a></li> 
                    <li><a href="/committee/">Our committee</a></li> 
                    <li><a href="/links/">Useful links</a></li> 
                    <li><span>Contact us</span></li> 
                </ul> 
            </div> 
            <div id="resources" class="section"> 
                <div class="header"> 
                    <h1>Resources</h1> 
                </div>                
				<ul> 
                    <li><a href="/docs/Newsletter.pdf">Current newsletter</a></li> 
                    <li><a href="/docs/report.pdf?ver=2013">Chairman's report</a></li> 
                    <li><a href="/docs/membership.pdf">Membership form</a></li> 
                    <li><a href="/images/maps/QWFinal_Layout_lowres-3.gif">Map of Queen's Wood</a></li>
		    <li><a href="/docs/Breeding Bird Survey for Queen's Wood 2008.pdf">Breeding Bird Survey 2008</a></li>
		    <li><a href="/docs/Owl Survey for Queen's Wood 2007.pdf">Owl Survey 2007</a></li>
		    <li><a href="/docs/Frog pool.pdf">Frog Pool proposal</a></li>
		    <li><a href="/docs/Invertebrate Survey 2011 report.doc">Invertebrate Survey 2011</a></li>
		    <li><a href="/docs/Invertebrate Survey 2011 lists of species.doc">Invertebrate Survey species lists</a></li>

                </ul> 
            </div> 
        </div> 
        <div id="main"> 
            <div id="article" class="section"> 
                <div class="header"> 
                    <h1>Contact us</h1> 
                </div> 
                <div class="text"> 
					<p>Please use the form below to send us a message:</p>
					<br/>
					<div id="mail_form">
					<form action="" enctype="application/x-www-form-urlencoded" method="post" title="mail form">
					<table class="inline_table">
					<tr><td><p class="bold">From (email address):</p></td><td><input type="text" name="from" maxlength="256" size="64"></input></td></tr>
					<tr><td><p class="bold">To:</p></td><td><select name="rcpt_id"><?php output_recipient_options(); ?></select></td></tr>
					<tr><td><p class="bold">Subject:</p></td><td><input type="text" name="subject" maxlength="256" size="64"></input></td></tr>
					<tr><td colspan="2"><br/><p><textarea name="message" rows="8" cols="58"></textarea></p></td></tr>
					<tr><td colspan="2"><p><input type="submit" name="send" value="Send Message"></input></p></td></tr>
					</table>
					</form>
					</div>					
				</div> 
            </div> 
        </div> 
    </div>
	<div id="footer">&copy; fqw 2005 | <a href="http://validator.w3.org/check?uri=referer">xhtml</a> | <a href="http://jigsaw.w3.org/css-validator/validator?uri=http%3A%2F%2Fwww.fqw.org.uk%2Fstyles%2Fmain.css&warning=no&profile=css2">css</a>
</div> 
</div> 

</body>
</html>
