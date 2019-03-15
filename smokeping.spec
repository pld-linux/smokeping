%include	/usr/lib/rpm/macros.perl
Summary:	Smokeping - a latency grapher that uses rrdtool
Summary(pl.UTF-8):	Smokeping - narzędzie do tworzenia wykresów opóźnień sieci
Name:		smokeping
Version:	2.7.3
Release:	1
License:	GPL v2+
Group:		Networking/Utilities
Source0:	http://oss.oetiker.ch/smokeping/pub/%{name}-%{version}.tar.gz
# Source0-md5:	e0a8657241182f6c8bdb91cfca2589c7
Source1:	%{name}.init
Source2:	%{name}-apache.conf
Source3:	%{name}-config
Source4:	%{name}-lighttpd.conf
Source5:	%{name}.tmpfiles
Source6:	%{name}-httpd.conf
Patch0:		fix-paths.patch
Patch1:		no-thirdparty.patch
URL:		http://oss.oetiker.ch/smokeping/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	perl-Config-Grammar
BuildRequires:	perl-rrdtool
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
Requires:	perl-Config-Grammar
Requires:	rc-scripts >= 0.4.1.23
Requires:	rrdtool >= 1.2
Suggests:	bind-utils
Suggests:	curl
Suggests:	echoping
Suggests:	fping
Suggests:	openssh-clients
Suggests:	traceroute
Provides:	group(%{name})
Provides:	user(%{name})
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_noautoprovfiles	%{_datadir}/%{name}
%define		_noautoreq_perl		BER Smokeping Smokeping::ciscoRttMonMIB Smokeping::Colorspace Smokeping::Config Smokeping::Examples Smokeping::Graphs Smokeping::Info Smokeping::Master Smokeping::matchers::Avgratio Smokeping::matchers::base Smokeping::matchers::CheckLatency Smokeping::matchers::CheckLoss Smokeping::matchers::ExpLoss Smokeping::matchers::Median Smokeping::matchers::Medratio Smokeping::pingMIB Smokeping::probes::AnotherDNS Smokeping::probes::AnotherSSH Smokeping::probes::base Smokeping::probes::basefork Smokeping::probes::basevars Smokeping::probes::CiscoRTTMonDNS Smokeping::probes::CiscoRTTMonEchoICMP Smokeping::probes::CiscoRTTMonTcpConnect Smokeping::probes::Curl Smokeping::probes::DismanPing Smokeping::probes::DNS Smokeping::probes::EchoPing Smokeping::probes::EchoPingChargen Smokeping::probes::EchoPingDiscard Smokeping::probes::EchoPingDNS Smokeping::probes::EchoPingHttp Smokeping::probes::EchoPingHttps Smokeping::probes::EchoPingIcp Smokeping::probes::EchoPingLDAP Smokeping::probes::EchoPingPlugin Smokeping::probes::EchoPingSmtp Smokeping::probes::EchoPingWhois Smokeping::probes::FPing Smokeping::probes::FPing6 Smokeping::probes::FTPtransfer Smokeping::probes::IOSPing Smokeping::probes::LDAP Smokeping::probes::NFSping Smokeping::probes::OpenSSHEOSPing Smokeping::probes::OpenSSHJunOSPing Smokeping::probes::passwordchecker Smokeping::probes::Qstat Smokeping::probes::Radius Smokeping::probes::RemoteFPing Smokeping::probes::SendEmail Smokeping::probes::SipSak Smokeping::probes::skel Smokeping::probes::SSH Smokeping::probes::TacacsPlus Smokeping::probes::TCPPing Smokeping::probes::TelnetIOSPing Smokeping::probes::TelnetJunOSPing Smokeping::probes::WebProxyFilter Smokeping::RRDhelpers Smokeping::RRDtools Smokeping::Slave Smokeping::sorters::base Smokeping::sorters::Loss

