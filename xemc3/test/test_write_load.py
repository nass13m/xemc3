import xemc3
import gen_ds
import tempfile
import numpy as np
from xemc3.core.utils import prod
from hypothesis import given, assume, settings
import hypothesis.strategies as strat


def assert_ds_are_equal(d1, d2, check_attrs=True, rtol=1e-2, atol=1e-6):
    print()
    print(xemc3.core.load.files["LG_CELL"], xemc3.core.load._files_bak["LG_CELL"])
    print()
    d1k = [k for k in d1] + [k for k in d1.coords]
    d2k = [k for k in d2] + [k for k in d2.coords]
    if not set(d1k) == set(d2k):
        raise AssertionError(f"{d1.keys()} != {d2.keys()}")
    for k in d1:
        data_org = d1[k].data
        data_load = d2[k].data
        slc = np.isfinite(data_org)
        if not np.isclose(d1[k].data[slc], d2[k].data[slc], rtol=rtol).all():
            raise AssertionError(
                f"""var {k} is changed.
Before: {d1[k].data}

After: {d2[k].data}

np.isclose: {np.isclose(d1[k], d2[k],rtol=rtol).flatten()}"""
            )
        if check_attrs:
            if d1[k].attrs != d2[k].attrs:
                raise AssertionError(
                    f"attributes changed for {k}: {d1[k].attrs} != {d2[k].attrs}"
                )


@settings(deadline=None)
@given(strat.lists(strat.integers(min_value=1), min_size=3, max_size=3))
def test_write_load_simple(shape):
    assume(prod(shape) < 1e3)
    ds = gen_ds.gen_ds(shape)
    with tempfile.TemporaryDirectory() as dir:
        # print(ds)
        # print(ds["_plasma_map"])
        xemc3.write.fortran(ds, dir)
        dl = xemc3.load(dir)
        assert_ds_are_equal(ds, dl, False, 1e-2, 1e-2)
    with tempfile.TemporaryDirectory() as dir:
        xemc3.write.fortran.all(dl, dir)
        dn = xemc3.load.all(dir)
        # print(xemc3.core.load.files)
        assert_ds_are_equal(dl, dn, True, 1e-4)


@settings(deadline=None)
@given(strat.lists(strat.integers(min_value=1, max_value=100), min_size=3, max_size=3))
def test_write_load_full(shape):
    assume(prod(shape) < 1e3)
    ds = gen_ds.gen_full(shape)
    # if True:
    #    dir = "xemc3/test/test"
    with tempfile.TemporaryDirectory() as dir:
        xemc3.write.fortran(ds, dir)
        dl = xemc3.load(dir)
        assert_ds_are_equal(ds, dl, True, 1e-2, 1e-2)
    with tempfile.TemporaryDirectory() as dir:
        xemc3.write.fortran.all(dl, dir)
        dn = xemc3.load.all(dir)
        # print(xemc3.core.load.files)
        assert_ds_are_equal(dl, dn, True, 1e-4)


if __name__ == "__main__":
    test_write_load_full()