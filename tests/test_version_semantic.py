import pytest

from sphinx_external_toc_strict._version import (
    __version__,
    __version_tuple__,
)
from sphinx_external_toc_strict.version_semantic import (
    Version,
    _map_release,
    get_version,
    readthedocs_url,
    remove_v,
    sanitize_tag,
)

testdata_v = (
    ("v1.0.1", "1.0.1"),
    ("0!v1.0.1", "0!1.0.1"),
    ("1!v1.0.1", "1!1.0.1"),
    ("0!v1.0.1+g4b33a80.d20240129", "0!1.0.1+g4b33a80.d20240129"),
    ("1!v1.0.1+g4b33a80.d20240129", "1!1.0.1+g4b33a80.d20240129"),
    ("v0.1.1.dev0+g4b33a80.d20240129", "0.1.1.dev0+g4b33a80.d20240129"),
    ("v0.1.1.post0+g4b33a80.d20240129", "0.1.1.post0+g4b33a80.d20240129"),
    ("v0.1.1.a1dev1+g4b33a80.d20240129", "0.1.1.a1dev1+g4b33a80.d20240129"),
    ("v0.1.1.alpha1dev1+g4b33a80.d20240129", "0.1.1.alpha1dev1+g4b33a80.d20240129"),
    ("v0.1.1.b1dev1+g4b33a80.d20240129", "0.1.1.b1dev1+g4b33a80.d20240129"),
    ("v0.1.1.beta1dev1+g4b33a80.d20240129", "0.1.1.beta1dev1+g4b33a80.d20240129"),
    ("v0.1.1.rc1dev1+g4b33a80.d20240129", "0.1.1.rc1dev1+g4b33a80.d20240129"),
)


@pytest.mark.parametrize(
    "v_in, expected",
    testdata_v,
)
def test_remove_prepended_v(v_in, expected):
    """Contains a prepended v which is like a proverbial monkey+wrench+cog works.
    Only removes prepended v, **does not** fix with Version
    """
    actual = remove_v(v_in)
    assert actual == expected


testdata_valids = (
    ("0.0.1", "0.0.1"),  # tagged final version
    ("0.1.1.dev0+g4b33a80.d20240129", "0.1.1.dev0"),
    ("0.1.1.dev1+g4b33a80.d20240129", "0.1.1.dev1"),
    ("0.1.1.post0+g4b33a80.d20240129", "0.1.1.post0"),
    ("0.1.1.a1dev1+g4b33a80.d20240129", "0.1.1a1.dev1"),
    ("0.1.1.alpha1dev1+g4b33a80.d20240129", "0.1.1a1.dev1"),
    ("0.1.1.b1dev1+g4b33a80.d20240129", "0.1.1b1.dev1"),
    ("0.1.1.beta1dev1+g4b33a80.d20240129", "0.1.1b1.dev1"),
    ("0.1.1.rc1dev1+g4b33a80.d20240129", "0.1.1rc1.dev1"),
)
ids_valids = [
    "major minor patch",
    "dev0 with locals",
    "dev1 with locals",
    "post-release 0",
    "pre-release a1 dev1",
    "pre-release alpha1 dev1",
    "pre-release b1 dev1",
    "pre-release beta1 dev1",
    "release candidate dev1",
]

testdata_invalids = (("0.1.1.candidate1dev1+g4b33a80.d20240129", "0.1.1rc1.dev1"),)
ids_invalids = [
    "candidate is not a valid alias of rc",
]


@pytest.mark.parametrize(
    "v_in, expected",
    testdata_valids,
    ids=ids_valids,
)
def test_advertised_version_and_url(v_in, expected):
    """Check excepted versions and url occur"""
    v_actual = sanitize_tag(v_in)
    assert v_actual == expected
    assert expected in readthedocs_url(expected)


