package f_test

import (
    "testing"
    "fmt"
)

func f(nums []string) []string {
    width := nums[0]
    result := []string{}
    for _, val := range nums[1:] {
        valFormatted := fmt.Sprintf("%0"+width+"s", val)
        result = append(result, valFormatted)
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
     { actual: candidate([]string{"1", "2", "2", "44", "0", "7", "20257"}), expected: []string{"2", "2", "44", "0", "7", "20257"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
