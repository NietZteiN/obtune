import std.math;
import std.typecons;

Nullable!(long[string]) f(Nullable!(long[string]) dictionary) 
{
    if (!dictionary.isNull) {
        long[string] newDictionary = dictionary.get;
        newDictionary["1049"] = 55;
        return Nullable!(long[string])(newDictionary);
    }
    return Nullable!(long[string]).init;
}
unittest
{
    alias candidate = f;

{
        auto result = candidate(["noeohqhk": 623L].nullable);
        assert(!result.isNull && result.get == ["noeohqhk": 623L, "1049": 55L]);
}

}
void main(){}
