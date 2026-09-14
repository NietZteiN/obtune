
// Create a function that takes 3 numbers.
// Returns true if one of the numbers is equal to the sum of the other two, and all numbers are integers.
// Returns false in any other cases.
// 
// Examples
// AnyInt(5, 2, 7) ➞ true
// 
// AnyInt(3, 2, 2) ➞ false
// 
// AnyInt(3, -2, 1) ➞ true
// 
// AnyInt(3.6, -2.2, 2) ➞ false
func AnyInt(x, y, z interface{}) bool {

    xx, ok := x.(int)
    if !ok {
        return false
    }
    yy, ok := y.(int)
    if !ok {
        return false
    }
    zz, ok := z.(int)
    if !ok {
        return false
    }

    if (xx+yy == zz) || (xx+zz == yy) || (yy+zz == xx) {
        return true
    }
    return false
}

func TestAnyInt(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(true, AnyInt(2, 3, 1))
    assert.Equal(false, AnyInt(2.5, 2, 3))
    assert.Equal(false, AnyInt(1.5, 5, 3.5))
    assert.Equal(false, AnyInt(2, 6, 2))
    assert.Equal(true, AnyInt(4, 2, 2))
    assert.Equal(false, AnyInt(2.2, 2.2, 2.2))
    assert.Equal(true, AnyInt(-4, 6, 2))
    assert.Equal(true, AnyInt(2, 1, 1))
    assert.Equal(true, AnyInt(3, 4, 7))
    assert.Equal(false, AnyInt(3.0, 4, 7))
}
