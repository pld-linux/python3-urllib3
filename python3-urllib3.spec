# TODO: use system [backports.]ssl_match_hostname
#
# Conditional build:
%bcond_without	doc	# Sphinx documentation
%bcond_without	tests	# unit tests

%define		module		urllib3
Summary:	HTTP library with thread-safe connection pooling, file post, and more
Summary(pl.UTF-8):	Biblioteka HTTP z bezpieczną wątkowo pulą połączeń, wysyłaniem plików itd.
Name:		python3-%{module}
Version:	2.7.0
Release:	2
License:	MIT
Group:		Development/Languages/Python
#Source0Download: https://pypi.org/simple/urllib3/
Source0:	https://files.pythonhosted.org/packages/source/u/urllib3/%{module}-%{version}.tar.gz
# Source0-md5:	e79707b798a66c8165c9c441440f4e80
Patch0:		urllib3-parametrize-list.patch
URL:		https://urllib3.readthedocs.io/
%if %(locale -a | grep -q '^C\.utf8$'; echo $?)
BuildRequires:	glibc-localedb-all
%endif
BuildRequires:	python3 >= 1:3.9
BuildRequires:	python3-build >= 1.2.2.post1
BuildRequires:	python3-hatch-vcs >= 0.4.0
BuildRequires:	python3-hatch-vcs < 0.6
BuildRequires:	python3-hatchling >= 1.27.0
BuildRequires:	python3-hatchling < 2
BuildRequires:	python3-installer
BuildRequires:	python3-modules >= 1:3.9
BuildRequires:	python3-setuptools_scm >= 8
BuildRequires:	python3-setuptools_scm < 10
%if %{with tests}
BuildRequires:	python3-PySocks >= 1.7.1
BuildRequires:	python3-PySocks < 2
BuildRequires:	python3-anyio >= 4.8.0
%if "%{_ver_lt %{py3_ver} 3.14}" == "1"
BuildRequires:	python3-backports.zstd >= 1.0.0
%endif
BuildRequires:	python3-brotli >= 1.2.0
BuildRequires:	python3-cryptography >= 44.0.2
BuildRequires:	python3-h2 >= 4.1.0
BuildRequires:	python3-h2 < 5
BuildRequires:	python3-httpx >= 0.28.1
BuildRequires:	python3-hypercorn >= 0.15.0
BuildRequires:	python3-idna >= 3.10
BuildRequires:	python3-pyOpenSSL >= 25.0.0
BuildRequires:	python3-pytest >= 8.3.4
BuildRequires:	python3-pytest-memray >= 1.8.0
BuildRequires:	python3-pytest-socket >= 0.7.0
BuildRequires:	python3-pytest-timeout >= 2.3.1
BuildRequires:	python3-quart >= 0.20.0
BuildRequires:	python3-quart-trio >= 0.12.0
BuildRequires:	python3-trio >= 0.27.0
BuildRequires:	python3-trustme >= 1.2.1
# SO_REUSEPORT option
BuildRequires:	uname(release) >= 3.9
%endif
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 2.044
%if %{with doc}
BuildRequires:	python3-furo >= 2024.8.6
BuildRequires:	python3-requests >= 2.32.3
BuildRequires:	python3-sphinx_copybutton >= 0.5.2
BuildRequires:	python3-sphinxext.opengraph >= 0.9.1
BuildRequires:	sphinx-pdg-3 >= 7.2.6
%endif
Requires:	python3-modules >= 1:3.9
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Python HTTP module with connection pooling and file POST abilities.
Features are:
- Re-use the same socket connection for multiple requests (with
  optional client-side certificate verification).
- File posting (encode_multipart_formdata).
- Built-in redirection and retries (optional).
- Supports gzip and deflate decoding.
- Thread-safe and sanity-safe.

%description -l pl.UTF-8
Moduł HTTP dla Pythona z pulą połączeń i możliwością wysyłania
plików metodą POST. Możliwości:
- używanie tego samego połączenia dla wielu żądań (z opcjonalną
  weryfikacją certyfikatu po stronie klienta)
- wysyłanie plików (encode_multipart_formdata)
- wbudowane przekierowania i ponawianie prób (opcjonalne)
- obsługa kodowań gzip i deflate
- bezpieczeństwo względem wątków.

%package apidocs
Summary:	API documentation for Python urllib3 module
Summary(pl.UTF-8):	Dokumentacja API modułu Pythona urllib3
Group:		Documentation

%description apidocs
API documentation for Python urllib3 module.

%description apidocs -l pl.UTF-8
Dokumentacja API modułu Pythona urllib3.

%prep
%setup -q -n %{module}-%{version}
%patch -P0 -p1

%build
%py3_build_pyproject

%if %{with tests}
# TestHTTPS_TLSv1_[23] tests: fail because of no ["extensions"]["tls"] key in quart request scope(???)
# test_http2_probe_blocked_per_thread: needs TARPIT_HOST 240.0.0.0 to hang, it fails instantly without net
# TestHTTPProxyManager and TestHTTPSProxyVerification: the CONNECT proxy in dummyserver/asgi_proxy.py
# needs scope["extensions"]["_transport"] to hijack the socket; hypercorn 0.18 exposes no ASGI extensions at all
PYTHONPATH=$(pwd)/src \
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTEST_PLUGINS="anyio.pytest_plugin,pytest_memray.plugin,pytest_socket,pytest_timeout" \
%{__python3} -m pytest test -k 'not (test_client_intermediate or test_client_key_password or test_alpn_default or test_http2_probe_result_is_cached or test_basic_proxy or test_https_proxy or test_is_verified_http_proxy_to_https_target or test_is_verified_https_proxy_to_https_target or test_http_and_https_kwarg_ca_cert_data_proxy or test_https_proxy_with_proxy_ssl_context or test_oldapi or test_proxy_verified or test_headers or test_https_headers or test_proxy_pooling or test_scheme_host_case_insensitive or test_https_proxy_assert_fingerprint_md5 or test_https_proxy_assert_hostname or test_https_proxy_ipv4_san or test_https_proxy_ipv6_san or test_https_proxy_no_san_hostname_checks_common_name or test_proxy_https_target_tls_error or test_proxy_https_fqdn or test_cross_protocol_redirect or test_http2_probe_blocked_per_thread)'
%endif

%if %{with doc}
%{__make} -C docs html \
	SPHINXBUILD=sphinx-build-3 \
	SPHINXOPTS=
%endif

%install
rm -rf $RPM_BUILD_ROOT

%py3_install_pyproject

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc CHANGES.rst LICENSE.txt README.md
%{py3_sitescriptdir}/urllib3
%{py3_sitescriptdir}/urllib3-%{version}.dist-info

%if %{with doc}
%files apidocs
%defattr(644,root,root,755)
%doc docs/_build/html/{_images,_static,reference,*.html,*.js}
%endif
