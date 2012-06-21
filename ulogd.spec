%define		beta	beta4
Summary:	ULOGD - the Userspace Logging Daemon for iptables
Summary(pl.UTF-8):	Demon logujący w trybie użytkownika dla iptables
Name:		ulogd
Version:	2.0.0
Release:	0.1
License:	GPL
Group:		Networking/Daemons
Source0:	ftp://ftp.netfilter.org/pub/ulogd/%{name}-%{version}.tar.bz2
# Source0-md5:	211e68781e3860959606fc94b97cf22e
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.logrotate
Patch0:		%{name}-includes.patch
Patch1:		%{name}-ac.patch
URL:		http://netfilter.org/projects/ulogd/
BuildRequires:	autoconf
BuildRequires:	libdbi-devel
BuildRequires:	libnetfilter_acct-devel >= 1.0.0
BuildRequires:	libnetfilter_conntrack-devel >= 0.0.95
BuildRequires:	libnetfilter_log-devel >= 0.0.15
BuildRequires:	libnfnetlink-devel >= 0.0.39
BuildRequires:	libpcap-devel
BuildRequires:	mysql-devel
BuildRequires:	postgresql-devel
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	sed >= 4.0
BuildRequires:	sqlite3-devel
Requires(post):	fileutils
Requires(post,preun):	/sbin/chkconfig
Requires:	iptables
#Requires:	kernel >= 2.4.0test9
Requires:	rc-scripts
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This packages is intended for passing packets from the kernel to
userspace to do some logging there. It should work like that:
- register a target called ULOG with netfilter
- if the target is hit:
  - send the packet out using netlink multicast facility
  - return NF_ACCEPT immediately.

%description -l pl.UTF-8
Ten pakiet ma służyć do wysyłania pakietów z jądra do przestrzeni
użytkownika w celu logowania. Powinien działać tak:
- zarejestrować w netfilterze cel o nazwie ULOG
- jeżeli cel został osiągnięty:
  - wysłać pakiet poprzez netlink
  - zwrócić natychmiast NF_ACCEPT.

%package devel
Summary:	Header files for %{name}
Summary(pl.UTF-8):	Pliki nagłówkowe %{name}
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for %{name}.

%description devel -l pl.UTF-8
Pliki nagłówkowe %{name}.

%package dbi
Summary:	DBI plugin for ulogd
Summary(pl.UTF-8):	Wtyczka DBI dla ulogd
Group:		Networking/Daemons

%description dbi
DBI plugin for ulogd.

%description dbi -l pl.UTF-8
Wtyczka DBI dla ulogd.

%package mysql
Summary:	MySQL plugin for ulogd
Summary(pl.UTF-8):	Wtyczka MySQL dla ulogd
Group:		Networking/Daemons
Obsoletes:	iptables-ulogd-mysql

%description mysql
MySQL plugin for ulogd.

%description mysql -l pl.UTF-8
Wtyczka MySQL dla ulogd.

%package pcap
Summary:	PCAP plugin for ulogd
Summary(pl.UTF-8):	Wtyczka PCAP dla ulogd
Group:		Networking/Daemons

%description pcap
PCAP plugin for ulogd.

%description pcap -l pl.UTF-8
Wtyczka PCAP dla ulogd.

%package pgsql
Summary:	PostgreSQL plugin for ulogd
Summary(pl.UTF-8):	Wtyczka PostgreSQL dla ulogd
Group:		Networking/Daemons

%description pgsql
PostgreSQL plugin for ulogd.

%description pgsql -l pl.UTF-8
Wtyczka PostgreSQL dla ulogd.

%package sqlite
Summary:	SQLite plugin for ulogd
Summary(pl.UTF-8):	Wtyczka SQLite dla ulogd
Group:		Networking/Daemons

%description sqlite
SQLite plugin for ulogd.

%description sqlite -l pl.UTF-8
Wtyczka SQLite dla ulogd.

%prep
%setup -q
%patch0 -p1
%patch1 -p0

%build
#%if "%{_lib}" != "lib"
#sed -e 's@lib/@%{_lib}/@g' -i configure.in
#%endif

%{__autoconf}
%configure \
	--with-dbi \
	--with-dbi-lib=%{_libdir} \
	--with-mysql \
	--with-pgsql
%{__make} -j1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},/etc/{sysconfig,logrotate.d,rc.d/init.d,ulogd}} \
	$RPM_BUILD_ROOT/var/log

%{__make} install -j1 \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ulogd
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/ulogd
install %{SOURCE3} $RPM_BUILD_ROOT/etc/logrotate.d/ulogd
install %{name}.conf $RPM_BUILD_ROOT/etc/%{name}.conf
install -D %{name}.8 $RPM_BUILD_ROOT%{_mandir}/man8/%{name}.8

touch $RPM_BUILD_ROOT/var/log/ulogd{,.pktlog}

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ ! -f /var/log/ulogd ]; then
	touch /var/log/ulogd{,.pktlog}
	chmod 640 /var/log/ulogd{,.pktlog}
fi

/sbin/chkconfig --add ulogd
%service ulogd restart "ulogd daemon"

%preun
if [ "$1" = "0" ]; then
	%service ulogd stop
	/sbin/chkconfig --del ulogd
fi

%files
%defattr(644,root,root,755)
#%doc Changes doc/*.{ps,txt,html}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/ulogd
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ulogd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/ulogd
%attr(750,root,root) %dir %{_sysconfdir}/ulogd
%attr(754,root,root) /etc/rc.d/init.d/ulogd

%attr(755,root,root) %{_sbindir}/*
%dir %{_libdir}/ulogd
%attr(755,root,root) %{_libdir}/ulogd/ulogd_filter_HWHDR.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_filter_IFINDEX.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_filter_IP2BIN.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_filter_IP2HBIN.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_filter_IP2STR.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_filter_MARK.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_filter_PRINTFLOW.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_filter_PRINTPKT.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_filter_PWSNIFF.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_inpflow_NFACCT.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_inpflow_NFCT.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_inppkt_NFLOG.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_inppkt_ULOG.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_inppkt_UNIXSOCK.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_GPRINT.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_LOGEMU.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_NACCT.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_OPRINT.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_SYSLOG.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_XML.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_raw2packet_BASE.so

%attr(640,root,root) %ghost /var/log/*
%{_mandir}/man8/%{name}.*

%files devel
%defattr(644,root,root,755)
%{_libdir}/ulogd/*.la

%files dbi
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_DBI.so

%files mysql
%defattr(644,root,root,755)
%doc doc/mysql*
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_MYSQL.so

%files pcap
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_PCAP.so

%files pgsql
%defattr(644,root,root,755)
%doc doc/pgsql*
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_PGSQL.so

%files sqlite
%defattr(644,root,root,755)
%doc doc/sqlite*
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_SQLITE3.so
