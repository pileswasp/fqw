#!/usr/bin/perl
package password_protect_directories;

use strict; 

$|++;

$ENV{PATH} = "/bin:/usr/bin";
delete @ENV{ 'IFS', 'CDPATH', 'ENV', 'BASH_ENV' };

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


use DADA::Config 5.0.0 qw(!:DEFAULT);
use DADA::App::Guts; 
use DADA::MailingList::Settings;
use DADA::Profile::Htpasswd;

# we need this for cookies things
use CGI;
my $q = new CGI;
$q->charset($DADA::Config::HTML_CHARSET);
$q = decode_cgi_obj($q);
my $verbose = $q->param('verbose') || 0; 

my $Plugin_Config                        = {}; 
   $Plugin_Config->{Plugin_Name}         = 'Password Protect Directories'; 
   $Plugin_Config->{Plugin_URL}          = self_url(); 
   $Plugin_Config->{Allow_Manual_Run}    = 1; 
   $Plugin_Config->{Manual_Run_Passcode} = undef; 
   $Plugin_Config->{Base_Absolute_Path}  = $ENV{DOCUMENT_ROOT} . '/';
   $Plugin_Config->{Base_URL}            = 'http://' . $ENV{HTTP_HOST} . '/'; 

&init_vars; 

run()
	unless caller();

sub init_vars {

# DEV: This NEEDS to be in its own module - perhaps DADA::App::PluginHelper or something?

    while ( my $key = each %$Plugin_Config ) {

        if ( exists( $DADA::Config::PLUGIN_CONFIGS->{password_protect_directories}->{$key} ) ) {

            if ( defined( $DADA::Config::PLUGIN_CONFIGS->{password_protect_directories}->{$key} ) ) {

                $Plugin_Config->{$key} =
                  $DADA::Config::PLUGIN_CONFIGS->{password_protect_directories}->{$key};

            }
        }
    }
}

my $list       = undef;
my $root_login = 0;
my $ls; 

sub run {
	
	if ( !$ENV{GATEWAY_INTERFACE} ) {
	
		refresh_directories( { -verbose => $verbose } );
        # this (hopefully) means we're running on the cl...
    }
	elsif (   keys %{ $q->Vars }
        && $q->param('run')
        && xss_filter( $q->param('run') ) == 1
        && $Plugin_Config->{Allow_Manual_Run} == 1 )
    {
		print $q->header(); 
		print '<pre>'
		if $verbose; 
		refresh_directories( { -verbose => $verbose } );
           print '</pre>'
		 if $verbose; 
	}
	else { 
		my $admin_list; 
		( $admin_list, $root_login ) = check_list_security(
		    -cgi_obj  => $q,
		    -Function => 'password_protect_directories'
		);
		$list = $admin_list;
		$ls   = DADA::MailingList::Settings->new( { -list => $list } );
	
		my $f = $q->param('f') || undef;
		my %Mode = (
		    'default'                    => \&default,
			'edit_dir'                   => \&default, 
			'process_edit_dir'           => \&process_edit_dir, 
			'new_dir'                    => \&new_dir, 
			'delete_dir'                 => \&delete_dir, 
			'cgi_refresh_directories'    => \&cgi_refresh_directories, 
		);
		if ($f) {
		    if ( exists( $Mode{$f} ) ) {
		        $Mode{$f}->();    #call the correct subroutine
		    }
		    else {
		        &default;
		    }
		}
		else {
		    &default;
		}
	}
}


sub test_sub { 
	return 'Hello, World!'; 
}

sub cgi_refresh_directories { 
	$verbose = 0; 
	refresh_directories(); 
	print $q->redirect(-uri => $Plugin_Config->{Plugin_URL} . '?done=1'); 
}
sub refresh_directories {
	print "Starting...\n"
	 if $verbose; 
	foreach my $list(available_lists()) { 
		print "List: $list\n"
			 if $verbose; 
		my $htp     = DADA::Profile::Htpasswd->new({-list => $list});
		for my $id(@{$htp->get_all_ids}) {  
			print "id: $id\n"
				 if $verbose; 
			$htp->setup_directory({-id => $id});
		}
	}
	print "Done.\n"
		if $verbose;
}

