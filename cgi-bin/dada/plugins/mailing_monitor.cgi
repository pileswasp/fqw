#!/usr/bin/perl

package mailing_monitor;
use strict; 

$|++; 

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



BEGIN {
   if($] > 5.008){
      require Errno;
      require Config;
   }
}

use DADA::Config qw(!:DEFAULT);
use DADA::App::Guts;
use DADA::Mail::MailOut;
use DADA::MailingList::Schedules; 

use CGI;
my $q = new CGI;
   $q->charset($DADA::Config::HTML_CHARSET);
   $q = decode_cgi_obj($q);



my $Plugin_Config = {}; 
   $Plugin_Config->{Plugin_Name}         = 'Mailing Monitor';
   $Plugin_Config->{Plugin_URL}          = self_url();
   $Plugin_Config->{Allow_Manual_Run}    = 1;
   $Plugin_Config->{Manual_Run_Passcode} = undef; 

use Getopt::Long;

my $verbose = 1; 
my $admin_list = undef; 
my $root_login = undef; 
my $list       = undef; 


GetOptions(
    "verbose!"    => \$verbose
);

&init_vars; 

run()
	unless caller();
	
sub init_vars { 

    # DEV: This NEEDS to be in its own module - perhaps DADA::App::PluginHelper or something?

     while ( my $key = each %$Plugin_Config ) {

        if(exists($DADA::Config::PLUGIN_CONFIGS->{Mailing_Monitor}->{$key})){ 

            if(defined($DADA::Config::PLUGIN_CONFIGS->{Mailing_Monitor}->{$key})){ 

                $Plugin_Config->{$key} = $DADA::Config::PLUGIN_CONFIGS->{Mailing_Monitor}->{$key};

            }
        }
     }
}

sub run {

    if ( !$ENV{GATEWAY_INTERFACE} ) {
	    # this (hopefully) means we're running on the cl...
    
		DADA::Mail::MailOut::monitor_mailout( { -verbose => $verbose } );
		
        for(available_lists()){ 
            my $sched = DADA::MailingList::Schedules->new({-list => $_});
            if($sched->enabled) {
                $sched->run_schedules({ -verbose => $verbose });  
            }
        }
    }
    else {

		
        if (   keys %{ $q->Vars }
            && $q->param('run')
            && xss_filter( $q->param('run') ) == 1
            && $Plugin_Config->{Allow_Manual_Run} == 1 )
        {
			print $q->header(); 
			if(defined($q->param('verbose'))){ 
				$verbose = $q->param('verbose'); 
			}
			
			print '<pre>' 
			    if $verbose == 1; 
			    
			DADA::Mail::MailOut::monitor_mailout( { -verbose => $verbose } );
        			
			foreach(available_lists()){ 	
                my $sched = DADA::MailingList::Schedules->new({-list => $_});
                if($sched->enabled) {
    			    $sched->run_schedules({ -verbose => $verbose });  
                }
            }
            
            print '</pre>'
			    if $verbose == 1; 
            
        }
        else {

            ( $admin_list, $root_login ) = check_list_security(
                -cgi_obj  => $q,
                -Function => 'mailing_monitor'
            );
			$list = $admin_list; 


	      my $flavor = $q->param('flavor') || 'cgi_default';
	        my %Mode = ( 

	        'cgi_default'             => \&cgi_default, 
			'mailing_monitor_results' => \&mailing_monitor_results, 
	        ); 

	        if(exists($Mode{$flavor})) { 
	            $Mode{$flavor}->();  #call the correct subroutine 
	        }else{
	            &cgi_default;
	        }			
        }
    }
}

sub cgi_default { 
	
	my $curl_location = `which curl`;
       $curl_location = strip( make_safer($curl_location) );
    

	require DADA::Template::Widgets; 
	my $scrn = DADA::Template::Widgets::wrap_screen(
						{ 
							-screen => 'plugins/mailing_monitor/default.tmpl', 
							-with           => 'admin', 
							-wrapper_params => { 
								-Root_Login => $root_login,
								-List       => $list,  
							},
							-vars => { 
								Plugin_Name              => $Plugin_Config->{Plugin_Name},
								Plugin_URL               => $Plugin_Config->{Plugin_URL}, 
								Manual_Run_Passcode      => $Plugin_Config->{Manual_Run_Passcode}, 
								Allow_Manual_Run         => $Plugin_Config->{Allow_Manual_Run}, 
								curl_location            => $curl_location, 
								root_login               => $root_login, 
								},
								-list_settings_vars_param => {
				                    -list   => $list,
				                    -dot_it => 1,
				                },
						}
					);
	e_print($scrn);	
}

