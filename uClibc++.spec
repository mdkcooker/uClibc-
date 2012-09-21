%define	uclibc_cxx	uclibc-g++

Summary:	A C library optimized for size useful for embedded applications
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

%description
uClibc (pronounced yew-see-lib-see) is a c library for developing
embedded linux systems. it is much smaller than the gnu c library,
but nearly all applications supported by glibc also work perfectly
with uclibc. porting applications from glibc to uclibc typically
involves just recompiling the source code. uclibc even supports
shared libraries and threading. it currently runs on standard
linux and  mmu-less (also known as uclinux) systems with support
for alpha, arm, cris, i386, i960, h8300, m68k, mips/mipsel,
powerpc, sh, sparc, and v850 processors.

if you are building an embedded linux system and you find that
glibc is eating up too much space, you should consider using
uclibc. if you are building a huge fileserver with 12 terabytes of
storage, then using glibc may make more sense. unless, for
example, that 12 terabytes will be network attached storage and
you plan to burn linux into the system's firmware...

%define	libname	%mklibname %{name} %{version}
%package -n	%{libname}
Summary:	A C++ standard library for uClibc
Group:		System/Libraries

%description -n	%{libname}
uClibc (pronounced yew-see-lib-see) is a c library for developing
embedded linux systems. it is much smaller than the gnu c library,
but nearly all applications supported by glibc also work perfectly
with uclibc. porting applications from glibc to uclibc typically
involves just recompiling the source code. uclibc even supports
shared libraries and threading. it currently runs on standard
linux and  mmu-less (also known as uclinux) systems with support
for alpha, arm, cris, i386, i960, h8300, m68k, mips/mipsel,
powerpc, sh, sparc, and v850 processors.

if you are building an embedded linux system and you find that
glibc is eating up too much space, you should consider using
uclibc. if you are building a huge fileserver with 12 terabytes of
storage, then using glibc may make more sense. unless, for
example, that 12 terabytes will be network attached storage and
you plan to burn linux into the system's firmware...

%define	libdev	%mklibname %{name} -d
%package -n	%{libdev}
Summary:	Development files & libraries for uClibc
Group:		Development/C
Requires:	%{libname} = %{EVRD}

%description -n	%{libdev}
Small libc for building embedded applications.

%prep
%setup -q
%patch0 -p1 -b .no_warn_once~
%patch1 -p1 -b .gcc_envvars~
%patch2 -p1 -b .nostrip~
%patch3 -p1 -b .valtest~
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
exec g++ -muclibc -I%{uclibc_root}%{_includedir} -I%{uclibc_root}%{_includedir}/c++ -Wl,-rpath="\$LD_RUN_PATH" -nodefaultlibs -DGCC_HASCLASSVISIBILITY "\$@"  -lc -luClibc++ -lgcc -lgcc_eh
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

install -m755 %{uclibc_cxx} -D %{buildroot}%{uclibc_root}%{_bindir}/%{uclibc_cxx}
install -m644 %{name}.macros -D %{buildroot}%{_sysconfdir}/rpm/macros.d/%{name}.macros

rm -f %{buildroot}%{uclibc_root}/bin/g++-uc


%files
%{uclibc_root}%{_bindir}/%{uclibc_cxx}
%{_sysconfdir}/rpm/macros.d/%{name}.macros

%files -n %{libname}
%{uclibc_root}/%{_lib}/libuClibc++-%{version}.so
%{uclibc_root}/%{_lib}/libuClibc++.so.*

%files -n %{libdev}
%{uclibc_root}/%{_lib}/libuClibc++.a
%{uclibc_root}/%{_lib}/libuClibc++.so
%dir %{uclibc_root}%{_includedir}/c++
%{uclibc_root}%{_includedir}/c++/*

