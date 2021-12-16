Summary:	ULOGD - the Userspace Logging Daemon for iptables
Summary(pl.UTF-8):	Demon logujący w trybie użytkownika dla iptables
Name:		ulogd
Version:	2.0.7
Release:	5
License:	GPL v2+
Group:		Networking/Daemons
Source0:	https://netfilter.org/projects/ulogd/files/%{name}-%{version}.tar.bz2
# Source0-md5:	2bb2868cf51acbb90c35763c9f995f31
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.logrotate
Patch0:		%{name}-includes.patch
Patch1:		%{name}-ac.patch
Patch2:		configure-logging.patch
Patch3:		enable-nflog-by-default.patch
Patch4:		put-logfiles-in-var-log-ulog.patch
URL:		https://netfilter.org/projects/ulogd/
BuildRequires:	autoconf >= 2.50
BuildRequires:	automake >= 1:1.11
BuildRequires:	jansson-devel
BuildRequires:	libdbi-devel
BuildRequires:	libmnl-devel >= 1.0.3
BuildRequires:	libnetfilter_acct-devel >= 1.0.1
BuildRequires:	libnetfilter_conntrack-devel >= 1.0.2
BuildRequires:	libnetfilter_log-devel >= 1.0.0
BuildRequires:	libnfnetlink-devel >= 1.0.1
BuildRequires:	libpcap-devel
BuildRequires:	libtool
BuildRequires:	mysql-devel
BuildRequires:	postgresql-devel
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	sgml-tools
BuildRequires:	sqlite3-devel >= 3
Requires(post):	fileutils
Requires(post,preun):	/sbin/chkconfig
Requires:	iptables
Requires:	libmnl >= 1.0.3
Requires:	libnetfilter_acct >= 1.0.1
Requires:	libnetfilter_conntrack >= 1.0.2
Requires:	libnetfilter_log >= 1.0.0
Requires:	libnfnetlink >= 1.0.1
Requires:	rc-scripts
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This packages is intended for passing packets from the kernel to
userspace to do some logging there. It should work like that:
- register a target called ULOG with netfilter
- if the target is hit:
  - send the packet out using netlink multicast facility
  - return NF_CONTINUE immediately.

%description -l pl.UTF-8
Ten pakiet ma służyć do wysyłania pakietów z jądra do przestrzeni
użytkownika w celu logowania. Powinien działać tak:
- zarejestrować w netfilterze cel o nazwie ULOG
- jeżeli cel został osiągnięty:
  - wysłać pakiet poprzez netlink
  - zwrócić natychmiast NF_CONTINUE.

%package dbi
Summary:	DBI plugin for ulogd
Summary(pl.UTF-8):	Wtyczka DBI dla ulogd
Group:		Networking/Daemons
Requires:	%{name} = %{version}-%{release}

%description dbi
DBI plugin for ulogd.

%description dbi -l pl.UTF-8
Wtyczka DBI dla ulogd.

%package json
Summary:	JSON plugin for ulogd
Summary(pl.UTF-8):	Wtyczka JSON dla ulogd
Group:		Networking/Daemons
Requires:	%{name} = %{version}-%{release}

%description json
JSON plugin for ulogd.

%description json -l pl.UTF-8
Wtyczka JSON dla ulogd.

%package mysql
Summary:	MySQL plugin for ulogd
Summary(pl.UTF-8):	Wtyczka MySQL dla ulogd
Group:		Networking/Daemons
Obsoletes:	iptables-ulogd-mysql
Requires:	%{name} = %{version}-%{release}

%description mysql
MySQL plugin for ulogd.

%description mysql -l pl.UTF-8
Wtyczka MySQL dla ulogd.

%package pcap
Summary:	PCAP plugin for ulogd
Summary(pl.UTF-8):	Wtyczka PCAP dla ulogd
Group:		Networking/Daemons
Requires:	%{name} = %{version}-%{release}

%description pcap
PCAP plugin for ulogd.

%description pcap -l pl.UTF-8
Wtyczka PCAP dla ulogd.

%package pgsql
Summary:	PostgreSQL plugin for ulogd
Summary(pl.UTF-8):	Wtyczka PostgreSQL dla ulogd
Group:		Networking/Daemons
Requires:	%{name} = %{version}-%{release}

%description pgsql
PostgreSQL plugin for ulogd.

%description pgsql -l pl.UTF-8
Wtyczka PostgreSQL dla ulogd.

%package sqlite
Summary:	SQLite plugin for ulogd
Summary(pl.UTF-8):	Wtyczka SQLite dla ulogd
Group:		Networking/Daemons
Requires:	%{name} = %{version}-%{release}

%description sqlite
SQLite plugin for ulogd.

%description sqlite -l pl.UTF-8
Wtyczka SQLite dla ulogd.

%prep
%setup -q
%patch0 -p1
%patch1 -p0
%patch2 -p1
%patch3 -p1
%patch4 -p1

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--disable-silent-rules \
	--with-dbi \
	--with-dbi-lib=%{_libdir} \
	--with-mysql \
	--with-pgsql
%{__make} -j1

cd doc
sgml2html -s 0 ulogd.sgml

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},/etc/{sysconfig,logrotate.d,rc.d/init.d,ulogd}} \
	$RPM_BUILD_ROOT/var/log/{archive/ulog,ulog}

%{__make} install -j1 \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ulogd
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/ulogd
install %{SOURCE3} $RPM_BUILD_ROOT/etc/logrotate.d/ulogd
install %{name}.conf $RPM_BUILD_ROOT/etc/%{name}.conf

%{__rm} $RPM_BUILD_ROOT%{_libdir}/ulogd/*.la

touch $RPM_BUILD_ROOT/var/log/ulog/ulogd{,.pktlog}

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add ulogd
%service ulogd restart "ulogd daemon"

%preun
if [ "$1" = "0" ]; then
	%service ulogd stop
	/sbin/chkconfig --del ulogd
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS README TODO doc/ulogd.html
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/ulogd
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ulogd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/ulogd
%attr(750,root,root) %dir %{_sysconfdir}/ulogd
%attr(754,root,root) /etc/rc.d/init.d/ulogd

%attr(755,root,root) %{_sbindir}/ulogd
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
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_GRAPHITE.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_LOGEMU.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_NACCT.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_OPRINT.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_SYSLOG.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_XML.so
%attr(755,root,root) %{_libdir}/ulogd/ulogd_raw2packet_BASE.so

%attr(750,root,root) %dir /var/log/archive/ulog
%attr(750,root,root) %dir /var/log/ulog
%attr(640,root,root) %ghost /var/log/ulog/ulogd
%attr(640,root,root) %ghost /var/log/ulog/ulogd.pktlog
%{_mandir}/man8/ulogd.8*

%files dbi
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_DBI.so

%files json
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_JSON.so

%files mysql
%defattr(644,root,root,755)
%doc doc/mysql*.sql
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_MYSQL.so

%files pcap
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_PCAP.so

%files pgsql
%defattr(644,root,root,755)
%doc doc/pgsql*.sql
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_PGSQL.so

%files sqlite
%defattr(644,root,root,755)
%doc doc/sqlite3.table
%attr(755,root,root) %{_libdir}/ulogd/ulogd_output_SQLITE3.so
