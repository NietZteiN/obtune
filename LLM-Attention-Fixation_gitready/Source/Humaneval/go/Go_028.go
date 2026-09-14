
// Concatenate list of strings into a single string
// >>> Concatenate([])
// ''
// >>> Concatenate(['a', 'b', 'c'])
// 'abc'
func Concatenate(strings []string) string {

    if len(strings) == 0 {
		return ""
	}
	return strings[0] + Concatenate(strings[1:])
}

func TestConcatenate(t *testing.T) {
    assert := assert.New(t)
    assert.Equal("", Concatenate([]string{}))
    assert.Equal("xyz", Concatenate([]string{"x", "y", "z"}))
    assert.Equal("xyzwk", Concatenate([]string{"x", "y","z", "w", "k"}))
}