def test_setuptools_scm_version_file():
    """Autogenerated file by setuptools-scm"""
    if len(__version_tuple__) == 3:
        # 0.0.1
        ver = list(__version_tuple__)
        ver_short = ".".join(map(str, ver))
        ver_long = ver_short
        assert __version__ == f"{ver_long}"
    else:
        # 0.0.1.a1dev8
        ver = list(__version_tuple__[:3])
        ver_short = ".".join(map(str, ver))
        ver_dev = __version_tuple__[3]
        # ver_git = __version_tuple__[-1]
        ver_long = f"{ver_short}"
        if len(ver_dev) != 0:
            ver_long += f".{ver_dev}"

        # If no tags ver_git will not match, ignore (version) local
        left_side = sanitize_tag(__version__)
        right_side = sanitize_tag(ver_long)
        assert left_side == right_side


@pytest.mark.parametrize(
    "v_in, expected",
    testdata_invalids,
    ids=ids_invalids,
)
def test_sanitize_invalids(v_in, expected):
    with pytest.raises(ValueError):
        sanitize_tag(v_in)


testdata_strip_these = (
    ("1!1.0.1a1.dev1", "1.0.1a1.dev1"),
    ("1.0.1a1.dev1+4b33a80.4b33a80", "1.0.1a1.dev1"),
)
ids_strip_these = [
    "Strip epoch",
    "Strip locals",
]


@pytest.mark.parametrize(
    "v_in, expected",
    testdata_strip_these,
    ids=ids_strip_these,
)
def test_strip_epoch_and_locals(v_in, expected):
    """Convert repo version --> semantic version"""
    actual = sanitize_tag(v_in)
    assert actual == expected


testdata_vals = (
    (
        (0, 0, 1),
        {"releaselevel": "alpha", "serial": 0, "dev": 0},
        "0.0.1a0",
    ),
    (
        (0, 0, 1),
        {"releaselevel": "beta", "serial": 0, "dev": 0},
        "0.0.1b0",
    ),
    (
        (0, 0, 1),
        {"releaselevel": "candidate", "serial": 0, "dev": 0},
        "0.0.1rc0",
    ),
    (
        (0, 0, 1),
        {"releaselevel": "", "serial": 0, "dev": 0},
        "0.0.1",
    ),
    (
        (0, 0, 1),
        {"releaselevel": "alpha", "serial": 3, "dev": 10},
        "0.0.1a3.dev10",
    ),
    (
        (0, 0, 1),
        {"releaselevel": "post", "serial": 3, "dev": 0},
        "0.0.1post3",
    ),
)


@pytest.mark.parametrize(
    "args, kwargs, actual",
    testdata_vals,
)
def test_finals(args, kwargs, actual):
    """Used for display only. Allows release level, final"""
    # Flip the logic backwards
    finals = (
        None,
        0.12345,  # unsupported type
        False,
    )
    for final in finals:
        expect_info, expect_dev = get_version(
            actual,
            is_use_final=final,
        )
        assert kwargs["dev"] == expect_dev
        assert kwargs["serial"] == expect_info[-1]
        if len(kwargs["releaselevel"]) == 0:
            assert len(expect_info[-2]) == 0
        else:
            assert kwargs["releaselevel"] == expect_info[-2]
        assert args == expect_info[:3]


def test_final_allow():
    # Allow final
    actual = "1.0.1"
    l_actual = actual.split(".")
    l_actual2 = map(int, iter(l_actual))
    t_actual = tuple(l_actual2)
    expect_info, expect_dev = get_version(
        actual,
        is_use_final=True,
    )
    assert 0 == expect_dev
    assert 0 == expect_info[-1]
    assert "final" == expect_info[-2]
    assert t_actual == expect_info[:3]


