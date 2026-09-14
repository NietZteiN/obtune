
// Return length of given string
// >>> Strlen('')
// 0
// >>> Strlen('abc')
// 3
func Strlen(str string) int {

    return len(str)
}

func TestStrlen(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(0, Strlen(""))
    assert.Equal(1, Strlen("x"))
    assert.Equal(9, Strlen("asdasnakj"))
}