# How to obtain _noautoreq:
# 1. comment out _noauto* macros
# 2. repackage smokeping
# 3. select Provides from repackage output
# 4. xclip -o | sed 's/ perl/\nperl/g' | awk '{print $1}' | sort -u > perlprov
# 5. select Requires from repackage output
# 6. xclip -o | sed 's/ perl/\nperl/g' | awk '{print $1}' | sort -u > perlreq
# 7. cat perlprov perlprov perlreq | awk '{print $1}' | sort | uniq -c | \
#      grep '^      2 ' | sed 's/.*perl(//; s/)//' | tr '\n' ' '

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
Requires:	webserver(access)
Requires:	webserver(alias)
Requires:	webserver(cgi)
Conflicts:	apache-base < 2.4.0-1

%description cgi
CGI webinterface for smokeping.

%description cgi -l pl.UTF-8
Interfejs WWW (CGI) do smokepinga.

%prep
%setup -q

%patch0 -p1
%patch1 -p1

#sed -i -e 's,^Net::.*$,,' PERL_MODULES

sed -i -e 's#@prefix@/etc/\(.*\).dist#/etc/smokeping/\1#' etc/config.dist.in
sed -i -e 's#@prefix@/etc/#/etc/smokeping/#' etc/config.dist.in

%build
[ ! -f VERSION ] && echo %{version} > VERSION
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--enable-pkgonly
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_sysconfdir},%{_wwwconfdir}} \
	$RPM_BUILD_ROOT{%{_datadir}/%{name},%{_sharedstatedir}/%{name}/{img,rrd},%{_cgi_bindir}} \
	$RPM_BUILD_ROOT{%{_mandir}/man{1,3,5,7},/var/run/%{name}} \
	$RPM_BUILD_ROOT%{systemdtmpfilesdir}

%{__make} install DESTDIR=$RPM_BUILD_ROOT

# start of fixing paths
for f in basepage.html smokemail smokeping_secrets tmail; do
    mv $RPM_BUILD_ROOT/etc/smokeping/{$f.dist,$f}
done

rm -rf $RPM_BUILD_ROOT/etc/smokeping/examples

mv $RPM_BUILD_ROOT%{_prefix}/lib/{*.pm,Smokeping} $RPM_BUILD_ROOT%{_datadir}/%{name}

mv $RPM_BUILD_ROOT{%{_prefix}/htdocs/{css,js},%{_cgi_bindir}}
mv $RPM_BUILD_ROOT%{_bindir}/smokeping_cgi $RPM_BUILD_ROOT%{_cgi_bindir}/smokeping.cgi

mv $RPM_BUILD_ROOT%{_mandir}/man1/{smokeping_cgi.1,smokeping.cgi.1}
# end of fixing paths

install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_wwwconfdir}/apache.conf
cp -p %{SOURCE6} $RPM_BUILD_ROOT%{_wwwconfdir}/httpd.conf
cp -p %{SOURCE4} $RPM_BUILD_ROOT%{_wwwconfdir}/lighttpd.conf
cp -p %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/config
cp -p %{SOURCE5} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/%{name}.conf

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

%triggerin cgi -- apache-base
%webapp_register httpd %{_webapp}

%triggerun cgi -- apache-base
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
%doc CHANGES CONTRIBUTORS COPYRIGHT README TODO doc/*.txt doc/examples
%attr(755,root,root) %{_bindir}/smokeinfo
%attr(755,root,root) %{_bindir}/smokeping
%attr(755,root,root) %{_bindir}/tSmoke
%{_datadir}/smokeping
%exclude %{_cgi_bindir}/css
%exclude %{_cgi_bindir}/js
%exclude %{_datadir}/smokeping/smokeping.*cgi
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
%{systemdtmpfilesdir}/%{name}.conf

%files cgi
%defattr(644,root,root,755)
%dir %attr(750,root,http) %{_wwwconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_wwwconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_wwwconfdir}/httpd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_wwwconfdir}/lighttpd.conf
%{_cgi_bindir}/css
%{_cgi_bindir}/js
%attr(755,root,root) %{_cgi_bindir}/smokeping.cgi
