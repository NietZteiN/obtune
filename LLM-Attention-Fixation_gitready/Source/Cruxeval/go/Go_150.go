package f_test

import (
    "testing"
    "fmt"
)

func f(numbers []int, index int) []int {
    for _, n := range numbers[index:] {
        numbers = append(numbers[:index], append([]int{n}, numbers[index:]...)...)
        index++
    }
    
    return numbers[:index]
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{-2, 4, -4}, 0), expected: []int{-2, 4, -4} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
