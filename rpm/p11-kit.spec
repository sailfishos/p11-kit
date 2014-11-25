Name:           p11-kit
Version:        0.22.1
Release:        1
Summary:        Library for loading and sharing PKCS#11 modules

License:        BSD
URL:            http://p11-glue.freedesktop.org/p11-kit.html
Source0:        http://p11-glue.freedesktop.org/releases/p11-kit-%{version}.tar.gz
Source1:        trust-extract-compat
Patch0:         0001-Remove-serial-tests-flag-to-fix-automake-1.11.patch
BuildRequires:  libtasn1-devel >= 2.3
BuildRequires:  nss-softokn-freebl
BuildRequires:  libffi-devel
BuildRequires:  gettext-devel
BuildRequires:  gettext-libs
Requires:       p11-kit-nss-ckbi = %{version}-%{release}

%description
p11-kit provides a way to load and enumerate PKCS#11 modules, as well
as a standard configuration setup for installing PKCS#11 modules in
such a way that they're discoverable.


%package devel
Summary:        Development files for %{name}
Requires:       %{name} = %{version}-%{release}

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%package trust
Summary:        System trust module from %{name}
Requires:       %{name} = %{version}-%{release}

%description trust
The %{name}-trust package contains a system trust PKCS#11 module which
contains certificate anchors and black lists.


%package nss-ckbi
Summary:        Replacement CA library for NSS
Requires:       %{name}-trust = %{version}-%{release}
Provides:       nss-ckbi
Obsoletes:      nss-ckbi

%description nss-ckbi
This package replaces the nss-ckbi library with a compatible version that loads
CA certificates from the p11-kit trust module.


%prep
%setup -q -n %{name}-%{version}/%{name}
%patch0 -p1

%build
export NOCONFIGURE=1
%autogen
# These paths are the source paths that  come from the plan here:
# https://fedoraproject.org/wiki/Features/SharedSystemCertificates:SubTasks
%configure --disable-static --with-trust-paths=%{_sysconfdir}/pki/ca-trust/source:%{_datadir}/pki/ca-trust-source --with-hash-impl=freebl --disable-silent-rules
make %{?_smp_mflags} V=1

%install
make install DESTDIR=$RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/pkcs11/modules
rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/pkcs11/*.la
install -p -m 755 %{SOURCE1} $RPM_BUILD_ROOT%{_libdir}/p11-kit/
# Install the example conf with %%doc instead
rm $RPM_BUILD_ROOT%{_sysconfdir}/pkcs11/pkcs11.conf.example
ln -s %{_libdir}/pkcs11/p11-kit-trust.so $RPM_BUILD_ROOT%{_libdir}/libnssckbi.so

%check
make check


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%doc COPYING AUTHORS NEWS README
%doc p11-kit/pkcs11.conf.example
%dir %{_sysconfdir}/pkcs11
%dir %{_sysconfdir}/pkcs11/modules
%dir %{_datadir}/p11-kit
%dir %{_datadir}/p11-kit/modules
%dir %{_libdir}/p11-kit
%{_bindir}/p11-kit
%{_libdir}/libp11-kit.so.*
%{_libdir}/p11-kit-proxy.so
%{_libdir}/p11-kit/p11-kit-remote

%files devel
%{_includedir}/p11-kit-1/
%{_libdir}/libp11-kit.so
%{_libdir}/pkgconfig/p11-kit-1.pc

%files trust
%{_bindir}/trust
%dir %{_libdir}/pkcs11
%{_libdir}/pkcs11/p11-kit-trust.so
%{_datadir}/p11-kit/modules/p11-kit-trust.module
%{_libdir}/p11-kit/trust-extract-compat

%files nss-ckbi
%{_libdir}/libnssckbi.so
