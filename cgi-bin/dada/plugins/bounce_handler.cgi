#!/usr/bin/perl

package bounce_handler;
use strict;
$|++;

#---------------------------------------------------------------------#
# bounce_handler.cgi
#
# Documentation:
#
#  http://dadamailproject.com/d/bounce_handler.cgi.html
#
#---------------------------------------------------------------------#

# A weird fix.
BEGIN {
    if ( $] > 5.008 ) {
        require Errno;
        require Config;
    }
}

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


use DADA::Config;
use DADA::App::Guts;
use DADA::Mail::Send;
use DADA::MailingList::Subscribers;
use DADA::MailingList::Settings;
use DADA::Template::HTML;
use DADA::App::BounceHandler;
use CGI;
my $q = new CGI;
$q->charset($DADA::Config::HTML_CHARSET);
$q = decode_cgi_obj($q);

my $Plugin_Config = {
    Server                   => undef,
    Username                 => undef,
    Password                 => undef,
    Port                     => 'AUTO',
    USESSL                   => 0,
    AUTH_MODE                => 'BEST',
    Log                      => $DADA::Config::LOGS . '/bounces.txt',
    MessagesAtOnce           => 100,
    Max_Size_Of_Any_Message  => 2621440,
    Allow_Manual_Run         => 1,
    Manual_Run_Passcode      => undef,
    Enable_POP3_File_Locking => 1,
    Plugin_URL               => self_url(),
    Plugin_Name              => 'Bounce Handler',
};

#---------------------------------------------------------------------#
# Nothing else to be configured.                                      #

use Getopt::Long;
use MIME::Entity;

use Fcntl qw(
  O_CREAT
  O_RDWR
  LOCK_EX
  LOCK_NB
);

my $debug = 0;
my $help  = 0;
my $test;
my $server;
my $username;
my $password;
my $verbose = 0;
my $log;
my $messages         = 0;
my $erase_score_card = 0;
my $version;
my $list = undef;
my $admin_list;
my $root_login;

GetOptions(
    "help"             => \$help,
    "test=s"           => \$test,
    "server=s"         => \$server,
    "username=s"       => \$username,
    "password=s"       => \$password,
    "verbose"          => \$verbose,
    "log=s"            => \$log,
    "messages=i"       => \$messages,
    "erase_score_card" => \$erase_score_card,
    "version"          => \$version,
    "list=s"           => \$list,
);

&init_vars;

run()
  unless caller();

sub init_vars {

# DEV: This NEEDS to be in its own module - perhaps DADA::App::PluginHelper or something?

    while ( my $key = each %$Plugin_Config ) {
        if ( exists( $DADA::Config::PLUGIN_CONFIGS->{Bounce_Handler}->{$key} ) ) {
            if (defined($DADA::Config::PLUGIN_CONFIGS->{Bounce_Handler}->{$key})){
                $Plugin_Config->{$key} = $DADA::Config::PLUGIN_CONFIGS->{Bounce_Handler}->{$key};
            }
        }
    }
}

sub init {

    $Plugin_Config->{Server}         = $server   if $server;
    $Plugin_Config->{Username}       = $username if $username;
    $Plugin_Config->{Password}       = $password if $password;
    $Plugin_Config->{Log}            = $log      if $log;
    $Plugin_Config->{MessagesAtOnce} = $messages if $messages > 0;

    if ($test) {
        $debug = 1
          if $test eq 'bounces';
    }

    $verbose = 1
      if $debug == 1;

}

sub run {
    if ( !$ENV{GATEWAY_INTERFACE} ) {
        my $r = cl_main();
        if ( $verbose || $help || $test || $version ) {
            print $r;
        }
        exit;
    }
    else {
        &cgi_main();
    }
}

sub test_sub {
    return "Hello, World!";
}

sub cgi_main {

    if (   keys %{ $q->Vars }
        && $q->param('run')
        && xss_filter( $q->param('run') ) == 1
        && $Plugin_Config->{Allow_Manual_Run} == 1 )
    {
        print cgi_manual_start();
    }
    else {

        ( $admin_list, $root_login ) = check_list_security(
            -cgi_obj  => $q,
            -Function => 'bounce_handler'
        );

        $list = $admin_list;

        my $ls = DADA::MailingList::Settings->new( { -list => $list } );
        my $li = $ls->get();

        my $flavor = $q->param('flavor') || 'cgi_default';
        my %Mode = (

            'cgi_default'                => \&cgi_default,
            'cgi_parse_bounce'           => \&cgi_parse_bounce,
            'cgi_scorecard'              => \&cgi_scorecard,
            'export_scorecard_csv'       => \&export_scorecard_csv, 
            'cgi_bounce_score_search'    => \&cgi_bounce_score_search,
            'cgi_show_plugin_config'     => \&cgi_show_plugin_config,
            'ajax_parse_bounces_results' => \&ajax_parse_bounces_results,
			'manually_enter_bounces'     => \&manually_enter_bounces, 
            'cgi_erase_scorecard'        => \&cgi_erase_scorecard,
            'edit_prefs'                 => \&edit_prefs,
        );

        if ( exists( $Mode{$flavor} ) ) {
            $Mode{$flavor}->();    #call the correct subroutine
        }
        else {
            &cgi_default;
        }
    }
}

