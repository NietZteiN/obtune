import (
    "strconv"
)

// Change numerical base of input number x to base.
// return string representation after the conversion.
// base numbers are less than 10.
// >>> ChangeBase(8, 3)
// '22'
// >>> ChangeBase(8, 2)
// '1000'
// >>> ChangeBase(7, 2)
// '111'
func ChangeBase(x int, base int) string {

    if x >= base {
        return ChangeBase(x/base, base) + ChangeBase(x%base, base)
    }
    return strconv.Itoa(x)
}

func TestChangeBase(t *testing.T) {
    assert := assert.New(t)
    assert.Equal("22", ChangeBase(8, 3))
    assert.Equal("100", ChangeBase(9, 3))
    assert.Equal("11101010", ChangeBase(234, 2))
    assert.Equal("10000", ChangeBase(16, 2))
    assert.Equal("1000", ChangeBase(8, 2))
    assert.Equal("111", ChangeBase(7, 2))
    for i := 2; i < 8; i++ {
        assert.Equal(strconv.Itoa(i), ChangeBase(i, i+1))
    }
}
