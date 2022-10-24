%undefine _annotated_build

# Use "--without tests" to disable the testsuite.  The default is to run them.
%bcond_without tests

# Use "--without annocheck" to disable the installation of the annocheck program.
%bcond_without annocheck

# Set this to zero to disable the requirement for a specific version of gcc.
# This should only be needed if there is some kind of problem with the version
# checking logic.
%global with_hard_gcc_version_requirement 1

Name:    annobin
Version: 10.66
Release: 1
Summary: Binary annotation plugin for GCC
License: GPLv3+
URL:     https://fedoraproject.org/wiki/Toolchain/Watermark
Source:  https://nickc.fedorapeople.org/annobin-%{version}.tar.xz
%ifarch riscv64
Patch1:  fix-riscv64-abi.patch
%endif
# For the latest sources use:  git clone git://sourceware.org/git/annobin.git
BuildRequires: gcc gcc-plugin-devel gcc-c++

%description
A plugin for GCC that records extra information in the files that it compiles,
and a set of scripts that analyze the recorded information.  These scripts can
determine things ABI clashes in compiled binaries, or the absence of required
hardening options.

%if %{with tests}
%package tests
Summary: Test scripts and binaries for checking the behaviour and output of the annobin plugin

%description tests
Provides a means to test the generation of annotated binaries and the parsing
of the resulting files.
%endif

%if %{with annocheck}
%package annocheck
Summary: A tool for checking the security hardening status of binaries
BuildRequires: gcc elfutils elfutils-devel elfutils-libelf-devel rpm-devel binutils-devel

%description annocheck
Installs the annocheck program which uses the notes generated by annobin to
check that the specified files were compiled with the correct security
hardening options.
%endif

%global ANNOBIN_PLUGIN_DIR %(gcc --print-file-name=plugin)
%global gcc_vr %(gcc --version | gawk 'match (\$0, ".*Red Hat \([^\\)-]*\)", a) { print a[1]; }')

# This is a gcc plugin, hence gcc is required.
%if %{with_hard_gcc_version_requirement}
Requires: gcc == %{gcc_vr}
BuildRequires: gcc == %{gcc_vr}
%else
Requires: gcc
%endif

%package help
Summary: Documents for annobin
Buildarch: noarch
Requires: man info

%description help
Man pages and other related documents for annobin

%prep
%autosetup -p1
touch aclocal.m4 gcc-plugin/config.h.in
touch configure */configure Makefile.in */Makefile.in
touch doc/annobin.info

%build
%configure --quiet --with-gcc-plugin-dir=%{ANNOBIN_PLUGIN_DIR}
%make_build
cp gcc-plugin/.libs/annobin.so.0.0.0 %{_tmppath}/tmp-annobin.so
make -C gcc-plugin clean
make -C gcc-plugin CXXFLAGS="%{optflags} -fplugin=%{_tmppath}/tmp-annobin.so"
rm %{_tmppath}/tmp-annobin.so

%install
%make_install
%{__rm} -f %{buildroot}%{_infodir}/dir

%if %{with tests}
%check
make check
%endif

%files
%{ANNOBIN_PLUGIN_DIR}
%license COPYING3 LICENSE
%exclude %{_datadir}/doc/annobin-plugin/COPYING3
%exclude %{_datadir}/doc/annobin-plugin/LICENSE
%doc %{_datadir}/doc/annobin-plugin/annotation.proposal.txt
%doc %{_infodir}/annobin.info.gz

%if %{with annocheck}
%{_bindir}/annocheck
%doc %{_mandir}/man1/annocheck.1.gz
%{_includedir}/libannocheck.h
%{_libdir}/libannocheck.*
%endif

%files help
%doc %{_mandir}/man1/annobin.1.gz
%doc %{_mandir}/man1/built-by.1.gz
%doc %{_mandir}/man1/check-abi.1.gz
%doc %{_mandir}/man1/hardened.1.gz
%doc %{_mandir}/man1/run-on-binaries-in.1.gz

%changelog
* Sun Apr 17 2022 YukariChiba <i@0x7f.cc> - 10.66-1
- Upgrade version to 10.66
- Fix 999_illegal_reference_to_global_options due to lookup global_options.x_riscv_abi for POINTER_SIZE

* Thu Feb 13 2020 openEuler Buildteam <buildteam@openeuler.org> - 8.23-2
- Package init

