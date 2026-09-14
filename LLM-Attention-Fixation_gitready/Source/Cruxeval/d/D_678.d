import std.math;
import std.typecons;
import std.array;
import std.algorithm;
import std.string;

Nullable!(long[string]) f(string text) 
{
    long[string] freq;
    foreach (c; text.toLower().split(""))
    {
        if (c in freq)
        {
            freq[c] += 1;
        }
        else
        {
            freq[c] = 1;
        }
    }
    return Nullable!(long[string])(freq);
}
unittest
{
    alias candidate = f;

{
        auto result = candidate("HI");
        assert(!result.isNull && result.get == ["h": 1L, "i": 1L]);
}

}
void main(){}
