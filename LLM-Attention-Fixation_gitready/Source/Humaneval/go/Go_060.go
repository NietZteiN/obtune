
// SumToN is a function that sums numbers from 1 to n.
// >>> SumToN(30)
// 465
// >>> SumToN(100)
// 5050
// >>> SumToN(5)
// 15
// >>> SumToN(10)
// 55
// >>> SumToN(1)
// 1
func SumToN(n int) int {

    if n <= 0 {
		return 0
	} else {
		return n + SumToN(n - 1)
	}
}

func TestSumToN(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(1, SumToN(1))
    assert.Equal(21, SumToN(6))
    assert.Equal(66, SumToN(11))
    assert.Equal(465, SumToN(30))
    assert.Equal(5050, SumToN(100))
}
