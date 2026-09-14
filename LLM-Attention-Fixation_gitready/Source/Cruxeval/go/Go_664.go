package f_test

import (
    "testing"
    "fmt"
)

func f(tags map[string]string) string {
    resp := ""
    for key := range tags {
        resp += key + " "
    }
    return resp
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[string]string{"3": "3", "4": "5"}), expected: "3 4 " },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
