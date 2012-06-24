# TODO
# - resolve permission problem for webserver access to /usr/sbin/fping
# - generated config does not always match the used webserver vhost (don't autogenerate it at all?)
# - finish -cgi and main files, afaik templates/ needed only by -cgi
# - use .patch not decruft()
# - use other user than root for daemon (uid=stats perhaps)
%include	/usr/lib/rpm/macros.perl
Summary:	Smokeping - a latency grapher that uses rrdtool
Summary(pl):	Smokeping - narz�dzie do tworzenia wykres�w op�nie� sieci
Name:		smokeping
Version:	2.0.5
Release:	2.5
License:	GPL v2
Group:		Networking/Utilities
Source0:	http://people.ee.ethz.ch/~oetiker/webtools/smokeping/pub/%{name}-%{version}.tar.gz
# Source0-md5:	c965439c147012b91585c3e134225b4d
Source1:	%{name}.init
Source2:	%{name}.conf
Source3:	%{name}-config
URL:		http://people.ee.ethz.ch/~oetiker/webtools/smokeping/
BuildRequires:	perl-tools-pod
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRequires:	rpmbuild(macros) >= 1.264
BuildRequires:	rrdtool
BuildRequires:	sed >= 4.0
Requires(post):	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
Requires:	fping
Requires:	rc-scripts
Requires:	rrdtool >= 1.2
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/%{name}
%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_wwwconfdir	%{_webapps}/%{_webapp}
%define		_cgi_bindir	%{_prefix}/share/%{name}

%description
SmokePing is a ICMP latency logging and graphing system. It consists
of a daemon process which organizes the latency measurements and a CGI
which presents the graphs with interesting smoke-like effects.

%description -l pl
Smokeping jest narz�dziem do tworzenia wykres�w aktywno�ci sieci.
U�ywaj�c pakiet�w ICMP zapisuje czas odpowiedzi poszczeg�lnych host�w
i wy�wietla je w postaci czytelnego wykresu.

%package cgi
Summary:	CGI webinterface for smokeping
Summary(pl):	Interfejs WWW (CGI) do smokepinga
Group:		Applications/WWW
Requires:	%{name} = %{version}-%{release}
Requires:	webapps

%description cgi
CGI webinterface for smokeping.

%description cgi -l pl
Interfejs WWW (CGI) do smokepinga.

%prep
%setup -q

decruft() { %{__sed} -i -e "s|$1|$2|g" `grep -lr "$1" *` ;}

# eliminate Tobi's quirks
decruft /usr/sepp/bin %{_bindir}

decruft /home/oetiker/data/projects/AADJ-smokeping/dist/etc	%{_sysconfdir}
decruft /home/oetiker/data/projects/AADJ-smokeping/dist/lib	%{_datadir}/%{name}

# rrdtool package goes into standard perl tree
decruft '^use lib .*rrdtool.*;' ''

# there's no SpeedyCGI for apache2? use regular perl...
decruft %{_bindir}/speedy %{_bindir}/perl

# working config in wrong location
decruft "etc/config.dist" "%{_sysconfdir}/config"

sed -i -e 's@^#!/usr/bin/perl-5.8.4@#!/usr/bin/perl@' bin/smokeping.dist
sed -i -e 's#use lib qw(lib);#use lib qw(%{_datadir}/%{name});#' bin/smokeping.dist

%build
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_sysconfdir},%{_wwwconfdir},%{_sbindir}} \
	$RPM_BUILD_ROOT{%{_datadir}/%{name},%{_sharedstatedir}/%{name}/{img,rrd},%{_cgi_bindir}} \
	$RPM_BUILD_ROOT%{_mandir}/man1

