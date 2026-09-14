package f_test

import (
    "testing"
    "fmt"
)

func f(text string, suffix string) string {
    if string(suffix[0]) == "/" {
        return text + suffix[1:]
    }
    return text
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("hello.txt", "/"), expected: "hello.txt" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
