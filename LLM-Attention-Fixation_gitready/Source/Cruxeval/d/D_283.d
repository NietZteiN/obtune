import std.typecons;

string f(Nullable!(long[string]) dictionary, string key) 
{
    if (dictionary.isNull)
    {
        return key;
    }

    dictionary.get().remove(key);
    if (dictionary.get().length > 0 && dictionary.get().keys[0] == key)
    {
        key = dictionary.get().keys[1];
    }
    return key;
}

unittest
{
    alias candidate = f;

    assert(candidate(["Iron Man": 4L, "Captain America": 3L, "Black Panther": 0L, "Thor": 1L, "Ant-Man": 6L].nullable, "Iron Man") == "Iron Man");
}
void main(){}
