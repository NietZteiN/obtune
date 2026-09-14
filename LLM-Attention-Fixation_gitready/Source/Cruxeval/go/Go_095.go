package f_test

import (
    "testing"
    "fmt"
)

func f(zoo map[string]string) map[string]string {
    result := make(map[string]string)
    for k, v := range zoo {
        result[v] = k
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
     { actual: candidate(map[string]string{"AAA": "fr"}), expected: map[string]string{"fr": "AAA"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
