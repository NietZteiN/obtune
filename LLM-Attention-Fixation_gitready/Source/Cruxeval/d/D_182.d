import std.math;
import std.typecons;
import std.algorithm;
import std.array;

Tuple!(string, long)[] f(Nullable!(long[string]) dic) 
{
    Tuple!(string, long)[] output;
    if (!dic.isNull) 
    {
        foreach (key, value; dic.get()) 
        {
            output ~= tuple(key, value);
        }
        output.sort();
    }
    return output;
}
unittest
{
    alias candidate = f;

    assert(candidate(["b": 1L, "a": 2L].nullable) == [tuple("a", 2L), tuple("b", 1L)]);
}
void main(){}