testdata_dev_pres = (
    ("0.1.1.a1dev1+g4b33a80.d20240129", "0.1.1a1.dev1"),
    ("0.1.1.alpha1dev1+g4b33a80.d20240129", "0.1.1a1.dev1"),
    ("0.1.1.b1dev1+g4b33a80.d20240129", "0.1.1b1.dev1"),
    ("0.1.1.beta1dev1+g4b33a80.d20240129", "0.1.1b1.dev1"),
    ("0.1.1.rc1dev1+g4b33a80.d20240129", "0.1.1rc1.dev1"),
)
ids_dev_pres = (
    "a1.dev1",
    "alpha1dev1",
    "b1dev1",
    "beta1dev1",
    "rc1dev1",
)


@pytest.mark.parametrize(
    "v_in, expected_in",
    testdata_dev_pres,
    ids=ids_dev_pres,
)
def test_dev_and_prerelease(v_in, expected_in):
    # Has both dev and is a prerelease
    expected = sanitize_tag(v_in)
    expect_info, expect_dev = get_version(expected)

    v = Version(expected)

    # v_pre = v.pre
    # v_pre_is = v.is_prerelease
    v_dev = v.dev

    # long format
    pre = expect_info[-2]
    assert pre in _map_release.keys()

    found_k = None
    for k, v in _map_release.items():
        if pre == k:
            found_k = k

    assert expect_dev == v_dev

    assert found_k is not None
    # pre is long format. So ``alpha`` rather than ``a``
    assert pre == found_k


testdata_dev_no_pres = (
    ("0.1.1.a1dev1+g4b33a80.d20240129", "0!0.1.1.dev1+g4b33a80.d20240129"),
    ("0.1.1.alpha1dev1+g4b33a80.d20240129", "0!0.1.1.dev0+g4b33a80.d20240129"),
    ("0.1.1.b1dev1+g4b33a80.d20240129", "0!0.1.1dev8+g4b33a80.d20240129"),
)
ids_dev_no_pres = [
    ".dev1",
    ".dev0",
    "dev8",
]


@pytest.mark.parametrize(
    "v_in, expected_in",
    testdata_dev_no_pres,
    ids=ids_dev_no_pres,
)
def test_dev_and_prerelease_no(v_in, expected_in):
    """Has dev and no releaselevel"""

    expected = sanitize_tag(expected_in)
    expect_info, expect_dev = get_version(expected)

    v = Version(expected)

    v_pre = v.pre
    # v_pre_is = v.is_prerelease
    v_dev = v.dev
    assert expect_dev == v_dev
    assert v_pre is None


testdata_post_only = (
    ("0.1.1.post0+g4b33a80.d20240129", "0.1.1.post0", 0),
    ("0.1.1.post8", "0.1.1.post8", 8),
    ("0.1.1.post5", "0.1.1post5", 5),
)
ids_post_only = [
    "post0 with locals",
    "post8 no locals",
    "post5 no locals",
]


@pytest.mark.parametrize(
    "v_in, expected_in, post_no",
    testdata_post_only,
    ids=ids_post_only,
)
def test_post_only(v_in, expected_in, post_no):
    """post only"""
    expected_post = post_no
    expected = sanitize_tag(v_in)
    expect_info, expect_dev = get_version(expected)

    v = Version(expected)

    v_post = v.post
    v_post_is = v.is_postrelease
    v_pre_is = v.is_prerelease
    assert v_post_is is True
    assert v_pre_is is False
    assert v_post == expected_post
    assert expect_info[-2] == "post"


testdata_package_name = (
    ("this-that"),
    ("this_that"),
)
ids_package_name = [
    "package name has hyphens",
    "app_name has underscores",
]


@pytest.mark.parametrize("package_name", testdata_package_name, ids=ids_package_name)
def test_readthedocs_package_name(package_name):
    ver_ = (
        None,
        "latest",
        "0.0.1",
    )
    for ver in ver_:
        str_url = readthedocs_url(package_name, ver_=ver)
        protocol_len = len("https://")
        uri = str_url[protocol_len:]
        package_name = uri.split(".")[0]
        assert "_" not in package_name