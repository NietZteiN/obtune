package f_test

import (
    "testing"
    "fmt"
)

func f(list_x []int) []int {
    item_count := len(list_x)
    new_list := make([]int, 0)
    for i := 0; i < item_count; i++ {
        new_list = append(new_list, list_x[len(list_x)-1])
        list_x = list_x[:len(list_x)-1]
    }
    return new_list
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{5, 8, 6, 8, 4}), expected: []int{4, 8, 6, 8, 5} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
