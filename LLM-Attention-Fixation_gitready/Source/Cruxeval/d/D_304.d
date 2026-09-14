import std.math;
import std.typecons;
import std.algorithm;
import std.array;

Nullable!(long[long]) f(Nullable!(long[long]) d) 
{
    if (!d.isNull && d.get.length > 1)
    {
        long[long] newDict;
        long key1 = d.get.keys.sort().back;
        long val1 = d.get[key1];
        d.get.remove(key1);
        long key2 = d.get.keys.sort().back;
        long val2 = d.get[key2];
        d.get.remove(key2);
        newDict[key1] = val1;
        newDict[key2] = val2;
        return Nullable!(long[long])(newDict);
    }
    return Nullable!(long[long]).init;
}
unittest
{
    alias candidate = f;

{
        auto result = candidate([2L: 3L, 17L: 3L, 16L: 6L, 18L: 6L, 87L: 7L].nullable);
        assert(!result.isNull && result.get == [87L: 7L, 18L: 6L]);
}

}
void main(){}