sub default {
	
	if($DADA::Config::SUBSCRIBER_DB_TYPE !~ /SQL/i){ 
		sql_backend_only_message(); 
		return; 
	}
	
	
	my $htp     = DADA::Profile::Htpasswd->new({-list => $list});
	my $entries = $htp->get_all_entries; 
	
	my $problems = $q->param('problems') || 0; 
	my $edit     = 0; 
	my $f        = $q->param('f'); 
	my $id       = undef; 
	if($f eq 'edit_dir'){ 
		$id = $q->param('id') || undef; 
		my $htp = DADA::Profile::Htpasswd->new({-list => $list});
		my $entry = $htp->get({-id => $id });
		$edit = 1; 
		$q->param('name', $entry->{name});
		$q->param('url', $entry->{url});
		$q->param('path', $entry->{path});
		
		$q->param('use_custom_error_page', $entry->{use_custom_error_page});
		$q->param('custom_error_page', $entry->{custom_error_page});
		$q->param('f', 'process_edit_dir'); 
	}
	my $errors = [];
	if($problems == 1){ 
		my %params = $q->Vars;
		for(keys %params){ 
			if($_ =~ m/^error_/){
				push(@$errors, {error => $_}); 
			}
		}
	}
	
	my $curl_location = `which curl`;
       $curl_location = strip( make_safer($curl_location) );

    require DADA::Template::Widgets;
    my $scrn = DADA::Template::Widgets::wrap_screen(
        {
            -screen         => 'plugins/password_protect_directories/default.tmpl',
            -with           => 'admin',
            -wrapper_params => {
                -Root_Login => $root_login,
                -List       => $ls->param('list'),
            },
			-expr => 1, 
            -vars => {
                done                             => $q->param('done') || 0,
				Plugin_URL                       => $Plugin_Config->{Plugin_URL}, 
				entries                          => $entries, 
				problems                         => $problems, 
				errors                           => $errors, 
				edit                             => $edit, 
				id                               => $id, 
				curl_location                    => $curl_location, 
				root_login                       => $root_login, 
				
				Allow_Manual_Run => $Plugin_Config->{Allow_Manual_Run},
			   Manual_Run_Passcode => $Plugin_Config->{Manual_Run_Passcode},
			   Base_Absolute_Path => $Plugin_Config->{Base_Absolute_Path},
			   Base_URL  => $Plugin_Config->{Base_URL},
			
            },

            -list_settings_vars_param => {
                -list   => $list,
                -dot_it => 1,
            },
        }
    );

	if($problems == 1 || $edit == 1){ 
		require HTML::FillInForm::Lite;
		my $h = HTML::FillInForm::Lite->new();
		$scrn = $h->fill( \$scrn, $q );
	}
	
	
    e_print($scrn);

}


sub new_dir { 
    my $name = xss_filter( $q->param('name') ) || undef;
    my $url  = xss_filter( $q->param('url') )  || undef;
    my $path = xss_filter( $q->param('path') ) || undef;
    my $use_custom_error_page = xss_filter( $q->param('use_custom_error_page') ) || 0;
    my $custom_error_page = xss_filter( $q->param('custom_error_page') )|| undef;
    my $default_password = xss_filter( $q->param('default_password') ) || undef;
	
	
	my $htp = DADA::Profile::Htpasswd->new({-list => $list});
	
	my ($status, $errors) = $htp->validate_protected_dir(
		{ 
			-fields => { 
		        -name                  => $name,
				-url                   => $url,
		        -path                  => $path ,
				-use_custom_error_page => $use_custom_error_page,
				-custom_error_page     => $custom_error_page,
				-default_password      => $default_password,
			}, 
		}		
	); 
	if($status == 1){ 

	   $htp->create(
			{ 
		        -name                  => $name,
				-url                   => $url,
		        -path                  => $path ,
				-use_custom_error_page => $use_custom_error_page,
				-custom_error_page     => $custom_error_page,
				-default_password      => $default_password,
			}
		);
		for my $id2(@{$htp->get_all_ids}) {  
			$htp->setup_directory({-id => $id2});
		}			
		print $q->redirect(-uri => $Plugin_Config->{Plugin_URL} . '?done=1'); 
	}
	else { 
		for(keys %$errors){ 
			$q->param('error_' . $_, $errors->{$_}); 
		}
		$q->param('problems', 1); 
		&default; 
		return; 
	}
}


sub sql_backend_only_message { 
	
    require DADA::Template::Widgets;
    my $scrn = DADA::Template::Widgets::wrap_screen(
        {
            -screen         => 'plugins/shared/sql_backend_only_message.tmpl',
            -with           => 'admin',
            -wrapper_params => {
                -Root_Login => $root_login,
                -List       => $ls->param('list'),
            },, 
            -vars => {
            },

            -list_settings_vars_param => {
                -list   => $list,
                -dot_it => 1,
            },
        }
    );	
	e_print($scrn);
}