sub cgi_default {

    my $ls = DADA::MailingList::Settings->new( { -list => $list } );
    my $li = $ls->get();

    my $done = $q->param('done') || 0;

    my @amount = (
        1,   2,   3,   4,   5,   6,   7,   8,   9,   10,  25,  50,
        100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650,
        700, 750, 800, 850, 900, 950, 1000
    );

    my $bounce_handler_softbounce_score_popup_menu = $q->popup_menu(
        -name    => 'bounce_handler_softbounce_score',
        -values  => [ ( 0 .. 10 ) ],
        -default => $ls->param('bounce_handler_softbounce_score'),
    );

    my $bounce_handler_hardbounce_score_popup_menu = $q->popup_menu(
        -name    => 'bounce_handler_hardbounce_score',
        -values  => [ ( 0 .. 10 ) ],
        -default => $ls->param('bounce_handler_hardbounce_score'),
    );

    my $bounce_handler_decay_score_popup_menu = $q->popup_menu(
        -name    => 'bounce_handler_decay_score',
        -values  => [ ( 0 .. 10 ) ],
        -default => $ls->param('bounce_handler_decay_score'),
    );

    my $bounce_handler_threshold_score_popup_menu = $q->popup_menu(
        -name    => 'bounce_handler_threshold_score',
        -values  => [ ( 0 .. 100 ) ],
        -default => $ls->param('bounce_handler_threshold_score'),
    );

    my $curl_location = `which curl`;
    $curl_location = strip( make_safer($curl_location) );

    my $parse_amount_widget = $q->popup_menu(
        -name     => 'parse_amount',
        -id       => 'parse_amount',
        '-values' => [@amount],
        -default  => $Plugin_Config->{MessagesAtOnce},
        -label    => '',
    );

    my $plugin_configured = 1;
    if (
           !defined( $Plugin_Config->{Server} )
        || !defined( $Plugin_Config->{Username} )
        || !defined( $Plugin_Config->{Password} )

      )
    {
        $plugin_configured = 0;
    }

    require DADA::Template::Widgets;
    my $scrn = DADA::Template::Widgets::wrap_screen(
        {
            -screen         => 'plugins/bounce_handler/default.tmpl',
            -with           => 'admin',
            -expr           => 1,
            -wrapper_params => {
                -Root_Login => $root_login,
                -List       => $list,
            },
            -vars => {

                screen => 'using_bounce_handler',

                MAIL_SETTINGS       => $DADA::Config::MAIL_SETTINGS,
                Username            => $Plugin_Config->{Username},
                Server              => $Plugin_Config->{Server},
                Plugin_URL          => $Plugin_Config->{Plugin_URL},
                Plugin_Name         => $Plugin_Config->{Plugin_Name},
                Allow_Manual_Run    => $Plugin_Config->{Allow_Manual_Run},
                Manual_Run_Passcode => $Plugin_Config->{Manual_Run_Passcode},
                curl_location       => $curl_location,
                plugin_configured   => $plugin_configured,
                parse_amount_widget => $parse_amount_widget,
                done                => $done,
                bounce_handler_softbounce_score_popup_menu =>
                  $bounce_handler_softbounce_score_popup_menu,
                bounce_handler_hardbounce_score_popup_menu =>
                  $bounce_handler_hardbounce_score_popup_menu,
                bounce_handler_decay_score_popup_menu =>
                  $bounce_handler_decay_score_popup_menu,
                bounce_handler_threshold_score_popup_menu =>
                  $bounce_handler_threshold_score_popup_menu,

            },
            -list_settings_vars_param => {
                -list   => $list,
                -dot_it => 1,
            },
        }
    );
    e_print($scrn);
}

sub edit_prefs {

    my $ls = DADA::MailingList::Settings->new( { -list => $list } );
    $ls->save_w_params(
        {
            -associate => $q,
            -settings  => {
                bounce_handler_softbounce_score           => undef,
                bounce_handler_hardbounce_score           => undef,
                bounce_handler_decay_score                => undef,
                bounce_handler_threshold_score            => undef,
                bounce_handler_forward_msgs_to_list_owner => 0,
                bounce_handler_when_threshold_reached     => undef,
            }
        }
    );

    print $q->redirect( -uri => $Plugin_Config->{Plugin_URL} . '?done=1' );
}

sub ajax_parse_bounces_results {

    if ( $q->param('test') ) {
        $test = $q->param('test');
    }
	else { 
		$test = undef; 
	}

    if ( defined( xss_filter( $q->param('parse_amount') ) ) ) {
        $Plugin_Config->{MessagesAtOnce} =
          xss_filter( $q->param('parse_amount') );
    }

    my $r = '';
    $r .= $q->header();
    $r .= '<pre>';
    $r .= cl_main();
    $r .= '</pre>';

    print $r;
}

sub cgi_parse_bounce {

    require DADA::Template::Widgets;
    my $scrn = DADA::Template::Widgets::wrap_screen(
        {
            -screen         => 'plugins/bounce_handler/parse_bounce.tmpl',
            -with           => 'admin',
            -wrapper_params => {
                -Root_Login => $root_login,
                -List       => $list,
            },

            -vars => {
                parse_amount   => xss_filter( $q->param('parse_amount') ),
                test           => xss_filter( $q->param('test') ),
                Plugin_Name    => $Plugin_Config->{Plugin_Name},
                Plugin_URL     => $Plugin_Config->{Plugin_URL},
                MessagesAtOnce => $Plugin_Config->{MessagesAtOnce},
            },
        }
    );
    e_print($scrn);

}

