#!/usr/bin/perl

package log_viewer; 

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



$ENV{PATH} = "/bin:/usr/bin"; 
delete @ENV{'IFS', 'CDPATH', 'ENV', 'BASH_ENV'};
# we need this for cookies things;
use CGI; 
CGI->nph(1) 
	if $DADA::Config::NPH == 1; 
	
	my $q = new CGI; 
	   $q->charset($DADA::Config::HTML_CHARSET);
       $q = decode_cgi_obj($q);


my $Plugin_Config = {}; 


# Usually, this doesn't need to be changed. 
# But, if you are having trouble saving settings 
# and are redirected to an 
# outside page, you may need to set this manually.

$Plugin_Config->{Plugin_URL}   = self_url(); 


$Plugin_Config->{Plugin_Name}  = 'Log Viewer'; 


# This refers to the, "tail" command: 
$Plugin_Config->{tail_command} =  'tail';



# use some of those Modules
use DADA::Config 7.0.0;
use DADA::Template::HTML; 
use DADA::App::Guts;
use DADA::MailingList::Settings; 
use DADA::App::LogSearch;


init_vars(); 

my $admin_list = undef; 
my $root_login = undef; 
my $list       = undef; 
my %Logs       = (); 

my $Default_Log = 'Usage Log';

my $process     = $q->param('process'); 

    my $logs        = {}; 
    my $lines       = $q->param('lines')    || 100; 
    my $log_name    = $q->param('log_name') || $Default_Log;

run()
  unless caller();


sub run { 
	if(!$ENV{GATEWAY_INTERFACE}){ 
	#	croak "There's no CLI for this plugin."; 
	}else{ 
		&cgi_main(); 
	}
}


sub test_sub { 
	return "Hello, World!"; 
}



sub init_vars { 

    # DEV: This NEEDS to be in its own module - perhaps DADA::App::PluginHelper or something?

     while ( my $key = each %$Plugin_Config ) {
        
        if(exists($DADA::Config::PLUGIN_CONFIGS->{'log_viewer'}->{$key})){ 
        
            if(defined($DADA::Config::PLUGIN_CONFIGS->{'log_viewer'}->{$key})){ 
                    
                $Plugin_Config->{$key} = $DADA::Config::PLUGIN_CONFIGS->{'log_viewer'}->{$key};
        
            }
        }
     }
}

sub cgi_main {

	( $admin_list, $root_login ) = check_list_security(
	    -cgi_obj    => $q,
	    -Function   => 'log_viewer',
	);
	$list = $admin_list; 
 
	
	%Logs = get_logs($list); 
	$logs = find_logs();
	
	my $ls = DADA::MailingList::Settings->new( { -list => $list } );
	my $li = $ls->get;

	my $flavor = $q->param('flavor') || 'cgi_view';

	my %Mode = (
	   'cgi_view'               => \&cgi_view, 
	   'ajax_view_logs_results' => \&ajax_view_logs_results, 
	   'ajax_delete_log'        => \&ajax_delete_log, 
	   'search_logs'            => \&search_logs, 
	   'download'               => \&download, 
	);

	if ( exists( $Mode{$flavor} ) ) {
	    $Mode{$flavor}->();    #call the correct subroutine
	}
	else {
	    &cgi_view;
	}

}



sub cgi_view { 

    # get the list information
    my $ls = DADA::MailingList::Settings->new({-list => $list}); 
    my $li = $ls->get; 
     

    my $logs_popup_menu = $q->popup_menu(
        -name     => 'log_name',
        -id       => 'log_name',
        '-values' => [ keys %$logs ],
        -default  => $log_name,
        style     => 'width:200px', 
    );
	my $log_lines = []; 
	for(100, 1,10,20,25,50,100,200,500,1000, 10000, 100000, 1000000){ 
		push(@$log_lines, {line_count => $_});
	}

	$Default_Log = $log_name; 
                      
    my @log_names = keys %$logs; 
    
	require DADA::Template::Widgets; 
	my $scrn = DADA::Template::Widgets::wrap_screen(
		{ 
			-screen         => 'plugins/log_viewer/default.tmpl', 
			-with           => 'admin',
            -wrapper_params => {
                -Root_Login => $root_login,
                -List       => $list,
            },
			-vars => { 
				log_names       => ($log_names[0] ? 1 : 0),
				logs_popup_menu => $logs_popup_menu, 
				log_lines       => $log_lines, 
				Plugin_URL      => $Plugin_Config->{Plugin_URL}, 
			},
		}
		
	); 
	e_print($scrn); 
	    
}



sub ajax_view_logs_results {

     my $scrn; 
        $scrn .=  '<div style="width:100%; overflow: auto; height: 500px" id="resultdiv">'; 
        $scrn .=  show_log($log_name, $lines); 
        $scrn .=  '</div>';
        
		print $q->header(); 
        e_print($scrn); 
}


sub show_log { 
	my ($log_name, $lines) = @_;
	my $loglines = log_lines($Logs{$log_name}, $lines); 
	my $html; 
	   $html .= '<pre>';
	for(@$loglines){ 
		$_ =~ s/\t/    /g;
		$html .= encode_html_entities($_, "\200-\377") . "\n";
	}
	$html .= '</pre>';
	return $html;
}