sub process_edit_dir { 
	
	my $name                  = xss_filter( $q->param('name') ) || undef;
    my $url                   = xss_filter( $q->param('url') )  || undef;
    my $path                  = xss_filter( $q->param('path') ) || undef;
    my $use_custom_error_page = xss_filter( $q->param('use_custom_error_page') ) || 0;
    my $custom_error_page     = xss_filter( $q->param('custom_error_page') )|| undef;
    my $default_password      = xss_filter( $q->param('default_password') ) || undef;
	my $id                    = xss_filter( $q->param('id') ) || undef;
	
	my $htp = DADA::Profile::Htpasswd->new({-list => $list});
	
	my ($status, $errors) = $htp->validate_protected_dir(
		{ 
			-fields => { 
		        -name                  => $name,
				-url                   => $url,
		        -path                  => $path ,
				-use_custom_error_page => $use_custom_error_page,
				-custom_error_page     => $custom_error_page,
				-default_password      => $default_password,
			}, 
		}		
	);
	if($status == 1){ 

	
		   $htp->update(
				{ 
					-id                    => $id, 
			        -name                  => $name,
					-url                   => $url,
			        -path                  => $path ,
					-use_custom_error_page => $use_custom_error_page,
					-custom_error_page     => $custom_error_page,
					-default_password      => $default_password,
				}
			);
			my $htp     = DADA::Profile::Htpasswd->new({-list => $list});
			   $htp->setup_directory({-id => $id});
			
		print $q->redirect(-uri => $Plugin_Config->{Plugin_URL} . '?done=1'); 
	}
	else { 
		for(keys %$errors){ 
			$q->param('error_' . $_, $errors->{$_}); 
		}
		$q->param('problems', 1); 
		$q->param('f', 'edit_dir');
		&default;  
		return; 
	}	
		
}

sub delete_dir { 
	my $id = $q->param('id'); 
	my $htp     = DADA::Profile::Htpasswd->new({-list => $list});
	   $htp->remove_directory_files({-id => $id}); 
	   $htp->remove({-id => $id});
	print $q->redirect(-uri => $Plugin_Config->{Plugin_URL} . '?done=1'); 
	
}



sub self_url { 
	my $self_url = $q->url; 
	if($self_url eq 'http://' . $ENV{HTTP_HOST}){ 
			$self_url = $ENV{SCRIPT_URI};
	}
	return $self_url; 	
}

__END__

=pod

=head1 Password Protect Directories Plugin

The Password Protect Directories plugin allows you to create an Apache Webserver-style C<.htaccess> and C<.htpasswd> file in specific directories that will then prompt a visitor for a username and password, before they can access the directory itself. 

The B<username> used will be one of your mailing list's subscribers B<email address>> The B<password> will be either their B<Dada Mail Profile password>, or if the subscriber doesn't have a Dada Mail Profile, you may set a default password. 

Since the password use is the Dada Mail Profile password, the user will be able to create, change and reset their own password. List Owners will also be able to reset this Profile Password in the, I<Membership E<gt>E<gt> View> Screen. Search the address you want to work with, click on their email address and once the screen has refreshed, scrolle down to, B<Member Profile> and look under, B<Profile Password> for a form to change this password. 

Profile passwords are saved in an encryped form, using C<crypt> and can't be unencrypted. When this plugin creates the .htpasswd file, it will simple copy the saved, encrypted password to this file, from the Dada Profile database table. 

Currently, only Apache-style, C<.htaccess>/C<.htpasswd> files are supported. 

=head1 Installation 

This plugin can be installed during a Dada Mail install/upgrade, using the included installer that comes with Dada Mail. The below installation instructions go through how to install the plugin manually.

If you install the plugin using the Dada Mail installer, you will still have set the cronjob manually, which is covered below.

=head2 Change permissions of "password_protect_directories.cgi" to 755

The, C<password_protect_directories.cgi> plugin will be located in your, I<dada/plugins> diretory. Change the script to, C<755>

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
 #					-Title      => 'Password Protect Directories',
 #					-Title_URL  => $PLUGIN_URL."/password_protect_directories.cgi",
 #					-Function   => 'password_protect_directories',
 #					-Activated  => 1,
 #					},

Uncomment the lines, by taking off the, "#"'s: 

 					{
 					-Title      => 'Password Protect Directories',
 					-Title_URL  => $PLUGIN_URL."/password_protect_directories.cgi",
 					-Function   => 'password_protect_directories',
 					-Activated  => 1,
 					},

