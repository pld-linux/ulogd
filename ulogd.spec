Summary:	ULOGD - the Userspace Logging Daemon for iptables
Summary(pl):	Demon loguj±cy w trybie u¿ytkownika dla iptables
Name:		ulogd
Version:	0.98
Release:	1
License:	GPL
Group:		Networking/Daemons
Source0:	ftp://ftp.netfilter.org/pub/ulogd/%{name}-%{version}.tar.gz
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.logrotate
Source4:	%{name}.conf
URL:		http://www.gnumonks.org/projects/ulogd
BuildRequires:	autoconf
BuildRequires:	mysql-devel
Requires(post,preun):	/sbin/chkconfig
Requires(post):	fileutils
#Requires:	kernel >= 2.4.0test9
Requires:	iptables
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc

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
Requires:	mysql
Obsoletes:	iptables-ulogd-mysql

%description mysql
MySQL plugin for ulogd.

%description mysql -l pl
Wtyczka MySQL dla ulogd.

%prep
%setup -q

%build
%{__autoconf}
%configure \
	--with-mysql
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},/etc/{sysconfig,logrotate.d,rc.d/init.d}} \
	$RPM_BUILD_ROOT/var/log

%{__make} install DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ulogd
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/ulogd
install %{SOURCE3} $RPM_BUILD_ROOT/etc/logrotate.d/ulogd
install %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}


touch $RPM_BUILD_ROOT/var/log/ulogd{,.pktlog}

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ ! -f /var/log/ulogd ]; then
	touch /var/log/ulogd{,.pktlog}
	chmod 640 /var/log/ulogd{,.pktlog}
fi

/sbin/chkconfig --add ulogd
if [ -f /var/lock/subsys/ulogd ]; then
	/etc/rc.d/init.d/ulogd restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/ulogd start\" to start ulogd daemon." 1>&2
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/ulogd ]; then
		/etc/rc.d/init.d/ulogd stop 1>&2
	fi
	/sbin/chkconfig --del ulogd
fi

%files
%defattr(644,root,root,755)
%doc Changes doc/*.{ps,txt,html}
%attr(640,root,root) %config(noreplace) %verify(not mtime md5 size) /etc/sysconfig/ulogd
%attr(640,root,root) %config(noreplace) %verify(not mtime md5 size) %{_sysconfdir}/ulogd.conf
%attr(640,root,root) /etc/logrotate.d/ulogd
%attr(754,root,root) /etc/rc.d/init.d/ulogd

%attr(755,root,root) %{_sbindir}/*
%attr(755,root,root) %{_libdir}/ulogd/ulogd_[BLOP]*.so

%attr(640,root,root) %ghost /var/log/*

%files mysql
%defattr(644,root,root,755)
%doc doc/mysql*
%attr(755,root,root) %{_libdir}/ulogd/ulogd_MYSQL.so
