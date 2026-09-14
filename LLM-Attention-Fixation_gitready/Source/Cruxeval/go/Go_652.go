package f_test

import (
    "testing"
    "fmt"
)

func f(myString string) string {
    if myString == "" || myString[0] < '0' || myString[0] > '9' {
        return "INVALID"
    }
    cur := 0
    for i := 0; i < len(myString); i++ {
        cur = cur*10 + int(myString[i]-'0')
    }
    return fmt.Sprintf("%d", cur)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("3"), expected: "3" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