sub cgi_manual_start {

    # This is basically just a wrapper around, cl_main();
    my $r = '';
    if (
        (
            xss_filter( $q->param('passcode') ) eq
            $Plugin_Config->{Manual_Run_Passcode}
        )
        || ( $Plugin_Config->{Manual_Run_Passcode} eq '' )

      )
    {

        my $verbose;
        if ( defined( xss_filter( $q->param('verbose') ) ) ) {
            $verbose = xss_filter( $q->param('verbose') );
        }
        else {
            $verbose = 1;
        }

        if ( defined( xss_filter( $q->param('test') ) ) ) {
            $test = $q->param('test');
        }

        if ( defined( xss_filter( $q->param('messages') ) ) ) {
            $Plugin_Config->{MessagesAtOnce} =
              xss_filter( $q->param('messages') );
        }
        if ( defined( $q->param('list') ) ) {
            $list = $q->param('list');
        }
        else {
            $list = undef;    # just to make that perfectly clear.
        }

        $r .= $q->header();
        if ($verbose) {
            $r .= '<pre>';
            $r .= cl_main();
            $r .= '</pre>';
        }
        else {
            cl_main();
        }
        return $r;

    }
    else {
        $r = $q->header();
        $r .= "$DADA::Config::PROGRAM_NAME $DADA::Config::VER Access Denied.";
    }

    return $r;
}

sub cgi_scorecard {

    my $page = $q->param('page') || 1;

    require DADA::App::BounceHandler::ScoreKeeper;
    my $bsk = DADA::App::BounceHandler::ScoreKeeper->new( { -list => $list } );

    my $num_rows  = $bsk->num_scorecard_rows;
    my $scorecard = $bsk->raw_scorecard(
        {
            -page    => $page,
            -entries => 100,
        }
    );

    my $pager        = undef;
    my $pages_in_set = [];

    require Data::Pageset;
    my $page_info = Data::Pageset->new(
        {
            'total_entries'    => $num_rows,
            'entries_per_page' => 100
            , #$ls->param('tracker_record_view_count'), # needs to be tweakable...
            'current_page' => $page,
            'mode'         => 'slide',    # default fixed
        }
    );

    foreach my $page_num ( @{ $page_info->pages_in_set() } ) {
        if ( $page_num == $page_info->current_page() ) {
            push( @$pages_in_set, { page => $page_num, on_current_page => 1 } );
        }
        else {
            push( @$pages_in_set,
                { page => $page_num, on_current_page => undef } );
        }
    }

    require DADA::Template::Widgets;
    my $scrn = DADA::Template::Widgets::screen(
        {
            -screen => 'plugins/bounce_handler/scorecard.tmpl',
            -vars   => {
                Plugin_URL    => $Plugin_Config->{Plugin_URL},
                Plugin_Name   => $Plugin_Config->{Plugin_Name},
                num_rows      => $num_rows,
                first_page    => $page_info->first_page(),
                last_page     => $page_info->last_page(),
                next_page     => $page_info->next_page(),
                previous_page => $page_info->previous_page(),
                pages_in_set  => $pages_in_set,
                scorecard     => $scorecard,

            }
        }
    );
    print $q->header();
    e_print($scrn);

}




sub export_scorecard_csv {
    require DADA::App::BounceHandler::ScoreKeeper;
    my $bsk = DADA::App::BounceHandler::ScoreKeeper->new( { -list => $list } );
    
    my $header = $q->header(
		-attachment => 'bounce_scorecard-' . $list . '-' . time . '.csv',
		-type       => 'text/csv', 
	);
	print $header;
	
    $bsk->print_csv_scorecard;
}




sub cgi_erase_scorecard {

    require DADA::App::BounceHandler::ScoreKeeper;
    my $bsk = DADA::App::BounceHandler::ScoreKeeper->new( { -list => $list } );
    $bsk->erase;

    print $q->redirect( -uri => $Plugin_Config->{Plugin_URL}, );

}

sub cgi_show_plugin_config {

    my $configs = [];
    for ( sort keys %$Plugin_Config ) {
        if ( $_ eq 'Password' ) {
            push( @$configs, { name => $_, value => '(Not Shown)' } );
        }
        else {
            push( @$configs, { name => $_, value => $Plugin_Config->{$_} } );
        }
    }

    require DADA::Template::Widgets;
    my $scrn = DADA::Template::Widgets::wrap_screen(
        {
            -screen         => 'plugins/bounce_handler/plugin_config.tmpl',
            -with           => 'admin',
            -wrapper_params => {
                -Root_Login => $root_login,
                -List       => $list,
            },
            -vars => {
                Plugin_URL  => $Plugin_Config->{Plugin_URL},
                Plugin_Name => $Plugin_Config->{Plugin_Name},
                configs     => $configs,
            },
        }
    );
    e_print($scrn);
}