sub mailing_monitor_results {
	
	if($root_login == 1){ 
		my (
			$r, 
			$total_mailouts,
			$active_mailouts,
			$paused_mailouts,
			$queued_mailouts,
			$inactive_mailouts
		) = DADA::Mail::MailOut::monitor_mailout( { -verbose => 0 } );
		print $q->header(); 
		print '<pre>'; 
		e_print($r); 
		print '</pre>';
		
		foreach(available_lists()){ 			    
            my $sched = DADA::MailingList::Schedules->new({-list => $_});
            if($sched->enabled) {
                print '<pre>'; 
    		   e_print($sched->run_schedules({ -verbose => 0 }));  
    			print '</pre>';
            }
        }
	} 
	else { 
		my (
			$r, 
			$total_mailouts,
			$active_mailouts,
			$paused_mailouts,
			$queued_mailouts,
			$inactive_mailouts
		) = DADA::Mail::MailOut::monitor_mailout( { -verbose => 0, -list => $list } );		
		print $q->header(); 
		
		print '<pre>'; 
		e_print($r); 
		
        my $sched = DADA::MailingList::Schedules->new({-list => $_});
        if($sched->enabled) {
    	    e_print($sched->run_schedules());  
		}
		
        print '</pre>';
		
	}


}

sub self_url { 
	my $self_url = $q->url; 
	if($self_url eq 'http://' . $ENV{HTTP_HOST}){ 
			$self_url = $ENV{SCRIPT_URI};
	}
	return $self_url; 	
}


=pod

=head1 Mailing Monitor Plugin

The Mailing Monitor plugin is used to monitor the health of mass mailings as they go out. Since mass mailings take a potentially a long time to finish, this plugin can help monitor a mass mailing, but more importantly, can help in restarting a mailing that has been, "B<dropped>". 

Mass Mailings can also be monitored in Dada Mail's list control panel under, B<Mass Mailing - Monitor Your Mailings> and done so in a much more  interactive way, so the power of this plugin is when it's run as a cronjob, "behind the scenes". This also allows you to not have your list control panel open in a browser, until your mass mailing is finished. 

Mass Mailings B<drop> because a mass mailing process may need to run longer than is allowed by your hosting environment - especially if you are on a shared hosting environment with limited and shared resources. 

=head2 Schedules

The Mailing Monitor plugin I<also> checks the awaiting schedules for messages scheduled in the B<Send a Message> and B<Send a Webpage> screens. Setting up the cronjob is required to ensure these scheduled mailings go out!

=head1 Installation 

This plugin can be installed during a Dada Mail install/upgrade, using the included installer that comes with Dada Mail. The below installation instructions go through how to install the plugin manually.

If you install the plugin using the Dada Mail installer, you will still have set the cronjob manually, which is covered below.

=head2 Change permissions of "mailing_monitor.cgi" to 755

The, C<mailing_monitor.cgi> plugin will be located in your, I<dada/plugins> diretory. Change the script to, C<755>

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
 #					-Title      => 'Mailing Monitor',
 #					-Title_URL  => $PLUGIN_URL."/mailing_monitor.cgi",
 #					-Function   => 'mailing_monitor',
 #					-Activated  => 0,
 #					},

Uncomment the lines, by taking off the, "#"'s: 

 					{
 					-Title      => 'Mailing Monitor',
 					-Title_URL  => $PLUGIN_URL."/mailing_monitor.cgi",
 					-Function   => 'mailing_monitor',
 					-Activated  => 0,
 					},

Save your C<.dada_config> file.

=head2 Setting the cronjob

Generally, setting the cronjob to have this plugin run automatically just means that you have to have a cronjob access a specific URL. The URL looks something like this:

 http://example.com/cgi-bin/dada/plugins/mailing_monitor.cgi?run=1&verbose=1

Where, I<http://example.com/cgi-bin/dada/plugins/mailing_monitor.cgi> is the URL to your copy of this plugin. 

A B<Best Guess> at what the entire cronjob that's needed (using the, C<curl> command to access the actual URL) to be set manually will appear in this plugin's list control panel under the fieldset labled, B<Manually Run Mailing Monitor> in the textbox labeled, B<curl command example (for a cronjob):>. It'll look something like this: 

 /usr/bin/curl  -s --get --data run=1\;passcode=\;verbose=0  --url http://example.com/cgi-bin/dada/plugins/mailing_monitor.cgi

Where, I<http://example.com/cgi-bin/dada/plugins/mailing_monitor.cgi> is the URL to this plugin. We suggest running this cronjob every 5 to 15 minutes. A complete cronjob, with the time set for, "every 5 minutes" would look like this: 

 */5 * * * * /usr/bin/curl  -s --get --data run=1\;passcode=\;verbose=0  --url http://example.com/cgi-bin/dada/plugins/mailing_monitor.cgi

=head3 Command Line

This plugin can also be called directory on the command line and that can itself be used for the cronjob: 

	cd /home/youraccount/cgi-bin/dada/plugins; /usr/bin/perl ./mailing_monitor.cgi

You may pass the, C<--noverbose> flag to have the script return nothing at all:

	cd /home/youraccount/cgi-bin/dada/plugins; /usr/bin/perl ./mailing_monitor.cgi --noverbose

By default, it will print out the mailing monitor report. 

=head1 BUGS AND LIMITATIONS

Please, let me know if you find any bugs.

=head1 SEE ALSO

The Mailing List Sending FAQ has a whole lot of information about Dada Mail's Mailing Monitor, plugin features and Batch Sending:

L<http://dadamailproject.com/support/documentation/FAQ-mailing_list_sending.pod.html>

=head1 AUTHOR

Justin Simoni 

See: http://dadamailproject.com/contact

=head1 LICENCE AND COPYRIGHT

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
