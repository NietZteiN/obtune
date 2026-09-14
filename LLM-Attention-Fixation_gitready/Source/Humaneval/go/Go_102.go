
// This function takes two positive numbers x and y and returns the
// biggest even integer number that is in the range [x, y] inclusive. If
// there's no such number, then the function should return -1.
// 
// For example:
// ChooseNum(12, 15) = 14
// ChooseNum(13, 12) = -1
func ChooseNum(x, y int) int {

    if x > y {
        return -1
    }
    if y % 2 == 0 {
        return y
    }
    if x == y {
        return -1
    }
    return y - 1
}

func TestChooseNum(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(14, ChooseNum(12,15))
    assert.Equal(-1, ChooseNum(13,12))
    assert.Equal(12354, ChooseNum(33,12354))
    assert.Equal(-1, ChooseNum(5234,5233))
    assert.Equal(28, ChooseNum(6,29))
    assert.Equal(-1, ChooseNum(27,10))
    assert.Equal(-1, ChooseNum(7,7))
    assert.Equal(546, ChooseNum(546,546))
}
