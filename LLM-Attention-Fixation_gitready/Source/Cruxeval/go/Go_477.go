package f_test

import (
    "testing"
    "fmt"
    "strings"
)

func f(text string) []interface{} {
    split := strings.Split(text, "|")
    topic := split[0]
    problem := split[1]
    if problem == "r" {
        problem = strings.ReplaceAll(topic, "u", "p")
    }
    return []interface{}{topic, problem}
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("|xduaisf"), expected: []interface{}{"", "xduaisf"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
