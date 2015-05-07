#!/usr/bin/perl
package global_config;
use strict;

use File::Copy; 

use FindBin;
use lib "$FindBin::Bin/../";
use lib "$FindBin::Bin/../DADA/perllib";
BEGIN { 
	my $b__dir = ( getpwuid($>) )[7].'/perl';
    push @INC,$b__dir.'5/lib/perl5',$b__dir.'5/lib/perl5/x86_64-linux-thread-multi',$b__dir.'lib',map { $b__dir . $_ } @INC;
}

# use some of those Modules
use DADA::Config 7.0.0;
use DADA::Template::HTML;
use DADA::App::Guts;
use DADA::MailingList::Settings;

# we need this for cookies things
use CGI;
my $q = new CGI;
$q->charset($DADA::Config::HTML_CHARSET);
$q = decode_cgi_obj($q);
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



my $Plugin_Config = {
	Plugin_Name => 'Global Config Helper', 	
};




my $admin_list; 
my $root_login; 
my $list; 




&init_vars;

run()
  unless caller();

sub run { 
	cgi_main(); 
}
sub init_vars {
# DEV: This NEEDS to be in its own module - perhaps DADA::App::PluginHelper or something?
    while ( my $key = each %$Plugin_Config ) {
        if ( exists( $DADA::Config::PLUGIN_CONFIGS->{'Global_Config'}->{$key} ) )
        {
            if (
                defined(
                    $DADA::Config::PLUGIN_CONFIGS->{'Global_Config'}->{$key}
                )
              )
            {
                $Plugin_Config->{$key} =
                  $DADA::Config::PLUGIN_CONFIGS->{'Global_Config'}->{$key};
            }
        }
    }
}



sub cgi_main {

    ( $admin_list, $root_login ) = check_list_security(
        -cgi_obj  => $q,
        -Function => 'bounce_handler'
    );

    $list = $admin_list;

    my $ls = DADA::MailingList::Settings->new( { -list => $list } );
    my $li = $ls->get();

    my $flavor = $q->param('f') || 'cgi_default';
    my %Mode = (

        'cgi_default'                => \&cgi_default,
'reconfigure'                => \&reconfigure, 

    );

    if ( exists( $Mode{$flavor} ) ) {
        $Mode{$flavor}->();    #call the correct subroutine
    }
    else {
        &cgi_default;
    }
}



sub cgi_default {

    # This will take care of all out security woes
    my ( $admin_list, $root_login ) = check_list_security(
        -cgi_obj  => $q,
        -Function => 'global_config'
    );
    my $list = $admin_list;

    # get the list information
    my $ls = DADA::MailingList::Settings->new( { -list => $list } );
    my $li = $ls->get;

    my $data = '';
    if ( !$q->param('process') ) {

	    require DADA::Template::Widgets;
	    my $scrn = DADA::Template::Widgets::wrap_screen(
	        {
	            -screen         => 'plugins/global_config/default.tmpl',
	            -with           => 'admin',
	            -expr           => 1,
	            -wrapper_params => {
	                -Root_Login => $root_login,
	                -List       => $list,
	            },
	            -vars => {
					screen => 'global_config',
	            },
	            -list_settings_vars_param => {
	                -list   => $list,
	                -dot_it => 1,
	            },
	        }
	    );
	    e_print($scrn);


    }
}

sub reconfigure { 
	
	my $installer_url            = installer_url(); 
	my $found_install_dir        = 0; 
	my $moved_installer_dir_back = 0; 
	my $chmoded_installer_script = 0; 
	
	my $installer_dir; 
	if($installer_dir = installer_dir()) { 
		$found_install_dir = 1; 
	}
	
	if($found_install_dir == 1) { 
		if(move_installer_dir_back($installer_dir) == 1){ 
			$moved_installer_dir_back = 1;
		}
	
		if($moved_installer_dir_back == 1) { 
			if(chmod_installer_script(0755)) { 
				$chmoded_installer_script = 1; 
			}
		}
	}
	
	if($found_install_dir == 1 && $moved_installer_dir_back == 1 && $chmoded_installer_script == 1){ 
		print $q->redirect(-uri => $installer_url); 
		return; 
	}
	else { 
		
		if($chmoded_installer_script == 0){ 
			chmod_installer_script(0644);
		}

		require DADA::Template::Widgets;
	    my $scrn = DADA::Template::Widgets::wrap_screen(
	        {
	            -screen         => 'plugins/global_config/reconfigure.tmpl',
	            -with           => 'admin',
	            -expr           => 1,
	            -wrapper_params => {
	                -Root_Login => $root_login,
	                -List       => $list,
	            },
	            -vars => {
					screen                    => 'global_config',
					installer_url             => $installer_url,
					found_install_dir         => $found_install_dir,
					moved_installer_dir_back  => $moved_installer_dir_back,  
					chmoded_installer_script  => $chmoded_installer_script,
	            },
	            -list_settings_vars_param => {
	                -list   => $list,
	                -dot_it => 1,
	            },
	        }
	    );
	    e_print($scrn);
	}	
}