Save your C<.dada_config> file.

=head1 Using Password Protect Directories

Once installed, log into a mailing list and under B<Plugins> click the link labeled, B<Password Protect Directories>

A form labeled, B<New Password Protected Directory> will allow you to set up a new directory to password protect. You may set up as many Password Protect Directories as you may like. 

=head2 Name

This allows you to set a name for your password-protected directory. This will be shown in the dialogue box, asking for the visitor's username and password

=head2 Protected URL 

This should hold the URL for the B<directory> that you want to password protect. For example: 

L<http://example.com/secret>

You should I<not> set this to a file in that directory: 

L<http://example.com/secret/index.html>

=head2 Corresponding Server Path

This should hold the B<Absolute Server Path> to where this directory is located on the server. For example: 

C</home/youraccount/public_html/secret>

To start you off, the B<best guess> absolute path to your public html directory is pre-filled in - in our example, C</home/youraccount/public_html/> - you will need to simply make sure this is correct and then fill in the directory path of where the directory you typed for, B<Protected URL> resides. 

=head2 Use a Custom Error Page

If checked, any problems with the login will go to the page listed under, B<Custom Error Page (Path):>

=head2 Custom Error Page (Path): 

This should hold the path of your custom error page and confusingly, should B<not> hold an absolute path, but rather the path, starting with a, C</> from your public html directory to the error page. For example: 

C</error_logging_in.html>

In our example, this will redirect us to the following URL, for the, C<http://example.com> site: 

L<http://example.com/error_logging_in.html> 

Make sure to not set this to a page inside your password protected directory, as that will just not work. 

=head2 Default Password 

This optionally, may hold a default password that any subscriber of your mailing list may use, if they B<do not have> a Dada Mail Profile. 

=head1 BUGS AND LIMITATIONS

Currently, if you have more than one mailing list that attempts to password protect the same directory, one mailing list will overwrite the C<.htaccess> and C<.htpasswd> created by any other mailing list. 

If you already have a C<.htaccess> and/or C<.htpasswd> file in the directory you attempt to password protect, created manually/outside of this plugin, it will also be overwritten by this plugin.

=head2 Setting the cronjob

You may set up a cronjob to periodically B<refresh> both the C<.htacces> and C<.htpasswd> files that this plugin creates. This can come in handy, if changes are made to user's Profile email address and/or Password and you need to keep both of these files updated. 

Generally, setting the cronjob to have this plugin run automatically just means that you have to have a cronjob access a specific URL. The URL looks something like this:

 http://example.com/cgi-bin/dada/plugins/password_protect_directories.cgi?run=1&verbose=1

Where, I<http://example.com/cgi-bin/dada/plugins/password_protect_directories.cgi> is the URL to your copy of this plugin. 

A B<Best Guess> at what the entire cronjob that's needed (using the, C<curl> command to access the actual URL) to be set manually will appear in this plugin's list control panel under the fieldset labled, B<Manually Run Password Protect Directories> in the textbox labeled, B<curl command example (for a cronjob):>. It'll look something like this: 

 /usr/bin/curl  -s --get --data run=1\;passcode=\;verbose=0  --url http://example.com/cgi-bin/dada/plugins/password_protect_directories.cgi

Where, I<http://example.com/cgi-bin/dada/plugins/password_protect_directories.cgi> is the URL to this plugin. We suggest running this cronjob every 5 to 15 minutes. A complete cronjob, with the time set for, "every 5 minutes" would look like this: 

 */5 * * * * /usr/bin/curl  -s --get --data run=1\;passcode=\;verbose=0  --url http://example.com/cgi-bin/dada/plugins/password_protect_directories.cgi

=head3 Command Line

This plugin can also be called directory on the command line and that can itself be used for the cronjob: 

	cd /home/youraccount/cgi-bin/dada/plugins; /usr/bin/perl ./password_protect_directories.cgi

You may pass the, C<--noverbose> flag to have the script return nothing at all:

	cd /home/youraccount/cgi-bin/dada/plugins; /usr/bin/perl ./password_protect_directories.cgi --noverbose

By default, it will print out the Password Protect Directories report. 

=head1 SEE ALSO

The B<Authentication, Authorization and Access Control> doc from Apache has an overview on the nuts and bolts of how this works: 

L<http://httpd.apache.org/docs/2.0/howto/auth.html>

=head1 Thanks

This plugin was originally commissioned by Jeff Berger for "Websites That Work" -- L<http://www.websitesthatworkusa.com>.

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