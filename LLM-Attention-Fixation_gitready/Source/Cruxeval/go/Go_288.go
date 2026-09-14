The error is due to a missing closing parenthesis in the function signature of `TestF`. The function signature should be `func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[int]int{55: 4, 4: 555, 1: 3, 99: 21, 499: 4, 71: 7, 12: 6}), expected: [][]int{[]interface{}{1, 3}, []interface{}{4, 555}} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
