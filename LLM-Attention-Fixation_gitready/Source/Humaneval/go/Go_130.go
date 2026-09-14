
// Everyone knows Fibonacci sequence, it was studied deeply by mathematicians in
// the last couple centuries. However, what people don't know is Tribonacci sequence.
// Tribonacci sequence is defined by the recurrence:
// Tri(1) = 3
// Tri(n) = 1 + n / 2, if n is even.
// Tri(n) =  Tri(n - 1) + Tri(n - 2) + Tri(n + 1), if n is odd.
// For example:
// Tri(2) = 1 + (2 / 2) = 2
// Tri(4) = 3
// Tri(3) = Tri(2) + Tri(1) + Tri(4)
// = 2 + 3 + 3 = 8
// You are given a non-negative integer number n, you have to a return a list of the
// first n + 1 numbers of the Tribonacci sequence.
// Examples:
// Tri(3) = [1, 3, 2, 8]
func Tri(n int) []float64 {

    if n == 0 {
        return []float64{1}
    }
    my_tri := []float64{1, 3}
    for i := 2; i < n + 1; i++ {
        if i &1 == 0 {
            my_tri = append(my_tri, float64(i) / 2 + 1)
        } else {
            my_tri = append(my_tri, my_tri[i - 1] + my_tri[i - 2] + (float64(i) + 3) / 2)
        }
    }
    return my_tri
}

func TestTri(t *testing.T) {
    assert := assert.New(t)
    assert.Equal([]float64{1, 3, 2.0, 8.0}, Tri(3))
    assert.Equal([]float64{1, 3, 2.0, 8.0, 3.0}, Tri(4))
    assert.Equal([]float64{1, 3, 2.0, 8.0, 3.0, 15.0}, Tri(5))
    assert.Equal([]float64{1, 3, 2.0, 8.0, 3.0, 15.0, 4.0}, Tri(6))
    assert.Equal([]float64{1, 3, 2.0, 8.0, 3.0, 15.0, 4.0, 24.0}, Tri(7))
    assert.Equal([]float64{1, 3, 2.0, 8.0, 3.0, 15.0, 4.0, 24.0, 5.0}, Tri(8))
    assert.Equal([]float64{1, 3, 2.0, 8.0, 3.0, 15.0, 4.0, 24.0, 5.0, 35.0}, Tri(9))
    assert.Equal([]float64{1, 3, 2.0, 8.0, 3.0, 15.0, 4.0, 24.0, 5.0, 35.0, 6.0, 48.0, 7.0, 63.0, 8.0, 80.0, 9.0, 99.0, 10.0, 120.0, 11.0}, Tri(20))
    assert.Equal([]float64{1}, Tri(0))
    assert.Equal([]float64{1, 3}, Tri(1))
}
