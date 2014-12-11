%define	libname	%mklibname %{name} %{version}
%define	libdev	%mklibname %{name} -d

%ifarch %{ix86}
%global ldflags %{ldflags} -fuse-ld=bfd
%endif

Summary:	A C++ standard library for uClibc
Name:		uClibc++
Version:	0.2.4
Release:	20
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
# fixes issue with not treati0001-Make-std-move-POD-avare.patchng as ios_base::right if no adjustfield flag set
# also implements handling of ios_base::internal
Patch9:		uClibc++-0.2.4-fix-ostream-adjustfield.patch
Patch10:	uClibc++-0.2.4-pass-strings-to-ostream-hack.patch
Patch11:	uClibc++-0.2.4-fix-lgcc_s-lgcc_eh-lsupc++.patch
Patch12:	uClibc++-0.2.4-add-cstdint-header.patch
Patch13:	uClibc++-0.2.4-drop-libsupc++-atexit_thread-object.patch

# patches from https://github.com/kibergus/StandardCplusplus
Patch101:	0001-Lacking-realization-of-std-terminate.-Call-terminate.patch
Patch102:	0001-Fix-std-find-to-use-operator-as-gcc-stdlibc-does.patch
Patch103:	uClibc++-0.2.4-add-initializer_list-and-construct-vector-from-one.patch
Patch104:	0001-Add-free-functions-begin-container-and-end-container.patch
Patch105:	0001-std-move-and-std-forward.patch
Patch106:	0001-Rewrite-lower_bound-and-upper_bound-in-a-more-compac.patch
Patch107:	uClibc++-0.2.4-Add-FIXME-to-problem-places-in-vector-realization.patch
Patch108:	uClibc++-0.2.4-optimized-copy-and-realization-for-std-move-std-move.patch
Patch109:	uClibc++-0.2.4-Allow-gcc-to-utilize-ld-st-with-increment-decrement-.patch
Patch110:	0001-allocator-now-supports-emplace-construction.patch
Patch111:	uClibc++-0.2.4-POD-avare-std-copy.patch
Patch112:	uClibc++-0.2.4-Make-std-move-POD-aware.patch

# patches from https://github.com/rpavlik/uClibcpp
Patch150:	0001-Extend-limits-more-types-some-implementations.patch

# fix borkage in P106
Patch200:	uClibc++-0.2.4-fix-upper_bounds-and-lower_bounds.patch

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
%patch8 -p1 -b .arm_eabi~
%patch9 -p1 -b .adjust~
%patch10 -p1 -b .ostr~
%patch11 -p1 -b .lsupc++~
%patch12 -p1 -b .cstdint~
%patch13 -p1 -b .atexit_thread~

%patch101 -p1 -b .terminate~
%patch102 -p1 -b .stdfind~
%patch103 -p1 -b .init_list~
%patch104 -p1 -b .container_free~
%patch105 -p1 -b .std_move~
%patch106 -p1 -b .bounds~
%patch107 -p1 -b .vector_realiz~
%patch108 -p1 -b .copy_opt~
%patch109 -p1 -b .inc_dec~
%patch110 -p1 -b .emplace_construct~
%patch111 -p1 -b .pod_copy~
%patch112 -p1 -b .pod_move~

%patch150 -p1 -b .extlimits~

%patch200 -p1 -b .bounds_fix~

sed -e 's#/lib64#/%{_lib}#g' %{SOURCE1} > .config
%ifarch %arm
sed -i 's/UCLIBCXX_HAS_LONG_DOUBLE=y/UCLIBCXX_HAS_LONG_DOUBLE=n/g' .config
%endif

cat > %{uclibc_cxx} << EOF
exec g++ -muclibc -nodefaultlibs -nostdinc++ -isystem %{uclibc_root}%{_includedir}/c++ -specs=%{uclibc_root}%{_datadir}/uclibc-gcc.specs  -DGCC_HASCLASSVISIBILITY "\$@"  -luClibc++
EOF
chmod +x %{uclibc_cxx}

%build
yes "" | %make oldconfig
export PATH="$PWD:$PATH"
%make TOPDIR="$PWD/" CC="%{uclibc_cxx}" OPTIMIZATION="%{uclibc_cflags} -std=gnu++11" BUILD_EXTRA_LIBRARIES="%{ldflags}" STRIPTOOL="/bin/true" WR_CXX="%{uclibc_cxx} -I../include -L../src -L../src/abi" IMPORT_LIBGCC_EH=y IMPORT_LIBGCC_SUPC=y 

# skip test as the test suite will compare float values which has different precission on cpus..
%check
export PATH="$PWD:$PATH"
mkdir -p test
sed -e "s#%{uclibc_root}/%{_lib}/libuClibc++.so#$PWD/src/libuClibc++.so#g" src/libuClibc++.so > test/libuClibc++.so
%make check TOPDIR="$PWD/" VERBOSE=2 CC="%{uclibc_cxx}" OPTIMIZATION="%{uclibc_cflags} -std=gnu++11" BUILD_EXTRA_LIBRARIES="%{ldflags}" STRIPTOOL="/bin/true" WR_CXX="%{uclibc_cxx} -I../include -L../test -L../src/abi" IMPORT_LIBGCC_EH=y IMPORT_LIBGCC_SUPC=y \
%ifarch %{ix86}
|| true
%endif

%install
%makeinstall_std

cp -a include/bits %{buildroot}%{uclibc_root}%{_includedir}/c++/bits
install -m755 %{uclibc_cxx} -D %{buildroot}%{_bindir}/%{uclibc_cxx}

rm %{buildroot}%{uclibc_root}/bin/g++-uc


%files -n uclibc-%{libname}
%{uclibc_root}/%{_lib}/libuClibc++-%{version}.so
%{uclibc_root}/%{_lib}/libuClibc++.so.*

%files -n uclibc-%{libdev}
%{_bindir}/%{uclibc_cxx}
%{uclibc_root}%{_libdir}/libuClibc++.a
%{uclibc_root}%{_libdir}/libuClibc++.so
%dir %{uclibc_root}%{_includedir}/c++
%{uclibc_root}%{_includedir}/c++/*
