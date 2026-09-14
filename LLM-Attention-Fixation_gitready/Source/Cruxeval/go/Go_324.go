package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int) []int {
    asc := make([]int, len(nums))
    copy(asc, nums)
    desc := make([]int, len(nums))
    
    for i, j := 0, len(asc)-1; i < len(asc); i, j = i+1, j-1 {
        desc[i] = asc[j]
    }

    desc = desc[:len(asc)/2]
    return append(append(desc, asc...), desc...)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{}), expected: []int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
