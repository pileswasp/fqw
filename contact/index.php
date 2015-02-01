<?php

$recipients = 
array(
'General' => 'info@fqw.org.uk'
);

if (isset($_POST["send"]))
{
	process_mail_data();
}
else
{
	render_index_page();
}

function process_mail_data()
{
	global $recipients;
	
	$from        = parse_data($_POST['from']);
	
	$recipientID = parse_data($_POST['rcpt_id']);
	$to          = $recipients[$recipientID];
	
	$subject     = parse_data($_POST['subject']);
	$message     = parse_data($_POST['message']);

	$headers="";
	$headers .= "X-Sender:  $from <$from>\n"; //
	$headers .= "From: $from <$from>\n";
	$headers .= "Reply-To: $from <$from>\n";
	$headers .= "Date: ".date("r")."\n";
	$headers .= "Return-Path: $from <$from>\n";
	$headers .= "Delivered-to: $to <$to>\n";
	$headers .= "Bcc: alastair@forestbrook.info <alastair@forestbrook.info>\n";
	$headers .= "MIME-Version: 1.0\n";
	$headers .= "Content-type: text/html;charset=ISO-8859-9\n";
	$headers .= "X-Priority: 1\n";
	$headers .= "Importance: High\n";
	$headers .= "X-MSMail-Priority: High\n";
	$headers .= "X-Mailer: PHP\n";
		
	mail($to, $subject, $message, $headers);

	include_once("success.htm");	
/*	
	echo "from: $from <br/>";
	echo "to: $to <br/>";
	echo "subject: $subject <br/>";
	echo "message: $message <br/>";
*/
}

function render_index_page()
{
	include_once("form.php");
}

function parse_data($value)
{
   # array holding strings to check...
   $suspicious_str = array
   (
       "content-type:"
       ,"charset="
       ,"mime-version:"
       ,"multipart/mixed"
       ,"bcc:"
   );

   // remove added slashes from $value...
   $value = stripslashes($value);

   foreach($suspicious_str as $suspect)
   {
       # checks if $value contains $suspect...
       if(eregi($suspect, strtolower($value)))
       {
           die
           (
               'Script processing cancelled: string
               (`<em>'.$value.'</em>`) contains text portions that
               are potentially harmful to this server. <em>Your input
               has not been sent!</em> Please use your browser\'s
               `back`-button to return to the previous page and try
               rephrasing your input.</p>'
           );
       }
	   else
	   {
	   		return $value;
	   }
   }
}

?>