sub ajax_delete_log { 
    my @log_names = keys %$logs;     
    if(exists($logs->{$log_name})){ 
        my $file = $Logs{$log_name};
        make_safer($file);
        unlink($file); 	
    }
	print $q->header(); 
}



#---------------------------------------------------------------------#


sub find_logs { 
	my %found_logs;	
	for(keys %Logs){ 
		if(file_check($Logs{$_}) == 1){ 
			$found_logs{$_} = $Logs{$_};
		}
	}	
	return \%found_logs; 
}




sub log_name { 

    my $file_name = shift; 
    
    
    for(keys %Logs){ 
    
        if($file_name eq $Logs{$_}){ 
        
            return $_;
        }
    }



}




sub file_check { 
	my $filename = shift; 
	
	if(-f $filename && -e $filename){ 
		return 1;
	}else{ 
		return 0; 
	}
}




sub log_lines { 
	my ($filename, $lines) = @_;

	my $tail  = make_safer($Plugin_Config->{tail_command}); 
	$filename = make_safer($filename); 
	$lines    = make_safer($lines); 
	
	my $log = `$tail -n $lines $filename`;
	
	my @lines = split("\n", $log);
	
	if(($log_name eq "Usage Log") || ($log_name eq "Bounce Handler Log")){ 
	 
		my @good_lines; 	
		for(@lines){ 
			if (($_ =~ m/\[(.*?)\]\t$list(.*)/) || ($_ =~ m/\[(.*?)\]\t(.*?)\t$list(.*)/)){ 
				push(@good_lines, $_); 		
			}
		}
		@lines = @good_lines; 
	}
		
	
	
	return \@lines;
}




sub search_logs { 
	
	my $s_logs = shift || [values(%$logs)]; 
	my $query  = shift || $q->param('query'); 
	my $test   = shift || undef; 
	
	
	require Data::Dumper;
	
    my $only_content = 0; 
	my $list         = undef; 
	my $ls           = undef; 
	my $li           = undef; 
	my $return       = undef; 
	
	
	if(! $test){ 
		
		$only_content = xss_filter($q->param('only_content')) || 0;
		
		my ($admin_list, $root_login) = check_list_security(
											-cgi_obj  => $q,  
	                                        -Function => 'log_viewer'
										);
	    $list = $admin_list; 
	 
	
	    # get the list information
	     $ls = DADA::MailingList::Settings->new(
											{
												-list => $list,
											}
										); 
	     $li = $ls->get;
	
    }
	else { 
		$only_content = 1; 
	}
    
  

    # header 
    $return .= $q->header(admin_header_params()); 
    
    if($only_content != 1){ 

        $return .= admin_template_header(
								-Title       => "Log Viewer - Search",
                                -List        => $li->{list},
                                -Root_Login  => $root_login,
                                -HTML_Header => 0,
                              );
    }    
        
    if($only_content != 1){     

		  $return .= "<p id=\"breadcrumb\"><a href=\"" . $Plugin_Config->{Plugin_URL} . "\">" . $Plugin_Config->{Plugin_Name} . "</a> &#187; Search Results</p>	";


          $return .= $q->h1("Results for: " . $q->param('query')); 
    }
    
    my $searcher = DADA::App::LogSearch->new; 
    my $results  = $searcher->search({
        -query => $query,
        -files => $s_logs, 
    }); 
           
    my @terms = split(' ', $q->param('query')); 
    
    for my $file_name(keys %$results){ 
        
        if($results->{$file_name}->[0]){ 
        
            $return .= $q->h1(log_name($file_name));
            
            for my $l(@{$results->{$file_name}}){ 
            
                my @entries = split("\t", $l); 
                
                $return .= '<ul>'; 
                for my $diff_lines(@entries){ 
                  
					# BUGFIX: [ 2124123 ] 3.0.0 - Log viewer does not escape ">" "<" etc. 
					# http://sourceforge.net/tracker/index.php?func=detail&aid=2124123&group_id=13002&atid=113002
					#$diff_lines = plaintext_to_html({-str =>$diff_lines});
					$diff_lines =~ s/& /&amp; /g;
			        $diff_lines =~ s/</&lt;/g;
			        $diff_lines =~ s/>/&gt;/g;
			        $diff_lines =~ s/\"/&quot;/g;
					$diff_lines = convert_to_ascii($diff_lines);
					# DEV: This will probably work, so long as the lines do not have new line endings, 
					
                    $diff_lines = $searcher->html_highlight_line({-query => $query, -line => $diff_lines }); 

						
                  	$return .= $q->li({-style => 'list-style-type:none"'}, $diff_lines);
					
				}
				$return .= '</ul><hr />'; 
				
            }
        }
   
   
    }
    
    if($only_content != 1){ 

        $return .= admin_template_footer(
					-List => $list, 
					-Form => 0
					); 
    
    }

	if($test){ 
		return $return; 
	}
	else { 
		e_print($return); 
	}


}