sub cgi_bounce_score_search {

    my $query = xss_filter( $q->param('query') );

    my $chrome = 1;
    if ( defined( $q->param('chrome') ) ) {
        $chrome = $q->param('chrome') || 0;
    }

    if ( !defined($query) ) {
        $q->redirect( -uri => $Plugin_Config->{Plugin_URL} );
        return;
    }

    require DADA::App::BounceHandler::Logs;
    my $bhl     = DADA::App::BounceHandler::Logs->new;
    my $results = $bhl->search(
        {
            -query => $query,
            -list  => $list,
            -file  => $Plugin_Config->{Log},
        }
    );
    my $results_found = 0;
    if ( $results->[0] ) {
        $results_found = 1;
        @$results      = reverse(@$results);
    }

    require DADA::MailingList::Subscribers;
    my $lh = DADA::MailingList::Subscribers->new( { -list => $list } );

    my $valid_email        = 0;
    my $subscribed_address = 0;
    if ( DADA::App::Guts::check_for_valid_email($query) == 0 ) {
        $valid_email = 1;
        if ( $lh->check_for_double_email( -Email => $query ) == 1 ) {
            $subscribed_address = 1;
        }
    }

# This is just to add newlines to the values of the diagnostic stuff, so it's not all clumped together:
    for (@$results) {
        for my $pt_diags ( @{ $_->{diagnostics} } ) {
            $pt_diags->{diagnostic_value} =
              encode_html_entities( $pt_diags->{diagnostic_value} );
            $pt_diags->{diagnostic_value} =~ s/(\n|\r)/\<br \/\>\n/g;

        }
    }

    my %tmpl_vars = (
        query              => $query,
        subscribed_address => $subscribed_address,
        valid_email        => $valid_email,
        search_results     => $results,
        results_found      => $results_found,
        S_PROGRAM_URL      => $DADA::Config::S_PROGRAM_URL,
        Plugin_URL         => $Plugin_Config->{Plugin_URL},
        Plugin_Name        => $Plugin_Config->{Plugin_Name},
    );
    require DADA::Template::Widgets;
    my $scrn = '';
    if ( $chrome == 0 ) {
        print $q->header();
        $scrn = DADA::Template::Widgets::screen(
            {
                -screen => 'plugins/bounce_handler/bounce_score_search.tmpl',
                -vars   => { %tmpl_vars, chrome => 0,},
                -list_settings_vars_param => {
                    -list   => $list,
                    -dot_it => 1,
                },
            },

        );
    }
    else {

        $scrn = DADA::Template::Widgets::wrap_screen(
            {
                -screen         => 'bounce_score_search.tmpl',
                -with           => 'admin',
                -wrapper_params => {
                    -Root_Login => $root_login,
                    -List       => $list,
                },
                -vars                     => { %tmpl_vars, },
                -list_settings_vars_param => {
                    -list   => $list,
                    -dot_it => 1,
                },
            }

        );
    }
    e_print($scrn);
}



sub manually_enter_bounces { 
	
	my $process = xss_filter(strip($q->param('process'))) || 0; 
	
	require DADA::Template::Widgets; 
	
	if(! $process ) {  
        my $scrn = DADA::Template::Widgets::wrap_screen(
            {
                -screen         => 'plugins/bounce_handler/manually_enter_bounces.tmpl',
                -with           => 'admin',
                -wrapper_params => {
                    -Root_Login => $root_login,
                    -List       => $list,
                },
                -vars                     => { 
					Plugin_URL => $Plugin_Config->{Plugin_URL},
				},
                -list_settings_vars_param => {
                    -list   => $list,
                    -dot_it => 1,
                },
            }

        );
	    e_print($scrn);	
	}
	else { 
		my $msg = $q->param('msg'); 
		   $msg =~ s/\r\n/\n/g;
		
		my $bh = DADA::App::BounceHandler->new($Plugin_Config);
		my ($found_list, $need_to_delete, $msg_report, $rule_report, $diag ) =
		   $bh->parse_bounce( 
			{ 
				-message => $msg, 
				-test    => 1, 
				-list    => $list, 
			} 
		);
		my $diags_ht = [];
		
		for my $i_d ( keys %$diag ) {
			my $v = encode_html_entities( $diag->{$i_d} ); 
			   $v  =~ s/(\n|\r)/\<br \/\>\n/g;
            push(@$diags_ht, 
				{
					diagnostic_label => $i_d, 
					diagnostic_value => $v , 
				}
			);
        }

	    require DADA::App::BounceHandler::Rules;
	    my $bhr = DADA::App::BounceHandler::Rules->new;
		my $rule = $bhr->rule($diag->{matched_rule}); 
        
		require Data::Dumper; 
        my $scrn = DADA::Template::Widgets::screen(
            {
                -screen         => 'plugins/bounce_handler/manually_enter_bounces_results.tmpl',
                -with           => 'admin',
                -wrapper_params => {
                    -Root_Login => $root_login,
                    -List       => $list,
                },
                -vars                     => { 
					msg_report  => $msg_report, 
					diagnostics =>  $diags_ht, 
					rule_title  => $diag->{matched_rule}, 
					rule        => Data::Dumper::Dumper($rule), 
				},
                -list_settings_vars_param => {
                    -list   => $list,
                    -dot_it => 1,
                },
            }

        );
		print $q->header(); 
	    e_print($scrn);	

	}
}

sub cl_main {

    &init;
    if ( $help == 1 ) {
        return help();
    }
    elsif ($erase_score_card) {
        my $bh = DADA::App::BounceHandler->new($Plugin_Config);
        return $bh->erase_score_card( { -list => $list } );
    }
    elsif ( defined($test) && $test ne 'bounces' ) {
        my $bh = DADA::App::BounceHandler->new($Plugin_Config);
        $bh->test_bounces(
            {
                -test_type => $test,
                -list      => $list
            }
        );
    }
    elsif ( defined($version) ) {
        return version();
    }
    else {

        my $bh = DADA::App::BounceHandler->new($Plugin_Config);
        $bh->parse_all_bounces(
            {
                -list => $list,
                -test => $test,
            }
        );
    }
}

sub help {
    require DADA::Template::Widgets;
    return DADA::Template::Widgets::screen(
        { -screen => 'plugins/bounce_handler/cl_help.tmpl' } );
}

