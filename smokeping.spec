Summary:	Smokeping - a traffic grapher that uses rrdtool
Summary(pl):	Smokeping - narzêdzie do tworzenia wykresów aktywno¶ci sieci
Name:		smokeping
Version:	1.30
Release:	0.1
Vendor:		Tobias Oetiker
License:	GPL
Group:		Networking/Utilities
Source0:	http://people.ee.ethz.ch/~oetiker/webtools/smokeping/pub/%{name}-%{version}.tar.gz
# Source0-md5:	b7e909fb4d851995edc05afffb1a1e4b
Source1:	%{name}.init
Source2:	%{name}.conf
URL:		http://people.ee.ethz.ch/~oetiker/webtools/smokeping/
BuildRequires:	perl-base
Requires:	fping
Requires:	perl-base
Requires:	rrdtool
Requires:	webserver
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_wwwrootdir	/home/services/httpd
%define		_wwwconfig	/etc/httpd/conf/httpd.conf
%define		_wwwconfdir	/etc/httpd/conf

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

%install
rm -rf $RPM_BUILD_ROOT

install -D etc/basepage.html.dist $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/basepage.html
install -D etc/config.dist $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/config
install -D etc/config-echoping.dist $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/config-echoping
install -D etc/smokemail.dist $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/smokemail
install -D -m 755 bin/smokeping.dist $RPM_BUILD_ROOT%{_bindir}/smokeping
install -d $RPM_BUILD_ROOT%{_libdir}/smokeping
cp -r lib/* $RPM_BUILD_ROOT%{_libdir}/smokeping
install -d $RPM_BUILD_ROOT%{_wwwrootdir}/%{name}/{rrd,img}
install -D -m755 htdocs/%{name}.cgi.dist $RPM_BUILD_ROOT%{_wwwrootdir}/cgi-bin/%{name}
install -D -m 755 %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install -D %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/%{name}.conf
install -d $RPM_BUILD_ROOT%{_mandir}/man1
install doc/*.1 $RPM_BUILD_ROOT%{_mandir}/man1

%clean
rm -rf $RPM_BUILD_ROOT

%post
# TODO -> create /etc/smokeping/config
/sbin/chkconfig --add %{name} 
if [ -f /var/lock/subsys/%{name} ]; then
        /etc/rc.d/init.d/%{name} restart 1>&2
else
        echo "Run \"/etc/rc.d/init.d/%{name} start\" to start smokeping."
fi

if ! grep -q "^Include.*/smokeping.conf" %{_wwwconfig}; then 
	echo >> %{_wwwconfig} 
	echo "#added by SmokePing instalator" >> %{_wwwconfig} 
	echo "Include %{_wwwconfdir}/smokeping.conf" >> %{_wwwconfig} 
	echo >> %{_wwwconfig} 
fi 

if [ -f /var/lock/subsys/httpd ]; then
        /etc/rc.d/init.d/httpd restart 1>&2
fi

%preun
# TODO -> remove "Include %{_wwwconfdir}/smokeping.conf"
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
%doc CHANGES CONTRIBUTORS COPYRIGHT TODO README doc/*.txt doc/*.html
%attr(755,root,root) %{_bindir}/*
%{_libdir}/smokeping
%{_mandir}/man1/*.1*
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/%{name}/config
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/%{name}/config-echoping
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/%{name}/smokemail
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/%{name}/basepage.html
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%attr(755,root,root) /etc/rc.d/init.d/%{name}
%dir %{_wwwrootdir}/%{name}
%dir %{_wwwrootdir}/%{name}/rrd
%dir %{_wwwrootdir}/%{name}/img
%{_wwwrootdir}/cgi-bin/%{name}
