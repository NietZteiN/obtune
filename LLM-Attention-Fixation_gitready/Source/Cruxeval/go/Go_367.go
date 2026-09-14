package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int, rmvalue int) []int {
    res := make([]int, len(nums))
    copy(res, nums)
    
    for i := 0; i < len(res); {
        if res[i] == rmvalue {
            res = append(res[:i], res[i+1:]...)
        } else {
            i++
        }
    }
    
    return res
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{6, 2, 1, 1, 4, 1}, 5), expected: []int{6, 2, 1, 1, 4, 1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
