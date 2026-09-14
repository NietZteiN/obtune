
// Given length of a side and high return area for a triangle.
// >>> TriangleArea(5, 3)
// 7.5
func TriangleArea(a float64, h float64) float64 {

    return a * h / 2
}

func TestTriangleArea(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(7.5, TriangleArea(5, 3))
    assert.Equal(2.0, TriangleArea(2, 2))
    assert.Equal(40.0, TriangleArea(10, 8))
}