sub download { 
 
	
	use File::Basename; 
	my $name = fileparse($Logs{$log_name});
	my ($file_name, $file_ending) = split(/\./, $name, 2); 
	
	my $header  = 'Content-disposition: attachement; filename=' . $file_name . '-' . time . '.' . $file_ending . "\n"; 
	   $header .= 'Content-type: text/plain' . "\n\n"; 
	
		print $header; 
	
		open my $LOG, '<:encoding('. $DADA::Config::HTML_CHARSET . ')', make_safer($Logs{$log_name}) or die $!; 
		my $line; 
		while(defined($line = <$LOG>)){ 
			 e_print($line); 
		}
		close($LOG); 
}	

sub get_logs { 
	
	my $l_list = shift; 
	my %logs = (
		'Usage Log'      		 => $DADA::Config::PROGRAM_USAGE_LOG,
		'Error Log'      		 => $DADA::Config::PROGRAM_ERROR_LOG,
		'Clickthrough Log (raw)' => $DADA::Config::LOGS . '/' . $l_list . '-clickthrough.log', 
		'Bounce Handler Log'     => $DADA::Config::LOGS . '/' . 'bounces.txt', 
	);
	
	my $mass_mailing_logs = mass_mailing_logs($l_list); 
	my $bridge_received_msgs = bridge_received_msgs($l_list); 
	
    
    
	if(keys %$mass_mailing_logs) { 
	    %logs = (%logs, %{$mass_mailing_logs});
	}
	if(keys %$bridge_received_msgs) { 
	    %logs = (%logs, %{$bridge_received_msgs}); 
	}
	return %logs; 
}

sub mass_mailing_logs { 
    my $list = shift; 
    
    my $dir  = $DADA::Config::LOGS;
    my $file;
    my @files;
    $dir = DADA::App::Guts::make_safer($dir);
    
    opendir( DIR, $dir ) or die "$!";
    while ( defined( $file = readdir DIR ) ) {
        next if $file =~ /^\.\.?$/;
        $file =~ s(^.*/)();
        if ( -f $dir . '/' . $file ) {
            if($file =~ m/sendout\-$list/) { 
                push( @files, $file );
            }
        }

    }
    closedir(DIR);
    # sendout-example-list-20131222202213.73210509_at_dadamailproject.com-log
    
    my $mass_mailing_logs = {}; 
        
    require DADA::MailingList::Archives; 
    my $ma = DADA::MailingList::Archives->new({-list => $list});
    foreach my $found_file(@files) { 
        my ($throway, $list_shortname, $mailing_type, $mid, $orig_fn) = split('-', $found_file, 5);   
        
        $mid =~ s/\.(.*?)$//; 
              
        my $subject = 'Mass Mailing: ';       
        if($mailing_type eq 'list'){ 
            if ( $ma->check_if_entry_exists($mid) ) {
                $subject .= $ma->get_archive_subject($mid);
            }
            else { 
                $subject .= 'Unarchived Message #' . $mid; 
            }
        } 
        else { 
            $subject .= '(' . $mailing_type . ')' . ' Message # ' . $mid; 
        }
        
        #my $date = scalar(localtime($mid)); 
        my $date = date_this(
            -Packed_Date => $mid, 
            -All         => 1
        ); 
        
        $subject .= ', ' . $date;
        
        $mass_mailing_logs->{$subject} = $DADA::Config::LOGS . '/' . $found_file;
    }
    
    return $mass_mailing_logs; 
    
    #return @files;
    
}



sub bridge_received_msgs { 
    my $list = shift; 
    
    my $dir  = $DADA::Config::TMP;
    my $file;
    my @files;
    my $mbox = {}; 
        
    $dir = DADA::App::Guts::make_safer($dir);
    my $file = $dir . '/' . 'bridge_received_msgs-' . $list . '.mbox'; 
    
    if(-f $file){ 
        $mbox->{'Bridge Received Messages (mbox)'} = $file;
        return $mbox; 
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

=head1 Plugin: log_viewer.cgi - View Logs Created by Dada Mail

This plugin allows you to view the Dada Mail, Error, Bounce and Clickthrough logs
that  Dada Mail creates in its activities through your web browser. 

=head1 Installation 

This plugin can be installed during a Dada Mail install/upgrade, using the included installer that comes with Dada Mail. The below installation instructions go through how to install the plugin manually.

=head2 Change permissions of "log_viewer.cgi" to 755

The, C<log_viewer.cgi> plugin will be located in your, I<dada/plugins> diretory. Change the script to, C<755>

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
 #					-Title      => 'View Logs',
 #					-Title_URL  => $PLUGIN_URL."/log_viewer.cgi",
 #					-Function   => 'log_viewer',
 #					-Activated  => 1,
 #					},

Uncomment the lines, by taking off the, "#"'s: 

 					{
 					-Title      => 'View Logs',
 					-Title_URL  => $PLUGIN_URL."/log_viewer.cgi",
 					-Function   => 'log_viewer',
 					-Activated  => 1,
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




