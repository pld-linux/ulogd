# TODO: (maybe ;)
# - pgsql support
# - sqlite support
Summary:	ULOGD - the Userspace Logging Daemon for iptables
Summary(pl):	Demon loguj±cy w trybie u¿ytkownika dla iptables
Name:		ulogd
Version:	1.23
Release:	2
License:	GPL
Group:		Networking/Daemons
Source0:	ftp://ftp.netfilter.org/pub/ulogd/%{name}-%{version}.tar.bz2
# Source0-md5:	fa3dfcaacf31855626d5b731b04a077f
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.logrotate
Patch0:		%{name}-includes.patch
URL:		http://gnumonks.org/projects/ulogd/
BuildRequires:	autoconf
BuildRequires:	mysql-devel
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	sed >= 4.0
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

%description -l pl
Ten pakiet ma s³u¿yæ do wysy³ania pakietów z j±dra do przestrzeni
u¿ytkownika w celu logowania. Powinien dzia³aæ tak:
- zarejestrowaæ w netfilterze cel o nazwie ULOG
- je¿eli cel zosta³ osi±gniêty:
  - wys³aæ pakiet poprzez netlink
  - zwróciæ natychmiast NF_ACCEPT.

%package mysql
Summary:	MySQL plugin for ulogd
Summary(pl):	Wtyczka MySQL dla ulogd
Group:		Networking/Daemons
Obsoletes:	iptables-ulogd-mysql

%description mysql
MySQL plugin for ulogd.

%description mysql -l pl
Wtyczka MySQL dla ulogd.

%prep
%setup -q
%patch0 -p1

%build
%if "%{_lib}" != "lib"
sed -e 's@lib/@%{_lib}/@g' -i configure.in
sed -e 's@${MYSQLLIBS}@%{_libdir}@g' -i configure.in
%endif

%{__autoconf}
%configure \
	--with-mysql
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},/etc/{sysconfig,logrotate.d,rc.d/init.d,ulogd}} \
	$RPM_BUILD_ROOT/var/log

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ulogd
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/ulogd
install %{SOURCE3} $RPM_BUILD_ROOT/etc/logrotate.d/ulogd
install -D %{name}.8 $RPM_BUILD_ROOT/%{_mandir}/man8/%{name}.8

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
%doc Changes doc/*.{ps,txt,html}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/ulogd
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ulogd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/ulogd
%attr(750,root,root) %dir %{_sysconfdir}/ulogd
%attr(754,root,root) /etc/rc.d/init.d/ulogd

%attr(755,root,root) %{_sbindir}/*
%dir %{_libdir}/ulogd
%attr(755,root,root) %{_libdir}/ulogd/ulogd_[BLOPS]*.so

%attr(640,root,root) %ghost /var/log/*
%{_mandir}/man?/%{name}.*

%files mysql
%defattr(644,root,root,755)
%doc doc/mysql*
%attr(755,root,root) %{_libdir}/ulogd/ulogd_MYSQL.so
