Summary: 	Smokeping is a traffic grapher that uses rrdtool.
Summary(pl):	Smokeping jest narzêdziem do tworzenia wykresów aktywno¶ci sieci.
Name: 		smokeping
Version: 	1.30
Release: 	0.1	
Source0: 	http://people.ee.ethz.ch/~oetiker/webtools/smokeping/pub/%name-%version.tar.gz
# Source0-md5:	b7e909fb4d851995edc05afffb1a1e4b
Source1:	%name.init
Source2:	%name.conf
Vendor: 	Tobias Oetiker	
License: 	GPL
Group: 		Applications/Internet
Requires: 	rrdtool
Requires:	httpd
Requires:	fping
Requires:	perl
BuildRequires: 	perl
BuildArch:      noarch
BuildRoot: 	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)	

%define         _wwwrootdir             /home/services/httpd

%description
SmokePing is a ICMP latency logging and graphing system. It consists of a
daemon process which organizes the latency measurements and a CGI which
presents the graphs with interesting smoke-like effects.


%description -l pl
Smokeping jest narzêdziem do tworzenia wykresów aktywno¶ci sieci. U¿ywaj±c
pakietów ICMP zapisuje czas odpowiedzi poszczególnych hostów i wy¶wietla je
w postaci czytelnego wykresu.


%prep
%setup -q

%build
%{__make}

%install
rm -rf $RPM_BUILD_ROOT 
install -D -m 644 etc/basepage.html.dist $RPM_BUILD_ROOT/%{_sysconfdir}/%name/basepage.html
install -D -m 644 etc/config.dist $RPM_BUILD_ROOT/%{_sysconfdir}/%name/config
install -D -m 644 etc/config-echoping.dist $RPM_BUILD_ROOT/%{_sysconfdir}/%name/config-echoping
install -D -m 644 etc/smokemail.dist $RPM_BUILD_ROOT/%{_sysconfdir}/%name/smokemail
install -D -m 755 bin/smokeping.dist $RPM_BUILD_ROOT/%{_bindir}/smokeping
install -d $RPM_BUILD_ROOT/%{_libdir}/smokeping
cp -r lib/* $RPM_BUILD_ROOT/%{_libdir}/smokeping/
install -d $RPM_BUILD_ROOT/%{_wwwrootdir}/%{name}/{rrd,img}
install -D -m755 htdocs/%{name}.cgi.dist	$RPM_BUILD_ROOT/%{_wwwrootdir}/cgi-bin/%{name}
install -D -m 755 %{SOURCE1} $RPM_BUILD_ROOT/%{_sysconfdir}/init.d/%name
install -D -m 644 %{SOURCE2} $RPM_BUILD_ROOT/%{_sysconfdir}/httpd/conf.d/%{name}.conf
install -d $RPM_BUILD_ROOT/%{_mandir}/man1/
cp doc/*.1	$RPM_BUILD_ROOT/%{_mandir}/man1/


%clean
rm -rf $RPM_BUILD_ROOT 

%post
/sbin/chkconfig --add smokeping

%preun
if [ $1 = 0 ]; then
        /sbin/chkconfig --del smokeping
fi

%files
%defattr(-,root,root)
%doc CHANGES CONTRIBUTORS COPYRIGHT TODO README doc/*.txt doc/*.html
%{_bindir}/*
%{_libdir}/*/*
%{_mandir}/*/*
%config %{_sysconfdir}/%name/config
%config %{_sysconfdir}/%name/config-echoping
%config %{_sysconfdir}/%name/smokemail
%config %{_sysconfdir}/%name/basepage.html
%config %{_sysconfdir}/httpd/conf.d/%{name}.conf
%attr(755,root,root) %{_sysconfdir}/init.d/%name
%dir %{_wwwrootdir}/%{name}/rrd
%dir %{_wwwrootdir}/%{name}/img
%{_wwwrootdir}/cgi-bin/%{name} 
