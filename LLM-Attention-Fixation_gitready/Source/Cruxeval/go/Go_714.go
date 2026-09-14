package f_test

import (
    "testing"
    "fmt"
)

func f(array []int) []string {
    for i, j := 0, len(array)-1; i < j; i, j = i+1, j-1 {
        array[i], array[j] = array[j], array[i]
    }
    array = []int{}
    for i := 0; i < len(array); i++ {
        array = append(array, 'x')
    }
    for i, j := 0, len(array)-1; i < j; i, j = i+1, j-1 {
        array[i], array[j] = array[j], array[i]
    }
    result := []string{}
    for _, v := range array {
        result = append(result, string(rune(v)))
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
     { actual: candidate([]int{3, -2, 0}), expected: []string{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