sub version {

    my $r = '';
    $r .= "$Plugin_Config->{Plugin_Name}\n";
    $r .= "$DADA::Config::PROGRAM_NAME Version: $DADA::Config::VER\n";
    $r .= "Perl Version: $]\n\n";

    my @ap = (
        'No sane man will dance. - Cicero ',
        'Be happy. It is a way of being wise.  - Colette',
        'There is more to life than increasing its speed. - Mahatma Gandhi',
        'Life is short. Live it up. - Nikita Khrushchev'
    );

    $r .= "Random Aphorism: " . $ap[ int rand( $#ap + 1 ) ] . "\n\n";
    return $r;

}

sub self_url { 
	my $self_url = $q->url; 
	if($self_url eq 'http://' . $ENV{HTTP_HOST}){ 
			$self_url = $ENV{SCRIPT_URI};
	}
	return $self_url; 	
}


=pod

=head1 Name

Bounce Handler for Dada Mail

=head1 User Guide

For a guide on using Bounce Handler, see the B<Dada Mail Manual>: 

L<http://dadamailproject.com/pro_dada/using_bounce_handler.html>

For more information on Pro Dada/Dada Mail Manual: 

L<http://dadamailproject.com/purchase/pro.html>

=head1 Description

Bounce Handler intelligently handles bounces from Dada Mail list messages.

Messages sent to subscribers of your mailing list that bounce back will be directed to the B<List Administrator Address>. This email account is then checked periodically by Bounce Handler. 

Bounce Handler then reads awaiting messages and B<parses> the messages in an attempt to understand why the message has bounced. 

The B<parsed> message will then be B<examined> and an B<action> will be taken. 

The usual action that is taken is to apply a B<score> to the email address that has bounced the message. Once the B<Score Threshold> is reached, the email address is unsubscribed from the mailing list. 

=head1 Obtaining a Copy of the Plugin

Bounce Handler is located in the, I<dada/plugins> directory of the main Dada Mail distribution, under the name, B<bounce_handler.cgi>

=head1 Requirements

Please make sure you have these requirements before installing this plugin: 

=over

=item * A POP3 Email Account

Bounce Handler works by checking a email address via POP3. (IMAP is currently not supported).  

You will need to create a new email address account for Bounce Handler to utilize. 

Example: create B<bounces@yourdomain.com>, where, I<yourdomain.com> is the name of the domain Dada Mail is installed on. 

Guidelines on this address: 

=over

=item * Do NOT use this address for anything except Bounce Handler

No one will be checking this POP3 account via a mail reader.

Doing so won't break Dada Mail, but it will stop Bounce Handler from working correctly, if when checking messages, your mail reader then removes those messages from the POP3 account.  If you do need to periodically check this inbox, make sure to have your mail reader set to B<not> automatically remove the messages. 

=item * The email address MUST belong to the domain you have Dada Mail installed

Meaning, if your domain is, "yourdomain.com", the bounce email address should be something like, "bounces@yourdomain.com". In other words, do not use a Yahoo! Gmail, or Hotmail account for your bounce address. This will most likely disrupt all regular mail sending in Dada Mail. 

=item * Bounce Handler MUST be able to check the POP3 account

Check to make sure that the POP3 server (usually, port 110) is not blocked from requests coming from your hosting account server.  

=back

=back

=head1 Recommended

These points are not required, but recommended to use Bounce Handler:

=over

=item * Ability to set Cron Jobs. 

Bounce Handler can be configured to run automatically by using a cronjob.

If you do not know how to set up a cronjob, attempting to set one up for Dada Mail will result in much aggravation. Please read up on the topic before attempting! 

=back

=head1 Installation

This plugin can be installed during a Dada Mail install/upgrade, using the included installer that comes with Dada Mail. The below installation instructions go through how to install the plugin B<manually>. We suggest using the Dada Mail Installer. 

If you do install this way, note that you still have to create the create the Bounce Handler email account as well set the cronjob. Both are covered below. 

=head1 Lightning Configuration/Installation Instructions 

=over

=item * Create the bounce handler email account

=item * Configure your mailing list to use this email address for its, "List Administrator Address"

Set this email address as our "List Administrator Address" in the list control panel, under,

B<Your Mailing List - List Information> 

=item * Configure the plugin in your .dada_config file

(covered below)

=item * chmod 755 the bounce_handler.cgi script

=item * visit the plugin via a web browser. 

=item * Set the cronjob (optional)

=back

=head1 Screencasts

=head2 Part 1 

L<https://www.youtube.com/watch?v=tvdIj1s19Vo>

=head2 Part 2

L<https://www.youtube.com/watch?v=CnsM994xa7A>

=head1 Configuration

There's a few things you need to configure for this plugin. Configure the plugin variables in your C<.dada_config> file (not in the plugin itself!)

=head3 POP3 Server Information. 

Create a new POP3 email account. This email account will be the address that
bounced messages will be delivered to. 

Open up your C<.dada_config> file for editing. 

Search and see if the following lines are present: 

 # start cut for plugin configs
 =cut

 =cut
 # end cut for plugin configs

If they are present, remove them. 

You can then configure the plugin variables on these lines: 

	Bounce_Handler => { 
	
	    Server                    			=> undef, 
	    Username                  			=> undef, 
	    Password                  			=> undef, 
	    # etc.
	},
	
For example: 

Bounce_Handler => { 
	
		Server                    			=> 'mail.yourdomain.com', 
		Username                  			=> 'bounces+yourdomain.com', 
		Password                  			=> 'password', 
	    # etc.
},


=head2 Set this address as the default List Administration Email Address

You may also want to set a default value for the, List Adminstration Email, so that all new lists already have Bounce Handler enabled. 

Find this chunk of lines in your C<.dada_config> file: 

	# start cut for list settings defaults
	=cut
	
	%LIST_SETUP_INCLUDE = (
		set_smtp_sender              => 1, # For SMTP   
		add_sendmail_f_flag          => 1, # For Sendmail Command
		admin_email                  => 'bounces@example.com',
	);
	
	=cut
	# end cut for list settings defaults

Remove the =cut lines, similar to before: 

	# start cut for list settings defaults
	=cut

	=cut
	# end cut for list settings defaults

And then change the, C<admin_email> to your bounce handler email address: 


	%LIST_SETUP_INCLUDE = (
		set_smtp_sender              => 1, # For SMTP   
		add_sendmail_f_flag          => 1, # For Sendmail Command
		admin_email                  => 'bounces@yourdomain.com',
	);

=head2 List Control Panel Menu

Now, edit your C<.dada_config> file, so that it shows Bounce Handler in the left-hand menu, under the, B<Plugins> heading: 

First, see if the following lines are present in your C<.dada_config> file: 

 # start cut for list control panel menu
 =cut

 =cut
 # end cut for list control panel menu

If they are, remove them. 

Then, find these lines: 


 #					{-Title      => 'Bounce Handler',
 #					 -Title_URL  => $PLUGIN_URL."/bounce_handler.cgi",
 #					 -Function   => 'bounce_handler',
 #					 -Activated  => 1,
 #					},

Uncomment the lines, by taking off the, "#"'s: 

 					{-Title      => 'Bounce Handler',
 					 -Title_URL  => $PLUGIN_URL."/bounce_handler.cgi",
 					 -Function   => 'bounce_handler',
 					 -Activated  => 1,
 					},

Save your C<.dada_config> file.


=head2 Telling Dada Mail to use Bounce Handler. 

You're going to have to tell Dada Mail explicitly that you want
bounces to go to the bounce handler. The first step is to set the 
B<Dada List Administrator> to your bounce email address. You'll set this per mailing list in the each mailing list's control panel, under 

B<Your Mailing List -  List Information>

After that, you'll need to configure outgoing email messages to set the B<Dada List Administrator> address in the C<Return-Path> header. Sounds scary, but it's easy enough.  

=head3 If you're using th sendmail command: 

In the list control panel, go to B<Mail Sending - Sending Options> and 
check: B<Add the Sendmail '-f' flag when sending messages ...>

This I<should> set the sending to the admin email, and in turn, set the
B<Return-Path> header. Dada Mail is shipped to have this option set by default. 

=head3 If you're using SMTP sending: 

In the list control panel, go to: B<Mail Sending - Sending Options>
and check the box labeled: B<Set the Sender of SMTP mailings to the 
list administration email address>  Dada Mail is shipped to have this option set by default. 

=head3 If you're using Amazon SES: 

Dada Mail will automatically have bounces go to the List Administration Address when using Amazon SES. Make sure before you configure any of the above that you Verify this email address, just like you would a Amazon SES Sender. If you do not, your messages sent through Dada Mail will not be delivered.

=head2 Testing

To test out any of these configurations, Send yourself a test message through Dada Mail
and view the source of the message itself, in your mail reader. In the
mail headers, you should see the B<Return-Path> header: 


 Return-Path: <dadabounce@myhost.com>
 Delivered-To: justin@myhost.com
 Received: (qmail 75721 invoked from network); 12 May 2003 04:50:01 -0000
 Received: from myhost.com (208.10.44.140)
   by hedwig.myhost.com with SMTP; 12 May 2003 04:50:01 -0000
 Date:Sun, 11 May 2003 23:50:01 -0500
 From:justin <justin@myhost.com>
 Subject:Test, Test, Test
 To:justin@myhost.com
 Sender:dadabounce@myhost.com
 Reply-To:justin <justin@myhost.com>
 Precedence:list
 Content-type:text/plain; charset=iso-8859-1

The first line has the B<Return-Path> header should have the Bounce Handler Email set: 

	Return-Path: <dadabounce@myhost.com>

In this example, my List Owner address, B<justin@myhost.com> still occupies the C<To:> and C<Reply-To headers>, so whoever replies to my message will reply to me, I<not> Bounce Handler.

=head1 Configuring the Cronjob to Automatically Run Bounce Handler

We're going to assume that you already know how to set up the actual cronjob, 
but we'll be explaining in depth on what the cronjob you need to set B<is>.

=head2 Setting the cronjob via curl

Generally, setting the cronjob to have Bounce Handler run automatically, just 
means that you have to have a cronjob access a specific URL (via a utility, like curl). The URL looks something like this: 

 http://example.com/cgi-bin/dada/plugins/bounce_handler.cgi?run=1&verbose=1

Where, L<http://example.com/cgi-bin/dada/plugins/bounce_handler.cgi> is the URL to your copy of C<bounce_handler.cgi>

You'll see the specific URL used for your installation of Dada Mail in the web-based control panel for Bounce Handler, under the fieldset legend, B<Manually Run Bounce Handler>, under the heading, B<Manual Run URL:>

This will have Bounce Handler check any awaiting messages. 

A I<Pretty Good Guess> of what the entire cronjob should be set to is located 
in the web-based crontrol panel for Bounce Handler, under the fieldset legend, B<Manually Run Bounce Handler>, under the heading, B<curl command example (for a cronjob):>

=head3 Customizing your cronjob with added parameters

=head4 passcode

Since anyone (or anything) can run your Bounce Handler, by following that same URL, (C<http://example.com/cgi-bin/dada/plugins/bounce_handler.cgi?run=1&verbose=1>), you can set up a simple B<Passcode>, to have some semblence of security over who runs the program. 

Set a B<passcode> in Bounce Handler's Config variable, B<Manual_Run_Passcode>. This is done in your C<.dada_config> file - the same place the B<mail server>, B<username> and B<password> were set. Find the lines in your C<.dada_config> file that look like this: 

	$PLUGIN_CONFIGS = { 
	
		Bounce_Handler => {
			Server                      => 'mail.yourdomain.com', 
			Username                    => 'bounces+yourdomain.com', 
			Password                    => 'password', 
			Port                        => undef,
			USESSL                      => undef,
			AUTH_MODE                   => undef,
			Plugin_Name                 => undef,
			Plugin_URL                  => undef,
			Allow_Manual_Run            => undef,
			Manual_Run_Passcode         => undef,
			Enable_POP3_File_Locking    => undef, 
			Log                         => undef,
			MessagesAtOnce              => undef,
			Max_Size_Of_Any_Message     => undef,
			Rules                       => undef,
			
		},

Find the config parameter named, B<Manual_Run_Passcode> and set it to whatever you'd like this Passcode to be: 

		Manual_Run_Passcode         => 'sneaky',

Then change the URL to include this passcode. In our examples, it would then look like this: 

 http://example.com/cgi-bin/dada/plugins/bounce_handler.cgi?run=1&passcode=sneaky

The example cronjob for curl in Bounce Handler's list control panel should also update use the new passcode. 

=head3 messages

Sets how many messages should be checked and parsed in one execution of the program. Example: 

 http://example.com/cgi-bin/dada/plugins/bounce_handler.cgi?run=1&messages=10

=head3 verbose

When set to, B<1>, you'll receive the a report of how Bounce Handler is doing parsing and adding scores (and what not). This is sometimes not so desired, especially in a cron environment, since all this informaiton will be emailed to you (or someone) everytime the script is run.

If you set B<verbose> to, "0", under normal operation, Bounce Handler won't show any output, but if there's a server error, you'll receive an email about it. This is probably a good thing. Example (for cronjob-run curl command): 

 * * * * * /usr/local/bin/curl -s --get --data run=1\;verbose=0 --url http://example.com/cgi-bin/dada/plugins/bounce_handler.cgi

=head3 test

Runs Bounce Handler in test mode by checking the bounces and parsing them, but not actually carrying out any rules (no scores added, no email addresses unsubscribed). 

=head1 Command Line Interface

There's a slew of optional arguments you can give to this script. To use Bounce Handler via the command line, first change into the directory that Bounce Handler resides in, and issue the command: 

 ./bounce_handler.cgi --help

For a full list of parameters. 

You may set the cronjob via the command line interface, rather than the web-based way. You may run into file permission problems when running it this way, depending on your server setup. 

=head2 Command Line Interface for Cronjobs: 

The secret is to actually have two commands in one. The first command changes into the same directory as the C<bounce_handler.cgi> script, the second invokes the script with the parameters you'd like. 

For example: 

 */5 * * * * cd /home/myaccount/cgi-bin/dada/plugins; /usr/bin/perl ./bounce_handler.cgi  >/dev/null 2>&1

Where, I</home/myaccount/cgi-bin/dada/plugins> is the full path to the directory the C<dada_bounc_handler.pl> script resides.

=head1 Plugin Configs

These plugin configs are located in your C<.dada_config> file, as mentioned above. 

=head2 Server, Username, Password

These configs need to be set, to hook Bounce Handler to the email address you want the bounce messages to go. 

=head2 Port

Defaults to: B<110> for regular connections, C<995> for SSL connections. 

Sets the B<port> Bounce Handler uses connect to the POP server. 

=head2 USESSL

Defaults to: B<0>. Set to, B<1>, if you'd like (and can) connect to the POP server with an SSL connection.

=head2 AUTH_MODE

Defaults to: B<BEST>

Allowed parameters: B<BEST>, B<PASS>, B<APOP>, B<CRAM-MD5>. 

If the default of, B<BEST> isn't working, try the various allowed parameters. B<PASS> passes the POP3 password in cleartext. 

=over

=item * BEST

Tries, B<APOP>, B<CRAM-MD5> and B<PASS> modes, in that order of availability. 

=back

=head2 Plugin_Name

The name of this plugin. 

Defaults to: B<Bounce Handler>

=head2 Plugin_URL

The URL of the plugin. This is usually figured out by default, but if it's not (you'll know, as links are broken in the plugin and nothing seems to work) you may have to set this, manually. 

=head2 Allow_Manual_Run

Defaults to B<1> (enabled)

Sets whether you may use the B<manual run URL> to run Bounce Handler. The manual run URL is what the curl-powered cronjob uses. If you want to disable this method, set this config variable to, B<0>

=head2 Manual_Run_Passcode

This is covered above, under, B<passcode> 

=head2 Enable_POP3_File_Locking

Defaults to B<1> 

When enabled, Bounce Handler will use a lock file to make sure only one connection to the POP server is done at one time. Disable this by setting this parameter to, B<0>. 

=head2 Log

Sets the path to the logfile Bounce Handler creates. Defaults to:
 C<bounces.txt> in your C<.dada_files/.logs> directory. 

=head2 MessagesAtOnce

Sets how many messages are checke, per running of the plugin. 

Defaults to: B<100>

Since there could be many bounce messages awaiting to be checked, there is a limit that's set on how many mesages are looked at, at one time. This also means that it may take a few runnings of the plugin to clear all the awaiting messages. 

=head3 Max_Size_Of_Any_Message

Defaults to: B<2,621,440> bytes (2.5 megs). Set in, B<octets>

Sets the maximum size of any bounced message that Bounce Handler will deal with. Anything larger than this will simply be ignored and deleted. 


=head1 More on Scores, Thresholds, etc

By default, Bounce Handler assigns a particular score to each email address that bounces back a message. These scores are tallied each time an email address bounces a message.

Since Dada Mail understands the differences between B<Hard Bounces> and B<Soft Bounces>, it'll append a smaller score for soft bounces, and a larger score for hard bounces. There's also a B<Decay Rate>, an amount that all scores are decreased by, every time a mass mailing is sent out.

Once the email address's B<Bounce Score> reaches the B<Threshold>, the email address is then removed from the list. 

=head1 Special Debugging Mode
 
=head2 manually_enter_bounces

Visit the plugin with the following query string, 

L<http://example.com/cgi-bin/dada/plugins/bounce_handler.cgi?flavor=manually_enter_bounces>

(C<manually_enter_bounces>) to enter a special debugging mode, where you can just paste in the source of a bounce message, 
and see how Bounce Handler will handle it, without actually processing the message. 

=head1 FAQs

=head2 Bounce Email Address

=head3 Do you use only one Bounce Email Address  for all the mailing lists? 

Yes. 

Even though there's only one Bounce Email Address, it is used by all the mailing lists of your Dada Mail, but Bounce Handler will work with every mailing list I<individually>. Each mailing list also has a separate Bounce Scorecard. 

=head1 Introduction to Bounce Handler Rules

Bounce Handler Rules are what's used when the bounced message is parsed and examined. They're a set of things to look for, and match, in an attempt to figure out what type of bounced message was given back. 

An example Rule: 

     {
        exim_user_unknown => { 
            Examine => { 
                Message_Fields => { 
                    Status      => [qw(5.x.y)], 
                    Guessed_MTA => [qw(Exim)],  
                }, 
                Data => { 
                    Email       => 'is_valid',
                    List        => 'is_valid', 
                }
            },
                Action => { 
                     add_to_score => 'hardbounce_score',
                }, 
            }
    }, 

B<exim_user_unknown> is the title of the rule -  just a label, nothing else.

B<Examine> holds a set of parameters that the handler looks at when
trying to figure out what to do with a bounced message. This example
has a B<Message_Fields> entry and inside that, a B<Status> entry. The
B<Status> entry holds a list of status codes. The ones in shown there
all correspond to hard bounces; the mailbox probably doesn't exist. 

B<Message_Fields> also hold a, B<Guessed_MTA> entry - it's explicitly looking for a bounce back from the, I<Exim> mail server. 

B<Examine> also holds a B<Data> entry, which holds the B<Email> or B<List> 
entries, or both. Their values are either 'is_valid', or 'is_invalid'. 

So, to sum this all up, this rule will match a message that has B<Status:> 
B<Message Field> contaning a user unknown error code, B<(5.1.1, etc)> and also a B<Guessed_MTA> B<Message Field> containing, B<Exim>. The message
also has to be parsed to have found a valid email and list name. 

If this all matches, the B<Action> is... acted upon. In this case, the offending email address will be appended a, B<Bounce Score> of,
 whatever, B<hardbounce_score> is, which by is default, B<4>. 

If you would like to have the bounced address automatically removed, without any sort of scoring happening, change the B<action> from,

    add_to_score => 'hardbounce_score',

to: 

    unsubscribe_bounced_email => 'from_list'

Also, changing B<from_list>, to B<from_all_lists> will do the trick. 

Here's a schematic of all the different things you can do: 

 {
 rule_name => {
	 Examine => {
		Message_Fields => {
			Status               => qw([    ]), 
			Last-Attempt-Date    => qw([    ]), 
			Action               => qw([    ]), 
			Status               => qw([    ]), 
			Diagnostic-Code      => qw([    ]), 
			Final-Recipient      => qw([    ]), 
			Remote-MTA           => qw([    ]), 
			# etc, etc, etc
			
		},
		Data => { 
			Email => 'is_valid' | 'is_invalid' 
			List  => 'is_valid' | 'is_invalid' 
		}
	},
	Action => { 
	           add_to_score             =>  $x, # where, "$x" is a number
			   unsubscribe_bounced_email => 'from_list' | 'from_all_lists',
	},
 },	

Rules also support the use of regular expressions for matching any of the B<Message_Fields>. 

To tell the parser that you're using a regular expression, make the Message_Field key end in '_regex': 

 'Final-Recipient_regex' => [(qr/RFC822/)], 

=head2 Customizing Bounce Handler Rules

The default set of Bounce Handler Rules can be found at,

I<dada/data/bounce_handler_rules.pl>

Bounce Handler will also look for a copy of this file in your

I<.dada_files/.configs>

directory, which you can then customize with your own rules. When Dada Mail is upgrading, your customizations will then not be lost. 

=head1 COPYRIGHT

Copyright (c) 1999 - 2014 Justin Simoni 
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

Parts of this script were swiped from Mail::Bounce::Qmail module, fetched from here: 

http://mikoto.sapporo.iij.ad.jp/cgi-bin/cvsweb.cgi/fmlsrc/fml/lib/Mail/Bounce/Qmail.pm

The copyright of that code stated: 

Copyright (C) 2001,2002,2003 Ken'ichi Fukamachi
All rights reserved. This program is free software; you can
redistribute it and/or modify it under the same terms as Perl itself.

Thanks Ken'ichi

=cut
