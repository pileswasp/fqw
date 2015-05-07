#!/usr/bin/perl
use strict; 

use FindBin;
use lib "$FindBin::Bin/../";
use lib "$FindBin::Bin/../DADA/perllib";
BEGIN { 
	my $b__dir = ( getpwuid($>) )[7].'/perl';
    push @INC,$b__dir.'5/lib/perl5',$b__dir.'5/lib/perl5/x86_64-linux-thread-multi',$b__dir.'lib',map { $b__dir . $_ } @INC;
}

use CGI::Carp qw(fatalsToBrowser set_message);
    BEGIN {
       sub handle_errors {
		my $TIME = scalar(localtime());
        print qq{
		<html>
		<head></head>
		<body>
		<div style="padding:5px;border:3px dotted #ccc; font-family:helvetica; font-size:.7em; line-height:150%; width:600px;margin-left:auto;margin-right:auto;margin-top:100px;">
		<img alt="Dada Mail" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJYAAAC
		WCAMAAAAL34HQAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAAxQTFRFCAgIXV
		1dp6en/f39XG2aJgAAAqpJREFUeNrs3OGO4yAMBOB0+/7vvFWRLMtjjAkEqDT5dddyy1fJNwSH7vU+8
		rrIWsX6+15k/TTr+l6v12s6jqxlrA/oUtdEHFm7WKXOyPotltZ8CmuijKw1LCks7ZiVFGQtYOlocF8n
		63CWZAGWkbxF1uGsYGEW1mBGkPUoyw13fJesY1k6GuKyWxoQZM0I9ya6t9TIeojV3KPWsqNwydrOisP
		duKWSPn+4l/tkTWc1w702Rm+QyNrIaoZ7HB/3GkxkzWVl2rW1lgRZJ7Ay4a6Lzx1G1kZWJtx18XVth8
		oqrh+R6iffZE1hJcM9sxgj64KrTCf1R9YUVibcm9Ggb5qFheMxhsgaZwVLr2tyh5UBWiYv4mcoY8iax
		cr8nzcmd5ihaGLtB5I1yJK1sxkNGZOulQyrfAyyBll4jieYT48pk5lTlfqD6c0PWY+ycNZaN0EPKOML
		SGK9ycIP3MgtsjpTHnG1w3baoUsK+w7mmNeEOwiyOnc+meDQ9WFYZhssAl2R2Xt5snpYZv02/YKgIkv
		cByxcKrDmyJrIynTtyw/VT8Jilukc+TfcZC1hmfN2+q8Bq3yAaU9fyRpjmcR3tzqi1JVH1mks3KCaZq
		IkSNfXSMhaw9IpgEeZcQdF1oGs2taldivcdQaIrC2sN3yfGXdK+W/JkrWLFfeG+pYQss5gjVxk3WaZj
		oNOcPf15ADsYtQmImucVfvVAKYb2OwbmplqveDgOTdZt1lB8z1o6WLX3sxE1kaWbqPXWLX2vXvjRdbT
		LHcCt27co1c4mKz1rGAC8wr+Agi3EN1FAlmNpZqsuyw32bEa8EGXW4LN2sKnLGTdY8Xh7tbN1bqSrOh
		ZNVlpFpYOHkw3LPNPZBuD05C1niXvmeM4Zkwt94NmrjnpRdZcFvtbv8z6F2AA/5G8jEIpBJoAAAAASU
		VORK5CYII=" style="float:left;padding:10px"/></p>
		<h1>Yikes! App/Server Problem!</h1>
		<p>We apologize, but the server encountered a problem when attempting to complete its task.</p> 
		<p>More information about this error may be available in the <em>program's own error log</em>.</p> 
		<p><a href="mailto:$ENV{SERVER_ADMIN}">Contact the Server Admin</a></p>
		<p>Time of error: <strong>$TIME</strong></p> 	
		</div>
		</body> 
		</html> 
		};
	}
	set_message(\&handle_errors);
}


# use some of those Modules
use DADA::Config 7.0.0;
use DADA::Template::HTML; 
use DADA::Template::Widgets; 
use DADA::App::Guts;
use DADA::MailingList::Settings; 


my $Start_Marker = '# Start Root Password'; 
my $End_Marker   = '# End Root Password'; 





