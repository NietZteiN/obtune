package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int, val int) int {
    var sum int
    for _, num := range nums {
        for i := 0; i < val; i++ {
            sum += num
        }
    }
    return sum
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{10, 4}, 3), expected: 42 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