sub installer_dir { 
	# installer-disabled.
	  #  my $dirs = []; 
		my $looking_for = qr/^installer\-disabled\./; 
		my $dada_dir = $FindBin::Bin . '/../';
		my $f;
	    opendir( DADADIR, $dada_dir )
	      or croak
	"$DADA::Config::PROGRAM_NAME $DADA::Config::VER error, can't open '" . $dada_dir . "' to read because: $!";
	
	    while ( defined( $f = readdir DADADIR ) ) {
		#	print $q->p($f); 
			
	        ##don't read '.' or '..'
	        next if $f =~ /^\.\.?$/;
			#
	        $f =~ s(^.*/)();
	
			next unless -d $dada_dir . '/' . $f; 
	
			if($f =~ m/$looking_for/) { 
			#	push(@$dirs, $f); 
				return $f; 
			}
	    }

	    closedir(DADADIR);
}

sub move_installer_dir_back { 
	my $installer_dir = shift; 
	my $current_installer_dir_abs = make_safer($FindBin::Bin . '/../' . $installer_dir); 
	my $future_installer_dir_abs  = make_safer($FindBin::Bin . '/../' . 'installer'); 
	if(move($current_installer_dir_abs, $future_installer_dir_abs)) { 
		return 1; 
	}
	else { 
		return undef; 
	}
}

sub chmod_installer_script { 
	my $chmod_octet = shift || 0755;
	my $install_script  = make_safer($FindBin::Bin . '/../' . 'installer/install.cgi'); 
	
	if(chmod($chmod_octet, $install_script)) { 
		return 1; 
	}
	else { 
		return undef; 
	}
}

sub installer_url { 
	my $installer_url = $DADA::Config::PROGRAM_URL; 
       $installer_url =~ s{mail\.cgi}{installer\/install\.cgi};
	$installer_url .= '?install_type=upgrade&f=check_install_or_upgrade&current_dada_files_parent_location=' 
					. uriescape(current_dada_files_parent_loc()); 	
	return $installer_url; 
}

sub current_dada_files_parent_loc { 
	my $config_dir = $DADA::Config::PROGRAM_CONFIG_FILE_DIR;
	   $config_dir =~ s{\/.dada_files/\.configs$}{}; 
	return $config_dir; 
}

=pod

=head1 Plugin: Global Config - Reconfigure Dada Mail's Global Configuration

This plugin allows you to easily drop back into Dada Mail's included Installer, allowing you to then change its global configuration, just like you would, during an installation or upgrade. 

Dada Mail's global configuration is saved in its C<.dada_config> file, which the installer writes during an install/upgrade. This file can be edited after an installation or upgrade by hand, but can be much easier done with this plugin. 

By default, when installed, this plugin will only be accessable when logged in using the Dada Mail Root Password. 

=head1 Installation 

This plugin can be installed during a Dada Mail install/upgrade, using the included installer that comes with Dada Mail. The below installation instructions go through how to install the plugin manually.

=head2 Change permissions of "global_config.cgi" to 755

The, C<global_config.cgi> plugin will be located in your, I<dada/plugins> diretory. Change the script to, C<755>

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
 #					-Title      => 'Global Configuration',
 #					-Title_URL  => $PLUGIN_URL."/global_config.cgi",
 #					-Function   => 'global_config',
 #					-Activated  => 0,
 #					},

Uncomment the lines, by taking off the, "#"'s: 

 					{
 					-Title      => 'Global Configuration',
 					-Title_URL  => $PLUGIN_URL."/global_config.cgi",
 					-Function   => 'global_config',
 					-Activated  => 0,
 					},

Save your C<.dada_config> file.

=head1 COPYRIGHT 

Copyright (c) 1999 - 2014 

Justin Simoni

http://justinsimoni.com

All rights reserved. 

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
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

=cut


