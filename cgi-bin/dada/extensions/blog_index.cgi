#!/usr/bin/perl 
use strict;

use FindBin;
use lib "$FindBin::Bin/../";
use lib "$FindBin::Bin/../DADA/perllib";

BEGIN { 
	my $b__dir = ( getpwuid($>) )[7].'/perl';
    push @INC,$b__dir.'5/lib/perl5',$b__dir.'5/lib/perl5/x86_64-linux-thread-multi',$b__dir.'lib',map { $b__dir . $_ } @INC;
}

use DADA::Config 7.0.0;

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


my $Plugin_Config = {};
$Plugin_Config->{Default_List}       = undef;
$Plugin_Config->{Entries}            = undef;
$Plugin_Config->{Style}              = 'full';
$Plugin_Config->{Allow_QS_Overrides} = 1;

use CGI;
use Try::Tiny;

use DADA::App::Guts;
use DADA::MailingList::Settings;
use DADA::MailingList::Archives;
use DADA::App::ScreenCache;
my $c = DADA::App::ScreenCache->new;

&init_vars;
&main;

sub init_vars {

# DEV: This NEEDS to be in its own module - perhaps DADA::App::PluginHelper or something?

    while ( my $key = each %$Plugin_Config ) {

        if ( exists( $DADA::Config::PLUGIN_CONFIGS->{blog_index}->{$key} ) ) {

            if (
                defined( $DADA::Config::PLUGIN_CONFIGS->{blog_index}->{$key} ) )
            {

                $Plugin_Config->{$key} =
                  $DADA::Config::PLUGIN_CONFIGS->{blog_index}->{$key};

            }
        }
    }
}

sub main {

    my $q = CGI->new;
    $q->charset($DADA::Config::HTML_CHARSET);

    $q = decode_cgi_obj($q);
    my $mode = 'js';
    if ( $q->param('mode') ) {
        $mode = $q->param('mode');
    }

    my $list = $Plugin_Config->{Default_List};
    if ( $q->param('list') ) {
        $list = xss_filter( $q->param('list') );
    }

    if ( $Plugin_Config->{Allow_QS_Overrides} == 1 ) {

        if ( $q->param('entries') ) {
            $Plugin_Config->{Entries} = xss_filter( $q->param('entries') );
        }
        if ( $q->param('style') ) {
            $Plugin_Config->{Style} = xss_filter( $q->param('style') );
            if (   $Plugin_Config->{Style} ne 'blurb'
                && $Plugin_Config->{Style} ne 'full' )
            {
                $Plugin_Config->{Style} = 'full';
            }
        }
    }

    my $ls = DADA::MailingList::Settings->new( { -list => $list } );
    my $ah = DADA::MailingList::Archives->new( { -list => $list } );
    my $entries = $ah->get_archive_entries();

    my $amount;
    if ( defined( $Plugin_Config->{Entries} )
        && $Plugin_Config->{Entries} >= 1 )
    {
        $amount = int( $Plugin_Config->{Entries} - 1 );
    }
    else {
        $amount = $ls->param('archive_index_count');
    }

    if ( $amount > $#$entries ) {
        $amount = $#$entries;
    }

    my $cache_filename =
        $list
      . '.blog_index.'
      . $Plugin_Config->{Style} . '.'
      . $amount . '.'
      . $mode . '.scrn';
    if ( $c->cached($cache_filename) ) {
        $c->show($cache_filename);
        return;
    }







    my @archive_entries = ();

    my $i = 0;
    for ( $i = 0 ; $i <= $amount ; $i++ ) {

        my $entry = $entries->[$i];

        my ( $subject, $message, $format, $raw_msg ) =
          $ah->get_archive_info($entry);

        # ?
        my $pretty_subject = $ah->_parse_in_list_info( -data => $subject );

        $pretty_subject = pretty($pretty_subject);

        my $pretty_date = date_this(
            -Packed_Date   => $entry,
            -Write_Month   => $ls->param('archive_show_month'),
            -Write_Day     => $ls->param('archive_show_day'),
            -Write_Year    => $ls->param('archive_show_year'),
            -Write_H_And_M => $ls->param('archive_show_hour_and_minute'),
            -Write_Second  => $ls->param('archive_show_second'),
        );

        my $from_email = find_from_whom($raw_msg)
          || $ls->param('list_owner_email');

        my $massaged_message_for_display;
        if ( $Plugin_Config->{Style} eq 'blurb' ) {

            $massaged_message_for_display =
              $ah->message_blurb( -key => $entry ),
              ;
        }
        elsif ( $Plugin_Config->{Style} eq 'full' ) {

            my $content_type;

            ( $massaged_message_for_display, $content_type ) =
              $ah->massaged_msg_for_display({ -key => $entry, -body_only => 1 });

        }
        else {
            die 'Unsupported $Plugin_Config->{Style} type!';
        }

        push(
            @archive_entries,
            {
                pretty_subject => $pretty_subject,
                $subject       => $subject,
                pretty_date    => $pretty_date,
                message        => $massaged_message_for_display,
                PROGRAM_URL    => $DADA::Config::PROGRAM_URL,
                list           => $list,
                message_id     => $entry,

                'list_settings.enable_gravatars' =>
                  $ls->param('enable_gravatars'),
                can_use_gravatar_url => can_use_gravatar_url(),
                gravatar_img_url     => gravatar_img_url(
                    {
                        -email => $from_email,
                        -size  => '80',
                        -default_gravatar_url =>
                          $ls->param('default_gravatar_url'),
                    }
                ),

                blurb_style => ( $Plugin_Config->{Style} eq 'blurb' ) ? 1 : 0,

            }
        );

    }

    my $scrn;

    require DADA::Template::Widgets;

    $scrn = DADA::Template::Widgets::screen(
        {
            -screen => 'extensions/blog_index/blog_index.tmpl',
            -vars   => {

                list            => $list,
                archive_entries => \@archive_entries,

                PROGRAM_URL => $DADA::Config::PROGRAM_URL,
                list        => $list,

                #message_id     => $entry,
                blurb_style => ( $Plugin_Config->{Style} eq 'blurb' ) ? 1 : 0,

            },
            -list_settings_vars => {
                -list   => $list,
                -dot_it => 1,

            }
        }
    );

    if ( $mode eq 'js' ) {

        $scrn = "document.write('" . js_enc($scrn) . "');";
        $scrn = $q->header('text/javascript') . $scrn;
        e_print($scrn);
    }
    elsif ( $mode eq 'html' ) {
        $scrn = $q->header() . $scrn;
        e_print($scrn);
    }

    $c->cache($cache_filename, \$scrn);

}

