
// Given the lengths of the three sides of a triangle. Return true if the three
// sides form a right-angled triangle, false otherwise.
// A right-angled triangle is a triangle in which one angle is right angle or
// 90 degree.
// Example:
// RightAngleTriangle(3, 4, 5) == true
// RightAngleTriangle(1, 2, 3) == false
func RightAngleTriangle(a, b, c int) bool {

    return a*a == b*b + c*c || b*b == a*a + c*c || c*c == a*a + b*b
}

func TestRightAngleTriangle(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(true, RightAngleTriangle(3, 4, 5))
    assert.Equal(false, RightAngleTriangle(1, 2, 3))
    assert.Equal(true, RightAngleTriangle(10, 6, 8))
    assert.Equal(false, RightAngleTriangle(2, 2, 2))
    assert.Equal(true, RightAngleTriangle(7, 24, 25))
    assert.Equal(false, RightAngleTriangle(10, 5, 7))
    assert.Equal(true, RightAngleTriangle(5, 12, 13))
    assert.Equal(true, RightAngleTriangle(15, 8, 17))
    assert.Equal(true, RightAngleTriangle(48, 55, 73))
    assert.Equal(false, RightAngleTriangle(1, 1, 1))
    assert.Equal(false, RightAngleTriangle(2, 2, 10))
}