# we need this for cookies things
use CGI; 
my $q = new CGI; 
   $q->charset($DADA::Config::HTML_CHARSET);
   $q = decode_cgi_obj($q);

my $URL = self_url(); 

# This will take care of all out security woes
my ($admin_list, $root_login) = check_list_security(-cgi_obj  => $q, 
                                                    -Function => 'change_root_password');
my $list = $admin_list; 

# get the list information
my $ls = DADA::MailingList::Settings->new({-list => $list}); 
my $li = $ls->get; 
                             
	               
if(!$q->param('process')){ 

	my $scrn = DADA::Template::Widgets::wrap_screen(
						{
				            -screen         => 'plugins/change_root_password/default.tmpl',
							-with           => 'admin', 
							-wrapper_params => { 
								-Root_Login => $root_login,
								-List       => $list,  
							},
							-vars => { 
								 ROOT_PASS_IS_ENCRYPTED => $DADA::Config::ROOT_PASS_IS_ENCRYPTED, 
								
							        new_pass_no_match => ($q->param('new_pass_no_match') == 1) ? 1 : 0, 
							        old_root_pass_incorrect => ($q->param('old_root_pass_incorrect') == 1) ? 1 : 0, 
								
							},
						}
					);
    e_print($scrn); 

}else{ 


    
    if(!$q->param('old_password')){ 
        
        print $q->redirect(-url => $URL . '?old_root_pass_incorrect=1'); 
        return; 
        
    }else{ 
    
    
    
       if($DADA::Config::ROOT_PASS_IS_ENCRYPTED == 1){ 	
            require DADA::Security::Password; 
            my $root_password_check = DADA::Security::Password::check_password($DADA::Config::PROGRAM_ROOT_PASSWORD, $q->param('old_password')); 
            if($root_password_check == 1){
                # we are good.
            } else { 
                print $q->redirect(-url => $URL . '?old_root_pass_incorrect=1'); 
                return; 
            }
        }else{ 
            
            if($DADA::Config::PROGRAM_ROOT_PASSWORD eq $q->param('old_password')){ 
                # we are good.
            } else { 
            
                print $q->redirect(-url => $URL . '?old_root_pass_incorrect=1'); 
                return; 
                
            }
        }
                               
    }
    
    if($q->param('new_password') ne $q->param('again_new_password')){ 
    
        print $q->redirect(-url => $URL . '?new_pass_no_match=1'); 
        return; 
    }
    
    
    # Well, if everything works out, we're cool. 
    my $file = $DADA::Config::CONFIG_FILE; 
    open my $CONFIG, '<:encoding(' . $DADA::Config::HTML_CHARSET . ')', $file
    or die "Cannot read config file at: '" . $file
    . "' because: "
    . $!;
    my $config =  do { local $/; <$CONFIG> };
    close($CONFIG) or die $!; 
    
    my $qmsp = quotemeta($Start_Marker); 
    my $qmep = quotemeta($End_Marker); 
    
    require DADA::Security::Password; 
    
    my $pw = $q->param('new_password');
        
    my $root_pass = DADA::Security::Password::encrypt_passwd($pw);
    
    my $new_pass = "\n" . '$ROOT_PASS_IS_ENCRYPTED = 1; ' . "\n \n" . '$PROGRAM_ROOT_PASSWORD  = \'' . $root_pass . "'; \n"; 
    
    $config =~ s/($qmsp)(.*?)($qmep)/$Start_Marker\n$new_pass\n$End_Marker/sm; 
    
   # die $root_pass; 
    
    open my $CONFIGW, '>:encoding(' . $DADA::Config::HTML_CHARSET . ')' , $file
    or die "Cannot write config file at: '" . $file
    . "' because: "
    . $!;
    print $CONFIGW $config or die $!; 
    close($CONFIGW) or die $!; 
    
    print $q->redirect(-uri => $DADA::Config::S_PROGRAM_URL . '?f=logout&login_url='. $DADA::Config::S_PROGRAM_URL . '/' . $DADA::Config::ADMIN_FLAVOR_NAME); 
    exit;

}




sub self_url { 
	my $self_url = $q->url; 
	if($self_url eq 'http://' . $ENV{HTTP_HOST}){ 
			$self_url = $ENV{SCRIPT_URI};
	}
	return $self_url; 	
}



