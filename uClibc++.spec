%define	libname	%mklibname %{name} %{version}
%define	libdev	%mklibname %{name} -d

Summary:	A C++ standard library for uClibc
Name:		uClibc++
Version:	0.2.4
Release:	8
License:	LGPLv2.1
Group:		System/Libraries
URL:		http://cxx.uclibc.org/
Source0:	http://cxx.uclibc.org/src/%{name}-%{version}.tar.xz
Source1:	uClibc++-0.2.4-config
Patch0:		uClibc++-0.2.4-drop-dead-linker-flags.patch
Patch1:		uClibc++-0.2.4-wrapper-env-variables.patch
Patch2:		uClibc++-0.2.4-dont-force-stripping-during-linking.patch
Patch3:		uClibc++-0.2.4-fix-good-output-of-valarraytest.patch
Patch4:		uClibc++-0.2.4-devel-prefix.patch
Patch5:		uClibc++-0.2.4-string-getline-noskipws-fix.patch
Patch6:		uClibc++-0.2.4-fix-ordered-comparison-of-pointer-with-integer-zero.patch
Patch7:		uClibc++-0.2.4-add-missing-istream-operator-implementation.patch
Patch8:		arm-eabi_fix.patch
BuildRequires:	stdc++-static-devel uClibc-devel >= 0.9.33.2-15

%description
uClibc++ is a C++ standard library targeted towards the embedded
systems/software market. As such it may purposefully lack features
which you might normally expect to find in a full fledged C++ standard
library. The library will focus on space savings as opposed to performance.

%package -n	uclibc-%{libname}
Summary:	A C++ standard library for uClibc
Group:		System/Libraries
%rename		%{libname}

%description -n	uclibc-%{libname}
uClibc++ is a C++ standard library targeted towards the embedded
systems/software market. As such it may purposefully lack features
which you might normally expect to find in a full fledged C++ standard
library. The library will focus on space savings as opposed to performance.

%package -n	uclibc-%{libdev}
Summary:	Development files & libraries for uClibc++
Group:		Development/C
Requires:	uclibc-%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}
%rename		%{name}
%rename		%{libdev}

%description -n	uclibc-%{libdev}
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
%patch4 -p1 -b .devel~
%patch5 -p1 -b .gl_noskipws~
%patch6 -p1 -b .ptr_cmp~
%patch7 -p1 -b .istream_op~
%patch8 -p1 -b .arm_eabi
sed -e 's#/lib64#/%{_lib}#g' %{SOURCE1} > .config

# using 'rpm --eval' here for multilib purposes..
#TODO: figure out binutils --sysroot + multilib in binutils package?
cat > %{uclibc_cxx} << EOF
#!/bin/sh
export C_INCLUDE_PATH="\$(rpm --eval %%{uclibc_root}%%{_includedir}):\$(gcc -print-search-dirs|grep install:|cut -d\  -f2)include"
#XXX: this should add rpath, but for some reason it no longer happens and we
# have to pass the -rpath option to the linker as well
export LD_RUN_PATH="\$(rpm --eval %%{uclibc_root}/%%{_lib}:%%{uclibc_root}%%{_libdir})"
export LIBRARY_PATH="\$LD_RUN_PATH"
exec g++ -muclibc -I%{uclibc_root}%{_includedir} -I%{uclibc_root}%{_includedir}/c++ -Wl,-rpath="\$LD_RUN_PATH" -Wl,-nostdlib -nodefaultlibs -DGCC_HASCLASSVISIBILITY "\$@"  -luClibc++
EOF
chmod +x %{uclibc_cxx}

%build
yes "" | %make oldconfig
export PATH="$PWD:$PATH"
%make CC="%{uclibc_cc}" OPTIMIZATION="%{uclibc_cflags} -std=gnu++11" BUILD_EXTRA_LIBRARIES="%{ldflags}" STRIPTOOL="/bin/true" WR_CXX="%{uclibc_cxx} -I../include -L../src"

# skip test as the test suite will compare float values which has different precission on cpus..
%ifnarch %{ix86}
%check
export PATH="$PWD:$PATH"
mkdir -p test
sed -e "s#%{uclibc_root}/%{_lib}/libuClibc++.so#$PWD/src/libuClibc++.so#g" src/libuClibc++.so > test/libuClibc++.so
%make check VERBOSE=2 CC="%{uclibc_cc}" OPTIMIZATION="%{uclibc_cflags} -std=gnu++11" BUILD_EXTRA_LIBRARIES="%{ldflags}" STRIPTOOL="/bin/true" WR_CXX="%{uclibc_cxx} -I../include -L../test"
%endif

%install
%makeinstall_std

install -m755 %{uclibc_cxx} -D %{buildroot}%{_bindir}/%{uclibc_cxx}

rm -f %{buildroot}%{uclibc_root}/bin/g++-uc


%files -n uclibc-%{libname}
%{uclibc_root}/%{_lib}/libuClibc++-%{version}.so
%{uclibc_root}/%{_lib}/libuClibc++.so.*

%files -n uclibc-%{libdev}
%{_bindir}/%{uclibc_cxx}
%{uclibc_root}%{_libdir}/libuClibc++.a
%{uclibc_root}%{_libdir}/libuClibc++.so
%dir %{uclibc_root}%{_includedir}/c++
%{uclibc_root}%{_includedir}/c++/*
