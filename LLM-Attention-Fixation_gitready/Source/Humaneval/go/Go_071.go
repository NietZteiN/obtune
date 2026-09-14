import (
    "math"
)

// Given the lengths of the three sides of a triangle. Return the area of
// the triangle rounded to 2 decimal points if the three sides form a valid triangle.
// Otherwise return -1
// Three sides make a valid triangle when the sum of any two sides is greater
// than the third side.
// Example:
// TriangleArea(3, 4, 5) == 6.00
// TriangleArea(1, 2, 10) == -1
func TriangleArea(a float64, b float64, c float64) interface{} {

    if a+b <= c || a+c <= b || b+c <= a {
		return -1
	}
	s := (a + b + c) / 2
	area := math.Pow(s * (s - a) * (s - b) * (s - c), 0.5)
	area = math.Round(area*100)/100
	return area
}

func TestTriangleArea(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(6.00, TriangleArea(3, 4, 5))
    assert.Equal(-1, TriangleArea(1, 2, 10))
    assert.Equal(8.18, TriangleArea(4, 8, 5))
    assert.Equal(1.73, TriangleArea(2, 2, 2))
    assert.Equal(-1, TriangleArea(1, 2, 3))
    assert.Equal(16.25, TriangleArea(10, 5, 7))
    assert.Equal(-1, TriangleArea(2, 6, 3))
    assert.Equal(0.43, TriangleArea(1, 1, 1))
    assert.Equal(-1, TriangleArea(2, 2, 10))
}
