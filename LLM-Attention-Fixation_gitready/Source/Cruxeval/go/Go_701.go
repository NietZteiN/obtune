package f_test

import (
    "testing"
    "fmt"
    "strings"
)

func f(stg string, tabs []string) string {
    for _, tab := range tabs {
        stg = strings.TrimRight(stg, tab)
    }
    return stg
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("31849 let it!31849 pass!", []string{"3", "1", "8", " ", "1", "9", "2", "d"}), expected: "31849 let it!31849 pass!" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
