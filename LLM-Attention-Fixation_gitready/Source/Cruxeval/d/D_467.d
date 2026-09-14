import std.math;
import std.typecons;

Nullable!(long[string]) f(Nullable!(string[string]) nums) 
{
    if (!nums.isNull) {
        auto copy = nums.get();
        auto newDict = new long[string];
        foreach (key, value; copy) {
            newDict[key] = value.length;
        }
        return Nullable!(long[string])(newDict);
    }
    return Nullable!(long[string]).init;
}
unittest
{
    alias candidate = f;

{
        auto result = candidate(Nullable!(string[string]).init);
        assert(result.isNull);
}

}
void main(){}