sub can_use_gravatar_url {

    my $can_use_gravatar_url = 1;
    try {
        require Gravatar::URL;
    }
    catch {
        $can_use_gravatar_url = 0;
    };
    return $can_use_gravatar_url;
}

sub find_from_whom {
    my $raw_msg = shift;
    return undef if !defined $raw_msg;

    my $from_address = undef;
    try {
        require MIME::Parser;
        my $parser = new MIME::Parser;
        $parser = optimize_mime_parser($parser);
        my $entity = $parser->parse_data($raw_msg);
        my $orig_header_from;
        if ( $orig_header_from = $entity->head->get( 'From', 0 ) ) {
            require Email::Address;
            $from_address =
              ( Email::Address->parse($orig_header_from) )[0]->address;
        }

    }
    catch {
        return undef;
    };
    return $from_address;
}

=pod

=head1 NAME

blog_index.cgi - A simple blog-style view of your list's archived messages

=head1 DESCRIPTION

This small extension script prints out the last, B<x> archived messages, in a blog-style fashion, with the text of all the archived messages shown on one screen. You can then embed this into a page you may have on your site, either by calling the extension like a Javascript library, or calling it as an old-school Apache Server Side Include. 

In a pinch, you can then use Dada Mail in a more blog-like manner, by creating new entries to your Dada Mail-powered blog by creating new archive messages: 

In Dada Mail's, "Send a Message" screen, there's a fieldset labeled, B<Archive Options>. Expanding this fieldset will reveal options to, B<Archive, but DO NOT Send> the message you're creating and also an option to B<Backdate> the entry. This will allow you to add new entries to your list's archives, without having to send the messages out to your subscribers. 

One thing I find useful is to have my blog powered by Dada Mail: I can make new entries more frequently, but just archive and not sending - much more frequently than I feel comfortable sending to my entire list, but have all the entries available on my blog. That way, my mailing list gets the more important messages sent and if I want to get a bit chatty, I can, without deluging my list with messages they may not want to have fill up their inbox. 

This simple extension does not support some of the more familiar blog-like things, such as commenting on an entry, but does provide other features. Since Dada Mail already supports RSS/Atom feeds for its archived messages, your blog powered by Dada Mail does as well. The core of Dada Mail also supports full text searching of archived messages. 

For a simple site where a blog is just one part of the entire site, such simplicity may be all you really need. 


=head1 USAGE

=head2 Use it like a CGI script. 

Put it in your, B<extensions> directory (ala: cgi-bin/dada/extensions), chmod 755, visit it in your web browser. 

=head2 As a Javascript Library

To add this form to your HTML page, just add a line that looks like this: 
	
	<script type="text/javascript" src="http://example.com/cgi-bin/dada/extensions/blog_index.cgi"></script> 

Where, I<http://example.com/cgi-bin/dada/extensions/blog_index.cgi> is the URL to this extension. 

=head2 As a Server Side Include

You can also call it as a server side include, like this: 

  <!--#include virtual="/cgi-bin/dada/blog_index?mode=html" -->

Make sure to add the query string, C<mode=html>

=head2 By Itself

Not really a method, but you can view the HTML and Javascript produced by visiting the extension in your web browser, with the same query string you use for the Server Side Include: 

L<http://example.com/cgi-bin/dada/blog_index.cgi?mode=html>

