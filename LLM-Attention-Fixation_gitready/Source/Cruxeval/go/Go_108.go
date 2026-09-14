package f_test

import (
	"testing"
	"reflect"
	"fmt"
)

func f(varr interface{}) int {
	amount := 0
	if reflect.TypeOf(varr).Kind() == reflect.Slice || reflect.TypeOf(varr).Kind() == reflect.Array {
		amount = reflect.ValueOf(varr).Len()
	} else if reflect.TypeOf(varr).Kind() == reflect.Map {
		amount = len(reflect.ValueOf(varr).MapKeys())
	}

	nonzero := 0
	if amount > 0 {
		nonzero = amount
	}
	return nonzero
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(1), expected: 0 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
