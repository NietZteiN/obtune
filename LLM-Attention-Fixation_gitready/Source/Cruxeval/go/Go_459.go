package f_test

import (
    "testing"
    "fmt"
)

func f(arr []string, d map[string]string) map[string]string {
    for i := 1; i < len(arr); i += 2 {
        d[arr[i]] = arr[i-1]
    }

    return d
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"b", "vzjmc", "f", "ae", "0"}, map[string]string{}), expected: map[string]string{"vzjmc": "b", "ae": "f"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