install etc/basepage.html.dist $RPM_BUILD_ROOT%{_sysconfdir}/basepage.html
install etc/config.dist $RPM_BUILD_ROOT%{_sysconfdir}
#install etc/config-echoping.dist $RPM_BUILD_ROOT%{_sysconfdir}/config-echoping
install etc/smokemail.dist $RPM_BUILD_ROOT%{_sysconfdir}/smokemail
install bin/smokeping.dist $RPM_BUILD_ROOT%{_sbindir}/smokeping
install bin/tSmoke.dist $RPM_BUILD_ROOT%{_sbindir}/tSmoke
install htdocs/smokeping.cgi.dist $RPM_BUILD_ROOT%{_cgi_bindir}/smokeping.cgi
cp -r lib/* $RPM_BUILD_ROOT%{_datadir}/%{name}
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT%{_wwwconfdir}/httpd.conf
install %{SOURCE2} $RPM_BUILD_ROOT%{_wwwconfdir}/apache.conf
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/config
install doc/*.1 $RPM_BUILD_ROOT%{_mandir}/man1

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ "$1" = "1" ]; then

firstgate=`route -n |awk '$1=="0.0.0.0" && $4 ~ /G/ {print $2}' | head -n 1`
echo "
+ gateway
 menu   = Default Gateway
 title  = Default Gateway Router
 host   = $firstgate

+ dns
 menu   = DNS Servers
 title  = Domain Name Servers
        " >> %{_sysconfdir}/config
for dns in `awk '$1 ~ /^nameserver/ {print $2}' /etc/resolv.conf | LC_ALL=C sort -u` ; do
((dnscnt++))
echo "++ dns$dnscnt
  menu  = DNS Server $dnscnt
  title = Domain Name Server $dnscnt
  host  = $dns
        " >> %{_sysconfdir}/config
done

[ "$HOSTNAME" ] && %{__sed} -i -e "s|localhost|$HOSTNAME|g" %{_sysconfdir}/config

fi

/sbin/chkconfig --add %{name}
if [ -f /var/lock/subsys/%{name} ]; then
	/etc/rc.d/init.d/%{name} restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/%{name} start\" to start smokeping."
fi

%preun
if [ $1 = 0 ]; then
	if [ -f /var/lock/subsys/%{name} ]; then
		/etc/rc.d/init.d/%{name} stop 1>&2
	fi

	/sbin/chkconfig --del %{name}
fi

%triggerin cgi -- apache1
%webapp_register apache %{_webapp}

%triggerun cgi -- apache1
%webapp_unregister apache %{_webapp}

%triggerin cgi -- apache >= 2.0.0
%webapp_register httpd %{_webapp}

%triggerun cgi -- apache >= 2.0.0
%webapp_unregister httpd %{_webapp}

%triggerpostun -- %{name} < 2.0.5-0.3
# we put trigger on main package, because we can't trigger in new package
# this will create .rpmnew files when one installs -cgi package. but that's more than okay
if [ -f /etc/httpd/httpd.conf/99_%{name}.conf.rpmsave ]; then
	install -d %{_wwwconfdir}
	mv -f /etc/httpd/httpd.conf/99_%{name}.conf.rpmsave %{_wwwconfdir}/httpd.conf
fi

if [ -f /var/lock/subsys/httpd ]; then
	/etc/rc.d/init.d/httpd reload 1>&2
fi

%banner -e %{name} << EOF
The CGI program is available as %{name}-cgi package.
EOF

%files
%defattr(644,root,root,755)
%doc CHANGES CONTRIBUTORS COPYRIGHT README TODO doc/*.txt doc/*.html
%attr(755,root,root) %{_sbindir}/*
%{_datadir}/smokeping
%exclude %{_datadir}/smokeping/*.cgi
%{_mandir}/man1/*.1*
%dir %{_sysconfdir}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*
%attr(754,root,root) /etc/rc.d/init.d/*
%dir %{_sharedstatedir}/%{name}
%{_sharedstatedir}/%{name}/rrd
%dir %attr(775,root,http) %{_sharedstatedir}/%{name}/img

%files cgi
%defattr(644,root,root,755)
%dir %attr(750,root,http) %{_wwwconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_wwwconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_wwwconfdir}/httpd.conf
%attr(755,root,root) %{_cgi_bindir}/*.cgi
