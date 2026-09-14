package f_test

import (
    "testing"
    "fmt"
    "strings"
)

func f(mess string, char string) string {
    for strings.Contains(mess[strings.LastIndex(mess, char)+1:], char) {
        mess = mess[:strings.LastIndex(mess, char)+1] + mess[strings.LastIndex(mess, char)+2:]
    }
    return mess
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("0aabbaa0b", "a"), expected: "0aabbaa0b" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
