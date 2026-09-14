import std.math;
import std.typecons;
import std.algorithm;
import std.array;

Nullable!(long[string]) f(string[] values, long value) 
{
    long[string] new_dict;
    foreach (v; values)
    {
        new_dict[v] = value;
    }
    new_dict[values.sort().array.join] = value * 3;
    return new_dict.nullable;
}
unittest
{
    alias candidate = f;

{
        auto result = candidate(["0", "3"], 117L);
        assert(!result.isNull && result.get == ["0": 117L, "3": 117L, "03": 351L]);
}

}
void main(){}
