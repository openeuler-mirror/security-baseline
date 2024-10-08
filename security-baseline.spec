Summary:        CtyunOS security-baseline
Name:           security-baseline
Version:        0.1.1
Release:        8
License:        MulanPSL v2
URL:            https://gitlab.ctyun.cn/org-ctyunos/security-baseline

Provides:       security-baseline
BuildRequires:	 python3
Requires:       wget git util-linux bash
Requires:       coreutils python3 python3-pip
Source1:        %{name}-%{version}.tar.gz

%description
This package provides ecurity-baseline.

Provides:       %{name} = %{version}-%{release}

%prep
tar -xvf %{_sourcedir}/%{name}-%{version}.tar.gz


%build
cd %{name}

%install
cd %{_builddir}/%{name}

#install -d -m 755 $RPM_BUILD_ROOT/usr/share/security-baseline/scripts
install -d -m 755 $RPM_BUILD_ROOT/usr/share/security-baseline/bin
install -d -m 755 $RPM_BUILD_ROOT/usr/bin/
ls  %{_sourcedir}
pip3 install pyinstaller
pip3 install prettytable
pyinstaller  -F   %{_builddir}/%{name}/main.py
mv dist/main security-baseline
rm  -rf dist
rm -rf build
ls
#install -m 755 %{_builddir}/%{name}/* $RPM_BUILD_ROOT/usr/share/security-baseline/scripts/
install -m 755 %{_builddir}/%{name}/security-baseline $RPM_BUILD_ROOT/usr/bin/security-baseline

%files
#/usr/share/security-baseline/*
/usr/bin/security-baseline


%postun
if [ $1 == 0 ]; then             
        rm -f /usr/bin/security-baseline
        rm -rf /usr/share/security-baseline/
fi



%post

%changelog
* Mon Mar 20 2023 wuksh <wuksh@chinatelecom.com> - 0.1.1-8
- update 0.1 version


