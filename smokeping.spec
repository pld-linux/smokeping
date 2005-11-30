Summary:	Smokeping - a latency grapher that uses rrdtool
Summary(pl):	Smokeping - narzêdzie do tworzenia wykresów opó¼nieñ sieci
Name:		smokeping
Version:	2.0.5
Release:	0.2
License:	GPL v2
Group:		Networking/Utilities
Source0:	http://people.ee.ethz.ch/~oetiker/webtools/smokeping/pub/%{name}-%{version}.tar.gz
# Source0-md5:	c965439c147012b91585c3e134225b4d
Source1:	%{name}.init
Source2:	%{name}.conf
Source3:	%{name}-config
URL:		http://people.ee.ethz.ch/~oetiker/webtools/smokeping/
BuildRequires:	perl-tools-pod
BuildRequires:	rrdtool
BuildRequires:	sed >= 4.0
PreReq:		rc-scripts
Requires(post,preun):	/sbin/chkconfig
Requires:	fping
Requires:	perl-base
Requires:	perl-rrdtool
Requires:	rrdtool >= 1.2
Requires:	webserver
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_wwwconfdir	/etc/httpd/httpd.conf
%define		_cgi_bindir	/home/services/httpd/cgi-bin

%description
SmokePing is a ICMP latency logging and graphing system. It consists
of a daemon process which organizes the latency measurements and a CGI
which presents the graphs with interesting smoke-like effects.

%description -l pl
Smokeping jest narzêdziem do tworzenia wykresów aktywno¶ci sieci.
U¿ywaj±c pakietów ICMP zapisuje czas odpowiedzi poszczególnych hostów
i wy¶wietla je w postaci czytelnego wykresu.

%prep
%setup -q

%build
%{__make}

decruft() { %{__perl} -pi -e "s|$1|$2|g" `grep -lr "$1" *` ;}

# eliminate Tobi's quirks
decruft /usr/sepp/bin %{_bindir}

decruft /home/oetiker/data/projects/AADJ-smokeping/dist/etc	%{_sysconfdir}/%{name}
decruft /home/oetiker/data/projects/AADJ-smokeping/dist/lib	%{_datadir}/%{name}

# rrdtool package goes into standard perl tree
decruft '^use lib .*rrdtool.*;' ''

# there's no SpeedyCGI for apache2? use regular perl...
decruft %{_bindir}/speedy %{_bindir}/perl

# working config in wrong location
decruft "etc/config.dist" "%{_sysconfdir}/%{name}/config"

sed -i -e 's@^#!/usr/bin/perl-5.8.4@#!/usr/bin/perl@' bin/smokeping.dist
sed -i -e 's#use lib qw(lib);#use lib qw(%{_datadir}/%{name});#' bin/smokeping.dist

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_sysconfdir}/%{name},%{_wwwconfdir},%{_bindir}} \
	$RPM_BUILD_ROOT{%{_datadir}/%{name},%{_sharedstatedir}/%{name}/{img,rrd},%{_cgi_bindir}} \
	$RPM_BUILD_ROOT%{_mandir}/man1

install etc/basepage.html.dist $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/basepage.html
install etc/config.dist $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
#install etc/config-echoping.dist $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/config-echoping
install etc/smokemail.dist $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/smokemail
install bin/smokeping.dist $RPM_BUILD_ROOT%{_bindir}/smokeping
install bin/tSmoke.dist $RPM_BUILD_ROOT%{_bindir}/tSmoke
install htdocs/smokeping.cgi.dist $RPM_BUILD_ROOT%{_cgi_bindir}/smokeping.cgi
cp -r lib/* $RPM_BUILD_ROOT%{_datadir}/%{name}
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT%{_wwwconfdir}/99_%{name}.conf
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/config
install doc/*.1 $RPM_BUILD_ROOT%{_mandir}/man1

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ "$1" = "1" ]; then

firstgate=`route -n |awk '$1=="0.0.0.0" && $4 ~ /G/ {print $2}' |head -1`
echo "
+ gateway
 menu   = Default Gateway
 title  = Default Gateway Router
 host   = $firstgate

+ dns
 menu   = DNS Servers
 title  = Domain Name Servers
        " >>%{_sysconfdir}/%{name}/config
for dns in `awk '$1 ~ /^nameserver/ {print $2}' /etc/resolv.conf |sort -u` ; do
((dnscnt++))
echo "++ dns$dnscnt
  menu  = DNS Server $dnscnt
  title = Domain Name Server $dnscnt
  host  = $dns
        " >>%{_sysconfdir}/%{name}/config
done

[ "$HOSTNAME" ] && %{__perl} -pi -e "s|localhost|$HOSTNAME|g" %{_sysconfdir}/%{name}/config

fi

/sbin/chkconfig --add %{name}

if [ -f /var/lock/subsys/%{name} ]; then
	/etc/rc.d/init.d/%{name} restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/%{name} start\" to start smokeping."
fi

if [ -f /var/lock/subsys/httpd ]; then
	/etc/rc.d/init.d/httpd restart 1>&2
fi

%preun
if [ $1 = 0 ]; then
	if [ -f /var/lock/subsys/%{name} ]; then
		/etc/rc.d/init.d/%{name} stop 1>&2
	fi

	/sbin/chkconfig --del %{name}

	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi

%files
%defattr(644,root,root,755)
%doc CHANGES CONTRIBUTORS COPYRIGHT README TODO doc/*.txt doc/*.html
%attr(755,root,root) %{_bindir}/*
%{_datadir}/smokeping
%{_mandir}/man1/*.1*
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/*
%config(noreplace) %verify(not md5 mtime size) %{_wwwconfdir}/*
%attr(754,root,root) /etc/rc.d/init.d/*
%attr(755,root,root) %{_cgi_bindir}/*
%dir %{_sharedstatedir}/%{name}
%{_sharedstatedir}/%{name}/rrd
%attr(775,root,http) %{_sharedstatedir}/%{name}/img
