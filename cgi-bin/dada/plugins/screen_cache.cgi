#!/usr/bin/perl

package screen_cache;

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



use DADA::Config 7.0.0;
# we need this for cookies things
use CGI;
my $q = new CGI;
$q->charset($DADA::Config::HTML_CHARSET);
$q = decode_cgi_obj($q);

my $verbose = 0;

my $Plugin_Config = {};

$Plugin_Config->{Plugin_URL}         = self_url();

# Set to, 1, to enable
$Plugin_Config->{Allow_Manual_Run}   = 1;

# Pick some sort of passcode, for a semblance of security 
$Plugin_Config->{Manual_Run_Passcode} = '';




use     DADA::App::ScreenCache;
my $c = DADA::App::ScreenCache->new;

# use some of those Modules
use DADA::Template::HTML;
use DADA::App::Guts;
use DADA::MailingList::Settings;




run()
  unless caller();

sub run {
    main();
}

sub main {
	my $process = $q->param('process'); 
	
    if ($process) {
        if ( $process eq 'view' ) {
            $c->show( $q->param('filename'),{-check_for_header => 1} );
        }
        elsif ( $process eq 'remove' ) {
            $c->remove( $q->param('filename') );
            view();
        }
        elsif ( $process eq 'flush' ) {
            $c->flush;
            view();
        }
    }
    else {
	    if (   keys %{ $q->Vars }
	        && $q->param('run')
	        && xss_filter( $q->param('run') ) == 1
	        && $Plugin_Config->{Allow_Manual_Run} == 1 )
	    {
	        cgi_manual_start();
	    }
		else { 
        	view();
		}	
    }
}

sub view {

    my ( $admin_list, $root_login ) = check_list_security(
        -cgi_obj  => $q,
        -Function => 'screen_cache'
    );
    my $list = $admin_list;	
    my $file_list = $c->cached_screens;

    my $app_file_list = [];

    for my $entry (@$file_list) {
        my $cutoff_name = $entry->{name};
        my $l    = length($cutoff_name);
        my $size = 50;
        my $take = $l < $size ? $l : $size;
        $cutoff_name = substr( $cutoff_name, 0, $take );
        $entry->{cutoff_name} = $cutoff_name;
        $entry->{dotdot} = $l < $size ? '' : '...';

        push( @$app_file_list, $entry );

    }

    my $curl_location = `which curl`;
    $curl_location = strip( make_safer($curl_location) );

    require DADA::Template::Widgets;
    my $scrn = DADA::Template::Widgets::wrap_screen(
        {
			-screen         => 'plugins/screen_cache/view.tmpl', 
			-with           => 'admin', 
			-wrapper_params => { 
				-Root_Login => $root_login,
				-List       => $list,  
			},
            -vars   => {
				Plugin_URL          => $Plugin_Config->{Plugin_URL}, 
				Allow_Manual_Run    => $Plugin_Config->{Allow_Manual_Run},  
				Manual_Run_Passcode => $Plugin_Config->{Manual_Run_Passcode},
                file_list           => $app_file_list,
				curl_location       => $curl_location, 
                cache_active        => $DADA::Config::SCREEN_CACHE ne "1" ? 0 : 1,
            },
        }
    );
    e_print($scrn);

}

sub cgi_manual_start {

    if (
        (
            xss_filter( $q->param('passcode') ) eq
            $Plugin_Config->{Manual_Run_Passcode}
        )
        || ( $Plugin_Config->{Manual_Run_Passcode} eq '' )
      )
    {

        print $q->header();

        if ( defined( xss_filter( $q->param('verbose') ) ) ) {
            $verbose = xss_filter( $q->param('verbose') );
        }
        else {
            $verbose = 1;
        }

     	$c->flush;
		print 'All cached screens have been removed.'
			if $verbose; 
    }
    else {
        print $q->header();
        print	"$DADA::Config::PROGRAM_NAME $DADA::Config::VER Authorization Denied.";
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

=head1 NAME 

screen_cache.cgi - View/Removed Dada Mail cached sceens

=head1 Obtaining The Plugin

screen_cache.cgi is located in the, I<dada/plugins> directory of the Dada Mail distribution, under the name: C<screen_cache.cgi>

=head1 DESCRIPTION 

See the feature overview on Dada Mail's Screen Cache: 

L<http://dadamailproject.com/support/documentation/features-screen_cache.pod.html>

This plugins allows you to view and remove any currently cached screens. 


=head1 Installation 

This plugin can be installed during a Dada Mail install/upgrade, using the included installer that comes with Dada Mail. The below installation instructions go through how to install the plugin manually.

=head2 Change permissions of "screen_cache.cgi" to 755

The, C<screen_cache.cgi> plugin will be located in your, I<dada/plugins> diretory. Change the script to, C<755>

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
 #					-Title      => 'Screen Cache',
 #					-Title_URL  => $PLUGIN_URL."/screen_cache.cgi",
 #					-Function   => 'screen_cache',
 #					-Activated  => 0,
 #					},

Uncomment the lines, by taking off the, "#"'s: 

 					{
 					-Title      => 'Screen Cache',
 					-Title_URL  => $PLUGIN_URL."/screen_cache.cgi",
 					-Function   => 'screen_cache',
 					-Activated  => 0,
 					},

Save your C<.dada_config> file.

=head1 Using screen_cache.cgi as a cronjob

This plugin can also be used as a simple cronjob, to periodically flush all the cached screens. 

All that needs to be done is to visit the screen periodically using the URL labeled, B<Manual Run URL:> in the list control panel of this plugin. 

A sample curl command, useful for a cronjob is listed in the textbox labeled, B<curl command example (for a cronjob):>

Running this cronjob every hour, or day, or week, should be plenty. 

You may also just use the, C<rm> command directly, but this has the possibility of removing the wrong directory!


=head1 COPYRIGHT

Copyright (c) 1999 - 2014 Justin Simoni All rights reserved. 

=head1 LICENSE

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

=cut


