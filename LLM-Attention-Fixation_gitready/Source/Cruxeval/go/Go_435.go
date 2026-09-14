package f_test

import (
    "testing"
    "fmt"
    "strings"
)

func f(numbers []string, num int, val int) string {
    for len(numbers) < num {
        numbers = append(numbers[:len(numbers) / 2], append([]string{fmt.Sprintf("%d", val)}, numbers[len(numbers) / 2:]...)...)
    }
    for i := 0; i < len(numbers) / (num-1) - 4; i++ {
        numbers = append(numbers[:len(numbers) / 2], append([]string{fmt.Sprintf("%d", val)}, numbers[len(numbers) / 2:]...)...)
    }
    return strings.Join(numbers, " ")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{}, 0, 1), expected: "" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
