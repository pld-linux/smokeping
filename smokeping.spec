%include	/usr/lib/rpm/macros.perl
Summary:	Smokeping - a latency grapher that uses rrdtool
Summary(pl.UTF-8):	Smokeping - narzędzie do tworzenia wykresów opóźnień sieci
Name:		smokeping
Version:	2.4.2
Release:	9
License:	GPL v2+
Group:		Networking/Utilities
Source0:	http://oss.oetiker.ch/smokeping/pub/%{name}-%{version}.tar.gz
# Source0-md5:	eb8e7679fcad35e59d7c51f2328250a2
Source1:	%{name}.init
Source2:	%{name}.conf
Source3:	%{name}-config
Source4:	%{name}-lighttpd.conf
URL:		http://oss.oetiker.ch/smokeping/
BuildRequires:	perl-tools-pod
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	sed >= 4.0
Requires(post):	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/lib/rpm/user_group.sh
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(pre):	/usr/sbin/usermod
Requires(triggerpostun):	findutils
Requires:	rc-scripts >= 0.4.1.23
Requires:	rrdtool >= 1.2
Suggests:	bind-utils
Suggests:	curl
Suggests:	echoping
Suggests:	echoping
Suggests:	fping
Suggests:	openssh-clients
Suggests:	traceroute
Provides:	group(%{name})
Provides:	user(%{name})
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_noautoprovfiles	%{_datadir}/%{name}
%define		_noautoreq		perl(BER) perl(CGI::Session::Driver) perl(CGI::Session::Driver::DBI) perl(CGI::Session::ErrorHandler) perl(Config::Grammar) perl(Digest::HMAC) perl(Digest::HMAC_MD5) perl(JSON) perl(JSON::Converter) perl(JSON::Parser) perl(Smokeping) perl(Smokeping::ciscoRttMonMIB) perl(Smokeping::Colorspace) perl(Smokeping::Config) perl(Smokeping::Examples) perl(Smokeping::Graphs) perl(Smokeping::Master) perl(Smokeping::matchers::Avgratio) perl(Smokeping::matchers::base) perl(Smokeping::probes::base) perl(Smokeping::probes::basefork) perl(Smokeping::probes::basevars) perl(Smokeping::probes::EchoPing) perl(Smokeping::probes::EchoPingHttp) perl(Smokeping::probes::EchoPingPlugin) perl(Smokeping::probes::FPing) perl(Smokeping::probes::passwordchecker) perl(Smokeping::RRDhelpers) perl(Smokeping::RRDtools) perl(Smokeping::Slave) perl(Smokeping::sorters::base) perl(SNMP_Session) perl(SNMP_util)

# How to obtain _noautoreq:
# 1. comment out _noauto* macros
# 2. repackage smokeping
# 3. select Provides from repackage output
# 4. xclip -o | sed 's/ perl/\nperl/' > perlprov
# 5. select Requires from repackage output
# 6. xclip -o | sed 's/ perl/\nperl/' > perlreq
# 7. cat perlprov perlreq | awk '{print $1}' | sort | uniq -c | grep '^      2 ' | awk '{print $2}' | tr '\n' ' '

%define		_sysconfdir	/etc/%{name}
%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_wwwconfdir	%{_webapps}/%{_webapp}
%define		_cgi_bindir	%{_prefix}/share/%{name}

%description
SmokePing is a ICMP latency logging and graphing system. It consists
of a daemon process which organizes the latency measurements and a CGI
which presents the graphs with interesting smoke-like effects.

%description -l pl.UTF-8
Smokeping jest narzędziem do tworzenia wykresów aktywności sieci.
Używając pakietów ICMP zapisuje czas odpowiedzi poszczególnych hostów
i wyświetla je w postaci czytelnego wykresu.

%package cgi
Summary:	CGI webinterface for smokeping
Summary(pl.UTF-8):	Interfejs WWW (CGI) do smokepinga
Group:		Applications/WWW
Requires:	%{name} = %{version}-%{release}
Requires:	webapps

%description cgi
CGI webinterface for smokeping.

%description cgi -l pl.UTF-8
Interfejs WWW (CGI) do smokepinga.

%prep
%setup -q

decruft() { grep -lr "$1" . | xargs %{__sed} -i -e "s|$1|$2|g"; }

# eliminate Tobi's quirks
decruft /usr/sepp/bin %{_bindir}

# rrdtool package goes into standard perl tree
decruft '^use lib .*rrdtool.*;' ''

decruft /usr/bin/speedy-5.8.8 %{_bindir}/speedy

sed -i -e '/\/home\/oposs\/smokeping\/software\/lib/d' htdocs/tr.cgi.dist
sed -i -e '/\/home\/oetiker\/checkouts\/smokeping\/trunk\/software\/lib/d' htdocs/smokeping.cgi.dist
sed -i -e 's|/home/oetiker/checkouts/smokeping/trunk/software/etc/config.dist|%{_sysconfdir}/config|' htdocs/smokeping.cgi.dist
# working config in wrong location
decruft "etc/config.dist" "%{_sysconfdir}/config"

sed -i -e 's#use lib qw(lib);#use lib qw(%{_datadir}/%{name});#' bin/smokeping.dist

sed -i -e 's#"cropper/#"/smokeping/cropper/#' etc/basepage.html.dist

%build
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_sysconfdir},%{_wwwconfdir},%{_sbindir}} \
	$RPM_BUILD_ROOT{%{_datadir}/%{name},%{_sharedstatedir}/%{name}/{img,rrd},%{_cgi_bindir}} \
	$RPM_BUILD_ROOT{%{_mandir}/man{1,3,5,7},/var/run/%{name}}

