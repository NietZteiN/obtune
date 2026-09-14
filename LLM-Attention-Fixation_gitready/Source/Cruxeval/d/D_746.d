import std.math;
import std.typecons;
import std.stdio;
import std.string;

Nullable!(string[string]) f(Nullable!(string[string]) dct) 
{
    Nullable!(string[string]) result;
    if (dct.isNull) {
        return result;
    }

    foreach (value; dct.get().byValue)
    {
        string item = value.split('.')[0] ~ "@pinc.uk";
        result.get()[value] = item;
    }

    return result;
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
