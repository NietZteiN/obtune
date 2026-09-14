package f_test

import (
    "testing"
    "fmt"
)

func f(fields []interface{}, update_dict map[string]string) map[string]string {
    di := make(map[string]string)
    for _, field := range fields {
        di[field.(string)] = ""
    }
    for key, value := range update_dict {
        di[key] = value
    }
    return di
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]interface{}{"ct", "c", "ca"}, map[string]string{"ca": "cx"}), expected: map[string]string{"ct": "", "c": "", "ca": "cx"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
