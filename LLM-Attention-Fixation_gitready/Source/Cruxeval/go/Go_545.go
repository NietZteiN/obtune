package f_test

import (
    "testing"
    "fmt"
)

func f(array []int) []int {
    var result []int
    index := 0
    for index < len(array) {
        result = append(result, array[len(array)-1])
        array = array[:len(array)-1]
        index += 2
    }
    return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{8, 8, -4, -9, 2, 8, -1, 8}), expected: []int{8, -1, 8} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