=pod

=head1 NAME

change_root_password.cgi - B<EXPERIMENTAL> Dada Mail plugin to allow you to easily change the Dada Mail Root Password. 

=head1 DEPRECATED

The plugin, B<change_root_password.cgi> has now landed itself on the DEPRECATED list of plugins that comes with Dada Mail. Since the new, B<Global Config> plugin allows you to easily change the Dada Mail Root Password, amongst many other things, this plugin can now be retired. 

=head1 VERSION

Refer to the version of Dada Mail you're using - NEVER use a version of this proggy with an earlier or later version of Dada Mail. 

=head1 USAGE

This script is a Dada Mail plugin. Once configured, you should be able to log into your list and access this plugin under the, B<Plugins> menu. 

B<Note>, that by default, this plugin can only be accessed if you log into a list using the B<Dada Mail Root Password>.

=head1 DESCRIPTION

=head1 Installation

This plugin can be installed during a Dada Mail install/upgrade, using the included installer that comes with Dada Mail. The below installation instructions go through how to install the plugin manually. 

=head1 CONFIGURATION AND ENVIRONMENT

=head2 Please Read Before Installing

Before getting into configuration of the plugin, do note that this is an B<experimental> plugin, so it is slightly awkward in a few places. Make sure you have the correct environment set up to use it. 

Here's what you'll need to have: 

=over

=item * Outside Config File (.dada_config)

Currently, this plugin only works when you do a contemporary installation of Dada Mail. Refer to the installation instructions that come with Dada Mail to understand the difference between a contemporary installation and a basic installation. If you use the installer that comes with Dada Mail, you will have a B<Contemporary Installation> of Dada Mail. 


=item * Specific Markers in the Outside Config File

This plugin very simply looks for a, B<Start Marker> and an, B<End Marker> and between these two markers should be the following variables: 

=over

=item *  $ROOT_PASS_IS_ENCRYPTED

(can either be set to 1 or 0)

=item *  $PROGRAM_ROOT_PASSWORD

=back

By default, the two markers are set in this very plugin under the variables, B<$Start_Marker> and B<$End_Marker>. So, in your C<.dada_config> file, you should have something that looks similar to this: 

 # Start Root Password
 
 $ROOT_PASS_IS_ENCRYPTED = 1; 
  
 $PROGRAM_ROOT_PASSWORD  = 'S5R8IqNB7C3cQ';  
 
 # End Root Password

If your C<.dada_config> file does not have a part of its content that looks like this, this plugin will not work. 

=back

=head2 Change permissions of "change_root_password.cgi" to 755

The, C<change_root_password.cgi> plugin will be located in your, I<dada/plugins> diretory. Change the script to, C<755>

=head2 Configure your .dada_config file

Now, edit your C<.dada_config> file, so that it shows the plugin in the left-hand menu, under the, B<Plugins> heading: 

First, see if the following lines are present in your C<.dada_config> file: 

 # start cut for list control panel menu
 =cut

 =cut
 # end cut for list control panel menu

If they are, remove them. 

Then, find these lines: 

 #					{
 #					-Title      => 'Change the Program Root Password',
 #					-Title_URL  => $PLUGIN_URL."/change_root_password.cgi",
 #					-Function   => 'change_root_password',
 #					-Activated  => 0,
 #					},

Uncomment the lines, by taking off the, "#"'s: 

 					{
 					-Title      => 'Change the Program Root Password',
 					-Title_URL  => $PLUGIN_URL."/change_root_password.cgi",
 					-Function   => 'change_root_password',
 					-Activated  => 0,
 					},

Save your C<.dada_config> file.


=head1 DEPENDENCIES

You'll most likely want to use the version of this plugin with the version of Dada Mail is comes with. 

=head1 INCOMPATIBILITIES

=head1 BUGS AND LIMITATIONS

Please, let me know if you find any bugs.

=head1 AUTHOR

Justin Simoni 

See: http://dadamailproject.com/contact

=head1 LICENSE AND COPYRIGHT

Copyright (c) 1999 - 2014 Justin Simoni All rights reserved. 

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, 
Boston, MA  02111-1307, USA.

=cut

