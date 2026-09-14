package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int, target int) []interface{} {
    lows := make([]int, 0)
    higgs := make([]int, 0)
    for _, i := range nums {
        if i < target {
            lows = append(lows, i)
        } else {
            higgs = append(higgs, i)
        }
    }
    lows = nil
    result := make([]interface{}, 2)
    result[0] = lows
    result[1] = higgs
    return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{12, 516, 5, 2, 3, 214, 51}, 5), expected: []interface{}{[]interface{}{}, []int{12, 516, 5, 214, 51}} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
