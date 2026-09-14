
// Add two numbers x and y
// >>> Add(2, 3)
// 5
// >>> Add(5, 7)
// 12
func Add(x int, y int) int {

    return x + y
}

func TestAdd(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(1, Add(0, 1))
    assert.Equal(1, Add(1, 0))
    assert.Equal(5, Add(2, 3))
    assert.Equal(12, Add(5, 7))
    assert.Equal(12, Add(7, 5))
    for i := 0; i < 100; i++ {
        x := rand.Int31n(1000)
        y := rand.Int31n(1000)
        assert.Equal(int(x+y), Add(int(x), int(y)))
    }
}
