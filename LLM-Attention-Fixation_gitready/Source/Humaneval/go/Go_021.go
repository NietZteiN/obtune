
// Given list of numbers (of at least two elements), apply a linear transform to that list,
// such that the smallest number will become 0 and the largest will become 1
// >>> RescaleToUnit([1.0, 2.0, 3.0, 4.0, 5.0])
// [0.0, 0.25, 0.5, 0.75, 1.0]
func RescaleToUnit(numbers []float64) []float64 {

    smallest := numbers[0]
	largest := smallest
	for _, n := range numbers {
		if smallest > n {
			smallest = n
		}
		if largest < n {
			largest = n
		}
	}
	if smallest == largest {
		return numbers
	}
	for i, n := range numbers {
		numbers[i] = (n - smallest) / (largest - smallest)
	}
	return numbers
}

func TestRescaleToUnit(t *testing.T) {
    assert := assert.New(t)
    assert.Equal([]float64{0.0, 1.0}, RescaleToUnit([]float64{2.0, 49.9}))
    assert.Equal([]float64{1.0, 0.0}, RescaleToUnit([]float64{100.0, 49.9}))
    assert.Equal([]float64{0.0, 0.25, 0.5, 0.75, 1.0}, RescaleToUnit([]float64{1.0, 2.0, 3.0, 4.0, 5.0}))
    assert.Equal([]float64{0.25, 0.0, 1.0, 0.5, 0.75}, RescaleToUnit([]float64{2.0, 1.0, 5.0, 3.0, 4.0}))
    assert.Equal([]float64{0.25, 0.0, 1.0, 0.5, 0.75}, RescaleToUnit([]float64{12.0, 11.0, 15.0, 13.0, 14.0}))
}