=head2 By Copying the HTML/Javascript

You could also try just copying the source that this script produces from the URL above, and paste it into a page/script/etc that you'd like. 

Probably not the best idea, but I'll throw that idea for ya. 

=head1 CONFIGURATION

There's no configuration that you are B<required> to do, but there's many things that you B<can> do. We'll try to cover everything: 

=head2 $Plugin_Config->{Default_List} 

This extension currently shows B<one> list's archives at one time - there's no collating of archive entries from different lists, or anything. 

The, C<Default_List> config variable holds what the default list can be. Set it to a list's shortname:

 $Plugin_Config->{Default_List}  = 'mylistshortname';

If no list is set, you will need to tack on a query string to the end of the script, when you call it: 

 http://example.com/cgi-bin/dada/extensions/blog_index.cgi?list=mylistshortname

In this example, C<mylistshortname> is your list's shortname and: 

 ?list=mylistshortname

Is the entire query string you'll have to tack on. 

If you've configured this variable incorrectly, you'll most likely receive an error in your web browser, so take care in setting it correctly. 

=head1 DIAGNOSTICS

None, really.

=head1 CONFIGURATION AND ENVIRONMENT

There are a few variables at the top of the script that will need to be changed. They are: 

=over

=item * $Plugin_Config{Default_List}

B<Required> 

You'll need to set B<$Plugin_Config{Default_List}> to a valid list shortname that you would like to use for your blog index. 

=item * $Plugin_Config{Entries}

B<Optional> 

B<$Plugin_Config{Entries}> holds the count of how many archived messages you'd like shown at once. If set to C<undef> or a number below, B<1>, this extension will use the default value set in the B<Manage Archives - Archive Options - Advanced> list control panel screen (which itself defaults to, B<10>. 

=item * $Plugin_Config{Style}

B<Optional> 

Currently, there are two styles supported when showing the archived messages, B<full> and, B<blurb>

If this variable is set to, B<full>, the entire archived message will be shown. 

If this variable is set to, B<blurb>, only the first few words (basically) will be shown and a link to the rest will be provided. 

=item * Allow_QS_Overrides

B<Optional> 

If set to, C<1> you're allowed to set the C<style> and C<entries> configurations in the query string, like this: 

 http://example.com/cgi-bin/dada/extensions/blog_index.cgi?list=mylistshortname&entries=10&style=full

C<entries> corresponds to, <$Plugin_Config{Entries}>

C<style> corresponds to, <$Plugin_Config{Style}>

=item * $Plugin_Config{Template}

B<Optional> 

This variable holds the embedded template for the actual HTML to display. If you'd like to change the design of the HTML that's outputting, here's the place to do it. 

The Template is written in the HTML::Template system, just like much of the rest of Dada Mail. 

Some of the variables that are available: 

=over

=item * archive_entries

This holds all the archived entries that are to be displayed. You'll most likely want to call it in a loop: 

 <!-- tmpl_loop archive_entries --> 
    ...
 <!--/tmp_loop> 

You can also use it to check the existance of entries available: 

 <!-- tmpl_unless archive_entries --> 
    Currently, there are no archived entries! 
 <!--/tmpl_unless--> 

When you're looping over all the archived messages, other variables will be available to you, inside the loop: 

=over

=item * pretty_subject

"pretty-fied" version of the subject. If you want the raw subject, use the C<subject> variable. 

=item * pretty_date

"pretty-fied" version of the date the message was posted on. Should be following the formatting options you've set in: B<Manage Archive - Archive Options - Advanced>

=item * blurb_style

Is set to, B<1> if you're using the, B<blurb> style in, C<$Plugin_Config->{Style}>. 

=item * message

Will hold the actual email message body. If you're using the, B<full> style, the message will already be converted to HTML (if needed) and massaged in a way that it'll look really well without any help. 

If you're using the B<blurb> style, the message will be a plaintext string, with all HTML encoding stripped. 

=item * PROGRAM_URL

Holds the URL to your Dada Mail Installation 

=item * list

Holds the value that you've set in, B<$List> 

=item * message_id

Holds the B<message_id> that's associated with the archived message. 

=back

=item * list 

Holds the value that you've set in, B<$List> 

(This is also available to you, B<outside> of the C<archive_entries> loop. 

=item * PROGRAM_URL

Holds the URL to your Dada Mail Installation 

(This is also available to you, B<outside> of the C<archive_entries> loop. 


=back


=back

=head1 SEE ALSO

Dada Mail also can share its archives using its built-in RSS/Atom feeds. In your list control panel, go to: 

B<Manage Archive - Archive Options - Advanced>

=head1 DEPENDENCIES

=head1 INCOMPATIBILITIES

=head1 BUGS AND LIMITATIONS

Currently, this extension is simple, and only handles one list at a time. 

If this extension becomes popular, I may give it the capability to handle all lists and at the same time, as well as have some of the more interesting archive capabilities support (embedded attachments, etc) 

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