install etc/basepage.html.dist $RPM_BUILD_ROOT%{_sysconfdir}/basepage.html
install etc/config.dist $RPM_BUILD_ROOT%{_sysconfdir}
install etc/smokemail.dist $RPM_BUILD_ROOT%{_sysconfdir}/smokemail
install etc/smokeping_secrets.dist $RPM_BUILD_ROOT%{_sysconfdir}/smokeping_secrets
install etc/tmail.dist $RPM_BUILD_ROOT%{_sysconfdir}/tmail
install bin/smokeping.dist $RPM_BUILD_ROOT%{_sbindir}/smokeping
install bin/tSmoke.dist $RPM_BUILD_ROOT%{_sbindir}/tSmoke
cp -r htdocs/{cropper,resource,script,tr.html} $RPM_BUILD_ROOT%{_cgi_bindir}
install htdocs/smokeping.cgi.dist $RPM_BUILD_ROOT%{_cgi_bindir}/smokeping.cgi
install htdocs/tr.cgi.dist $RPM_BUILD_ROOT%{_cgi_bindir}/tr.cgi
cp -r lib/* $RPM_BUILD_ROOT%{_datadir}/%{name}
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT%{_wwwconfdir}/httpd.conf
install %{SOURCE2} $RPM_BUILD_ROOT%{_wwwconfdir}/apache.conf
install %{SOURCE4} $RPM_BUILD_ROOT%{_wwwconfdir}/lighttpd.conf
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/config
install doc/*.1 $RPM_BUILD_ROOT%{_mandir}/man1
# TODO: man(3) pages from subdirectories are packaged in %_docdir too, clean them up
install doc/{,Config/,Smokeping/{,matchers/,probes/,sorters/}}*.3 $RPM_BUILD_ROOT%{_mandir}/man3
install doc/*.5 $RPM_BUILD_ROOT%{_mandir}/man5
install doc/*.7 $RPM_BUILD_ROOT%{_mandir}/man7

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 207 %{name}
%useradd -u 207 -d /var/lib/%{name} -g %{name} -s /bin/false -c "Smokeping User" %{name}
%addusertogroup smokeping adm

%post
/sbin/chkconfig --add %{name}

%preun
if [ "$1" = 0 ]; then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" = 0 ]; then
	%userremove %{name}
	%groupremove %{name}
fi

%triggerin cgi -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun cgi -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin cgi -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun cgi -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%triggerin cgi -- lighttpd
%webapp_register lighttpd %{_webapp}

%triggerun cgi -- lighttpd
%webapp_unregister lighttpd %{_webapp}

%triggerpostun -- %{name} < 2.0.5-0.3
# we put trigger on main package, because we can't trigger in new package
# this will create .rpmnew files when one installs -cgi package. but that's more than okay
if [ -f /etc/httpd/httpd.conf/99_%{name}.conf.rpmsave ]; then
	install -d %{_wwwconfdir}
	mv -f /etc/httpd/httpd.conf/99_%{name}.conf.rpmsave %{_wwwconfdir}/httpd.conf
fi

%service -q httpd reload

%banner -e %{name} << EOF
The CGI program is available as %{name}-cgi package.
EOF

%triggerpostun -- %{name} < 2.4.2-3
find /var/lib/smokeping/rrd -type f -user root -group root -name \*.rrd -mtime -7 -exec chown smokeping \{\} \;
find /var/lib/smokeping/rrd -type d -user root -group root -exec chown smokeping \{\} \;

%files
%defattr(644,root,root,755)
%doc CHANGES CONTRIBUTORS COPYRIGHT README TODO doc/*.html doc/*.txt doc/Config doc/Smokeping doc/examples
%attr(755,root,root) %{_sbindir}/smokeping
%attr(755,root,root) %{_sbindir}/tSmoke
%{_datadir}/smokeping
%exclude %{_cgi_bindir}/cropper
%exclude %{_datadir}/smokeping/smokeping.cgi
%exclude %{_cgi_bindir}/resource
%exclude %{_cgi_bindir}/script
%exclude %{_datadir}/smokeping/tr.cgi
%exclude %{_datadir}/smokeping/tr.html
%{_mandir}/man1/smokeping.1*
%{_mandir}/man1/smokeping.cgi.1*
%{_mandir}/man1/tSmoke.1*
%{_mandir}/man3/*.3*
%{_mandir}/man5/*.5*
%{_mandir}/man7/*.7*
%dir %{_sysconfdir}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/basepage.html
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/config
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/config.dist
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/smokemail
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/smokeping_secrets
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/tmail
%attr(754,root,root) /etc/rc.d/init.d/smokeping
%dir %{_sharedstatedir}/%{name}
%dir %attr(775,root,smokeping) %{_sharedstatedir}/%{name}/rrd
%dir %attr(775,root,http) %{_sharedstatedir}/%{name}/img
%dir %attr(770,root,smokeping) /var/run/%{name}

%files cgi
%defattr(644,root,root,755)
%dir %attr(750,root,http) %{_wwwconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_wwwconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_wwwconfdir}/httpd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_wwwconfdir}/lighttpd.conf
%{_cgi_bindir}/cropper
%attr(755,root,root) %{_cgi_bindir}/smokeping.cgi
%{_cgi_bindir}/resource
%{_cgi_bindir}/script
%attr(755,root,root) %{_cgi_bindir}/tr.cgi
%{_cgi_bindir}/tr.html
