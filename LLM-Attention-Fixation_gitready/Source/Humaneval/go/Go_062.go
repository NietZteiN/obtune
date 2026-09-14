
// xs represent coefficients of a polynomial.
// xs[0] + xs[1] * x + xs[2] * x^2 + ....
// Return Derivative of this polynomial in the same form.
// >>> Derivative([3, 1, 2, 4, 5])
// [1, 4, 12, 20]
// >>> Derivative([1, 2, 3])
// [2, 6]
func Derivative(xs []int) []int {

    l := len(xs)
	y := make([]int, l - 1)
	for i := 0; i < l - 1; i++ {
		y[i] = xs[i + 1] * (i + 1)
	}
	return y
}

func TestDerivative(t *testing.T) {
    assert := assert.New(t)
    assert.Equal([]int{1, 4, 12, 20}, Derivative([]int{3, 1, 2, 4, 5}))
    assert.Equal([]int{2, 6}, Derivative([]int{1, 2, 3}))
    assert.Equal([]int{2, 2}, Derivative([]int{3, 2, 1}))
    assert.Equal([]int{2, 2, 0, 16}, Derivative([]int{3, 2, 1,0, 4}))
    assert.Equal([]int{}, Derivative([]int{1}))
}
