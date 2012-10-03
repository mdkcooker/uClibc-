%define	uclibc_cxx	uclibc-g++
%define	libname	%mklibname %{name} %{version}
%define	libdev	%mklibname %{name} -d

Summary:	A C++ standard library for uClibc
Name:		uClibc++
Version:	0.2.4
Release:	1
License:	LGPLv2.1
Group:		System/Libraries
URL:		http://uclibc.org/
Source0:	http://cxx.uclibc.org/src/%{name}-%{version}.tar.xz
Source1:	uClibc++-0.2.4-config
Patch0:		uClibc++-0.2.4-drop-dead-linker-flags.patch
Patch1:		uClibc++-0.2.4-wrapper-env-variables.patch
Patch2:		uClibc++-0.2.4-dont-force-stripping-during-linking.patch
Patch3:		uClibc++-0.2.4-fix-good-output-of-valarraytest.patch
Requires:	%{libdev} = %{EVRD}
BuildRequires:	stdc++-static-devel uClibc-devel

%description
uClibc++ is a C++ standard library targeted towards the embedded
systems/software market. As such it may purposefully lack features
which you might normally expect to find in a full fledged C++ standard
library. The library will focus on space savings as opposed to performance.

%package -n	%{libname}
Summary:	A C++ standard library for uClibc
Group:		System/Libraries

%description -n	%{libname}
uClibc++ is a C++ standard library targeted towards the embedded
systems/software market. As such it may purposefully lack features
which you might normally expect to find in a full fledged C++ standard
library. The library will focus on space savings as opposed to performance.

%package -n	%{libdev}
Summary:	Development files & libraries for uClibc++
Group:		Development/C
Requires:	%{libname} = %{EVRD}
%if %{with uclibc}
Requires:	uclibc-%{libname} = %{EVRD}
%endif
Provides:	%{name}-devel = %{EVRD}

%description -n	%{libdev}
uClibc++ is a C++ standard library targeted towards the embedded
systems/software market. As such it may purposefully lack features
which you might normally expect to find in a full fledged C++ standard
library. The library will focus on space savings as opposed to performance.

%prep
%setup -q
%patch0 -p1 -b .no_warn_once~
%patch1 -p1 -b .gcc_envvars~
%patch2 -p1 -b .nostrip~
%ifarch x86_64
%patch3 -p1 -b .valtest~
%endif
cp %{SOURCE1} .config

# using 'rpm --eval' here for multilib purposes..
#TODO: figure out binutils --sysroot + multilib in binutils package?
cat > %{uclibc_cxx} << EOF
#!/bin/sh
export C_INCLUDE_PATH="\$(rpm --eval %%{uclibc_root}%%{_includedir}):\$(gcc -print-search-dirs|grep install:|cut -d\  -f2)include"
#XXX: this should add rpath, but for some reason it no longer happens and we
# have to pass the -rpath option to the linker as well
export LD_RUN_PATH="\$(rpm --eval %%{uclibc_root}/%%{_lib}:%%{uclibc_root}%%{_libdir})"
export LIBRARY_PATH="\$LD_RUN_PATH"
exec g++ -muclibc -I%{uclibc_root}%{_includedir} -I%{uclibc_root}%{_includedir}/c++ -Wl,-rpath="\$LD_RUN_PATH" -Wl,-nostdlib -nodefaultlibs -DGCC_HASCLASSVISIBILITY "\$@"  -lc -luClibc++ -lgcc -lgcc_eh
EOF
chmod +x %{uclibc_cxx}

cat > %{name}.macros << EOF
%%uclibc_cxx		%{uclibc_cxx}
%%uclibc_cxxflags	%%{uclibc_cflags}
EOF

%build
yes "" | %make oldconfig
export PATH=$PWD:$PATH
%make CC="%{uclibc_cc}" OPTIMIZATION="%{uclibc_cflags}" BUILD_EXTRA_LIBRARIES="%{ldflags} -Wl,-O2" STRIPTOOL="/bin/true" WR_CXX="%{uclibc_cxx} -I../include -L../src"

%check
export PATH=$PWD:$PATH
%make check VERBOSE=2 CC="%{uclibc_cc}" OPTIMIZATION="%{uclibc_cflags}" BUILD_EXTRA_LIBRARIES="%{ldflags} -Wl,-O2" STRIPTOOL="/bin/true" WR_CXX="%{uclibc_cxx} -I../include -L../src"

%install
%makeinstall_std

install -m755 %{uclibc_cxx} -D %{buildroot}%{_bindir}/%{uclibc_cxx}
install -m644 %{name}.macros -D %{buildroot}%{_sysconfdir}/rpm/macros.d/%{name}.macros

rm -f %{buildroot}%{uclibc_root}/bin/g++-uc


%files
%{_bindir}/%{uclibc_cxx}
%{_sysconfdir}/rpm/macros.d/%{name}.macros

%files -n %{libname}
%{uclibc_root}/%{_lib}/libuClibc++-%{version}.so
%{uclibc_root}/%{_lib}/libuClibc++.so.*

%files -n %{libdev}
%{uclibc_root}/%{_lib}/libuClibc++.a
%{uclibc_root}/%{_lib}/libuClibc++.so
%dir %{uclibc_root}%{_includedir}/c++
%{uclibc_root}%{_includedir}/c++/*

