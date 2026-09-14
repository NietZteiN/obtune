package f_test

import (
    "testing"
    "fmt"
    "strconv"
)

func f(array []int, const_int int) []string {
    output := []string{"x"}
    for i := 1; i < len(array) + 1; i++ {
        if i % 2 != 0 {
            output = append(output, strconv.Itoa(array[i - 1] * -2))
        } else {
            output = append(output, strconv.Itoa(const_int))
        }
    }
    return output
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 2, 3}, -1), expected: []string{"x", "-2", "-1", "-6"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
